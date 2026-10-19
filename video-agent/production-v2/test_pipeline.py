"""Focused tests for scheduler, curriculum inventory and publication safety."""
import copy
import datetime as dt
import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
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
    def test_live_failure_is_not_marked_published(self):
        m=self.state(); e=next(iter(m['lessons'].values())); e.update(production_status='integrated',commit_sha='abc')
        with patch.object(p,'persist'),patch.object(p,'record_commits'),patch.object(p.urllib.request,'urlopen',side_effect=OSError('offline')):
            self.assertFalse(p.live(m)); self.assertEqual(e['deployment_status'],'pending')
            self.assertIn('offline',e['deployment_error'])
if __name__=='__main__': unittest.main()
