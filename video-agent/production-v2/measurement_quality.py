#!/usr/bin/env python3
"""Manual, resumable Measurement correction using the founder-approved calibration.
Legacy production defaults and scheduling are deliberately not changed.
"""
import os,sys,json,time,re,copy,math,fcntl,subprocess,hashlib
from pathlib import Path
import numpy as np,soundfile as sf
from PIL import Image,ImageDraw
import sherpa_onnx
from scipy.signal import resample_poly
import pipeline as p
from measurement_content import LESSONS
from graphics import draw as legacy_draw,text,INK,TEAL,GOLD
from measurement_graphics import draw_model
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
WORK=Path(os.environ.get('MATHMAGIC_QUALITY_WORK','/workspace/measurement-quality-render'))
MODEL=Path(os.environ.get('MATHMAGIC_QUALITY_MODEL','/workspace/voice-calibration/kokoro-multi-lang-v1_0'))
ASR=Path(os.environ.get('MATHMAGIC_QUALITY_ASR','/workspace/voice-calibration/sherpa-onnx-zipformer-small-en-2023-06-26'))
STATE=HERE/'measurement-quality-manifest.json';FPS=25
VOICE=dict(model='Kokoro v1.0 multilingual ONNX',name='hf_alpha',speaker_id=31,phonemizer='en',licence='Apache-2.0',approval='Founder approved 40.4-second calibration 2ff0ffce',paid_calls=0)
def save(path,data):p.save(path,data)
def words(text):return re.findall(r'[a-z]+',text.lower())
def number(n):
 small=['zero','one','two','three','four','five','six','seven','eight','nine','ten','eleven','twelve','thirteen','fourteen','fifteen','sixteen','seventeen','eighteen','nineteen']
 if n<20:return [small[n]]
 if n<100:return [['','','twenty','thirty','forty','fifty','sixty','seventy','eighty','ninety'][n//10]]+(number(n%10) if n%10 else [])
 if n<1000:return number(n//100)+['hundred']+(number(n%100) if n%100 else [])
 return number(n//1000)+['thousand']+(number(n%1000) if n%1000 else [])
def recognise(rec,samples,sr,start):
 stream=rec.create_stream();stream.accept_waveform(16000,resample_poly(samples,2,3));rec.decode_stream(stream);out=[]
 for token,ts in zip(stream.result.tokens,stream.result.timestamps):
  if token.startswith(('▁',' ')) or not out:out.append(dict(word=token.replace('▁','').strip().lower(),start=start+float(ts)))
  else:out[-1]['word']+=token.lower()
 return [w for w in out if w['word']],stream.result.text

def line_time(line,ws,start,end):
 """Do not display a numeric result before it is spoken; hold prior working meanwhile."""
 nums=re.findall(r'\d[\d,]*',line);target=number(int(nums[-1].replace(',',''))) if nums else []
 seq=[w for w in ws if w['word'] not in ['and']];fallback=False
 if target:
  for i in range(len(seq)-len(target)+1):
   if [w['word'] for w in seq[i:i+len(target)]]==target:return min(end-.15,seq[i+len(target)-1]['start']+.10),'number phrase'
  # Recognition may differ: fail safely by showing the result only after speech.
  return max(start,end-.35),'late-safe ASR fallback'
 ignored={'the','a','an','is','in','and','or','to','of','for','with','each','use','same','not'}
 keys=[w for w in words(line) if len(w)>3 and w not in ignored]
 for w in ws:
  if w['word'] in keys:return w['start'],'keyword'
 return start,'scene context'

def calibrate_cue(c):
 """Keep established corrections readable and complete models at spoken results."""
 if c['role']=='misconception':
  for event in c['board_events']:event.update(at=c['start'],reason='persistent teaching context')
  c['reveal_at']=c['start']
 for event in c['board_events']:
  if event['reason']=='late-safe ASR fallback':
   operators=[w for w in c['words'] if w['word'] in ['subtraction','subtract','addition','multiply']]
   if operators:event.update(at=operators[0]['start'],reason='spoken calculation strategy')
   elif '=' in event['text']:
    inputs=re.findall(r'\d[\d,]*',event['text'].split('=')[0])
    if inputs:
     when,reason=line_time(inputs[-1],c['words'],c['start'],c['end'])
     if reason=='number phrase':event.update(at=when,reason='spoken input dimensions')
 # Alternative decomposition is shown when that strategy is introduced, not
 # when the same numerical answer was first obtained by subtraction.
 if len(c['board_events'])>1 and any('split'==w['word'] for w in c['words']):
  e=c['board_events'][1]
  if '×' in e['text'] and '+' in e['text']:
   e.update(at=next(w['start'] for w in c['words'] if w['word']=='split'),reason='spoken split strategy')
 if c['chapter'].endswith(': explain') or c['role']=='answer':
  numeric=[e['at'] for e in c['board_events'] if e['reason']=='number phrase']
  if numeric:
   finish=max(c['start']+.8,min(numeric));c['motion_end']=finish;c['reveal_at']=finish
 if c.get('model',{}).get('kind')=='composite' and c['chapter'].endswith(': plan'):
  strategy=[w['start'] for w in c['words'] if w['word']=='subtraction']
  if strategy:c['inferred_visible_at']=strategy[0]
 return c

def synth(l,folder,tts,rec):
 key=p.json_hash([l,VOICE,p.sha(MODEL/'model.onnx'),3]);cache=folder/'timeline.json'
 if cache.exists():
  d=json.loads(cache.read_text())
  if d['input_hash']==key and p.sha(folder/'narration.wav')==d['narration_sha256']:return d
 cues=[];captions=[];all_audio=[];cursor=0;asr=[]
 for i,b in enumerate(l['beats']):
  speed=.94 if b['role']=='question' else .98 if b['role'] in ['explanation','misconception'] else 1.0
  wav=folder/(p.json_hash([b['text'],VOICE,speed])+'.wav')
  if wav.exists():samples,sr=sf.read(wav,dtype='float32')
  else:
   a=tts.generate(b['text'],sid=31,speed=speed);samples=np.asarray(a.samples);sr=a.sample_rate
   # Peak headroom before PCM conversion; gain only, no pitch/time processing.
   peak=float(np.max(abs(samples)));gain=min(1.0,.95/peak);samples=samples*gain;sf.write(wav,samples,sr,subtype='PCM_16');save(wav.with_suffix('.gain.json'),dict(native_peak=peak,gain=gain))
  assert sr==24000 and np.sqrt(np.mean(samples*samples))>.008 and np.max(abs(samples))<.999
  end=cursor+len(samples)/sr;ws,heard=recognise(rec,samples,sr,cursor);assert ws
  c=dict(copy.deepcopy(b),index=i,start=cursor,end=end,words=ws,asr_text=heard,native_synthesis_speed=speed,peak_headroom_gain=json.loads(wav.with_suffix('.gain.json').read_text())['gain'] if wav.with_suffix('.gain.json').exists() else 1.0)
  # Match sentence captions to independently recognised sentence starts.
  sentences=re.split(r'(?<=[.!?])\s+',b['text']);starts=[];at=0
  for sentence in sentences:
   first=words(sentence)[0];first='to' if first=='today' else first
   matches=[j for j in range(at,len(ws)) if ws[j]['word']==first]
   j=matches[0] if matches else min(at,len(ws)-1);starts.append(max(cursor,ws[j]['start']));at=j+1
  # Low-confidence repeated starts fall back to a single truthful utterance caption.
  if len(set(starts))!=len(starts):sentences=[b['text']];starts=[cursor]
  for j,s in enumerate(sentences):captions.append(dict(start=starts[j],end=starts[j+1] if j+1<len(starts) else end,text=s))
  board_events=[]
  for line in b['board']:
   when,reason=line_time(line,ws,cursor,end)
   if b['role'] in ['learning_goal','success_criteria','recap','misconception'] or b['role']=='question':when,reason=cursor,'persistent teaching context'
   board_events.append(dict(text=line,at=when,reason=reason))
  c['board_events']=board_events
  # A mathematical model moves through the utterance, not its first 0.8 seconds.
  first=ws[0]['start'];last=ws[-1]['start'];c['motion_start']=first;c['motion_end']=max(first+.8,last)
  c['reveal_at']=max(first,last-.15) # never pre-empt the spoken answer
  cues.append(calibrate_cue(c));all_audio.append(samples);cursor=end
  asr.append(dict(scene=i,reference=b['text'],recognised=heard));print(l['id'],'narration',i+1,'/12',flush=True)
 audio=np.concatenate(all_audio);sf.write(folder/'narration.wav',audio,24000,subtype='PCM_16')
 d=dict(input_hash=key,cues=cues,captions=captions,pauses=[],duration=cursor,narration_sha256=p.sha(folder/'narration.wav'),voice=VOICE['model']+' hf_alpha',voice_id=31,sample_rate=24000,inserted_silence_samples=0,audio_postprocessing=False,alignment='Native utterance PCM boundaries and independent offline ASR token emission timestamps; approximate word timing, not certified forced alignment')
 save(cache,d);save(folder/'recognition.json',asr);return d

BACKGROUND_CACHE={}
def picture(l,c,folder,progress,elapsed,previous_board):
 """Reuse existing model drawing and type, changing only reveals and temporal focus."""
 now=c['start']+elapsed;board=[e['text'] for e in c['board_events'] if e['at']<=now]
 if not board and (c['chapter'].endswith(': explain') or c['role']=='answer'):board=previous_board[-2:]
 base=dict(c,board=board,model=None,note='')
 # Native question timing is guided speech, not an inserted four-second silence.
 if c['role']=='question':base['role']='prediction'
 cachekey=(l['id'],c['index'],tuple(board))
 if cachekey not in BACKGROUND_CACHE:
  image=folder/'frame.png';legacy_draw(l,base,image,1);BACKGROUND_CACHE[cachekey]=Image.open(image).convert('RGB')
  if len(BACKGROUND_CACHE)>12:del BACKGROUND_CACHE[next(iter(BACKGROUND_CACHE))]
 im=BACKGROUND_CACHE[cachekey].copy();d=ImageDraw.Draw(im)
 m=copy.deepcopy(c.get('model'))
 if m:
  m['reveal']=c['role'] in ['answer','misconception'] or c['chapter'].endswith(': explain')
  m['reveal']=m['reveal'] and now>=c['reveal_at']
  if c['role']=='question':m['reveal']=False
  kind=m['kind'];modelprogress=1 if c['role']=='question' else progress
  # The complete input ribbon remains visible; the trace is an additional moving guide.
  draw_model(d,m,1 if kind=='ruler' else modelprogress)
  if kind=='composite' and m.get('boundary') and now<c.get('inferred_visible_at',-1):
   scale=min(1400/m['w'],365/m['h']);left=960-m['w']*scale/2;top=535
   x=left+m['w']*scale+85;y=top+(m['h']-m['b'])*scale/2
   d.rectangle((x-65,y-2,x+65,y+48),fill='white')
   x=left+(m['w']-m['a'])*scale/2;y=top+m['h']*scale+15
   d.rectangle((x-65,y-2,x+65,y+48),fill='white')
  if kind=='ruler' and c['role']!='question':
   left=260;span=1400/max(12,m['end']+1);x=left+m['start']*span;end=left+m['end']*span
   d.line((x,750,x+(end-x)*progress,750),fill=GOLD,width=9)
   for k in range(m['end']-m['start']+1):
    if k<=(m['end']-m['start'])*progress:d.line((x+k*span,740,x+k*span,760),fill=GOLD,width=4)
  elif kind=='combined':
   # Highlight each concrete group while it is discussed; totals remain hidden.
   n=m['whole']+1;index=min(n-1,int(progress*n));x=960-(n*390-60)/2+index*390
   d.rounded_rectangle((x-4,576,x+334,784),radius=20,outline=GOLD,width=7)
  elif kind=='units':
   index=min(3,int(progress*4));x=220+index*380;d.rounded_rectangle((x-4,596,x+354,804),radius=22,outline=GOLD,width=7)
  elif kind=='scale' and c['role']!='question':
   # Existing tick labels remain persistent; a separate guide progresses to the reading.
   x=340+1240*m['value']/m['maximum']*progress;d.line((340,785,x,785),fill=GOLD,width=8)
 if c['role']=='question':text(d,'Predict • follow the model • explain your thinking',960,235,34,GOLD,True)
 return im

def render(l,folder,t):
 out=folder/'final.partial.mp4';key=p.json_hash([t['input_hash'],p.sha(Path(__file__)),p.sha(HERE/'measurement_graphics.py'),p.sha(HERE/'graphics.py')])
 if (folder/'render-key.json').exists() and json.loads((folder/'render-key.json').read_text())['key']==key and out.exists():return out
 clips=[];previous=[]
 for i,c in enumerate(t['cues']):
  clip=folder/f'quality-{i:02}-{key[:10]}.mp4';frames=round(c['end']*30)-round(c['start']*30);duration=frames/30
  if not clip.exists():
   # 25 genuinely changing mathematical frames/s; 30fps output matches existing players.
   n=math.ceil(duration*FPS);cmd=['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r',str(FPS),'-i','pipe:0','-an','-vf','fps=30,format=yuv420p','-frames:v',str(frames),'-c:v','libx264','-preset','veryfast','-crf','23','-threads','2',str(clip.with_suffix('.partial.mp4'))]
   proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
   try:
    for j in range(n):
     elapsed=min(c['end']-c['start']-.001,j/FPS);now=c['start']+elapsed;progress=min(1,max(0,(now-c['motion_start'])/(c['motion_end']-c['motion_start'])))
     im=picture(l,c,folder,progress,elapsed,previous);proc.stdin.write(im.tobytes())
   finally:proc.stdin.close()
   assert proc.wait()==0;clip.with_suffix('.partial.mp4').replace(clip)
  previous=c['board'] or previous;clips.append(clip);print(l['id'],'timed graphics',i+1,'/12',flush=True)
 listing=folder/'clips.txt';listing.write_text(''.join(f"file '{x.as_posix()}'\n" for x in clips))
 p.command(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',listing,'-i',folder/'narration.wav','-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','128k','-movflags','+faststart',out]);save(folder/'render-key.json',dict(key=key))
 (folder/'captions.vtt').write_text(p.formatted_captions(t));(folder/'transcript.txt').write_text('\n\n'.join(b['text'] for b in l['beats'])+'\n');p.command(['ffmpeg','-v','error','-y','-ss','2','-i',out,'-frames:v','1','-vf','scale=1280:720',folder/'poster.jpg']);return out

def run():
 import pathlib as _vq_pathlib, sys as _vq_sys
 _vq_root=next(p for p in _vq_pathlib.Path(__file__).resolve().parents if (p/'video-agent/video-production-contract.json').is_file())
 _vq_sys.path.insert(0,str(_vq_root/'tools/video-quality'))
 from guard import enforce as _vq_enforce
 _vq_enforce()
 WORK.mkdir(exist_ok=True);lock=(WORK/'batch.lock').open('w');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 calibration=json.loads((ROOT/'video-agent/calibration/measurement/timing.json').read_text());assert p.sha(MODEL/'model.onnx')==calibration['model_sha256']
 voice=dict(VOICE,model_sha256=calibration['model_sha256'],voices_sha256=p.sha(MODEL/'voices.bin'))
 old_release=HERE/'measurement-v2-release.json'
 if not old_release.exists():old_release.write_text((HERE/'measurement-release.json').read_text())
 old=json.loads(old_release.read_text());backup=dict(base_commit='d2bc93b685bff8465ac822adafbf95b77831d100',cards={},assets={},reason='Preserve all PR50 media; founder approved calibrated narration and replacement batch')
 for l in old['lessons']:
  for field in ['src','captions','transcript','poster']:
   path=l[field];backup['assets'][path]=dict(bytes=(ROOT/path).stat().st_size,sha256=p.sha(ROOT/path))
 save(HERE/'measurement-previous-integrations.json',backup)
 m=json.loads(STATE.read_text()) if STATE.exists() else dict(topic='measurement',voice=voice,founder_approval='User: All good, go ahead with all',paid_calls=0,legacy_automation='unchanged/suspended',lessons={})
 current_sources=dict(producer=p.sha(Path(__file__)),graphics=p.sha(HERE/'graphics.py'),measurement_graphics=p.sha(HERE/'measurement_graphics.py'))
 if m.get('source_fingerprints'):assert m['source_fingerprints']==current_sources, 'Source changed: revalidate affected scenes before resuming'
 m['source_fingerprints']=current_sources
 tts=sherpa_onnx.OfflineTts(sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(kokoro=sherpa_onnx.OfflineTtsKokoroModelConfig(model=str(MODEL/'model.onnx'),voices=str(MODEL/'voices.bin'),tokens=str(MODEL/'tokens.txt'),data_dir=str(MODEL/'espeak-ng-data'),lang='en'),num_threads=2)))
 rec=sherpa_onnx.OfflineRecognizer.from_transducer(tokens=str(ASR/'tokens.txt'),encoder=str(ASR/'encoder-epoch-99-avg-1.int8.onnx'),decoder=str(ASR/'decoder-epoch-99-avg-1.int8.onnx'),joiner=str(ASR/'joiner-epoch-99-avg-1.int8.onnx'),num_threads=2)
 lessons=copy.deepcopy(LESSONS)
 for l in lessons:
  l['file']=l['file'].replace('_V2_','_V3_');key=l['id'];folder=WORK/key;folder.mkdir(exist_ok=True)
  # Reuse the challenge's own answer model, with the answer hidden during prediction.
  q=next(c for c in l['beats'] if c['role']=='question');a=next(c for c in l['beats'] if c['role']=='answer');q['model']=copy.deepcopy(a.get('model'));q['model']['reveal']=False;q['text']+=' Look at the model, and keep your prediction in mind.'
  e=m['lessons'].setdefault(key,{})
  if e.get('status')=='verified':
   assert e['script_sha256']==p.json_hash(l), 'Verified script changed: review before resuming'
   assert p.sha(ROOT/('videos/'+l['file']+'.mp4'))==e['qa']['sha256'];continue
  e.update(status='synthesising',script_sha256=p.json_hash(l));save(STATE,m);t=synth(l,folder,tts,rec);e['status']='rendering';save(STATE,m);final=render(l,folder,t);qa=p.verify(final,t,folder/'narration.wav');p.verify_sidecars(l,folder,t)
  frames=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',final,'-an','-vf','scale=32:18','-pix_fmt','gray','-f','rawvideo','-']),np.uint8).reshape(-1,576);assert frames.std(axis=1).min()>3
  assert t['inserted_silence_samples']==0 and len(t['cues'])==12 and len(t['captions'])>=12
  qa.update(blank_frames=0,frames_checked=len(frames),inserted_silence_samples=0,synchronisation=t['alignment'],perceptual_voice_review=VOICE['approval'],native_mathematical_animation_fps=FPS,unique_scenes=12,late_safe_reveals=sum(e['reason']=='late-safe ASR fallback' for c in t['cues'] for e in c['board_events']))
  p.promote_media(l,folder,qa);samples,rate=sf.read(folder/'narration.wav',dtype='int16');audio=HERE/'audio'/(key+'-calibrated.flac');sf.write(audio,samples,rate,format='FLAC',subtype='PCM_16');assert np.array_equal(samples,sf.read(audio,dtype='int16')[0]);save(HERE/'scripts'/(key+'-calibrated.json'),l);save(HERE/'timings'/(key+'.json'),t)
  e.update(status='verified',qa=qa,voice=voice,narration_sha256=t['narration_sha256'],source_audio=str(audio.relative_to(ROOT)),source_audio_sha256=p.sha(audio));save(STATE,m);print(key,'VERIFIED',flush=True)
 assert len(m['lessons'])==5 and all(e['status']=='verified' for e in m['lessons'].values())
 release=dict(topic='measurement',source_commit=p.git('rev-parse','HEAD'),quality_calibration='2ff0ffce1f5e85dbbf8c74d28635eeb38d7278e6',voice=voice,lessons=[]);page=ROOT/'measurement.html';html=page.read_text()
 for l in lessons:
  e=m['lessons'][l['id']];t=json.loads((WORK/l['id']/'timeline.json').read_text());stem='videos/'+l['file'];info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-of','json',ROOT/(stem+'.mp4')]))
  release['lessons'].append(dict(id=l['id'],section=l['section'],title=l['title'],src=stem+'.mp4',captions=stem+'.vtt',transcript=stem+'_transcript.txt',poster=stem+'_poster.jpg',bytes=e['qa']['bytes'],sha256=e['qa']['sha256'],duration=float(info['format']['duration']),narration_duration=t['duration'],caption_cues=len(t['captions']),caption_language='en-GB',status='verified',presenter=False,source_audio=e['source_audio'],source_audio_sha256=e['source_audio_sha256']))
  pattern=r'<aside class="video-resource" data-mathmagic-v2="'+l['id']+r'">.*?</aside>'
  html,n=re.subn(pattern,lambda _:p.wrapper(l).replace('<video controls','<video tabindex="0" controls'),html,flags=re.S);assert n==1,(l['id'],n)
 page.write_text(html);save(HERE/'measurement-release.json',release);m['integrated']=True;save(STATE,m);print('PASS: all five calibrated media bundles verified and integrated; old files unchanged.',flush=True)
if __name__=='__main__':run()
