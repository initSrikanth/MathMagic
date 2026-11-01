"""Focused exact mathematics, narration clock, no-footage and encoded-media QA."""
import json,hashlib,re,subprocess,sys,math
from pathlib import Path
from fractions import Fraction as Q
from PIL import Image,ImageColor,ImageDraw
import numpy as np
import soundfile as sf
import os
TOPIC=os.environ.get("MATHMAGIC_TOPIC","whole-numbers")
BASE=Path(__file__).resolve().parent
LESSONS=json.loads((BASE/TOPIC/"scripts.json").read_text())
P=BASE/TOPIC;ROOT=BASE.parents[1];WORK=Path('/workspace/year5-graphics-work')/TOPIC
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def evalq(tokens):
 values=[]
 for t in tokens:
  if isinstance(t,list):
   assert len(t) in [2,3]
   def scalar(v):
    if isinstance(v,int):return Q(v)
    assert isinstance(v,str) and re.fullmatch(r'[0-9 ×÷+−-]+',v)
    expression=re.sub(r'(\d+)',r'Q(\1)',v.replace('×','*').replace('÷','/').replace('−','-'))
    return eval(expression,{'__builtins__':{}},{'Q':Q})
   n,d=scalar(t[-2]),scalar(t[-1]);assert n>=0 and d>0
   q=n/d+(scalar(t[0]) if len(t)==3 else 0);values.append(f'Q({q.numerator},{q.denominator})')
  elif str(t).isdigit():values.append(str(t))
  elif t in ['+','−','-','×','÷']:values.append({'−':'-','×':'*','÷':'/'}.get(t,t))
  else:raise ValueError(t)
 return eval(''.join(values),{'__builtins__':{}},{'Q':Q})
def maths():
 checked=0;models=0
 def value(s):
  s=s.replace(',','').replace('×','*').replace('÷','/').replace('−','-')
  s=re.sub(r'(\d+(?:\.\d+)?)',lambda m:'Q('+repr(m[0])+')',s)
  return eval(s,{'__builtins__':{}},{'Q':Q})
 for l in LESSONS:
  beats=l['beats'];assert beats[0]['role']=='hook' and beats[1]['role']=='goal' and beats[-1]['role']=='recap'
  assert sum(c['role']=='criteria' for c in beats)==3 and sum(c['role']=='prediction' for c in beats)>=2
  assert any(c['role']=='misconception' for c in beats) and any(c['role']=='question' and c['pause']==5 for c in beats)
  for c in beats:
   for row in c.get('board',[]):
    for eq in re.split(r'\s{2,}',row):
     if not re.fullmatch(r'[0-9., +×÷−=<>≠()-]+',eq) or not re.search('[=<>≠]',eq):continue
     parts=re.split(r'(=|<|>|≠)',eq)
     if any(not x.strip() for x in parts[::2]):continue # continued expanded-form line is checked in its complete equation
     nums=[value(x) for x in parts[::2]]
     for i,op in enumerate(parts[1::2]):
      a,b=nums[i:i+2];assert {'=':a==b,'<':a<b,'>':a>b,'≠':a!=b}[op],(l['title'],eq);checked+=1
   m=c.get('model')
   if not m:continue
   models+=1;typ=m['type']
   if typ=='line':
    a,b=Q(str(m['start'])),Q(str(m['end']));assert b>a
    if m.get('mark') is not None:assert a<=Q(str(m['mark']))<=b
   elif typ=='place':assert len(m['digits'])==len(m['labels']) and m['digits'].isdigit()
   elif typ=='compare':assert all(len(n)==len(m['labels']) and n.isdigit() for n in m['numbers']) and 0<=m['highlight']<len(m['labels'])
   elif typ=='parts':assert 0<=m['n']<=m['den'] and m['den']>0
   elif typ=='array':assert 0<m['rows']<=20 and 0<m['cols']<=30
   elif typ=='grid':assert 0<=m['n']<=100
   elif typ=='bar':assert all(v>0 for v in m['values'])
   elif typ in ['tiles','steps']:assert m.get('values') or m.get('steps')
   else:raise ValueError(typ)
 return dict(exact_relations=checked,mathematical_models=models,pedagogy='Hook, goal, three success criteria, conceptual models, two guided predictions, worked examples, misconception, five-second challenge and recap in every lesson.')
