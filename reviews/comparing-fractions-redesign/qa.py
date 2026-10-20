"""Focused media, pedagogy, exact-rational geometry and pause checks."""
import json,subprocess,hashlib,sys
from pathlib import Path
from fractions import Fraction as Q
from collections import defaultdict
import numpy as np
from PIL import Image,ImageColor,ImageDraw
from lesson import C
P=Path(__file__).parent;W=Path('/workspace/work/comparing-redesign-render');video=P/'Comparing_Fractions_Redesigned_Prototype.mp4'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert Q(3,4)>Q(2,4) and Q(1,2)>Q(1,4)
assert Q(1,2)==Q(3,6)<Q(4,6)==Q(2,3)
assert Q(2,3)==Q(8,12)<Q(9,12)==Q(3,4)
assert [c['stage'] for c in C]==sorted(c['stage'] for c in C)
assert set(c['stage'] for c in C)==set('ABCDEFG')
assert all(c.get('hide') and not c.get('equation') and c.get('concrete') for c in C if c['stage']=='A')
first_equation=next(i for i,c in enumerate(C) if c.get('equation'));assert C[first_equation]['stage']=='B'
assert any(c.get('annotation')=='both' for c in C)
assert any(c.get('tone')=='misconception' for c in C)
challenge=next(i for i,c in enumerate(C) if c['stage']=='F');assert C[challenge]['pause']==5
assert all(c['pause']>=3 for c in C if c.get('tone')=='question')
assert all('/' not in c['chapter']+c['note'] for c in C)
# Actual final-pixel checks at each part's centre, including concrete chocolate models.
for i,c in enumerate(C):
 im=Image.open(W/f'{i:02}.png')
 for j,r in enumerate(c['rows']):
  assert 0<=r['n']<=r['d'];assert r['d']>0
  for k in range(r['d']):
   x=round(260+(k+.5)*1260/r['d']);y=490+j*170+30
   col=('#008B8B' if r['colour']=='teal' else '#BF6500') if k<r['n'] else '#E5EFF8'
   if c.get('concrete'):col=('#744126' if j==0 else '#A65C22') if k<r['n'] else '#F0DEC8'
   assert im.getpixel((x,y))==ImageColor.getrgb(col),(i,j,k,im.getpixel((x,y)),col)
 if c.get('subdivide') and c['stage'] in 'EF':
  prev=C[i-1]
  for j,r in enumerate(c['rows']):assert Q(r['n'],r['d'])==Q(prev['rows'][j]['n'],prev['rows'][j]['d']),('Changed quantity',i,j)
  # New partition animation preserves shading after the opening graphic dissolve.
  for frame in [15,30,59]:
   pic=Image.open(W/f'{i:02}-anim-{frame:02}.png')
   for j,r in enumerate(c['rows']):
    for k in range(r['d']):
     x=round(260+(k+.5)*1260/r['d']);y=490+j*170+30
     col=('#008B8B' if r['colour']=='teal' else '#BF6500') if k<r['n'] else '#E5EFF8'
     assert pic.getpixel((x,y))==ImageColor.getrgb(col),(i,frame,j,k)
meta=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)]));v=next(s for s in meta['streams'] if s['codec_type']=='video');a=next(s for s in meta['streams'] if s['codec_type']=='audio')
assert (v['width'],v['height'],v['r_frame_rate'],v['codec_name'],v['pix_fmt'],a['codec_name'])==(1920,1080,'30/1','h264','yuv420p','aac')
subprocess.run(['ffmpeg','-v','error','-i',str(video),'-f','null','-'],check=True,capture_output=True)
raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(video),'-map','0:a','-ac','1','-ar','24000','-f','f32le','-']);samples=np.frombuffer(raw,dtype='<f4');assert np.isfinite(samples).all() and np.max(np.abs(samples))<.999
T=json.loads((P/'timeline.json').read_text());assert len(T)==len(C);stages=defaultdict(float);pauses=[]
for i,t in enumerate(T):
 assert t['text']==C[i]['text']
 if i:assert abs(T[i-1]['end']-t['start'])<1/24000
 speech=samples[round(t['start']*24000):round(t['speech_end']*24000)];assert np.sqrt(np.mean(speech*speech))>.008
 assert abs((t['end']-t['pause_start'])-t['pause_seconds'])<1/24000
 assert t['pause_start']>=t['speech_end']
 if C[i]['pause']>=3:pauses.append(dict(scene=i,start=t['pause_start'],end=t['end'],seconds=t['pause_seconds']))
 stages[t['stage']]+=t['end']-t['start']
