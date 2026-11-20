"""Finite Statistics-only batch using the existing production-v2 native tools.
Review outputs stay outside the website tree; this entry never integrates/publishes.
"""
from pathlib import Path
import sys,json,re,copy,hashlib,importlib.util,subprocess,datetime,os,shutil,time
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).parent;WORK=Path('/workspace/statistics-video-work')
sys.path.insert(0,str(ROOT/'video-agent/production-v2'));sys.path.insert(0,str(ROOT/'tools/video-quality'))
from contract import assert_generation_allowed,load,branded
from guard import enforce as _vq_enforce
import measurement_quality as q
import numpy as np,soundfile as sf,sherpa_onnx
sp=importlib.util.spec_from_file_location('statistics_drawing',HERE/'graphics.py');g=importlib.util.module_from_spec(sp);sp.loader.exec_module(g)
MODEL=WORK/'kokoro-multi-lang-v1_0';ASR=WORK/'sherpa-onnx-zipformer-small-en-2023-06-26'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def persist(d):q.save(HERE/'checkpoint.json',d)
def prepare(i):
 l=json.loads((HERE/'scripts'/f'lesson{i}.json').read_text());l['learning_goal']=json.loads((HERE/'lessons.json').read_text())[i-1]['goal'];l['graphics_sha256']=sha(HERE/'graphics.py');parents=l['beats'];l['beats']=[]
 for j,b in enumerate(parents):
  for text in re.split(r'(?<=[.!?])\s+',b['text']):
   if not text.strip():continue
   c=copy.deepcopy(b);c['text']=text;c['parent_index']=j;c['statistics_model']=g.model_for(i,j);l['beats'].append(c)
 return l

def measured_events(l,t):
 # Recogniser emissions are approximate word events, never certified forced alignment.
 parent_events={}
 for c in t['cues']:
  m=c['statistics_model'];kind=m['kind'];labels=m.get('labels',[])
  triggers={'types':['nominal','ordinal','discrete'],'line':['monday','tuesday','wednesday','thursday'],'columns':[str(x).lower() for x in labels],'table':[str(x).lower() for x in labels],'counters':['zero','one','two','three','four']}.get(kind,[])
  if kind in ['columns','table'] and labels==['0','1','2','3','4']:triggers=['zero','one','two','three','four']
  events=[{'at':w['start'],'index':k,'word':w['word']} for w in c['words'] for k,word in enumerate(triggers) if w['word'].lower()==word]
  c['statistics_focus_events']=events;parent_events.setdefault(c['parent_index'],[]).extend(events)
  # Whole-sentence captions use actual PCM boundaries. They match synthesis input;
  # ASR recognition.json is kept for discrepancy review, not proof of perfect speech.
  c['caption_method']='Actual native sentence PCM boundaries'
 t['captions']=[{'start':c['start'],'end':c['end'],'text':c['text']} for c in t['cues'] if c['role']!='thinking_pause']
 for c in t['cues']:
  c['parent_focus_events']=parent_events[c['parent_index']]
 t['alignment']='Native sentence PCM boundaries; independent ASR emission timestamps for visual focus, approximate not forced alignment. Recognition/reference differences retained for human review.'
 return t

def thinking_pauses(t,folder):
 if t.get('statistics_pedagogical_pauses'):return t
 native=folder/'narration-native.wav';shutil.copy2(folder/'narration.wav',native);pcm,sr=sf.read(native,dtype='float32');pieces=[];cues=[];shift=0;pauses=[]
 for i,c in enumerate(t['cues']):
  before=copy.deepcopy(c);pieces.append(pcm[round(before['start']*sr):round(before['end']*sr)])
  for key in ['start','end','motion_start','motion_end','reveal_at']:c[key]+=shift
  for w in c['words']:w['start']+=shift
  for e in c['board_events']:e['at']+=shift
  cues.append(c)
  if c['parent_index'] in [4,6] and (i==len(t['cues'])-1 or t['cues'][i+1]['parent_index']!=c['parent_index']):
   start=c['end'];end=start+5;pieces.append(np.zeros(sr*5,dtype='float32'));pause=copy.deepcopy(c);pause.update(role='thinking_pause',text='',start=start,end=end,motion_start=start,motion_end=end,reveal_at=end,words=[],board=['Think about your prediction'],board_events=[{'text':'Think about your prediction','at':start,'reason':'Explicitly authorised thinking opportunity'}]);cues.append(pause);pauses.append([start,end,'Owner-requested prediction pause, not graphics compensation']);shift+=5
 sf.write(folder/'narration.wav',np.concatenate(pieces),sr,subtype='PCM_16')
 t.update(cues=cues,meaningful_narration_seconds=t['duration'],duration=t['duration']+shift,narration_sha256=sha(folder/'narration.wav'),native_narration_sha256=sha(native),pauses=pauses,pedagogical_pause_samples=shift*sr,statistics_pedagogical_pauses=True)
 return t

