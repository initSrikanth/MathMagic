import pathlib as _vq_pathlib, sys as _vq_sys
_vq_root=next(p for p in _vq_pathlib.Path(__file__).resolve().parents if (p/'video-agent/video-production-contract.json').is_file())
_vq_sys.path.insert(0,str(_vq_root/'tools/video-quality'))
from guard import enforce as _vq_enforce
_vq_enforce()
from pathlib import Path
import json,sys,math,subprocess,hashlib,time,os,textwrap
import numpy as np
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parent
REPO=Path(os.environ.get('MATHMAGIC_REPO','/workspace/MathMagic-decimals-46'))
sys.path.insert(0,str(REPO/'video-agent/production-v2'))
from measurement_graphics import draw_model
D=json.loads((R/'timing.json').read_text());words=json.loads((R/'words.json').read_text())['words'];C={c['name']:c for c in D['cues']}
def word(name,token,n=0):
 matches=[w['start'] for w in words if C[name]['start']<=w['start']<C[name]['end'] and w['word']==token]
 assert len(matches)>n,(name,token,matches)
 return matches[n]
events={'trace_start':word('trace','trace'),'trace_finish':word('trace','seven'),'equation_nine':word('calculate','nine'),'equation_minus':word('calculate','minus'),'equation_two':word('calculate','two'),'equation_equals':word('calculate','equal'),'equation_seven':word('calculate','seven'),'ribbon_start_highlight':word('hook','two'),'zero_misconception':word('hook','zero')}
assert C['predict']['end']<=events['trace_start']<events['trace_finish']<events['equation_seven']
(R/'events.json').write_text(json.dumps(dict(method='Visual events follow independently recognised token emission timestamps; review required for exact perceptual alignment',events=events),indent=2))
# Reuse the existing accurate ruler asset. Only the timing overlays are new.
base=Image.new('RGB',(1920,1080),'#fffdf8');draw_model(ImageDraw.Draw(base),dict(kind='ruler',start=2,end=9,reveal=False),1)
ruler=base.crop((0,450,1920,770)).resize((960,160),Image.Resampling.LANCZOS)
fonts={n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n) for n in [17,18,20,22,26,30,38]}
def txt(d,s,x,y,size=22,fill='#16324b',anchor='mm'):d.text((x,y),s,font=fonts[size],fill=fill,anchor=anchor)
def wrap(s,width=78):return textwrap.wrap(s,width)
def frame(t):
 im=Image.new('RGB',(960,540),'#fffdf8');d=ImageDraw.Draw(im)
 d.rounded_rectangle((20,14,940,88),16,fill='#dff4f0');txt(d,'A ruler mystery',480,40,30);txt(d,'Measuring the distance between two marks',480,70,18)
 cue=next((c for c in D['cues'] if c['start']<=t<c['end']),D['cues'][-1]);name=cue['name']
 titles={'hook':'Nine centimetres… or something else?','goal':'Learning Goal: measure the distance, not the final label.','predict':'Your prediction: how many one-centimetre spaces?','trace':'Follow each equal interval from the start to the end.','calculate':'Length = end reading − start reading','recap':'Check the start → count intervals → explain.'}
 txt(d,titles[name],480,120,22)
 im.paste(ruler,(0,170));d=ImageDraw.Draw(im)
 # Coordinate transform from the existing ruler: crop origin (0,450), scale 0.5.
 x=lambda v:130+v*(700/12);y=265
 if t>=events['ribbon_start_highlight']:
  d.ellipse((x(2)-14,y-14,x(2)+14,y+14),outline='#d15c20',width=3);txt(d,'Start: 2',x(2),306,18)
 if name=='predict':
  # A question marker moves gradually; the solution stays hidden.
  u=(t-cue['start'])/(cue['end']-cue['start']);txt(d,'?',x(2)+7*(700/12)*u,337,26,'#d15c20')
 if t>=events['trace_start']:
  p=min(1,max(0,(t-events['trace_start'])/(events['trace_finish']-events['trace_start'])));steps=7*p
  d.line((x(2),322,x(2+steps),322),fill='#d15c20',width=7)
  for k in range(8):
   if k<=steps:d.line((x(2+k),315,x(2+k),330),fill='#d15c20',width=3)
  txt(d,(f'{min(7,int(steps))} intervals traced' if p<1 else '7 equal intervals'),480,360,22)
 if t>=events['equation_nine']:
  parts=['9','−','2','=','7 cm'];times=[events[k] for k in ['equation_nine','equation_minus','equation_two','equation_equals','equation_seven']]
  txt(d,' '.join(p for p,at in zip(parts,times) if t>=at),480,410,38,'#087f83')
 elif name in ['hook','goal','predict']:txt(d,'Each numbered interval is 1 cm.',480,395,22)
 # Captions follow complete synthesis chunks; split into readable timed sentence spans below.
 caps=[c for c in CAPTIONS if c['start']<=t<c['end']]
 if caps:
  d.rounded_rectangle((25,451,935,524),10,fill='#17354a')
  for j,line in enumerate(wrap(caps[0]['text'],88)):txt(d,line,480,476+j*24,18,'white')
 return im
# Caption boundaries are located with recognised first words, not proportional scene durations.
import re
CAPTIONS=[]
for cue in D['cues']:
 sentences=re.split(r'(?<=[.!?])\s+',cue['text']);ws=[w for w in words if cue['start']<=w['start']<cue['end']];cursor=0;starts=[]
 for sentence in sentences:
  first=re.findall('[a-z]+',sentence.lower())[0];first='to' if first=='today' else first
  matches=[i for i in range(cursor,len(ws)) if ws[i]['word']==first]
  idx=matches[0] if matches else cursor;starts.append(max(cue['start'],ws[min(idx,len(ws)-1)]['start']));cursor=idx+1
 for i,s in enumerate(sentences):CAPTIONS.append(dict(start=starts[i],end=starts[i+1] if i+1<len(starts) else cue['end'],text=s))
def stamp(t):
 ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02}.{ms%1000:03}'
(R/'captions.vtt').write_text('WEBVTT\n\n'+'\n\n'.join(stamp(c['start'])+' --> '+stamp(c['end'])+'\n'+c['text'] for c in CAPTIONS)+'\n')
(R/'captions.json').write_text(json.dumps(CAPTIONS,indent=2))
out=R/'measurement-voice-animation-calibration.mp4';frames=math.ceil(D['duration']*25);started=time.monotonic()
p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','960x540','-r','25','-i','pipe:0','-i',str(R/'narration.wav'),'-map','0:v:0','-map','1:a:0','-c:v','libx264','-preset','veryfast','-crf','23','-pix_fmt','yuv420p','-threads','2','-c:a','aac','-b:a','128k','-movflags','+faststart','-shortest',str(out)],stdin=subprocess.PIPE)
for i in range(frames):p.stdin.write(frame(i/25).tobytes())
p.stdin.close();assert p.wait()==0
sheet=Image.new('RGB',(960,540*3))
for i,t in enumerate([15,23,30]):sheet.paste(frame(t),(0,i*540))
sheet.resize((640,1080)).save(R/'preview.jpg');print('RENDER',round(time.monotonic()-started,2),'seconds',out.stat().st_size,'bytes')
