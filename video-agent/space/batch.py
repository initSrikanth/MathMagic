"""Resume only lessons2–10 with the approved offline pipeline; never publish."""
from pathlib import Path
import sys,os,json,hashlib,copy,subprocess,fcntl,shutil,importlib.util,math,importlib
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).parent
sys.path[:0]=[str(ROOT/'video-agent/production-v2'),str(ROOT/'tools/video-quality'),str(HERE)]
import measurement_quality as q
import batch_graphics as drawing
from contract import assert_generation_allowed,load,branded,rendered_texts
import numpy as np,soundfile as sf,sherpa_onnx
WORK=Path('/tmp/mathmagic-space-production');OUTPUT=Path('/workspace/output/space');STATE=HERE/'batch-manifest.json'
MODEL=Path('/workspace/voice-calibration/kokoro-multi-lang-v1_0');ORIGINAL=Path('/workspace/output/Space_Lesson1_3D_Objects_Review_1080p.mp4');ORIGINAL_SHA='32f712baa2e9baa0b56d2569b53152289079d4d5caac5fb42ec9b0264d3547c1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def lessons():
 s=importlib.util.spec_from_file_location('space_remaining_content',HERE/'remaining_lessons.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m.LESSONS
def validate(l):
 assert_generation_allowed('space_production',[l],load()['approved_voice'])
 bs=l['beats'];assert len(bs)>=21
 assert bs[0]['role']=='opening'and bs[1]['text'].startswith('Today we are learning ')
 assert len(bs[3]['board'])==3 and all(x.startswith('I can ')for x in bs[3]['board'])
 assert bs[-1]['role']=='recap'and sum(b['role']=='question'for b in bs)>=2 and any(b['role']=='misconception'for b in bs)
 count=sum(len(b['text'].split())for b in bs);assert count>=850,(l['id'],count,'Add substantive teaching before synthesis')
 for b in bs:
  key=b['model']['key'];assert key=='default'or key in drawing.SCENES,key
  assert not any(branded(t)for t in rendered_texts(b))
 return count
def pauses(folder,t):
 if t.get('declared_prediction_pauses'):return t
 pcm,sr=sf.read(folder/'narration.wav',dtype='float32');chunks=[];shift=0;windows=[]
 for c in t['cues']:
  start,end=c['start'],c['end'];chunks.append(pcm[round(start*sr):round(end*sr)])
  for k in ['start','end','motion_start','motion_end','reveal_at']:c[k]+=shift
  c['speech_end']=c['end']
  for w in c['words']:w['start']+=shift
  for e in c['board_events']:e['at']+=shift
  for cap in t['captions']:
   if not cap.get('_shifted')and start<=cap['start']<end:cap['start']+=shift;cap['end']+=shift;cap['_shifted']=True
  if c['role']=='question':chunks.append(np.zeros(sr*5,dtype='float32'));c['end']+=5;windows.append([c['speech_end'],c['end'],'authorised five-second prediction']);shift+=5
 for cap in t['captions']:cap.pop('_shifted',None)
 sf.write(folder/'narration.wav',np.concatenate(chunks),sr,subtype='PCM_16');t.update(duration=t['duration']+shift,narration_sha256=sha(folder/'narration.wav'),pauses=windows,declared_prediction_pauses=True);q.save(folder/'timeline.json',t);return t
def render_key(t):
 return q.p.json_hash([t['input_hash'],q.p.sha(Path(q.__file__)),q.p.sha(q.HERE/'measurement_graphics.py'),q.p.sha(q.HERE/'graphics.py')])
def reuse_unchanged_scenes(folder,t,prior):
 if not prior:return
 oldkey,newkey=render_key(prior),render_key(t);proof=[]
 for old,new in zip(prior['cues'],t['cues']):
  same=all(old.get(k)==new.get(k)for k in ['text','model','chapter','role','board'])
  if not same or abs((old['end']-old['start'])-(new['end']-new['start']))>1e-6:continue
  index=new['index'];src=folder/f'quality-{index:02}-{oldkey[:10]}.mp4';dst=folder/f'quality-{index:02}-{newkey[:10]}.mp4'
  if src.exists()and not dst.exists():os.link(src,dst);proof.append(dict(scene=index,sha256=sha(src)))
 # Native unchanged utterances retain their clock. Cumulative frame rounding differs
 # by at most one frame after the two repaired, adjacent introduction utterances.
 q.save(folder/'scene-reuse.json',dict(reused=proof,maximum_expected_boundary_difference_seconds=1/30))
 print('UNCHANGED_SCENES_REUSED',len(proof),flush=True)

def check_frames(final):
 raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(final),'-vf','scale=96:54','-pix_fmt','gray','-f','rawvideo','-']);a=np.frombuffer(raw,dtype=np.uint8).reshape(-1,54*96);s=a.std(axis=1);assert s.min()>2,'Blank or corrupt mathematical frame';return dict(decoded_frames=len(a),minimum_frame_luma_std=float(s.min()),blank_frames=0)
