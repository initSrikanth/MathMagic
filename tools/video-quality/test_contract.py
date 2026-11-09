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
if __name__=='__main__':unittest.main()
