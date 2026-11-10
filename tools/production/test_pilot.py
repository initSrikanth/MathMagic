"""Checkpoint/release safety tests; no media mutation, network or student data."""
import json
import os
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import pilot

class PilotTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.root = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)
    def test_cache_requires_pass_same_inputs_same_runtime_and_intact_log(self):
        log=self.root/'test.log';log.write_text('actual verification output')
        r={'status':'PASS','input_sha256':'key','runtime':{'node':'22'},'log_sha256':pilot.digest(log)}
        self.assertTrue(pilot.cache_valid(r,'key',{'node':'22'},log))
        for changed in [{**r,'status':'RUNNING'},{**r,'status':'FAIL'},{**r,'input_sha256':'changed'},{**r,'runtime':{'node':'24'}}]:
            self.assertFalse(pilot.cache_valid(changed,'key',{'node':'22'},log))
        log.write_text('tampered');self.assertFalse(pilot.cache_valid(r,'key',{'node':'22'},log))
    def test_rule_input_and_missing_file_invalidate_fingerprint(self):
        for f in ['rule','input','tools/production/pilot.py','tools/production/profiles/demo.json']:
            p=self.root/f;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('initial')
        p={'topic':'demo','rules':['rule'],'inputs':{'curriculum':['input']}}
        with patch.object(pilot,'ROOT',self.root):
            before=pilot.fingerprint(p,'curriculum');(self.root/'rule').write_text('new rule')
            self.assertNotEqual(before,pilot.fingerprint(p,'curriculum'))
            before=pilot.fingerprint(p,'curriculum');(self.root/'input').unlink()
            self.assertNotEqual(before,pilot.fingerprint(p,'curriculum'))
    def test_two_unchanged_failures_are_not_blindly_retried(self):
        pilot.write_json(self.root/'curriculum.json',{'input_sha256':'key','status':'FAIL','attempts':2})
        with patch.object(pilot,'fingerprint',return_value='key'),patch.object(pilot,'runtime',return_value={}),patch.object(pilot,'curriculum') as call:
            with self.assertRaisesRegex(RuntimeError,'two unchanged failures'):
                pilot.run_stage({},'curriculum',self.root,resume=True)
            call.assert_not_called()
    def test_ci_never_treats_local_cached_result_as_a_gate(self):
        log=self.root/'curriculum.log';log.write_text('old')
        pilot.write_json(self.root/'curriculum.json',{'input_sha256':'key','status':'PASS','runtime':{},'log_sha256':pilot.digest(log),'attempts':1})
        with patch.object(pilot,'fingerprint',return_value='key'),patch.object(pilot,'runtime',return_value={}),patch.dict('os.environ',{'CI':'true'}),patch.object(pilot,'curriculum',return_value={'fresh':True}) as call:
            r=pilot.run_stage({},'curriculum',self.root,resume=True)
            call.assert_called_once();self.assertEqual(r['evidence'],{'fresh':True})
    def test_partial_or_tampered_evidence_cannot_release(self):
        p={'topic':'demo','manual_evidence':'manual.json','manual_requirements':['listening']}
        for s in pilot.STAGES:
            log=self.root/(s+'.log');log.write_text('verified')
            pilot.write_json(self.root/(s+'.json'),{'input_sha256':'key','status':'PASS','log_sha256':pilot.digest(log),'run_id':os.environ.get('GITHUB_RUN_ID'),'source_commit':os.environ.get('GITHUB_SHA'),'worktree_dirty':False})
        with patch.object(pilot,'ROOT',self.root),patch.object(pilot,'fingerprint',return_value='key'),patch.object(pilot,'release',return_value={'lessons':[]}):
            r=pilot.report(p,self.root);self.assertFalse(r['release_ready']);self.assertEqual(r['manual_checks_unverified'],['listening'])
            pilot.write_json(self.root/'manual.json',{'listening':{'status':'PASS','reviewer':'owner','date':'2026-11-10','evidence_url':'https://github.com/owner/repo/issues/1'}})
            (self.root/'media.log').write_text('modified')
            r=pilot.report(p,self.root);self.assertFalse(r['release_ready']);self.assertEqual(r['stages']['media']['status'],'INVALID_EVIDENCE')
    def test_inventory_reports_other_topic_gaps_without_passing_them(self):
        (self.root/'video.mp4').write_bytes(b'fixture');(self.root/'captions.vtt').write_text('WEBVTT')
        good='<section id="lesson1"><video><source src="video.mp4"><track src="captions.vtt"></video><details>Transcript</details></section>'
        (self.root/'good.html').write_text(good);(self.root/'other.html').write_text('<section id="lesson1"><video><source src="video.mp4"></video></section>')
        with patch.object(pilot,'ROOT',self.root),patch.object(pilot.subprocess,'check_output',return_value='{}'):
            r=pilot.inventory({'audit_pages':['good.html','other.html'],'page':'good.html','lesson_count':1})
        self.assertEqual(r['audit_only_defects'],1);self.assertEqual(r['placements'][1]['issues'],['Missing captions','Missing transcript'])
    def test_successful_previous_runs_do_not_consume_failure_retry_allowance(self):
        pilot.write_json(self.root/'curriculum.json',{'input_sha256':'key','status':'PASS','attempts':8,'consecutive_failures':0})
        with patch.object(pilot,'fingerprint',return_value='key'),patch.object(pilot,'runtime',return_value={}),patch.object(pilot,'curriculum',side_effect=ValueError('temporary failure')):
            r=pilot.run_stage({},'curriculum',self.root,resume=True)
        self.assertEqual(r['status'],'FAIL');self.assertEqual(r['consecutive_failures'],1)
    def test_pr_deployment_checks_production_baseline_and_lists_unpublished_candidate(self):
        batch={'lessons':[{'src':'videos/a.mp4','captions':'videos/a.vtt','transcript':'videos/a.txt','poster':'videos/a.jpg'}]}
        files={f:b'production bytes' for f in ['page.html','css/topic.css','videos/a.mp4','videos/a.vtt','videos/a.txt','videos/a.jpg']}
        files['release.json']=json.dumps(batch).encode()
        for f,data in files.items():
            p=self.root/f;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
        (self.root/'css/topic.css').write_bytes(b'unpublished candidate bytes')
        class Response(io.BytesIO):
            status=200
        profile={'site':'https://example.test/','release':'release.json','site_assets':['page.html','css/topic.css']}
        def git(args,**kwargs):return files[args[-1].split(':',1)[1]]
        def fetch(req,**kwargs):return Response(files[req.full_url.replace(profile['site'],'')])
        with patch.object(pilot,'ROOT',self.root),patch.dict('os.environ',{'PILOT_DEPLOYMENT_BASE':'a'*40}),patch.object(pilot.subprocess,'check_output',side_effect=git),patch.object(pilot.urllib.request,'urlopen',side_effect=fetch):
            r=pilot.deployment(profile)
        self.assertEqual(r['unpublished_candidate_files'],['css/topic.css']);self.assertEqual(len(r['verified']),6)

if __name__=='__main__':unittest.main()
