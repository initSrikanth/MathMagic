import importlib.util,unittest,json,tempfile,hashlib
from pathlib import Path
from unittest.mock import patch
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('lcm_renderer',HERE/'render.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class LCMTests(unittest.TestCase):
 def test_exact_math(self):self.assertTrue(m.validate_math())
 def test_positive_lcm_not_zero(self):self.assertEqual(m.math.lcm(4,6),12)
 def test_draft_discloses_no_narration_and_has_no_final_eligibility(self):
  self.assertIsNone(m.LESSON['voice']['voice_id']);self.assertFalse(m.LESSON['paid_generation_allowed']);self.assertFalse(m.LESSON['publication_allowed'])
 def test_all_word_anchor_states_render_without_slash_notation(self):
  scenes,duration=m.draft_timeline();self.assertEqual(duration,80)
  for s in scenes:
   for w in s['words']:self.assertEqual(m.frame(min(w['start']+.04,79.99),scenes).size,(1920,1080))
 def test_audio_requires_exact_clone_and_matching_provider_settings(self):
  scenes,duration=m.draft_timeline();narr=' '.join(s['narration']for s in m.LESSON['scenes'])
  with tempfile.TemporaryDirectory()as td:
   r=Path(td);audio=r/'voice.mp3';audio.write_bytes(b'unit-test-only-not-audio')
   prov={'provider':'ElevenLabs','verified_clone_name':'Srikanth sogathur','verified_voice_id':'exact-original','approved_voice_id':'exact-original','actual_settings':{'speed':1},'approved_settings':{'speed':1},'model_id':'verified-original-model','audio_sha256':hashlib.sha256(audio.read_bytes()).hexdigest()}
   align={'characters':list(narr),'character_start_times_seconds':[i*.02 for i in range(len(narr))],'character_end_times_seconds':[(i+1)*.02 for i in range(len(narr))]}
   ap=r/'alignment.json';ap.write_text(json.dumps(align));pp=r/'provenance.json';pp.write_text(json.dumps(prov))
   with patch.object(m.subprocess,'check_output',return_value=b'{"format":{"duration":"80"}}'):
    actual,end=m.load_alignment(ap,audio,pp);self.assertEqual(end,80);self.assertEqual(actual[0]['start'],0)
    self.assertEqual(actual[-1]['end'],80)
    prov['verified_voice_id']='substitute';pp.write_text(json.dumps(prov))
    with self.assertRaises(AssertionError):m.load_alignment(ap,audio,pp)
    prov['verified_voice_id']='exact-original';prov['actual_settings']={'speed':1.2};pp.write_text(json.dumps(prov))
    with self.assertRaises(AssertionError):m.load_alignment(ap,audio,pp)
 def test_wrong_narration_rejected(self):
  with tempfile.TemporaryDirectory()as td:
   r=Path(td);audio=r/'voice.mp3';audio.write_bytes(b'unit-test-only')
   p={'provider':'ElevenLabs','verified_clone_name':'Srikanth sogathur','verified_voice_id':'v','approved_voice_id':'v','actual_settings':{},'approved_settings':{},'model_id':'model','audio_sha256':hashlib.sha256(audio.read_bytes()).hexdigest()}
   pp=r/'p.json';pp.write_text(json.dumps(p));ap=r/'a.json';ap.write_text(json.dumps({'characters':['w','r','o','n','g'],'character_start_times_seconds':[0,1,2,3,4],'character_end_times_seconds':[1,2,3,4,5]}))
   with patch.object(m.subprocess,'check_output',return_value=b'{"format":{"duration":"80"}}'),self.assertRaises(AssertionError):m.load_alignment(ap,audio,pp)
class HeyGenNarrationRegression(unittest.TestCase):
 def setUp(self):
  self.final=HERE.parents[1]/'reviews/lcm/final'
  self.audio=self.final/'LCM_Original_HeyGen_Narration.mp3';self.alignment=self.final/'heygen-speech-response.json'
  self.provenance=self.final/'voice-provenance.json'
 def test_real_provider_timestamps_match_the_approved_script(self):
  scenes,duration=m.load_alignment(self.alignment,self.audio,self.provenance)
  self.assertAlmostEqual(duration,87.640813,5);self.assertEqual(len(scenes),9)
  self.assertAlmostEqual(m.anchor(scenes[5],'One quarter equals three twelfths',3),47.461)
  self.assertAlmostEqual(m.anchor(scenes[6],'One sixth equals two twelfths',3),61.646)
  self.assertAlmostEqual(m.anchor(scenes[7],'That makes five twelfths',2),69.447)
 def test_substitute_voice_or_changed_speech_speed_is_rejected(self):
  for change in ['voice','speed']:
   with self.subTest(change=change),tempfile.TemporaryDirectory()as td:
    p=json.loads(self.provenance.read_text())
    if change=='voice':p['verified_voice_id']=p['approved_voice_id']='substitute'
    else:p['returned_regeneration_parameters']['speed']=.9
    dest=Path(td)/'p.json';dest.write_text(json.dumps(p))
    with self.assertRaises(AssertionError):m.load_alignment(self.alignment,self.audio,dest)
 def test_changed_audio_or_multiple_generation_provenance_is_rejected(self):
  for change in ['hash','requests']:
   with self.subTest(change=change),tempfile.TemporaryDirectory()as td:
    p=json.loads(self.provenance.read_text())
    if change=='hash':p['audio_sha256']='incorrect'
    else:p['speech_requests_submitted']=2
    dest=Path(td)/'p.json';dest.write_text(json.dumps(p))
    with self.assertRaises(AssertionError):m.load_alignment(self.alignment,self.audio,dest)
if __name__=='__main__':unittest.main()