def run():
 WORK.mkdir(exist_ok=True);OUTPUT.mkdir(parents=True,exist_ok=True);lock=(WORK/'batch.lock').open('w');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);assert sha(ORIGINAL)==ORIGINAL_SHA
 profile=load()['approved_voice'];assert sha(MODEL/'model.onnx')==profile['model_sha256']and sha(MODEL/'voices.bin')==profile['voices_sha256']
 state=json.loads(STATE.read_text())if STATE.exists()else dict(expected=10,preserved_representative=dict(path=str(ORIGINAL),sha256=ORIGINAL_SHA),lessons={},published=0,perceptually_verified=0,paid_calls=0)
 state.update(pid=os.getpid(),status='RENDERING_TECHNICAL_CANDIDATES',authority='Current user authorises remaining nine before listening; listening is a publication gate.',voice=profile,scratch=str(WORK));q.save(STATE,state)
 q.MODEL=MODEL;q.picture=drawing.picture
 tts=sherpa_onnx.OfflineTts(sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(kokoro=sherpa_onnx.OfflineTtsKokoroModelConfig(model=str(MODEL/'model.onnx'),voices=str(MODEL/'voices.bin'),tokens=str(MODEL/'tokens.txt'),data_dir=str(MODEL/'espeak-ng-data'),lang='en'),num_threads=2)))
 rec=sherpa_onnx.OfflineRecognizer.from_transducer(tokens=str(q.ASR/'tokens.txt'),encoder=str(q.ASR/'encoder-epoch-99-avg-1.int8.onnx'),decoder=str(q.ASR/'decoder-epoch-99-avg-1.int8.onnx'),joiner=str(q.ASR/'joiner-epoch-99-avg-1.int8.onnx'),num_threads=2)
 for n in range(2,11):
  if os.environ.get('SPACE_LESSONS')and n not in [int(x)for x in os.environ['SPACE_LESSONS'].split(',')]:continue
  l=next((x for x in lessons()if x['id']=='space-lesson'+str(n)),None);assert l,'Missing authored lesson'+str(n)
  importlib.reload(drawing);q.picture=drawing.picture
  validate(l);key=l['id'];entry=state['lessons'].get(key,{})
  source_record=WORK/('lesson'+str(n))/'script.json'
  same_script=source_record.exists()and json.loads(source_record.read_text())['beats']==l['beats']
  if entry.get('status')=='TECHNICAL_PASS'and same_script and Path(entry['output']).exists()and sha(entry['output'])==entry['sha256']:print('PRESERVED',key,flush=True);continue
  folder=WORK/('lesson'+str(n));folder.mkdir(exist_ok=True);l['drawing_sha256']=sha(HERE/'batch_graphics.py');l['source_sha256']=q.p.json_hash(l);state['lessons'][key]=dict(title=l['title'],status='SYNTHESISING',script_sha256=l['source_sha256']);q.save(STATE,state);q.save(folder/'script.json',l);shutil.copy2(HERE/'batch_graphics.py',folder/'rendered_graphics.py')
  try:
   for i,b in enumerate(l['beats']):
    for progress in [0,.5,1]:
     c=dict(b,index=i,start=0,end=20,speech_end=15,motion_start=0,motion_end=20,board_events=[dict(text=x,at=0)for x in b['board']]);drawing.picture(l,c,folder,progress,progress*15,[])
   prior=json.loads((folder/'timeline.json').read_text())if(folder/'timeline.json').exists()else None
   t=pauses(folder,q.synth(l,folder,tts,rec));assert t['duration']>=300,(key,t['duration'],'Narration too short; do not pad')
   for s,e,_ in t['pauses']:assert abs(e-s-5)<1e-8
   state['lessons'][key].update(status='RENDERING',duration=t['duration']);q.save(STATE,state)
   reuse_unchanged_scenes(folder,t,prior)
   final=q.render(l,folder,t);q.p.verify_sidecars(l,folder,t);qa=q.p.verify(final,t,folder/'narration.wav');qa.update(check_frames(final));qa.update(synchronisation=t['alignment'],captions=len(t['captions']),caption_transcript_match=True,caption_timing_valid=all(0<=c['start']<c['end']<=t['duration']for c in t['captions']),pauses=t['pauses'],voice=profile,perceptual_status='UNVERIFIED_NO_AUDIO_EVALUATOR',published=False,mathematics='Validated source/diagrams before rendering',source_sha256=l['source_sha256'])
   assert qa['caption_timing_valid'];assert not any(branded(c['text'])for c in t['captions']);assert not any(branded(c['asr_text'])for c in t['cues'])
   stem='Space_Lesson'+str(n).zfill(2)+'_'+l['title'].replace(' ','_')+'_1080p';out=OUTPUT/(stem+'.mp4');shutil.copyfile(final,out);assert sha(out)==qa['sha256']
   for src,suffix in [('captions.vtt','.vtt'),('transcript.txt','_transcript.txt'),('poster.jpg','_poster.jpg'),('timeline.json','_timing.json')]:shutil.copyfile(folder/src,OUTPUT/(stem+suffix))
   sf.write(folder/'narration.flac',*sf.read(folder/'narration.wav'),subtype='PCM_16');q.save(OUTPUT/(stem+'_qa.json'),qa);q.save(folder/'qa.json',qa)
   state['lessons'][key].update(status='TECHNICAL_PASS',output=str(out),sha256=qa['sha256'],bytes=qa['bytes'],duration=t['duration'],qa=str(OUTPUT/(stem+'_qa.json')),native_audio=str(folder/'narration.flac'),perceptual_status='UNVERIFIED',published=False);q.save(STATE,state);assert sha(ORIGINAL)==ORIGINAL_SHA;print('COMPLETED',key,t['duration'],qa['sha256'],flush=True)
  except Exception as exc:
   state['lessons'][key].update(status='FAILED',error=repr(exc));q.save(STATE,state);print('FAILED',key,repr(exc),flush=True)
 state.update(status='TECHNICAL_BATCH_COMPLETE_REVIEW_PENDING',rendered_total=1+sum(e.get('status')=='TECHNICAL_PASS'for e in state['lessons'].values()));q.save(STATE,state)
if __name__=='__main__':run()
