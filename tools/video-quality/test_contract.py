import unittest,json,copy,ast,sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).parent))
import contract as c
from math_check import equation_ok,inspect as inspect_math
class VideoContractTests(unittest.TestCase):
 def test_brand_variants(self):
  for s in ['MathMagic','MATH MAGIC','math-magic','math_magic','Try the practice on MathMagic!']:self.assertTrue(c.branded(s))
 def test_website_identifiers_are_not_rendered_text(self):self.assertEqual(list(c.rendered_texts({'file':'MathMagic_V3.mp4','id':'MathMagicProgress'})),[])
 def test_nested_rendered_brand_is_detected(self):self.assertTrue(any(c.branded(t) for t in c.rendered_texts({'beats':[{'board':['Try Math Magic']}]})))
 def test_generation_hold_blocks(self):
  with self.assertRaisesRegex(RuntimeError,'SUSPENDED'):c.assert_generation_allowed()
 def test_contract_covers_all_requested_year_levels(self):
  self.assertEqual(c.load()['applicable_year_levels'],[5,6,7])
 def test_preserved_wrong_voice_is_not_approved_for_synthesis_or_release(self):
  row=json.loads(c.REGISTER.read_text())['records'][20]
  result=c.assert_preservation_edit_allowed(row,{'text':'Explain your strategy.'})
  self.assertTrue(result['review_only'])
  self.assertFalse(result['voice_approved']);self.assertFalse(result['synthesis_allowed']);self.assertFalse(result['release_allowed'])
 def test_preservation_edit_cannot_introduce_branding(self):
  row=json.loads(c.REGISTER.read_text())['records'][0]
  with self.assertRaisesRegex(AssertionError,'branding'):c.assert_preservation_edit_allowed(row,{'text':'Visit MathMagic'})
 def test_scoped_correction_rejects_voice_replacement(self):
  row=copy.deepcopy(json.loads(c.REGISTER.read_text())['records'][0]);row['correction']['type']='accent_replacement'
  with self.assertRaisesRegex(AssertionError,'Voice/new-topic'):c.assert_scoped_correction_release([row])
 def test_scoped_correction_cannot_claim_full_or_accent_approval(self):
  row=copy.deepcopy(json.loads(c.REGISTER.read_text())['records'][0]);row['correction']['full_quality_status']='PASS'
  with self.assertRaisesRegex(AssertionError,'must not claim'):c.assert_scoped_correction_release([row])
 def test_scoped_correction_rejects_narration_regeneration(self):
  row=copy.deepcopy(json.loads(c.REGISTER.read_text())['records'][0]);row['correction']['narration_regenerated']=True
  with self.assertRaisesRegex(AssertionError,'Voice changes'):c.assert_scoped_correction_release([row])
 def test_scoped_correction_is_bound_to_actual_bytes(self):
  row=copy.deepcopy(json.loads(c.REGISTER.read_text())['records'][0]);row['correction']['replacement']['sha256']='0'*64
  with self.assertRaisesRegex(AssertionError,'Correction bytes changed'):c.assert_scoped_correction_release([row])
 def test_verified_scoped_corrections_can_release_without_full_quality_pass(self):
  rows=[r for r in json.loads(c.REGISTER.read_text())['records'] if r.get('correction')]
  self.assertEqual(len(rows),32);self.assertTrue(c.assert_scoped_correction_release(rows))
 def test_no_british_fallback_for_candidates(self):
  with self.assertRaisesRegex(AssertionError,'Unapproved voice'):c.assert_generation_allowed('remediation_candidate',[{'topic':'measurement','text':'Predict the length.'}],{'name':'bf_emma','speaker_id':7})
 def test_no_new_topic_in_candidate_mode(self):
  with self.assertRaisesRegex(AssertionError,'No new topic'):c.assert_generation_allowed('remediation_candidate',[{'topic':'future-topic','text':'Predict.'}],{'name':'hf_alpha','speaker_id':31})
 def test_no_brand_in_candidate(self):
  with self.assertRaisesRegex(AssertionError,'branding'):c.assert_generation_allowed('remediation_candidate',[{'topic':'measurement','text':'MathMagic'}],{'name':'hf_alpha','speaker_id':31})
 def test_unverified_library_cannot_be_certified(self):
  rows=copy.deepcopy(json.loads(c.REGISTER.read_text())['records']);rows[0]['final_status']='UNVERIFIED'
  with self.assertRaisesRegex(RuntimeError,'01: UNVERIFIED'):c.assert_release(rows)
 def test_unexamined_or_unbound_review_blocks(self):
  row=copy.deepcopy(json.loads(c.REGISTER.read_text())['records'][0]);row['final_status']='PASS'
  for a in row['attributes'].values():a['status']='PASS'
  with self.assertRaisesRegex(RuntimeError,'review missing'):c.assert_release([row])
 def test_thaw_does_not_waive_enthusiasm_calibration(self):
  cfg=copy.deepcopy(c.load());cfg['production_hold']['active']=False
  with patch.object(c,'load',return_value=cfg):
   with self.assertRaisesRegex(RuntimeError,'not perceptually approved'):c.assert_generation_allowed('production',[{'topic':'measurement','text':'Predict.'}],{'name':'hf_alpha','speaker_id':31})
 def test_overlay_branding(self):
  self.assertTrue(c.overlay_brand_literals('text(d, "MathMagic", 20, 30)'));self.assertFalse(c.overlay_brand_literals('print("MathMagic_file.mp4")'))
 def test_exact_worked_arithmetic(self):
  self.assertTrue(equation_ok('200 + 35 = 235 cm'));self.assertTrue(equation_ok('1/4 + 1/6 = 5/12'));self.assertFalse(equation_ok('8 × 5 = 13'));
  with self.assertRaises(AssertionError):inspect_math({'beats':[{'board':['2 + 2 = 5']}]})
 def test_all_generation_entries_have_guard(self):
  files=json.loads((Path(__file__).parent/'guarded-entries.json').read_text())
  self.assertGreaterEqual(len(files),16)
  for name in files:self.assertTrue(any(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='_vq_enforce' for n in ast.walk(ast.parse((c.ROOT/name).read_text()))),name)