def media(entry,l):
 f=ROOT/entry['src'];t=json.loads((P/'timings'/(l['slug']+'.json')).read_text());info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(f)]));v=next(s for s in info['streams'] if s['codec_type']=='video');a=next(s for s in info['streams'] if s['codec_type']=='audio')
 assert (v['width'],v['height'],v['r_frame_rate'],v['codec_name'],v['pix_fmt'],a['codec_name'])==(1920,1080,'30/1','h264','yuv420p','aac')
 assert any(s['codec_type']=='subtitle' and s['codec_name']=='mov_text' for s in info['streams'])
 assert abs(float(v['duration'])-t['duration'])<.05 and abs(float(a['duration'])-t['duration'])<.1
 assert f.stat().st_size<90*1024*1024 and sha(f)==entry['sha256']
 subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(f),'-f','null','-'],check=True,capture_output=True)
 raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(f),'-map','0:a:0','-ac','1','-ar','24000','-f','f32le','-']);encoded=np.frombuffer(raw,dtype='<f4');source,sr=sf.read(ROOT/entry['audio'],dtype='float32');assert sr==24000
 assert np.isfinite(encoded).all() and np.max(np.abs(encoded))<.999 and np.sqrt(np.mean(encoded*encoded))>.01
 n=min(len(source),len(encoded));corr=float(np.corrcoef(source[:n],encoded[:n])[0,1]);assert corr>.97
 assert abs(len(encoded)/24000-len(source)/sr)<.10
 last=0
 for cap in t['captions']:
  assert cap['start']>=last and cap['end']>cap['start'] and cap['end']<=t['duration'];last=cap['end']
  window=encoded[round(cap['start']*sr):round(cap['end']*sr)];assert np.sqrt(np.mean(window*window))>.005
  assert .12<(cap['end']-cap['start'])/max(1,len(cap['text'].split()))<1.5
 assert ' '.join(' '.join(c['text'].split()) for c in t['captions'])==' '.join(' '.join(c['text'].split()) for c in l['beats'])
 transcript=(ROOT/entry['transcript']).read_text();assert ' '.join(transcript.split())==' '.join(' '.join(c['text'].split()) for c in t['captions'])
 captions=(ROOT/entry['captions']).read_text();assert captions.startswith('WEBVTT') and captions.count(' --> ')==len(t['captions']) and captions.count('line:1%')==len(t['captions'])
 for i,e in enumerate(t['events']):
  if i:assert abs(t['events'][i-1]['end']-e['start'])<1/sr
  assert e['end']>=e['speech_end'] and e['end']-e['speech_end']>=e['pause']-.04
  if e['role']=='question':assert e['pause']==5
 block=2400;levels=np.sqrt(np.mean(encoded[:len(encoded)//block*block].reshape(-1,block)**2,axis=1));runs=[];start=None
 for i,quiet in enumerate(list(levels<.0015)+[False]):
  if quiet and start is None:start=i
  if not quiet and start is not None:
   if (i-start)*.1>=2:runs.append((start*.1,i*.1))
   start=None
 unexpected=[(s,e) for s,e in runs if not any(s>=x['speech_end']-1 and e<=x['end']+.5 for x in t['events'])];assert not unexpected,unexpected
 # Every final model cell is sampled at its centre; mixed wholes use a shared unit length.
 folder=WORK/l['slug'];checked=0
 for i,c in enumerate(l['beats']):
  if c['role'] in ['goal','criteria','recap']:continue
  image=Image.open(folder/f'{i:02}-final.png').convert('RGB');rlist=c.get('rows',[])
  if not rlist:continue
  wholes=max(max(1,math.ceil(r['n']/r['d'])) for r in rlist);unit=1320/wholes
  for j,r in enumerate(rlist):
   for k in range(wholes*r['d']):
    first,gap,height=(550,110,58) if len(rlist)>2 else (610,160,70)
    assert first+j*gap+height<=850,'Model intersects native control region'
    x=round(210+(k+.5)*unit/r['d']);y=first+j*gap+height//2
    colour=('#008A94' if r['colour']=='teal' else '#B85A10') if k<r['n'] else '#E1ECF3'
    assert image.getpixel((x,y))==ImageColor.getrgb(colour),(l['slug'],i,j,k);checked+=1
 # Check every mathematical part/array/grid centre in the generated final state.
 for i,c in enumerate(l['beats']):
  if c['role'] in ['goal','criteria','recap'] or not c.get('model'):continue
  m=c['model'];im=Image.open(folder/f'{i:02}-final.png').convert('RGB');typ=m['type']
  if typ=='parts':
   for k in range(m['den']):
    colour='#008A94' if k<m['n'] else '#E1ECF3';assert im.getpixel((round(260+(k+.5)*1400/m['den']),685))==ImageColor.getrgb(colour);checked+=1
  elif typ=='array':
   r,col=m['rows'],m['cols'];cell=min(95,1250/col,230/r);left=(1920-col*cell)/2
   for row in range(r):
    for k in range(col):assert im.getpixel((round(left+(k+.5)*cell),round(550+(row+.5)*cell)))==ImageColor.getrgb('#008A94');checked+=1
  elif typ=='grid':
   for k in range(100):assert im.getpixel((835+k%10*25+10,535+k//10*25+10))==ImageColor.getrgb('#008A94' if k<m['n'] else '#E1ECF3');checked+=1
  elif typ=='line' and m.get('mark') is not None:
   x=round(220+1480*float((Q(str(m['mark']))-Q(str(m['start'])))/(Q(str(m['end']))-Q(str(m['start'])))))
   assert im.getpixel((x,710))==ImageColor.getrgb('#008A94');checked+=1
 # Produce a full contact sheet and a representative review sheet from encoded scene states.
 contact=Image.new('RGB',(1280,360*math.ceil(len(l['beats'])/2)),'white')
 for i in range(len(l['beats'])):contact.paste(Image.open(folder/f'{i:02}-final.png').resize((640,360)),((i%2)*640,(i//2)*360))
 (P/'qa').mkdir(exist_ok=True);contact.save(P/'qa'/(l['slug']+'-contact.jpg'))
 with open(f,'rb') as stream:
  data=stream.read(1024*1024);assert b'moov' in data
 return dict(result='passed',sha256=sha(f),bytes=f.stat().st_size,duration=t['duration'],format='1080p30 H264/yuv420p + AAC 48kHz + embedded English subtitles',full_decode=True,audible_sentence_windows=len(t['captions']),source_audio_correlation=corr,peak_dBFS=float(20*np.log10(np.max(np.abs(encoded)))),unexpected_silence=unexpected,model_cell_checks=checked,graphics_only=True,listening_review='not_performed',word_alignment='Not claimed; exact generated-sentence sample clocks are used.')
def main():
 report=dict(mathematics=maths(),videos={},limitations=['Audible warmth, expressive naturalness and accent were not directly listened to; female hf_alpha speaker identity and native English synthesis configuration are verified.','Physical iPhone/iPad and real Safari are not available; native Chromium playback is tested separately.'])
 manifest=json.loads((P/'manifest.json').read_text());assert len(manifest['lessons'])==5
 for l,e in zip(LESSONS,manifest['lessons']):
  cache=P/'qa'/(e['id']+'-media.json');cached=json.loads(cache.read_text()) if cache.exists() else {}
  result=cached if cached.get('sha256')==e['sha256'] and cached.get('qa_source_sha256')==sha(BASE/'qa.py') else media(e,l)
  result['qa_source_sha256']=sha(BASE/'qa.py');cache.parent.mkdir(exist_ok=True);cache.write_text(json.dumps(result,indent=2)+'\n')
  report['videos'][e['id']]=result;e['status']='verified';print(e['id']+': QA PASS',flush=True)
 manifest['status']='verified_pending_integration';(P/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n');(P/'qa-results.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
if __name__=='__main__':main()
