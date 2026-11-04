#!/usr/bin/env python3
"""Read-only evidence collection. Never synthesises, renders replacements or claims perception."""
from pathlib import Path
import os,json,re,hashlib,subprocess,urllib.request,urllib.error,concurrent.futures,time,sys,threading
import numpy as np,soundfile as sf
from PIL import Image,ImageDraw
import sherpa_onnx
ROOT=Path(__file__).resolve().parents[2];REG=ROOT/'docs/video-quality-audit-35.json';CACHE=Path('/workspace/video-audit-35');EVID=ROOT/'docs/video-quality-evidence';BASE='https://initsrikanth.github.io/MathMagic/'
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
def get(path):
 target=CACHE/'live'/path;target.parent.mkdir(parents=True,exist_ok=True)
 for attempt in range(2):
  try:
   with urllib.request.urlopen(urllib.request.Request(BASE+path,headers={'Cache-Control':'no-cache'}),timeout=60) as f:data=f.read();meta=dict(status=f.status,headers=dict(f.headers))
   break
  except urllib.error.HTTPError as e:
   if attempt or e.code not in [429,502,503,504]:raise
   time.sleep(1)
 target.write_bytes(data);return data,meta

def download_all(db):
 for page in sorted({r['page'] for r in db['records']}):
  cached=CACHE/'live'/page
  if cached.exists() and cached.read_bytes()==(ROOT/page).read_bytes():continue
  b,m=get(page);assert b==(ROOT/page).read_bytes(),page
 lock=threading.Lock()
 def fetch(r):
  if r['verification_evidence'].get('published_bytes',{}).get('http')==200:
   cached=CACHE/'live'/r['mp4']
   assert cached.exists() and hashlib.sha256(cached.read_bytes()).hexdigest()==r['expected_sha256'];return
  data,meta=get(r['mp4']);digest=hashlib.sha256(data).hexdigest();assert len(data)==r['expected_bytes'] and digest==r['expected_sha256'];assert 'video/mp4' in meta['headers'].get('Content-Type',meta['headers'].get('content-type',''))
  with urllib.request.urlopen(urllib.request.Request(BASE+r['mp4'],headers={'Range':'bytes=0-1023'}),timeout=30) as f:assert f.status==206 and f.read()==data[:1024]
  sidecars={}
  for field in ['captions','transcript','poster']:
   b,_=get(r[field]);sidecars[field]=dict(exact=b==(ROOT/r[field]).read_bytes(),sha256=hashlib.sha256(b).hexdigest());assert sidecars[field]['exact']
  r['verification_evidence']['published_bytes']=dict(http=200,range_http=206,mime='video/mp4',bytes=len(data),sha256=digest,sidecars=sidecars,observed_at=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()))
  with lock:save(REG,db)
  print('LIVE',r['number'],r['lesson'],flush=True)
 def bounded(r):
  try:fetch(r)
  except Exception as e:
   r['verification_evidence']['live_fetch_error']=str(e)
   with lock:save(REG,db)
   print('LIVE BLOCKED',r['number'],str(e),flush=True)
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(bounded,db['records']))
 save(REG,db)