assert abs(float(meta['format']['duration'])-T[-1]['end'])<.1
assert T[challenge]['pause_seconds']==5
# Any long quiet interval must coincide with a declared processing/thinking pause.
block=2400;rms=np.sqrt(np.mean(samples[:len(samples)//block*block].reshape(-1,block)**2,axis=1));begin=None;long=[]
for k,quiet in enumerate(list(rms<.0015)+[False]):
 if quiet and begin is None:begin=k
 if not quiet and begin is not None:
  if (k-begin)*.1>=2:long.append((begin*.1,k*.1))
  begin=None
unexpected=[(s,e) for s,e in long if not any(s>=t['speech_end']-1 and e<=t['end']+.5 for t in T)]
assert not unexpected,unexpected
# MP4 faststart: moov atom precedes media data, so downloads can start playing early.
atoms=[]
with open(video,'rb') as f:
 while True:
  header=f.read(8)
  if len(header)<8:break
  size=int.from_bytes(header[:4],'big');name=header[4:].decode('ascii');atoms.append(name)
  if size==1:size=int.from_bytes(f.read(8),'big');f.seek(size-16,1)
  elif size>=8:f.seek(size-8,1)
  else:break
assert atoms.index('moov')<atoms.index('mdat')
# Contact sheet for visual review of every final cue.
contact=Image.new('RGB',(1280,360*((len(C)+1)//2)),'white')
for i in range(len(C)):contact.paste(Image.open(W/f'{i:02}.png').resize((640,360)),((i%2)*640,(i//2)*360))
contact.save(P/'visual-contact-sheet.jpg')
report=dict(file=video.name,bytes=video.stat().st_size,sha256=sha(video),duration_seconds=float(meta['format']['duration']),format='1920x1080, 30fps, H264 yuv420p, AAC 48kHz, faststart',full_decode='passed',audible_every_narration_segment=True,peak_dBFS=float(20*np.log10(np.max(np.abs(samples)))),unexpected_silence_over_two_seconds=unexpected,thinking_pauses=pauses,stage_duration_seconds=dict(stages),mathematics='All comparisons and equivalences passed exact-rational checks; every model part pixel checked; equivalent subdivisions preserve shaded quantity.',pedagogy='A-G sequence; concrete before symbols; fraction vocabulary; visual reasoning before comparison signs; guided predictions; denominator misconception; equivalent fraction modelling; five-second independent challenge; reflective recap.',curriculum='Year 5 same/related denominator foundations; thirds-versus-quarters challenge is guided extension using twelfths, not a claim that an LCM algorithm is required.',voice=dict(engine='Kokoro v1.0, sherpa-onnx 1.12.26',speaker='af_heart',id=3,accent='American English',native_synthesis_rates='0.87–0.94 depending on teaching role; not post-synthesis stretching',emotion_control='No explicit Kokoro emotion/emphasis controls exposed; rate changes are not evidence of expressive teaching performance.'),limitations=['Direct perceptual listening unavailable. Naturalness, pronunciation, warmth and emotional expressiveness require user review.','Same voice as previous Voice A; pedagogical design and native pacing improved, but no claim that underlying TTS expressiveness is solved.','Timings are measured narration segments, not word-level alignment.','Captions are segment-level transcript sidecars.'],models={p.name:sha(p) for p in [Path('/workspace/work/kokoro-multi-lang-v1_0/model.onnx'),Path('/workspace/work/kokoro-multi-lang-v1_0/voices.bin')]})
(P/'qa-results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
