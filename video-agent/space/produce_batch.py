"""Resumable review-only batch. Never touches the representative or site players.
Reuses approved hf_alpha31 synthesis, native speeds and 1080p production encoder.
"""
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import get_context
from pathlib import Path
import sys,json,hashlib,copy,shutil,subprocess,math,os,fcntl
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).parent
sys.path.insert(0,str(ROOT/'video-agent/production-v2'));sys.path.insert(0,str(ROOT/'tools/video-quality'))
import measurement_quality as q
import numpy as np,soundfile as sf,sherpa_onnx
from contract import assert_generation_allowed,load
from batch_content import LESSONS
import batch_graphics as g
from validate_batch import validate
WORK=Path('/workspace/space-video-work');OUT=Path('/workspace/output/space-review');STATE=HERE/'batch-manifest.json'
MODEL=Path('/workspace/voice-calibration/kokoro-multi-lang-v1_0');ASR=q.ASR
sha=q.p.sha

def add_pauses(folder,t):
 if t.get('declared_prediction_pauses'):return t
 pcm,sr=sf.read(folder/'narration.wav',dtype='float32');chunks=[];shift=0;pauses=[]
 for c in t['cues']:
  start,end=c['start'],c['end'];chunks.append(pcm[round(start*sr):round(end*sr)])
  for k in ['start','end','motion_start','motion_end','reveal_at']:c[k]+=shift
  c['speech_end']=c['end']
  for w in c['words']:w['start']+=shift
  for e in c['board_events']:e['at']+=shift
  for cap in t['captions']:
   if not cap.get('_shifted') and start<=cap['start']<end:cap['start']+=shift;cap['end']+=shift;cap['_shifted']=True
  if c['role']=='question':
   chunks.append(np.zeros(sr*5,dtype='float32'));c['end']+=5;pauses.append([c['speech_end'],c['end'],'five-second prediction thinking time; never graphics padding']);shift+=5
 for cap in t['captions']:cap.pop('_shifted',None)
 sf.write(folder/'narration.wav',np.concatenate(chunks),sr,subtype='PCM_16')
 t.update(duration=t['duration']+shift,narration_sha256=sha(folder/'narration.wav'),pauses=pauses,declared_prediction_pauses=True,inserted_silence_samples=sr*shift,inserted_silence_purpose='Three explicit five-second prediction pauses, as in approved representative configuration; no graphics-fit padding.')
 q.save(folder/'timeline.json',t);return t

def technical(final,folder,t,l):
 qa=q.p.verify(final,t,folder/'narration.wav');q.p.verify_sidecars(l,folder,t)
 frames=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-threads','1','-i',str(final),'-an','-vf','scale=32:18','-pix_fmt','gray','-f','rawvideo','-']),np.uint8).reshape(-1,576)
 assert frames.std(axis=1).min()>3
 # Quantify temporal/static flags for full review instead of calling them passed.
 dif=np.mean(abs(np.diff(frames.astype(float),axis=0)),axis=1);static=[];start=None
 for i,v in enumerate(dif):
  if v<.03 and start is None:start=i
  if (v>=.03 or i==len(dif)-1)and start is not None:
   if (i-start)/30>=8:static.append([round(start/30,3),round(i/30,3)])
   start=None
 qa.update(decoded_frames=len(frames),blank_frame_candidates=0,minimum_frame_std=float(frames.std(axis=1).min()),encoding=dict(video='h264',width=1920,height=1080,pixel_format='yuv420p',fps=30,audio='aac'),faststart=True,caption_cues=len(t['captions']),caption_timing_valid=True,caption_transcript_text_match=True,source_brand_free=True,declared_prediction_pauses=t['pauses'],word_timing_method=t['alignment'],synchronisation='Native utterance PCM boundaries; approximate offline ASR word emissions drive board timing. Not certified perceptual synchronisation.',extended_static_intervals=static,static_threshold_seconds=8,all_flagged_intervals_reviewed=False,perceptual_voice_review='UNVERIFIED',full_audio_listened=False,full_video_viewed=False,perceptual_status='PENDING_AUDIO_CAPABLE_REVIEW',published=False,paid_calls=0)
 return qa

def init_voice():
 global tts,rec
 q.MODEL=MODEL
 tts=sherpa_onnx.OfflineTts(sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(kokoro=sherpa_onnx.OfflineTtsKokoroModelConfig(model=str(MODEL/'model.onnx'),voices=str(MODEL/'voices.bin'),tokens=str(MODEL/'tokens.txt'),data_dir=str(MODEL/'espeak-ng-data'),lang='en'),num_threads=2)))
 rec=sherpa_onnx.OfflineRecognizer.from_transducer(tokens=str(ASR/'tokens.txt'),encoder=str(ASR/'encoder-epoch-99-avg-1.int8.onnx'),decoder=str(ASR/'decoder-epoch-99-avg-1.int8.onnx'),joiner=str(ASR/'joiner-epoch-99-avg-1.int8.onnx'),num_threads=2)