class NarrationRemediationTests(unittest.TestCase):
 def row(self):return copy.deepcopy(next(r for r in json.loads(c.REGISTER.read_text())['records'] if r.get('narration_replacement')))
 def test_unapproved_voice_replacement_is_rejected(self):
  from narration_release import verify
  r=self.row();r['narration_replacement']['owner_authorised']=False
  with self.assertRaises(AssertionError):verify([r])
 def test_replacement_cannot_claim_perceptual_pass(self):
  from narration_release import verify
  r=self.row();r['narration_replacement']['perceptual_status']='PASS'
  with self.assertRaises(AssertionError):verify([r])
 def test_scope_excludes_other_fifteen_narrations(self):
  from narration_release import verify
  r=self.row();r['number']=31
  with self.assertRaises(AssertionError):verify([r])
class SpaceAuthorisationTests(unittest.TestCase):
 def test_space_release_rejects_missing_owner_authorisation(self):
  cfg=copy.deepcopy(c.load());cfg['space_release_authorisation']['authorised']=False
  with patch.object(c,'load',return_value=cfg):
   with self.assertRaisesRegex(AssertionError,'owner approval'):c.assert_owner_approved_space_release()
 def test_space_release_rejects_changed_manifest(self):
  cfg=copy.deepcopy(c.load());cfg['space_release_authorisation']['manifest_sha256']='0'*64
  with patch.object(c,'load',return_value=cfg):
   with self.assertRaisesRegex(AssertionError,'manifest changed'):c.assert_owner_approved_space_release()
 def test_space_release_rejects_changed_reviewed_video_hash(self):
  cfg=copy.deepcopy(c.load());key=next(iter(cfg['space_release_authorisation']['approved_video_sha256']));cfg['space_release_authorisation']['approved_video_sha256'][key]='0'*64
  with patch.object(c,'load',return_value=cfg):
   with self.assertRaisesRegex(AssertionError,'reviewed hashes'):c.assert_owner_approved_space_release()
 def test_space_release_is_bound_to_approved_assets_and_players(self):
  self.assertEqual(len(c.assert_owner_approved_space_release()['lessons']),10)
 def test_current_space_generation_is_authorised(self):
  self.assertTrue(c.assert_generation_allowed('space_production',[{'id':'space-lesson1','topic':'space','codes':['AC9M5SP01'],'text':'Today we are learning about solids.'}],c.load()['approved_voice']))
 def test_space_authorisation_rejects_year6_scope(self):
  with self.assertRaises(AssertionError):c.assert_generation_allowed('space_production',[{'id':'space-lesson1','topic':'space','codes':['AC9M6SP01']}],c.load()['approved_voice'])
 def test_space_authorisation_does_not_accept_a_substitute_voice(self):
  with self.assertRaises(AssertionError):c.assert_generation_allowed('space_production',[{'id':'space-lesson1','topic':'space','codes':['AC9M5SP01']}],{'name':'bf_emma','speaker_id':7})
