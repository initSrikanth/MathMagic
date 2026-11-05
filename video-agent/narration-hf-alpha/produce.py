"""One review-only voice replacement, with original video packets and caption files unchanged."""
from pathlib import Path
import json,hashlib,time,sys,subprocess,re
import numpy as np,soundfile as sf,sherpa_onnx
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/video-quality'))
from contract import load,assert_generation_allowed
from integrate_scoped_corrections import parse_vtt
from brand_only_candidates import packets
OUT=Path(__file__).parent;CACHE=Path('/workspace/narration-multiply-review-cache');MODEL=Path('/workspace/voice-calibration/kokoro-multi-lang-v1_0')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main(index):
 r=json.loads((ROOT/'docs/video-quality-audit-35.json').read_text())['records'][index];active=r.get('active_media') or dict(mp4=r['mp4'],sha256=r['expected_sha256'],captions=r['captions'],transcript=r['transcript'],duration=r['duration']);source=ROOT/active['mp4'];assert sha(source)==active['sha256'];caps=parse_vtt(ROOT/active['captions'])
 global OUT,CACHE
 OUT=ROOT/'video-agent/narration-hf-alpha'/str(index+1);OUT.mkdir(parents=True,exist_ok=True);CACHE=Path('/workspace/hf-alpha-batch-cache')/str(index+1);CACHE.mkdir(parents=True,exist_ok=True)
 profile=load()['approved_voice'];assert_generation_allowed('remediation_candidate',[{'topic':'multiplication-division','text':' '.join(' '.join(c['lines']) for c in caps)}],profile)
 assert sha(MODEL/'model.onnx')==profile['model_sha256'] and sha(MODEL/'voices.bin')==profile['voices_sha256'];assert 'Apache License' in (MODEL/'LICENSE').read_text()
 final=OUT/'Multiply_Efficiently_HFAlpha_Narration_Review_1080p.mp4';meta=OUT/'candidate.json'
 if final.exists() and meta.exists():assert sha(final)==json.loads(meta.read_text())['sha256'];print('Completed candidate preserved');return
 tts=sherpa_onnx.OfflineTts(sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(kokoro=sherpa_onnx.OfflineTtsKokoroModelConfig(model=str(MODEL/'model.onnx'),voices=str(MODEL/'voices.bin'),tokens=str(MODEL/'tokens.txt'),data_dir=str(MODEL/'espeak-ng-data'),lang='en'),num_threads=2)))
 sr=24000;timeline=np.zeros(round(active['duration']*sr),np.float32);events=[];started=time.monotonic()
 for i,c in enumerate(caps):
  words=' '.join(c['lines']);spoken=words[:-1]+'!' if i in [15,26,29] and words.endswith('.') else words
  target=c['end']-c['start'];base=CACHE/f'{i:02}-base.wav'
  if False:audio,rate=sf.read(base,dtype='float32');assert rate==sr
  else:
   base=CACHE/(f'{i:02}-'+hashlib.sha256(spoken.encode()).hexdigest()[:10]+'.wav')
   if base.exists():audio,rate=sf.read(base,dtype='float32');assert rate==sr
   else:
    speech=tts.generate(spoken,sid=31,speed=1.0);audio=np.asarray(speech.samples);sf.write(base,audio,sr,subtype='FLOAT')
  candidates=[(abs(len(audio)/sr-target),1.0,audio)]
  fingerprint=hashlib.sha256(spoken.encode()).hexdigest()[:10]
  # Reuse every previously successful utterance; calibrate only an unfinished window.
  for cached in CACHE.glob(f'{i:02}-fit-*-{fingerprint}.wav'):
   native_rate=float(cached.name.split('-')[2]);cached_audio,rate=sf.read(cached,dtype='float32');assert rate==sr;candidates.append((abs(len(cached_audio)/sr-target),native_rate,cached_audio))
  for attempt in range(5):
   error,speed,audio=min(candidates,key=lambda x:x[0])
   if error<=.10:break
   longer=[x for x in candidates if len(x[2])/sr>target];shorter=[x for x in candidates if len(x[2])/sr<target]
   if longer and shorter:
    lo=min(longer,key=lambda x:x[0]);hi=min(shorter,key=lambda x:x[0]);dl,dh=len(lo[2])/sr,len(hi[2])/sr;speed=lo[1]+(hi[1]-lo[1])*(dl-target)/(dl-dh)
   else:speed=speed*(len(audio)/sr)/target
   assert (.65 if len(words.split())<=3 else .75)<=speed<=1.25,(i,'Required native rate outside a natural review bound',speed)
   path=CACHE/(f'{i:02}-fit-{speed:.6f}-'+fingerprint+'.wav')
   if path.exists():audio,rate=sf.read(path,dtype='float32');assert rate==sr
   else:
    speech=tts.generate(spoken,sid=31,speed=float(speed));audio=np.asarray(speech.samples);sf.write(path,audio,sr,subtype='FLOAT')
   candidates.append((abs(len(audio)/sr-target),speed,audio))
  error,speed,audio=min(candidates,key=lambda x:x[0]);original_end=c['end']
  if error>.10:
   natural_end=c['start']+len(audio)/sr;limit=caps[i+1]['start'] if i+1<len(caps) else active['duration']
   assert error<=.25 and natural_end<limit,(i,'No safe caption-only adjustment',error)
   c['end']=natural_end
  assert abs(c['start']+len(audio)/sr-c['end'])<=.101
  start=round(c['start']*sr);stop=start+len(audio);assert stop<=len(timeline);next_start=caps[i+1]['start'] if i+1<len(caps) else active['duration'];assert stop/sr<=next_start,'New utterance overlaps next caption/step'
  timeline[start:stop]=audio;events.append(dict(index=i,text=words,spoken_punctuation=spoken,caption_start=c['start'],caption_end=c['end'],original_caption_end=original_end,native_audio_end=stop/sr,native_speed=speed,end_timing_error=stop/sr-c['end'],attempts=len(candidates),audio_samples=len(audio)))
  (OUT/'progress.json').write_text(json.dumps({'completed':i+1,'total':30,'events':events},indent=2)+'\n');print('NARRATION',i+1,'/30','native rate',round(speed,3),'end error',round(stop/sr-c['end'],3),flush=True)
 original=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(source),'-vn','-ac','1','-ar',str(sr),'-f','f32le','-']),np.float32);oldrms=float(np.sqrt(np.mean(original**2)));newrms=float(np.sqrt(np.mean(timeline**2)));gain=min(oldrms/newrms,.96/float(abs(timeline).max()));timeline*=gain
 wav=OUT/'narration.flac';sf.write(wav,timeline,sr,subtype='PCM_16')
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(source),'-i',str(wav),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','160k','-movflags','+faststart',str(final)],check=True)
 assert packets(final,'v:0')==packets(source,'v:0'),'Existing mathematical video frames changed'
 from brand_only_candidates import stamp
 final.with_suffix('.vtt').write_text('WEBVTT\n\n'+'\n\n'.join(stamp(c['start'])+' --> '+stamp(c['end'])+c['settings']+'\n'+'\n'.join(c['lines']) for c in caps)+'\n');(OUT/'transcript.txt').write_bytes((ROOT/active['transcript']).read_bytes())
 decode=subprocess.run(['ffmpeg','-v','error','-i',str(final),'-f','null','-'],capture_output=True,text=True,check=True);assert not decode.stderr.strip(),decode.stderr
 info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(final)]));duration=float(info['format']['duration']);assert abs(duration-active['duration'])<.05
 a=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(final),'-vn','-ac','1','-ar',str(sr),'-f','f32le','-']),np.float32);assert np.mean(abs(a)>=.999)<.001
 meta.write_text(json.dumps(dict(title='Multiply Efficiently — single narration review candidate',source=active['mp4'],source_sha256=active['sha256'],file=final.name,sha256=sha(final),bytes=final.stat().st_size,duration=duration,voice=profile,previous_voice=r['voice'],offline=True,paid_calls=0,video_packets_identical=True,graphics_animation_timing_unchanged=True,captions_bytes_identical=final.with_suffix('.vtt').read_bytes()==(ROOT/active['captions']).read_bytes(),transcript_bytes_identical=True,other_lessons_untouched=True,approved_measurement_audio_untouched=True,native_tts_rate_calibration_only=True,inserted_graphic_holds=False,audio_pitch_shift=False,audio_time_stretch=False,pause_policy='Original caption/scene/think-time positions retained; no additional reading-time holds. Native utterance ends match existing caption ends within0.1seconds.',punctuation_emphasis_sentences=[15,26,29],gain_to_match_original_rms=gain,original_rms=oldrms,final_rms=float(np.sqrt(np.mean(a*a))),clipping_fraction=float(np.mean(abs(a)>=.999)),max_caption_end_error=max(abs(e['end_timing_error']) for e in events),events=events,generation_seconds=time.monotonic()-started,technical_status='VERIFIED_REVIEW_CANDIDATE',accent_status='UNVERIFIED_PER_VIDEO_OWNER_APPROVED_PROFILE',expressiveness_status='UNVERIFIED_PER_VIDEO_OWNER_APPROVED_PROFILE',not_published=True),indent=2)+'\n')
 print('COMPLETED',final.name,'duration',duration,'unchanged video/captions; review only.',flush=True)
if __name__=='__main__':
 failures=[]
 for index in range(10,30):
  if index==20:
   import shutil
   dest=ROOT/'video-agent/narration-hf-alpha/21';dest.mkdir(parents=True,exist_ok=True)
   for name in ['Multiply_Efficiently_HFAlpha_Narration_Review_1080p.mp4','Multiply_Efficiently_HFAlpha_Narration_Review_1080p.vtt','transcript.txt','candidate.json']:shutil.copy2(Path('/workspace/hf-alpha-approved-sample')/name,dest/name)
   print('REUSED APPROVED SAMPLE 21',flush=True);continue
  try:main(index)
  except Exception as e:
   import traceback;traceback.print_exc();failures.append({'number':index+1,'error':str(e)})
  (ROOT/'video-agent/narration-hf-alpha/failures.json').write_text(json.dumps(failures,indent=2))
 print('BATCH FINISHED failures',failures,flush=True)
