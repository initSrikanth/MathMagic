"""Focused tests for scheduler, curriculum inventory and publication safety."""
import copy
import datetime as dt
import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch, MagicMock
import pipeline as p

class ProductionTests(unittest.TestCase):
    def state(self): return p.initialise(p.initial())
    def test_inventory_matches_actual_lesson_sections(self):
        m=self.state(); self.assertEqual(len(m['lessons']),30)
        self.assertEqual(len({e['video_filename'] for e in m['lessons'].values()}),30)
    def test_five_hours_crosses_midnight(self):
        m=self.state(); start=dt.datetime(2026,10,19,22,17,tzinfo=dt.timezone.utc)
        m['next_batch_due']=p.iso(start+dt.timedelta(hours=5))
        self.assertFalse(p.due(m,start+dt.timedelta(hours=4,minutes=59)))
        self.assertTrue(p.due(m,start+dt.timedelta(hours=5)))
        self.assertTrue(p.due(m,start+dt.timedelta(hours=8)))
    def test_completed_curriculum_never_selects_more_work(self):
        m=self.state()
        for e in m['lessons'].values(): e['deployment_status']='verified_live'
        self.assertFalse(p.due(m))
    def test_rendered_is_not_deployed_or_committed(self):
        m=self.state(); e=next(iter(m['lessons'].values())); e['production_status']='verified'
        s=p.summary(m); self.assertEqual(s['videos_successfully_rendered'],1)
        self.assertEqual(s['videos_committed'],0); self.assertEqual(s['videos_deployed_and_verified_live'],0)
    def test_all_authored_arithmetic(self): self.assertEqual(p.maths()['lessons'],30)
    def test_decimals_goals_and_three_criteria_are_spoken_and_visible(self):
        lessons = [lesson for lesson in p.LESSONS if lesson['topic'] == 'decimals-percentages']
        self.assertEqual(len(lessons), 5)
        for lesson in lessons:
            with self.subTest(lesson=lesson['id']):
                opening, goal, criteria, concept = lesson['beats'][:4]
                self.assertEqual(opening['role'], 'opening')
                self.assertEqual(goal['role'], 'learning_goal')
                self.assertEqual(criteria['role'], 'success_criteria')
                self.assertEqual(concept['chapter'], 'Build the idea')
                self.assertEqual(len(goal['board']), 1)
                self.assertIn('Our learning goal is to', goal['text'])
                self.assertEqual(len(criteria['board']), 3)
                self.assertEqual(criteria['text'].count('I can '), 3)
                self.assertTrue(all(line.startswith(str(i) + '. ') for i, line in enumerate(criteria['board'], 1)))
                self.assertFalse(any(cue.get('equation') for cue in [opening, goal, criteria]))

    def test_staged_media_preserves_previous_video_until_verified(self):
        lesson=next(l for l in p.LESSONS if l['topic']=='decimals-percentages')
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); (root/'videos').mkdir()
            old=root/'videos'/(lesson['file']+'.mp4'); old.write_bytes(b'previous-video')
            folder=root/'staging'; folder.mkdir()
            staged=folder/'final.partial.mp4'; staged.write_bytes(b'new-video')
            with patch.object(p,'ROOT',root):
                with self.assertRaises(AssertionError):
                    p.promote_media(lesson,folder,{'sha256':p.sha(staged)})
                self.assertEqual(old.read_bytes(),b'previous-video')
                for name in ['captions.vtt','transcript.txt','poster.jpg']:
                    (folder/name).write_bytes(b'present')
                with self.assertRaises(AssertionError):
                    p.promote_media(lesson,folder,{'sha256':'incorrect-hash'})
                self.assertEqual(old.read_bytes(),b'previous-video')
                p.promote_media(lesson,folder,{'sha256':p.sha(staged)})
                self.assertEqual(old.read_bytes(),b'new-video')
                self.assertTrue((root/'videos'/(lesson['file']+'.vtt')).exists())
                self.assertTrue((root/'videos'/(lesson['file']+'_transcript.txt')).exists())
                self.assertTrue((root/'videos'/(lesson['file']+'_poster.jpg')).exists())

    def test_sidecar_validation_rejects_mismatched_captions(self):
        from PIL import Image
        lesson=next(l for l in p.LESSONS if l['topic']=='decimals-percentages')
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)
            timeline={'captions':[{'start':0.0,'end':1.5,'text':'Learning goal.'}]}
            (folder/'captions.vtt').write_text('WEBVTT\n\n00:00:00.000 --> 00:00:01.500\nLearning goal.\n')
            (folder/'transcript.txt').write_text('\n\n'.join(b['text'] for b in lesson['beats'])+'\n')
            Image.new('RGB',(1280,720),'white').save(folder/'poster.jpg')
            p.verify_sidecars(lesson,folder,timeline)
            (folder/'captions.vtt').write_text('WEBVTT\n\n00:00:00.000 --> 00:00:01.500\nIncorrect words.\n')
            with self.assertRaises(AssertionError):
                p.verify_sidecars(lesson,folder,timeline)

    def test_integration_is_scoped_and_idempotent_for_all_thirty_sections(self):
        # Use actual page markup, including nested Fractions div wrappers and aside wrappers.
        for l in p.LESSONS:
            with self.subTest(lesson=l['id']), tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp); (root/'videos').mkdir()
                page=root/(l['topic']+'.html'); before=(p.ROOT/page.name).read_text(); page.write_text(before)
                video=root/('videos/'+l['file']+'.mp4'); video.write_bytes(b'verified-media-fixture')
                m=self.state(); e=m['lessons'][l['id']]
                e.update(video_filename='videos/'+l['file']+'.mp4',qa={'sha256':p.sha(video)})
                m['active_batch']={'rollback_sha':'test-rollback'}
                # Wrapper's filename matches the fixture for this isolated integration test.
                test_l=l
                with patch.object(p,'ROOT',root), patch.object(p,'LESSONS',[test_l]):
                    p.integrate([l['id']],m); after=page.read_text()
                    self.assertEqual(after.count('data-mathmagic-v2="'+l['id']+'"'),1)
                    self.assertIn('src="videos/'+l['file']+'.mp4"',after)
                    # The integrator itself proves preservation outside the one resource wrapper.
                    p.integrate([l['id']],m); self.assertEqual(page.read_text(),after)
    def test_missing_or_changed_final_cannot_replace_live_content(self):
        l=p.LESSONS[0]; m=self.state(); e=m['lessons'][l['id']]; e.update(qa={'sha256':'wrong'})
        m['active_batch']={'rollback_sha':'test'}
        with self.assertRaises((AssertionError,FileNotFoundError)): p.integrate([l['id']],m)
    def test_stale_html_is_an_explicit_deployment_failure(self):
        m=self.state(); e=next(iter(m['lessons'].values())); e.update(production_status='integrated',commit_sha='abc')
        response=MagicMock(); response.__enter__.return_value.read.return_value=b'<html>Old deployment</html>'
        with patch.object(p,'persist'),patch.object(p,'record_commits'),patch.object(p.urllib.request,'urlopen',return_value=response):
            self.assertFalse(p.live(m)); self.assertIn('AssertionError',e['deployment_error'])
            self.assertEqual(e['deployment_status'],'pending')
    def test_live_failure_is_not_marked_published(self):
        m=self.state(); e=next(iter(m['lessons'].values())); e.update(production_status='integrated',commit_sha='abc')
        with patch.object(p,'persist'),patch.object(p,'record_commits'),patch.object(p.urllib.request,'urlopen',side_effect=OSError('offline')):
            self.assertFalse(p.live(m)); self.assertEqual(e['deployment_status'],'pending')
            self.assertIn('offline',e['deployment_error'])
if __name__=='__main__': unittest.main()