class StatisticsAuthorisationTests(unittest.TestCase):
 def lesson(self):return {'id':'statistics-lesson1','topic':'statistics','year_level':5,'codes':['AC9M5ST01'],'text':'Today we are learning to collect useful data.'}
 def test_statistics_only_generation_is_allowed(self):
  self.assertTrue(c.assert_generation_allowed('statistics_production',[self.lesson()],c.load()['approved_voice']))
  self.assertTrue(c.load()['production_hold']['active'])
  self.assertFalse(c.load()['statistics_generation_authorisation']['publication_authorised'])
 def test_statistics_requires_explicit_owner_authorisation(self):
  cfg=copy.deepcopy(c.load());cfg['statistics_generation_authorisation']['authorised']=False
  with patch.object(c,'load',return_value=cfg):
   with self.assertRaises(AssertionError):c.assert_generation_allowed('statistics_production',[self.lesson()],cfg['approved_voice'])
 def test_statistics_rejects_other_topics_years_and_ids(self):
  for patch_ in [{'topic':'space'},{'year_level':6},{'id':'statistics-lesson6'},{'codes':['AC9M6ST01']}]:
   with self.assertRaises(AssertionError):c.assert_generation_allowed('statistics_production',[dict(self.lesson(),**patch_)],c.load()['approved_voice'])
 def test_statistics_rejects_duplicate_lessons(self):
  with self.assertRaises(AssertionError):c.assert_generation_allowed('statistics_production',[self.lesson(),self.lesson()],c.load()['approved_voice'])
 def test_statistics_rejects_wrong_or_missing_voice_provenance(self):
  for patch_ in [{'voice':'bf_emma'},{'speaker_id':7},{'phonemizer':'en-gb'},{'model':'Another engine'},{'model_sha256':'0'*64},{'voices_sha256':None}]:
   with self.assertRaises(AssertionError):c.assert_generation_allowed('statistics_production',[self.lesson()],dict(c.load()['approved_voice'],**patch_))
 def test_statistics_rejects_branded_text(self):
  with self.assertRaises(AssertionError):c.assert_generation_allowed('statistics_production',[dict(self.lesson(),text='MathMagic')],c.load()['approved_voice'])
 def test_statistics_does_not_thaw_generic_production(self):
  with self.assertRaisesRegex(RuntimeError,'SUSPENDED'):c.assert_generation_allowed('production',[self.lesson()],c.load()['approved_voice'])
 def test_statistics_authorisation_does_not_approve_library_release(self):
  with self.assertRaisesRegex(RuntimeError,'VIDEO RELEASE BLOCKED'):c.assert_release(copy.deepcopy(json.loads(c.REGISTER.read_text())['records']))
class StatisticsReleaseTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  import statistics_release as release
  cls.release=release;cls.state=release.verify_candidates()
 def fixture(self):
  # In-memory test fixture only. Never write a test approval into the repository.
  a=json.loads(self.release.APPROVAL.read_text());a['approved']=True
  for v in a['videos']:
   v.update(reviewer='TEST FIXTURE ONLY',reviewed_at='2026-11-21',evidence_record='TEST ONLY — never a human attestation')
   for k in ['full_audio_listened','full_video_viewed','accent_and_expressiveness_approved','pedagogy_approved','mobile_legibility_approved']:v[k]=True
   v['flag_resolutions']={k:'TEST ONLY' for k in v['flag_resolutions']}
  return a
 def test_actual_approval_fails_closed_unless_complete(self):
  if json.loads(self.release.APPROVAL.read_text()).get('approved')is True:self.release.require_approval(self.state)
  else:
   with self.assertRaisesRegex(RuntimeError,'RELEASE BLOCKED'):self.release.require_approval(self.state)
 def test_generation_is_not_publication(self):
  self.assertFalse(c.load()['statistics_generation_authorisation']['publication_authorised']);self.assertTrue(c.load()['production_hold']['active'])
 def test_complete_in_memory_record_validates_structure(self):
  self.assertTrue(self.release.require_approval(self.state,self.fixture()))
 def test_exact_video_checksum_required(self):
  a=self.fixture();a['videos'][0]['video_sha256']='0'*64
  with self.assertRaisesRegex(AssertionError,'exact video'):self.release.require_approval(self.state,a)
 def test_exact_sidecars_required(self):
  a=self.fixture();a['videos'][1]['bundle_sha256']['captions']='0'*64
  with self.assertRaisesRegex(AssertionError,'sidecars'):self.release.require_approval(self.state,a)
 def test_actual_identity_date_and_record_required(self):
  for k in ['reviewer','reviewed_at','evidence_record']:
   a=self.fixture();a['videos'][0][k]=None
   with self.assertRaises(AssertionError):self.release.require_approval(self.state,a)
 def test_full_reviews_required_for_each_video(self):
  for k in ['full_audio_listened','full_video_viewed','accent_and_expressiveness_approved','pedagogy_approved','mobile_legibility_approved']:
   a=self.fixture();a['videos'][4][k]=False
   with self.assertRaisesRegex(AssertionError,'Human review missing'):self.release.require_approval(self.state,a)
 def test_all_92_flags_require_resolution(self):
  self.assertEqual(sum(len(self.release.flag_ids(r)) for r in self.state['lessons']),92)
  a=self.fixture();a['videos'][2]['flag_resolutions'].popitem()
  with self.assertRaisesRegex(AssertionError,'Every flagged'):self.release.require_approval(self.state,a)
 def test_all_five_and_correct_topic_required(self):
  for k,v in [('topic','space'),('videos',[])]:
   a=self.fixture();a[k]=v
   with self.assertRaises(AssertionError):self.release.require_approval(self.state,a)
 def test_player_changes_invalidate_review(self):
  a=self.fixture();a['player_assets']['js/statistics-video.js']='0'*64
  with self.assertRaisesRegex(AssertionError,'Player assets changed'):self.release.require_approval(self.state,a)
 def test_apply_pending_cannot_mutate_page_or_checkpoint(self):
  paths=[self.release.ROOT/'statistics.html',self.release.CHECKPOINT];before=[p.read_bytes()for p in paths]
  with patch.object(self.release,'require_approval',side_effect=RuntimeError('RELEASE BLOCKED')):
   with self.assertRaisesRegex(RuntimeError,'RELEASE BLOCKED'):self.release.apply()
  self.assertEqual(before,[p.read_bytes()for p in paths])
 def test_preview_contains_complete_accessible_players(self):
  if self.state.get('integrated')==5:
   self.release.assert_integrated_release();return
  page=self.release.integrated_html(self.state)
  self.assertEqual(page.count('data-statistics-video='),5);self.assertEqual(page.count('playsinline'),5)
  self.assertEqual(page.count('kind="captions"'),5);self.assertEqual(page.count('Read the video transcript'),5)
  self.assertNotIn('class="video-pending"',page)
if __name__=='__main__':unittest.main()
