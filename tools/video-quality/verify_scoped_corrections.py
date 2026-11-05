"""Bind objective correction QA to final files; leave full perceptual and accent status unverified."""
import json,hashlib,subprocess,sys,re,struct,concurrent.futures,time,os
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageColor
from contract import ROOT,REGISTER,branded,rendered_texts,load
from integrate_scoped_corrections import parse_vtt
from brand_only_candidates import cmd
OUT=ROOT/'video-agent/video-corrections-35';MEDIA=OUT/'release.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def inspect(c):
 target=c['replacement'];p=ROOT/target['mp4'];assert sha(p)==target['sha256'];path=ROOT/c['evidence'];ev=json.loads(path.read_text());prior=ev.get('scoped_qa',{})
 if prior.get('mp4_sha256')==target['sha256'] and prior.get('captions_sha256')==sha(ROOT/target['captions']) and prior.get('full_decode'):return c['number'],prior
 probe=json.loads(cmd(['ffprobe','-v','error','-show_format','-show_streams','-of','json',p]));v=next(s for s in probe['streams'] if s['codec_type']=='video');a=next(s for s in probe['streams'] if s['codec_type']=='audio');dur=float(probe['format']['duration']);assert (v['codec_name'],v['width'],v['height'],v['pix_fmt'],a['codec_name'])==('h264',1920,1080,'yuv420p','aac')
 # Decode every frame once, collecting low-resolution contrast evidence without retaining a huge frame cache.
 run=subprocess.run(['ffmpeg','-v','error','-i',p,'-an','-vf','fps=1,scale=96:54,format=gray','-f','rawvideo','-'],capture_output=True,check=True);assert not run.stderr.strip(),run.stderr.decode();frames=np.frombuffer(run.stdout,np.uint8).reshape(-1,54,96);assert len(frames)>1 and not np.any(frames.std(axis=(1,2))<3)
 atoms={};pos=0
 with p.open('rb') as f:
  while pos<p.stat().st_size:
   f.seek(pos);head=f.read(16);size,kind=struct.unpack('>I4s',head[:8]);size=struct.unpack('>Q',head[8:16])[0] if size==1 else size;atoms[kind.decode('ascii')]=pos
   if not size:break
   pos+=size
 assert atoms['moov']<atoms['mdat']
 audio=np.frombuffer(cmd(['ffmpeg','-v','error','-i',p,'-vn','-ac','1','-ar','16000','-f','f32le','-']),np.float32);rms=float(np.sqrt(np.mean(audio*audio)));clip=float(np.mean(abs(audio)>=.999));assert rms>=.008 and clip<.001
 caps=parse_vtt(ROOT/target['captions']);norm=lambda s:re.sub(r'\s+',' ',s).strip();assert all(0<=x['start']<x['end']<=dur+.1 for x in caps);assert all(x['end']<=y['start']+.01 for x,y in zip(caps,caps[1:]));assert norm(' '.join(' '.join(x['lines']) for x in caps))==norm((ROOT/target['transcript']).read_text())
 script=json.loads((ROOT/target['script']).read_text());assert not any(branded(t) for t in rendered_texts(script));assert not branded((ROOT/target['captions']).read_text()) and not branded((ROOT/target['transcript']).read_text())
 folder=OUT/'frames'/f"{c['number']:02}";folder.mkdir(parents=True,exist_ok=True);shots=[]
 times=[0,dur/2,max(0,dur-.12)]
 if c['type']=='mathematical_visual_only':times.extend([ev['corrected_seconds'][0]+.1,ev['corrected_seconds'][0]+2.5,ev['corrected_seconds'][1]-.1])
 if c['number']==4:times.extend([218.8,218.95,219.15])
 for i,t in enumerate(times):
  frame=folder/f'{i:02}.jpg';cmd(['ffmpeg','-v','error','-y','-ss',t,'-i',p,'-frames:v','1','-q:v','2',frame]);text=subprocess.check_output(['tesseract',str(frame),'stdout','--psm','11'],stderr=subprocess.DEVNULL,text=True);assert not branded(text),(c['number'],t,text);shots.append({'at':t,'frame':str(frame.relative_to(ROOT)),'ocr':text,'prohibited_brand_found':False})
 pixels=None
 if c['type']=='mathematical_visual_only':
  im=Image.open(ROOT/shots[-1]['frame']).convert('RGB');sys.path.insert(0,str(ROOT/'video-agent/production-v2'));from graphics import TEAL,GOLD,EMPTY
  def near(x,y,col):return np.linalg.norm(np.array(im.getpixel((x,y)))-np.array(ImageColor.getrgb(col)))<30
  if c['number']==15:
   top=[near(round(280+(i+.5)*126),475,TEAL) for i in range(10)];bottom=[near(round(280+(i+.5)*126),685,GOLD) for i in range(10)];assert top==[True]*5+[False]*5 and bottom==[True]*4+[False]*6;pixels={'top_filled_cells':5,'bottom_filled_cells':4,'equal_whole_width':1260,'cells_per_whole':10}
  else:
   assert near(960,620,TEAL);pixels={'left_endpoint':240,'right_endpoint':1680,'midpoint_x':960,'midpoint_is_half':(960-240)/(1680-240)==.5,'dot_colour_checked':True}
 qa=dict(mp4_sha256=target['sha256'],captions_sha256=sha(ROOT/target['captions']),transcript_sha256=sha(ROOT/target['transcript']),script_sha256=sha(ROOT/target['script']),encoding_valid=True,faststart=True,full_decode=True,contrast_samples=len(frames),blank_frame_candidates=0,caption_timing_valid=True,caption_transcript_match=True,source_brand_free=True,rendered_frame_ocr_brand_free=True,sampled_actual_frame_review=False,sampled_frame_count=len(shots),audio_rms=rms,clipping_fraction=clip,original_voice_preserved=bool(ev.get('packet_copy_proof') or ev.get('natural_quiet_boundaries_pcm_checked') or ev.get('original_audio_packets_exact')),narration_pitch_speed_unchanged=not ev['pitch_speed_changed'],mathematical_model_pixel_checks=pixels,actual_frame_samples=shots,perceptual_audio='UNVERIFIED',full_temporal_review='UNVERIFIED',accent_status='UNVERIFIED',scope=c['type'])
 ev['scoped_qa']=qa;path.write_text(json.dumps(ev,indent=2)+'\n');print('SCOPED QA',c['number'],'decode/captions/actual-frame OCR checked; sampled visual review pending',flush=True);return c['number'],qa

def main():
 m=json.loads(MEDIA.read_text());assert len(m['replacements'])==32
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:results=dict(pool.map(inspect,m['replacements']))
 for topic in sorted({c['topic'] for c in m['replacements']}):
  entries=[c for c in m['replacements'] if c['topic']==topic];sheet=Image.new('RGB',(1440,len(entries)*300),'white');draw=ImageDraw.Draw(sheet)
  for row,c in enumerate(entries):
   for col,shot in enumerate(results[c['number']]['actual_frame_samples'][:3]):sheet.paste(Image.open(ROOT/shot['frame']).resize((480,270)),(col*480,row*300));draw.text((col*480+4,row*300+274),f"{c['number']:02} {c['lesson'][:37]} {shot['at']:.1f}s",fill='black')
  sheet.save(OUT/'frames'/(topic+'-actual-outputs.jpg'))
 print('All32 final outputs objectively checked; seven actual-media contact sheets prepared. No listening or full-quality PASS claimed.')
if __name__=='__main__':main()
