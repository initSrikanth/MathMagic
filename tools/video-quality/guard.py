"""Fail-closed, dependency-free bootstrap shared by every production entry."""
import sys,json,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent
if str(HERE) not in sys.path:sys.path.insert(0,str(HERE))
from contract import assert_generation_allowed,assert_release,load,REGISTER

def enforce():
 c=load()
 # The current hold takes precedence before any synthesis, rendering or publication.
 if c['production_hold']['active']:return assert_generation_allowed()
 globs=sys._getframe(1).f_globals;declared=globs.get('VOICE',globs.get('VOICE_ID'));voice=None
 if isinstance(declared,dict):voice=declared
 elif isinstance(declared,int):voice={'name':c['approved_voice']['voice'] if declared==31 else 'unapproved','speaker_id':declared}
 if voice is None:raise RuntimeError('Unverified production entry: explicit voice/script provenance and scoped contract approval required; use remediation API for review-only work.')
 if c['approved_voice']['enhanced_enthusiasm_approval'] is None:raise RuntimeError('Enhanced expressive voice profile is not perceptually approved')
 modelsha=globs.get('MODEL_SHA')
 if modelsha:voice=dict(voice,model_sha256=modelsha)
 model=globs.get('MODEL')
 if isinstance(model,Path) and (model/'model.onnx').is_file():voice=dict(voice,model_sha256=hashlib.sha256((model/'model.onnx').read_bytes()).hexdigest(),voices_sha256=hashlib.sha256((model/'voices.bin').read_bytes()).hexdigest())
 return assert_generation_allowed(lessons=globs.get('LESSONS'),voice=voice)