def preflight():
 profile=load()['approved_voice']
 for name,field in [('model.onnx','model_sha256'),('voices.bin','voices_sha256')]:assert sha(MODEL/name)==profile[field]
 assert 'Apache License' in (MODEL/'LICENSE').read_text()
 for p in ['tokens.txt','espeak-ng-data']:assert (MODEL/p).exists()
 for p in ['tokens.txt','encoder-epoch-99-avg-1.int8.onnx','decoder-epoch-99-avg-1.int8.onnx','joiner-epoch-99-avg-1.int8.onnx']:assert (ASR/p).is_file()
 assert shutil.disk_usage(WORK).free>4*1024**3
 _vq_enforce('statistics_production',[prepare(i) for i in range(1,6)],profile)
 return profile

def qa_extra(l,t,folder,final,qa):
 from narration_release import parse_vtt
 captions=parse_vtt(folder/'captions.vtt');norm=lambda s:re.sub(r'\s+',' ',s).strip()
 assert norm(' '.join(' '.join(c['lines']) for c in captions))==norm((folder/'transcript.txt').read_text())
 assert all(0<=c['start']<c['end']<=t['duration']+.01 for c in captions)
 for p in [folder/'transcript.txt',folder/'captions.vtt']:assert not branded(p.read_text())
 recognized=json.loads((folder/'recognition.json').read_text());assert not any(branded(c['recognised']) for c in recognized)
 # Full decoded-frame contrast and a sampled OCR pass on the exact delivered file.
 raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(final),'-an','-vf','scale=32:18','-pix_fmt','gray','-f','rawvideo','-']);frames=np.frombuffer(raw,dtype=np.uint8).reshape(-1,576);assert float(frames.std(axis=1).min())>2
 ocr=[];samples=[2]+[c['start']+min(1,(c['end']-c['start'])/2) for c in t['cues'] if c['text']==next(x['text'] for x in t['cues'] if x['parent_index']==c['parent_index'])]
 for n,at in enumerate(samples):
  p=folder/f'review-frame-{n:02}.png';subprocess.run(['ffmpeg','-v','error','-y','-ss',str(at),'-i',str(final),'-frames:v','1',str(p)],check=True);heard=subprocess.check_output(['tesseract',str(p),'stdout','--psm','11'],stderr=subprocess.DEVNULL,text=True);assert not branded(heard);ocr.append({'at':at,'text':heard,'frame_sha256':sha(p)})
 q.save(folder/'frame-ocr.json',ocr)
 # Flag teaching intervals that need genuine review; no metric certifies perception.
 static_flags=[]
 for parent in sorted({c['parent_index'] for c in t['cues']}):
  cs=[c for c in t['cues'] if c['parent_index']==parent];events=sorted(set([cs[0]['start'],cs[-1]['end']]+[e['at'] for c in cs for e in c.get('statistics_focus_events',[])]+[e['at'] for c in cs for e in c['board_events']]))
  static_flags.extend({'start':a,'end':b,'seconds':b-a,'parent':parent,'status':'REQUIRES_VIEWING','reason':'No measured board/focus event for more than eight seconds; persistent context may be appropriate.'} for a,b in zip(events,events[1:]) if b-a>8)
 qa.update(decoded_frames=len(frames),minimum_frame_luma_std=float(frames.std(axis=1).min()),blank_frame_candidates=0,caption_timing_valid=True,caption_transcript_text_match=True,captions=len(captions),source_branding_check='PASS',asr_branding_check='PASS',sampled_frame_ocr_branding='PASS',sampled_frame_count=len(ocr),automated_branding_limitations='ASR/OCR may miss text/speech; sampled OCR is not exhaustive. Human full listening/viewing required.',static_scene_review_flags=static_flags,rushed_reveal_flags=[{'start':c['start'],'end':c['end']} for c in t['cues'] if c['end']-c['start']<.9],inserted_silence_samples=t.get('pedagogical_pause_samples',0),pause_purpose='Two owner-requested five-second prediction opportunities; never visual compensation/duration padding',meaningful_narration_seconds=t.get('meaningful_narration_seconds',t['duration']),planned_prediction_pauses=t['pauses'],perceptual_review='PENDING_FULL_LISTENING_AND_VIEWING',accent_status='UNVERIFIED',expressiveness_status='UNVERIFIED',pedagogical_review='PENDING',physical_ios='NOT_TESTED',approval_status='PENDING',published=False,synchronisation=t['alignment'],script_sha256=sha(HERE/'scripts'/f"lesson{l['id'][-1]}.json"))
 return qa