def inspect_one(r,rec):
 folder=CACHE/f"{r['number']:02}";folder.mkdir(exist_ok=True);evidence=EVID/f"{r['number']:02}";evidence.mkdir(parents=True,exist_ok=True);video=CACHE/'live'/r['mp4'];video=video if video.exists() and hashlib.sha256(video.read_bytes()).hexdigest()==r['expected_sha256'] else ROOT/r['mp4'];timeline=json.loads((ROOT/r['timing']).read_text());scenes=timeline.get('cues',timeline.get('events'));assert scenes
 info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',video]));v=next(x for x in info['streams'] if x['codec_type']=='video');a=next(x for x in info['streams'] if x['codec_type']=='audio');duration=float(info['format']['duration']);assert (v['codec_name'],v['width'],v['height'],a['codec_name'])==('h264',1920,1080,'aac')
 raw=subprocess.check_output(['ffmpeg','-v','error','-i',video,'-an','-vf','scale=32:18','-pix_fmt','gray','-f','rawvideo','-']);frames=np.frombuffer(raw,np.uint8).reshape(-1,576);fps=len(frames)/duration;std=frames.std(axis=1);delta=np.mean(abs(np.diff(frames.astype(np.float32),axis=0)),axis=1);runs=[];start=None
 for i,value in enumerate(delta):
  if value<.10 and start is None:start=i
  if (value>=.10 or i==len(delta)-1) and start is not None:
   end=i if value>=.10 else i+1
   if (end-start)/fps>=8:runs.append(dict(start=round(start/fps,2),end=round(end/fps,2),duration=round((end-start)/fps,2),interpretation='FLAG only: persistent working may be appropriate; compare with spoken concept'))
   start=None
 audio=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',video,'-vn','-ac','1','-ar','16000','-f','f32le','-']),np.float32);sr=16000;rms=float(np.sqrt(np.mean(audio*audio)));clip=float(np.mean(abs(audio)>=.999));silent=[]
 for i in range(0,len(audio)-1600,1600):
  if np.sqrt(np.mean(audio[i:i+1600]**2))<.001:silent.append(i/sr)
 pauses=[]
 for t in silent:
  if pauses and abs(t-pauses[-1][-1]-.1)<.01:pauses[-1].append(t)
  else:pauses.append([t])
 gaps=[dict(start=round(x[0],2),end=round(x[-1]+.1,2),duration=round(len(x)*.1,2)) for x in pauses if len(x)>=15]
 # Transcribe the whole decoded published soundtrack, one native scene at a time.
 recognised=[];brand_asr=[]
 for i,c in enumerate(scenes):
  start,end=c['start'],min(c['end'],duration);s=rec.create_stream();s.accept_waveform(sr,audio[round(start*sr):round(end*sr)]);rec.decode_stream(s);tokens=[]
  for token,at in zip(s.result.tokens,s.result.timestamps):
   if token.startswith(('▁',' ')) or not tokens:tokens.append(dict(word=token.replace('▁','').strip().lower(),start=start+float(at)))
   else:tokens[-1]['word']+=token.lower()
  item=dict(scene=i,start=start,end=end,text=s.result.text,tokens=tokens);recognised.append(item)
  if re.search(r'math\s*magic',s.result.text,re.I):brand_asr.append(dict(start=start,end=end,text=s.result.text))
 save(evidence/'full-audio-asr.json',dict(method='Independent local Zipformer recognition of every decoded audio sample by scene; not listening or certified forced alignment',scenes=recognised))
 # Inspect actual rendered scene frames and explicitly sample beginning/middle/end.
 at=[min(duration-.15,c['start']+min(1.5,(c['end']-c['start'])/2)) for c in scenes];phase=[min(2,duration/4),duration/2,max(0,duration-1.5)];all_times=sorted(set(round(t,3) for t in at+phase));shots=[];ocr=[]
 for i,t in enumerate(all_times):
  image=folder/f'frame-{i:03}.jpg';subprocess.run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',video,'-frames:v','1','-vf','scale=960:540',image],check=True)
  text=subprocess.check_output(['tesseract',str(image),'stdout','--psm','11'],stderr=subprocess.DEVNULL,text=True);ocr.append(dict(at=t,text=text,brand_found=bool(re.search(r'math\s*magic',text,re.I))));shots.append((t,image))
 cols=3;rows=(len(shots)+2)//3;sheet=Image.new('RGB',(1440,rows*294),'white');d=ImageDraw.Draw(sheet)
 for i,(t,image) in enumerate(shots):sheet.paste(Image.open(image).resize((480,270)),((i%cols)*480,(i//cols)*294));d.text(((i%cols)*480+4,(i//cols)*294+273),f'{r["number"]:02} | {t:.2f}s',fill='black')
 sheet.save(evidence/'scene-contact.jpg');save(evidence/'sampled-frame-ocr.json',dict(limitation='Samples every authored scene plus beginning/middle/end, not every frame; absence of OCR match cannot establish absence of branding',samples=ocr))
 phase_sheet=Image.new('RGB',(1440,300),'white');pd=ImageDraw.Draw(phase_sheet)
 for i,t in enumerate(phase):
  target=min(shots,key=lambda x:abs(x[0]-t));phase_sheet.paste(Image.open(target[1]).resize((480,270)),(i*480,0));pd.text((i*480+3,275),f'{r["number"]:02} {r["lesson"][:32]} {target[0]:.1f}s',fill='black')
 phase_sheet.save(evidence/'begin-middle-ending.jpg')
 caption_text=' '.join(c['text'] for c in timeline['captions']);transcript=(ROOT/r['transcript']).read_text();norm=lambda x:re.sub(r'\s+',' ',x).strip();transcript_match=norm(caption_text)==norm(transcript);caps=timeline['captions'];capvalid=all(0<=c['start']<c['end']<=duration+.1 for c in caps) and all(x['end']<=y['start']+.01 for x,y in zip(caps,caps[1:]));actual_vtt=(ROOT/r['captions']).read_text();caption_brand=bool(re.search(r'math\s*magic',actual_vtt,re.I))
 result=dict(duration=duration,encoding=dict(video=v['codec_name'],width=v['width'],height=v['height'],pixel_format=v.get('pix_fmt'),audio=a['codec_name'],sample_rate=a.get('sample_rate')),decoded_frames=len(frames),blank_frame_candidates=int(sum(std<3)),audio_rms=rms,clipping_fraction=clip,long_silent_gaps=gaps,extended_static_intervals=runs,full_audio_asr=str((evidence/'full-audio-asr.json').relative_to(ROOT)),brand_asr_matches=brand_asr,frame_contact=str((evidence/'scene-contact.jpg').relative_to(ROOT)),phase_contact=str((evidence/'begin-middle-ending.jpg').relative_to(ROOT)),sampled_frame_ocr=str((evidence/'sampled-frame-ocr.json').relative_to(ROOT)),ocr_brand_matches=[x for x in ocr if x['brand_found']],caption_timing_valid=capvalid,caption_transcript_text_match=transcript_match,caption_brand_found=caption_brand,actual_listening_performed=False,full_temporal_perceptual_viewing_performed=False)
 save(evidence/'technical.json',result);r['verification_evidence'].update(result)
 if brand_asr:r['attributes']['spoken_branding']['audio_confirmation']='Whole-soundtrack ASR found brand; no acoustic listening claim'
 if result['ocr_brand_matches']:r['attributes']['onscreen_branding']=dict(status='FAIL',evidence=[dict(at=x['at'],text=x['text']) for x in result['ocr_brand_matches']]);r['defects'].extend(dict(code='ONSCREEN_BRAND_OCR',start=x['at'],end=x['at'],detail=x['text']) for x in result['ocr_brand_matches'])
 r['attributes']['audio_loudness_clipping_silence_transitions']['automated_evidence']=dict(rms=rms,clipping_fraction=clip,long_gaps=gaps)
 r['attributes']['animation_progressive_reveals']['automated_flags']=runs
 r['attributes']['caption_accuracy_timing']['automated_timing_valid']=capvalid;r['attributes']['transcript_accuracy']['caption_source_text_match']=transcript_match
 if not capvalid or not transcript_match:r['defects'].append(dict(code='CAPTION_TRANSCRIPT_OR_TIMING_MISMATCH',start=0,end=duration,detail='Compare sidecars and real soundtrack before repair'));r['final_status']='FAIL'
 if caption_brand:r['final_status']='FAIL'
 print('AUDIT',r['number'],r['lesson'],'ASR brand',len(brand_asr),'OCR brand',len(result['ocr_brand_matches']),'static flags',len(runs),flush=True)

def main():
 db=json.loads(REG.read_text());CACHE.mkdir(exist_ok=True);download_all(db)
 model=Path('/workspace/voice-calibration/sherpa-onnx-zipformer-small-en-2023-06-26');rec=sherpa_onnx.OfflineRecognizer.from_transducer(tokens=str(model/'tokens.txt'),encoder=str(model/'encoder-epoch-99-avg-1.int8.onnx'),decoder=str(model/'decoder-epoch-99-avg-1.int8.onnx'),joiner=str(model/'joiner-epoch-99-avg-1.int8.onnx'),num_threads=2)
 for r in db['records']:
  done=EVID/f"{r['number']:02}"/'technical.json'
  if done.exists():print('CACHED evidence',r['number'],flush=True);continue
  inspect_one(r,rec);save(REG,db)
 db['automated_evidence_complete']=True;db['perceptual_audit_complete']=False;save(REG,db)
if __name__=='__main__':main()