def prepare(original,drawing_sha256):
 l=copy.deepcopy(original);l['drawing_sha256']=drawing_sha256;folder=WORK/f"lesson{l['number']}";folder.mkdir(exist_ok=True)
 t=add_pauses(folder,q.synth(l,folder,tts,rec));assert t['duration']>=300
 return l,folder,t


def main():
 OUT.mkdir(parents=True,exist_ok=True);WORK.mkdir(parents=True,exist_ok=True)
 lock=(WORK/'batch.lock').open('w');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 report=validate();profile=load()['approved_voice'];assert_generation_allowed('space_production',LESSONS,profile)
 assert sha(MODEL/'model.onnx')==profile['model_sha256'] and sha(MODEL/'voices.bin')==profile['voices_sha256']
 assert 'Apache License' in (MODEL/'LICENSE').read_text()
 fingerprints={p:sha(HERE/p)for p in ['batch_content.py','batch_graphics.py','produce_batch.py']}
 state=json.loads(STATE.read_text())if STATE.exists()else dict(expected_remaining=9,rendered_this_batch=0,perceptually_verified=0,published=0,paid_calls=0,voice=profile,representative=dict(sha256='32f712baa2e9baa0b56d2569b53152289079d4d5caac5fb42ec9b0264d3547c1',original_manifest_unchanged=True,local_mp4_present=False,status='Existing outside-git MP4 absent from fresh workspace; no regeneration or replacement attempted.'),lessons={})
 if state.get('source_fingerprints'):assert state['source_fingerprints']==fingerprints,'Sources changed: revalidate affected outputs before resuming'
 state['source_fingerprints']=fingerprints;q.save(STATE,state)
 q.MODEL=MODEL;q.picture=g.picture
 # A separate local process lets native voice inference and encoding overlap.
 pool=ProcessPoolExecutor(max_workers=1,mp_context=get_context('spawn'),initializer=init_voice)
 futures={l['id']:pool.submit(prepare,l,fingerprints['batch_graphics.py'])for l in LESSONS if state['lessons'].get(l['id'],{}).get('status')!='TECHNICALLY_VERIFIED'}
 for original in LESSONS:
  l=copy.deepcopy(original);l['drawing_sha256']=fingerprints['batch_graphics.py'];folder=WORK/f"lesson{l['number']}";folder.mkdir(exist_ok=True)
  e=state['lessons'].setdefault(l['id'],{});target=OUT/f"Space_Lesson{l['number']:02}_{l['title'].replace(' ','_')}_Review_1080p.mp4"
  if e.get('status')=='TECHNICALLY_VERIFIED':assert sha(target)==e['sha256'];continue
  e.update(status='SYNTHESISING',script_sha256=q.p.json_hash(l),output=str(target));q.save(STATE,state)
  l,folder,t=futures[l['id']].result();assert t['duration']>=300,'Less than five minutes: revise substance, never pad'
  e.update(status='RENDERING',duration=t['duration']);q.save(STATE,state)
  final=q.render(l,folder,t);qa=technical(final,folder,t,l)
  shutil.copyfile(final,target)
  assert sha(target)==qa['sha256']
  for src,suffix in [('captions.vtt','.vtt'),('transcript.txt','_transcript.txt'),('poster.jpg','_poster.jpg'),('timeline.json','_timing.json'),('recognition.json','_recognition.json')]:shutil.copyfile(folder/src,target.with_name(target.stem+suffix))
  sf.write(target.with_name(target.stem+'_narration.flac'),*sf.read(folder/'narration.wav'),subtype='PCM_16')
  q.save(target.with_name(target.stem+'_script.json'),l);q.save(target.with_name(target.stem+'_qa.json'),qa)
  e.update(status='TECHNICALLY_VERIFIED',qa=qa,sha256=qa['sha256'],bytes=qa['bytes']);state['rendered_this_batch']=sum(x.get('status')=='TECHNICALLY_VERIFIED'for x in state['lessons'].values());q.save(STATE,state)
  checks=''.join(f"{x['sha256']}  {Path(x['output']).name}\n"for x in state['lessons'].values()if x.get('sha256'));(OUT/'SHA256SUMS').write_text(checks)
  print('DELIVERABLE',l['id'],qa['duration'],qa['sha256'],flush=True)
 pool.shutdown(wait=True)
 state['status']='NINE_RENDERED_PUBLICATION_BLOCKED';q.save(STATE,state);print('COMPLETE: nine review videos; no publication',flush=True)
if __name__=='__main__':main()
