"""Single production contract reader. No synthesis, network calls or release side effects."""
import json,re,sys,hashlib,ast
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];CONFIG=ROOT/'video-agent/video-production-contract.json';REGISTER=ROOT/'docs/video-quality-audit-35.json'
RENDERED_KEYS={'text','chapter','board','note','equation','goal','criteria','hook','closing','goal_speech','criteria_speech','title','display','label','labels','context','message','subtitle','ending'}
def load():
 c=json.loads(CONFIG.read_text());assert c['schema']==1 and c['perceptual_review']['mandatory'] and c['release']['all_mandatory_attributes']=='PASS';return c

def branded(text,c=None):return any(re.search(p,str(text),re.I) for p in (c or load())['prohibited_branding']['patterns'])
def rendered_texts(value,key=None):
 if isinstance(value,dict):
  for k,v in value.items():yield from rendered_texts(v,k)
 elif isinstance(value,list):
  for item in value:yield from rendered_texts(item,key)
 elif isinstance(value,str) and key in RENDERED_KEYS:yield value

def assert_generation_allowed(purpose='production',lessons=None,voice=None):
 c=load()
 if c['production_hold']['active'] and purpose!='remediation_candidate':raise RuntimeError('VIDEO PRODUCTION SUSPENDED: '+c['production_hold']['reason']+'. Only explicitly scoped review candidates may be prepared; no publication.')
 if purpose=='production' and c['approved_voice']['enhanced_enthusiasm_approval'] is None:raise RuntimeError('Enhanced expressive voice profile is not perceptually approved')
 if purpose in ['production','remediation_candidate']:assert lessons and voice, 'Generation requires explicit script and voice provenance'
 if purpose=='remediation_candidate':
  allowed={r['topic'] for r in json.loads(REGISTER.read_text())['records']}
  assert all(l.get('topic') in allowed for l in lessons), 'No new topic under remediation hold'
 if voice:
  a=c['approved_voice'];assert voice.get('name',voice.get('voice'))==a['voice'] and voice.get('speaker_id')==a['speaker_id'],'Unapproved voice; no British/American fallback'
  if voice.get('model_sha256'):assert voice['model_sha256']==a['model_sha256']
  if voice.get('voices_sha256'):assert voice['voices_sha256']==a['voices_sha256']
 for l in lessons or []:
  assert not any(branded(t,c) for t in rendered_texts(l)), 'Prohibited branding in narration/overlay source'
 return c

def assert_release(records):
 c=load();errors=[]
 if c['approved_voice']['enhanced_enthusiasm_approval'] is None:errors.append('Enhanced enthusiasm voice profile has not received perceptual approval')
 for r in records:
  if r.get('final_status')!='PASS':errors.append(f"{r['number']:02}: {r['final_status']}")
  for k,a in r['attributes'].items():
   if a['status']!='PASS':errors.append(f"{r['number']:02} {k}: {a['status']}")
  ev=r.get('verification_evidence',{})
  if ev.get('video_sha256')!=r.get('expected_sha256'):errors.append(f"{r['number']:02}: technical evidence not bound to exact video")
  enc=ev.get('encoding',{})
  if any(enc.get(k)!=v for k,v in {'video':'h264','width':1920,'height':1080,'pixel_format':'yuv420p','audio':'aac'}.items()) or not ev.get('faststart'):errors.append(f"{r['number']:02}: encoding/faststart gate unresolved")
  if not ev.get('decoded_frames') or ev.get('blank_frame_candidates',1):errors.append(f"{r['number']:02}: full decode/blank-frame gate unresolved")
  if ev.get('audio_rms',0)<c['technical']['audio_rms_min'] or ev.get('clipping_fraction',1)>=c['technical']['clipping_fraction_max']:errors.append(f"{r['number']:02}: audio level/clipping gate unresolved")
  if not ev.get('caption_timing_valid') or not ev.get('caption_transcript_text_match'):errors.append(f"{r['number']:02}: caption/transcript alignment unresolved")
  review=r.get('perceptual_review',{})
  if not all(review.get(k) for k in ['reviewer','reviewed_at','full_audio_listened','full_video_viewed']):errors.append(f"{r['number']:02}: full perceptual review missing")
  if any(ev.get(k) for k in ['long_silent_gaps','extended_static_intervals','rapid_reveal_flags']) and not review.get('all_flagged_intervals_reviewed'):errors.append(f"{r['number']:02}: silence/static/rapid-reveal flags require review")
  if review.get('video_sha256')!=r.get('expected_sha256'):errors.append(f"{r['number']:02}: review not bound to exact video bytes")
 if errors:raise RuntimeError('VIDEO RELEASE BLOCKED:\n'+'\n'.join(errors))
 return True

def assert_preservation_edit_allowed(record,clean):
 """Allow review-only branding cuts, including bad voices, without approving synthesis or release."""
 assert record['mp4'] in {r['mp4'] for r in json.loads(REGISTER.read_text())['records']},'Existing inventory only'
 source=ROOT/record['mp4']
 assert hashlib.sha256(source.read_bytes()).hexdigest()==record['expected_sha256'],'Original media changed'
 assert not any(branded(t) for t in rendered_texts(clean)), 'Prohibited branding in edited source'
 return {'review_only':True,'voice_approved':False,'synthesis_allowed':False,'release_allowed':False}
if __name__=='__main__':
 c=load()
 if '--release' in sys.argv:assert_release(json.loads(REGISTER.read_text())['records'])
 print('Contract schema valid. Production hold:',c['production_hold']['active'],'; this is not a video-quality PASS.')


def overlay_brand_literals(source):
 tree=ast.parse(source);constants={}
 for node in tree.body:
  if isinstance(node,ast.Assign) and isinstance(node.value,ast.Constant) and isinstance(node.value.value,str):
   for target in node.targets:
    if isinstance(target,ast.Name):constants[target.id]=node.value.value
 hits=[]
 for node in ast.walk(tree):
  if not isinstance(node,ast.Call):continue
  name=node.func.id if isinstance(node.func,ast.Name) else node.func.attr if isinstance(node.func,ast.Attribute) else ''
  if name not in ['text','txt','wrapped','wrap']:continue
  values=([node.args[1]] if len(node.args)>1 else [])+[k.value for k in node.keywords if k.arg in ['text','s']]
  for v in values:
   strings=[n.value for n in ast.walk(v) if isinstance(n,ast.Constant) and isinstance(n.value,str)]
   strings += [constants[n.id] for n in ast.walk(v) if isinstance(n,ast.Name) and n.id in constants]
   if any(branded(s) for s in strings):hits.append({'line':node.lineno,'text':strings})
 return hits
