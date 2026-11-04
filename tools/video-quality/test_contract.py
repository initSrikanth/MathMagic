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
 def test_overlay_branding(self):
  self.assertTrue(c.overlay_brand_literals('text(d, "MathMagic", 20, 30)'));self.assertFalse(c.overlay_brand_literals('print("MathMagic_file.mp4")'))
 def test_exact_worked_arithmetic(self):
  self.assertTrue(equation_ok('200 + 35 = 235 cm'));self.assertTrue(equation_ok('1/4 + 1/6 = 5/12'));self.assertFalse(equation_ok('8 × 5 = 13'));
  with self.assertRaises(AssertionError):inspect_math({'beats':[{'board':['2 + 2 = 5']}]})
 def test_all_generation_entries_have_guard(self):
  files=json.loads((Path(__file__).parent/'guarded-entries.json').read_text())
  self.assertGreaterEqual(len(files),16)
  for name in files:self.assertTrue(any(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='_vq_enforce' for n in ast.walk(ast.parse((c.ROOT/name).read_text()))),name)
if __name__=='__main__':unittest.main()
