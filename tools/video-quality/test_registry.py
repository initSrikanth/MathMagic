"""Policy/schema unit tests with explicit probe stubs; real media checked by registry.py.

Human approvals below exist ONLY in disposable fixtures, never production data.
"""
import copy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import contract
import registry as r


class RegistryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root/'video-agent/media-registry').mkdir(parents=True)
        shutil.copy(r.ROOT/r.SCHEMA, self.root/r.SCHEMA)
        self.write('old.mp4', b'original fixture packets')
        subprocess.run(['git','init','-q',str(self.root)],check=True)
        self.git('add','.'); self.git('-c','user.name=Fixture','-c','user.email=fixture@example.invalid','commit','-qm','Fixture baseline')
        self.base = self.git('rev-parse','HEAD').decode().strip()
        self.original = {'id':'topic-original','policy':'unchanged','status':'retained',
                         'assets':{'video':self.desc('old.mp4')},'packets':self.packets(self.root/'old.mp4')}
        self.cfg = copy.deepcopy(contract.load())
        # Fixture-only authorisation. Never changes the real, unapproved profile.
        self.cfg['approved_voice']['enhanced_enthusiasm_approval']={'record':'https://example.invalid/fixture-only'}
        self.cfg['media_registry'] = {'schema_version':1,'path':r.INDEX,'preservation_commit':self.base,
            'schema_sha256':r.digest((self.root/r.SCHEMA).read_bytes()),
            'preserved_inventory':{'topic':['topic-original']},
            'preserved_records_sha256':r.digest(json.dumps({'topic-original':self.original},sort_keys=True,separators=(',',':')).encode())}
        self.manifest = {'schema_version':1,'topic':'topic','records':[copy.deepcopy(self.original)],
                         'placements':[{'section':'lesson','record':'topic-original'}]}
        self.index = {'schema_version':1,'preservation_commit':self.base,'preserved':[],
                      'topics':[{'id':'topic','page':'topic.html','inventory':['topic-original'],'legacy_numbers':[],
                                 'manifest':{}}]}
        self.write('topic.html','<section id="lesson"><video><source src="old.mp4"></video></section>')
        self.addCleanup(patch.stopall)
        patch.object(contract,'load',return_value=self.cfg).start()
        patch.object(r,'packet_fingerprint',side_effect=self.packets).start()
        self.flush()

    def git(self,*args):
        return subprocess.check_output(['git',*args],cwd=self.root,stderr=subprocess.PIPE)

    def write(self,path,value):
        p=self.root/path;p.parent.mkdir(parents=True,exist_ok=True)
        p.write_bytes(value if isinstance(value,bytes) else value.encode())

    def dump(self,path,value): self.write(path,json.dumps(value))

    def desc(self,path):
        p=self.root/path;return {'path':path,'bytes':p.stat().st_size,'sha256':r.digest(p.read_bytes())}

    def packets(self,path):
        return {k:{'count':1,'sha256':r.digest(path.read_bytes()+k.encode())} for k in ('video','audio')}

    def flush(self):
        self.dump('topic.json',self.manifest)
        self.index['topics'][0]['manifest']=self.desc('topic.json')
        self.dump(r.INDEX,self.index)

    def load(self): self.flush();return r.load_registry(self.root)

    def proposed(self,policy='replacement',approved=False):
        self.write('new.mp4',b'new fixture packets')
        self.write('new.vtt','WEBVTT\n\n00:00:00.000 --> 00:00:01.000\nRead the clock.\n')
        self.write('new.txt','Read the clock.');self.write('poster.jpg',b'fixture')
        voice={k:self.cfg['approved_voice'][k] for k in ['speaker_id','model_sha256','voices_sha256']};voice['name']=self.cfg['approved_voice']['voice']
        self.dump('script.json',{'schema_version':1,'topic':'topic','title':'Time','text':'Read the clock.','curriculum':['AC9M5M03'],'voice':voice})
        self.write('producer.py','Fixture producer');self.write('verifier.py','Independent fixture verifier')
        self.dump('alignment.json',{'video_sha256':self.desc('new.mp4')['sha256'],
              'captions_sha256':self.desc('new.vtt')['sha256'],'transcript_sha256':self.desc('new.txt')['sha256'],
              'utterances':[{'text':'Read the clock.'}]})
        assets={k:self.desc(p) for k,p in {'video':'new.mp4','captions':'new.vtt','transcript':'new.txt','poster':'poster.jpg','script':'script.json','alignment':'alignment.json','producer':'producer.py'}.items()}
        checks=r.read(r.SCHEMA)['$defs']['verification']['properties']['checks']['required']
        proof={'schema_version':1,'subject':{k:v['sha256'] for k,v in assets.items()},'verifier':self.desc('verifier.py'),
               'checks':{k:'PASS' for k in checks},'flags':[], 'metrics':{'audio_rms':.1,'clipping_fraction':0,'decoded_frames':30}}
        self.dump('proof.json',proof);assets['verification']=self.desc('proof.json')
        row={'id':'topic-proposal','policy':policy,'status':'pending','assets':assets,'packets':self.packets(self.root/'new.mp4'),'human_approval':{'status':'pending'}}
        if policy=='replacement':row['replaces']='topic-original'
        if approved:
            row['status']='approved';row['human_approval']={'status':'approved','reviewer':'Fixture Human','reviewed_at':'2026-11-13',
                'reference':'https://example.invalid/fixture-only','subject':r.subject(row),'full_audio_listened':True,'full_video_viewed':True,'script_approved':True,'all_flags_reviewed':True}
        return row

    def probe(self):
        return patch.object(r.subprocess,'check_output',return_value=json.dumps({'streams':[{'codec_type':'video','codec_name':'h264','width':1920,'height':1080,'pix_fmt':'yuv420p'},{'codec_type':'audio','codec_name':'aac'}],'format':{'duration':'2'}}).encode())

    def test_retained_media_and_packets_validate(self):self.assertEqual(len(self.load()['records']),1)

    def test_pending_registration_is_not_release(self):
        row=self.proposed();self.manifest['records'].append(row);self.index['topics'][0]['inventory'].append(row['id'])
        self.manifest['placements'][0]['record']=row['id'];self.write('topic.html','<section id="lesson"><video controls playsinline preload="metadata" poster="poster.jpg"><source src="new.mp4"><track kind="captions" src="new.vtt"></video></section>')
        reg=self.load()
        with self.assertRaisesRegex(AssertionError,'PENDING_HUMAN_APPROVAL'):r.assert_releasable(reg,root=self.root)

    def test_pending_unlinked_file_cannot_be_published(self):
        row=self.proposed();self.manifest['records'].append(row);self.index['topics'][0]['inventory'].append(row['id']);reg=self.load()
        with self.assertRaisesRegex(AssertionError,'PENDING_HUMAN_APPROVAL'):r.assert_releasable(reg,['new.mp4'],self.root)

    def test_missing_record(self):
        self.index['topics'][0]['inventory'].append('absent')
        with self.assertRaisesRegex(AssertionError,'Missing/unexpected'):self.load()

    def test_unexpected_record(self):
        self.manifest['records'].append(self.proposed())
        with self.assertRaisesRegex(AssertionError,'Missing/unexpected'):self.load()

    def test_duplicate_record_ids(self):
        self.manifest['records'].append(copy.deepcopy(self.original))
        with self.assertRaisesRegex(AssertionError,'Duplicate record'):self.load()

    def test_duplicate_topic_ids(self):
        self.index['topics'].append(copy.deepcopy(self.index['topics'][0]))
        with self.assertRaisesRegex(AssertionError,'Duplicate topic'):self.load()

    def test_removed_preserved_topic(self):
        self.cfg['media_registry']['preserved_inventory']['missing']=['missing-original']
        with self.assertRaisesRegex(AssertionError,'Preserved topic'):self.load()

    def test_removed_record_cannot_be_hidden_by_inventory_edit(self):
        self.manifest['records']=[self.proposed()];self.index['topics'][0]['inventory']=['topic-proposal']
        with self.assertRaisesRegex(AssertionError,'Preserved inventory'):self.load()

    def test_changed_checksum(self):
        self.manifest['records'][0]['assets']['video']['sha256']='0'*64
        with self.assertRaisesRegex(AssertionError,'Altered checksum'):self.load()

    def test_changed_packets(self):
        self.manifest['records'][0]['packets']['audio']['sha256']='0'*64
        with self.assertRaisesRegex(AssertionError,'packet identity'):self.load()

    def test_recomputed_checksums_do_not_rebaseline_unchanged_media(self):
        self.write('old.mp4',b'changed video');row=self.manifest['records'][0]
        row['assets']['video']=self.desc('old.mp4');row['packets']=self.packets(self.root/'old.mp4')
        with self.assertRaisesRegex(AssertionError,'preservation baseline'):self.load()

    def test_unchanged_id_cannot_point_to_different_baseline_file(self):
        # Blob identity alone is insufficient: ID/asset bindings are also pinned.
        self.manifest['records'][0]['legacy']={'number':999,'variant':'original'}
        with self.assertRaisesRegex(AssertionError,'Preserved record bindings'):self.load()

    def test_unknown_schema_version(self):
        self.index['schema_version']=2
        with self.assertRaisesRegex(AssertionError,'schema version'):self.load()

    def test_missing_required_schema_property(self):
        del self.manifest['records'][0]['packets']
        with self.assertRaisesRegex(AssertionError,'missing required'):self.load()

    def test_unknown_schema_property(self):
        self.index['approve_everything']=True
        with self.assertRaisesRegex(AssertionError,'unexpected field'):self.load()

    def test_boolean_cannot_pass_as_version_integer(self):
        self.index['schema_version']=True
        with self.assertRaisesRegex(AssertionError,'schema version'):self.load()

    def test_unsafe_path(self):
        self.manifest['records'][0]['assets']['video']['path']='../old.mp4'
        with self.assertRaisesRegex(AssertionError,'Unsafe registry path'):self.load()

    def test_missing_asset(self):
        (self.root/'old.mp4').unlink()
        with self.assertRaisesRegex(AssertionError,'Missing or escaped'):self.load()

    def test_unexpected_player(self):
        self.write('topic.html','<video><source src="other.mp4"></video>')
        with self.assertRaisesRegex(AssertionError,'Missing/unexpected player'):self.load()

    def test_missing_player(self):
        self.write('topic.html','<p>Missing video</p>')
        with self.assertRaisesRegex(AssertionError,'Missing/unexpected player'):self.load()

    def test_unregistered_media_extension(self):
        with self.assertRaisesRegex(AssertionError,'Unregistered media'):r.assert_releasable(self.load(),['unknown.webm'],self.root)

    def test_renamed_mp4_cannot_bypass_registration(self):
        self.write('hidden.bin',b'\x00\x00\x00\x18ftypisomfixture')
        with self.assertRaisesRegex(AssertionError,'Unregistered media'):r.assert_releasable(self.load(),['hidden.bin'],self.root)

    def test_unregistered_player_page(self):
        self.write('other.html','<video><source src="old.mp4"></video>')
        with self.assertRaisesRegex(AssertionError,'Unregistered topic player'):r.assert_releasable(self.load(),['other.html'],self.root)

    def test_positive_replacement_requires_independent_integrity(self):
        row=self.proposed(approved=True)
        with self.probe(),patch.object(r,'media_integrity') as verify:
            r.release_record(row,'topic',self.root);verify.assert_called_once_with(self.root/'new.mp4')

    def test_positive_new_media_after_explicit_hold_lift(self):
        row=self.proposed('new',True);self.cfg['production_hold']['active']=False
        with self.probe(),patch.object(r,'media_integrity'):r.release_record(row,'topic',self.root)

    def test_new_media_cannot_override_production_hold(self):
        row=self.proposed('new',True)
        with self.assertRaisesRegex(AssertionError,'hold remains'):r.release_record(row,'topic',self.root)

    def test_unapproved_replacement(self):
        with self.assertRaisesRegex(AssertionError,'PENDING_HUMAN'):r.release_record(self.proposed(),'topic',self.root)

    def rebind_fixture(self,row):
        for key in row['assets']:row['assets'][key]=self.desc(row['assets'][key]['path'])
        a=r.read('alignment.json',self.root);a['captions_sha256']=row['assets']['captions']['sha256'];self.dump('alignment.json',a)
        row['assets']['alignment']=self.desc('alignment.json')
        proof=r.read('proof.json',self.root);proof['subject']={k:v for k,v in r.subject(row).items() if k!='verification'};self.dump('proof.json',proof)
        row['assets']['verification']=self.desc('proof.json');row['human_approval']['subject']=r.subject(row)

    def test_voice_substitution_is_not_approved_by_metadata_status(self):
        row=self.proposed(approved=True);s=r.read('script.json',self.root);s['voice']['name']='bf_emma';self.dump('script.json',s);self.rebind_fixture(row)
        with self.assertRaisesRegex(AssertionError,'Unapproved voice'):r.release_record(row,'topic',self.root)

    def test_existing_full_release_voice_calibration_gate_is_preserved(self):
        row=self.proposed(approved=True);self.cfg['approved_voice']['enhanced_enthusiasm_approval']=None
        with self.assertRaisesRegex(AssertionError,'calibration approval'):r.release_record(row,'topic',self.root)

    def test_script_must_match_actual_aligned_words(self):
        row=self.proposed(approved=True);s=r.read('script.json',self.root);s['text']='Ignore the clock.';self.dump('script.json',s);self.rebind_fixture(row)
        with self.assertRaisesRegex(AssertionError,'script/audio/transcript mismatch'):r.release_record(row,'topic',self.root)

    def test_caption_outside_media_duration_is_rejected(self):
        row=self.proposed(approved=True);self.write('new.vtt','WEBVTT\n\n00:00:03.000 --> 00:00:04.000\nRead the clock.\n');self.rebind_fixture(row)
        with self.probe(),patch.object(r,'media_integrity'):
            with self.assertRaisesRegex(AssertionError,'Caption timing outside'):r.release_record(row,'topic',self.root)

    def test_missing_human_script_approval(self):
        row=self.proposed(approved=True);row['human_approval']['script_approved']=False
        with self.assertRaisesRegex(AssertionError,'script_approved'):r.release_record(row,'topic',self.root)

    def test_approval_bound_to_exact_assets(self):
        row=self.proposed(approved=True);row['human_approval']['subject']['video']='0'*64
        with self.assertRaisesRegex(AssertionError,'different bytes'):r.release_record(row,'topic',self.root)

    def test_incomplete_evidence(self):
        row=self.proposed(approved=True);proof=r.read('proof.json',self.root);del proof['checks']['full_decode'];self.dump('proof.json',proof)
        row['assets']['verification']=self.desc('proof.json');row['human_approval']['subject']=r.subject(row)
        with self.assertRaisesRegex(AssertionError,'missing required'):r.release_record(row,'topic',self.root)

    def test_unverified_script_alignment(self):
        row=self.proposed(approved=True);proof=r.read('proof.json',self.root);proof['checks']['script_alignment']='UNVERIFIED';self.dump('proof.json',proof)
        row['assets']['verification']=self.desc('proof.json');row['human_approval']['subject']=r.subject(row)
        with self.assertRaisesRegex(AssertionError,'Incomplete independent'):r.release_record(row,'topic',self.root)

    def test_producer_cannot_self_verify(self):
        row=self.proposed(approved=True);proof=r.read('proof.json',self.root);proof['verifier']=row['assets']['producer'];self.dump('proof.json',proof)
        row['assets']['verification']=self.desc('proof.json');row['human_approval']['subject']=r.subject(row)
        with self.assertRaisesRegex(AssertionError,'independent of producer'):r.release_record(row,'topic',self.root)

    def test_actual_decode_failure_overrides_positive_receipt(self):
        row=self.proposed(approved=True)
        with self.probe(),patch.object(r,'media_integrity',side_effect=AssertionError('broken actual bytes')):
            with self.assertRaisesRegex(AssertionError,'broken actual bytes'):r.release_record(row,'topic',self.root)

    def test_caption_text_mismatch(self):
        row=self.proposed(approved=True);self.write('new.vtt','WEBVTT\n\n00:00:00.000 --> 00:00:01.000\nDifferent words.\n')
        row['assets']['captions']=self.desc('new.vtt')
        a=r.read('alignment.json',self.root);a['captions_sha256']=row['assets']['captions']['sha256'];self.dump('alignment.json',a)
        row['assets']['alignment']=self.desc('alignment.json')
        proof=r.read('proof.json',self.root);proof['subject']={k:v for k,v in r.subject(row).items() if k!='verification'};self.dump('proof.json',proof)
        row['assets']['verification']=self.desc('proof.json');row['human_approval']['subject']=r.subject(row)
        with self.probe(),patch.object(r,'media_integrity'):
            with self.assertRaisesRegex(AssertionError,'Caption coverage'):r.release_record(row,'topic',self.root)

    def test_duplicate_json_object_key(self):
        self.write('bad.json','{"status":"pending","status":"approved"}')
        with self.assertRaisesRegex(AssertionError,'Duplicate JSON key'):r.read('bad.json',self.root)

    def test_pending_new_topic_needs_no_inventory_code_change(self):
        row=self.proposed('new');row['id']='future-lesson';del row['assets']['verification']
        script=r.read('script.json',self.root);script['topic']='future';self.dump('script.json',script);row['assets']['script']=self.desc('script.json')
        self.write('future.html','<section id="lesson"><video controls playsinline preload="metadata" poster="poster.jpg"><source src="new.mp4"><track kind="captions" src="new.vtt"></video></section>')
        self.dump('future.json',{'schema_version':1,'topic':'future','records':[row],'placements':[{'section':'lesson','record':row['id']}]})
        self.index['topics'].append({'id':'future','page':'future.html','inventory':[row['id']],'legacy_numbers':[],'manifest':self.desc('future.json')})
        self.assertEqual(len(self.load()['topics']),2)

    def test_future_media_cannot_claim_unchanged_exemption(self):
        row=self.proposed();row['policy']='unchanged';row['status']='retained';del row['human_approval'];del row['replaces']
        self.manifest['records'].append(row);self.index['topics'][0]['inventory'].append(row['id'])
        with self.assertRaisesRegex(AssertionError,'grandfathering'):self.load()

    def test_missing_declared_legacy_record(self):
        self.index['topics'][0]['legacy_numbers']=[1]
        with self.assertRaisesRegex(AssertionError,'legacy inventory'):r.legacy_inventory([],self.index,self.root)

    def test_direct_video_src_cannot_hide_unregistered_media(self):
        self.write('topic.html','<video src="unregistered.mp4"></video>')
        with self.assertRaisesRegex(AssertionError,'Missing/unexpected player'):self.load()

    def test_unexpected_legacy_record(self):
        with self.assertRaisesRegex(AssertionError,'legacy inventory'):r.legacy_inventory([{'topic':'topic','number':1}],self.index,self.root)

    def test_append_only_history_rejects_removing_topic(self):
        self.flush();self.git('add','.');self.git('-c','user.name=Fixture','-c','user.email=fixture@example.invalid','commit','-qm','Registered fixture')
        base=self.git('rev-parse','HEAD').decode().strip()
        self.write('video-agent/video-production-contract.json',json.dumps(self.cfg))
        # Include policy in the fixture base before exercising history.
        self.git('add','.');self.git('-c','user.name=Fixture','-c','user.email=fixture@example.invalid','commit','-qm','Policy')
        base=self.git('rev-parse','HEAD').decode().strip();reg=self.load();reg['topics']={}
        with self.assertRaisesRegex(AssertionError,'topic removed'):r.check_history(reg,base,self.root)

    def pending_history(self):
        row=self.proposed();proof=r.read('proof.json',self.root);proof['flags']=[{'id':'known-flag','status':'open'}]
        self.dump('proof.json',proof);row['assets']['verification']=self.desc('proof.json')
        self.manifest['records'].append(row);self.index['topics'][0]['inventory'].append(row['id'])
        self.flush();self.dump('video-agent/video-production-contract.json',self.cfg)
        self.git('add','.');self.git('-c','user.name=Fixture','-c','user.email=fixture@example.invalid','commit','-qm','Pending fixture')
        return self.git('rev-parse','HEAD').decode().strip(),row,proof

    def test_pending_review_can_append_verification(self):
        base,row,proof=self.pending_history();proof['flags'][0]['status']='reviewed'
        self.dump('proof-v2.json',proof);row['assets']['verification']=self.desc('proof-v2.json')
        self.assertEqual(r.check_history(self.load(),base,self.root),set())

    def test_pending_review_cannot_delete_known_flags(self):
        base,row,proof=self.pending_history();proof['flags']=[]
        self.dump('proof-v2.json',proof);row['assets']['verification']=self.desc('proof-v2.json')
        with self.assertRaisesRegex(AssertionError,'Known review flags removed'):r.check_history(self.load(),base,self.root)

    def test_pending_review_cannot_rewrite_old_receipt(self):
        base,row,proof=self.pending_history();proof['flags'][0]['status']='reviewed'
        self.dump('proof.json',proof);row['assets']['verification']=self.desc('proof.json')
        with self.assertRaisesRegex(AssertionError,'Altered checksum'):r.check_history(self.load(),base,self.root)

    def test_pending_media_cannot_change_in_place(self):
        base,row,proof=self.pending_history();row['assets']['video']=self.desc('old.mp4')
        reg={'index':copy.deepcopy(self.index),'topics':{'topic':self.index['topics'][0]},'records':{'topic-original':self.original,'topic-proposal':row}}
        with self.assertRaisesRegex(AssertionError,'Immutable pending media'):r.check_history(reg,base,self.root)


if __name__=='__main__': unittest.main()