def main():
 requested=[int(x) for x in sys.argv[1:]] or [1];assert requested and all(1<=x<=5 for x in requested) and len(set(requested))==len(requested)
 profile=preflight();state=json.loads((HERE/'checkpoint.json').read_text());state.update(status='PRODUCTION_PREFLIGHT_PASSED',models_present=True,contract_modified=True,generation_authorised=True,guard_error=None,blockers=['Full listening/viewing and approval required before integration/publication.']);persist(state)
 q.MODEL=MODEL;q.ASR=ASR;q.picture=g.picture
 tts=sherpa_onnx.OfflineTts(sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(kokoro=sherpa_onnx.OfflineTtsKokoroModelConfig(model=str(MODEL/'model.onnx'),voices=str(MODEL/'voices.bin'),tokens=str(MODEL/'tokens.txt'),data_dir=str(MODEL/'espeak-ng-data'),lang='en'),num_threads=2)))
 rec=sherpa_onnx.OfflineRecognizer.from_transducer(tokens=str(ASR/'tokens.txt'),encoder=str(ASR/'encoder-epoch-99-avg-1.int8.onnx'),decoder=str(ASR/'decoder-epoch-99-avg-1.int8.onnx'),joiner=str(ASR/'joiner-epoch-99-avg-1.int8.onnx'),num_threads=2)
 for i in requested:
  row=state['lessons'][i-1];l=prepare(i);folder=WORK/f'lesson{i}';folder.mkdir(exist_ok=True)
  if row.get('status')=='TECHNICALLY_VERIFIED_PENDING_APPROVAL':
   assert sha(row['video'])==row['video_sha256'];print('PRESERVED_VERIFIED',i,flush=True);continue
  row.update(status='SYNTHESISING',script_sha256=sha(HERE/'scripts'/f'lesson{i}.json'),proposed_narration_sha256=sha(HERE/f'lesson{i}_proposed_narration.txt'));state['status']='PRODUCING';persist(state)
  t=q.synth(l,folder,tts,rec);assert t.get('meaningful_narration_seconds',t['duration'])>=300; t=measured_events(l,thinking_pauses(t,folder));q.save(folder/'timeline.json',t)
  assert t['duration']>=300, f'Meaningful narration below five minutes: {t["duration"]}; do not pad'
  row.update(status='RENDERING',narration_duration=t['duration'],audio_sha256=t['narration_sha256'],timings=str(folder/'timeline.json'));persist(state)
  final=q.render(l,folder,t);qa=qa_extra(l,t,folder,final,q.p.verify(final,t,folder/'narration.wav'));q.p.verify_sidecars(l,folder,t);q.save(folder/'qa.json',qa)
  row.update(status='TECHNICALLY_VERIFIED_PENDING_APPROVAL',video=str(final),video_sha256=sha(final),captions=str(folder/'captions.vtt'),transcript=str(folder/'transcript.txt'),poster=str(folder/'poster.jpg'),quality_evidence=str(folder/'qa.json'),approval_status='PENDING',perceptual_review='NOT_PERFORMED');state['rendered']=sum(r.get('status')=='TECHNICALLY_VERIFIED_PENDING_APPROVAL' for r in state['lessons']);state['captions']=state['transcripts_of_actual_audio']=state['rendered'];state['generation_attempts']=state['rendered'];state['status']='PARTIAL_REVIEW_CANDIDATES' if state['rendered']<5 else 'FIVE_TECHNICALLY_VERIFIED_PENDING_APPROVAL';persist(state);print('VERIFIED_REVIEW_CANDIDATE',i,qa['sha256'],round(t['duration'],2),flush=True)
if __name__=='__main__':main()
