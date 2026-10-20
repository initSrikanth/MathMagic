"""One review-only lesson, reusing production-v2 geometry and FFmpeg composition."""
import sys,json,math,subprocess,hashlib
from pathlib import Path
import numpy as np
import soundfile as sf
import sherpa_onnx
from PIL import Image,ImageDraw
from lesson import C
OUT=Path(__file__).parent;ROOT=OUT.resolve().parents[1]
sys.path.insert(0,str(ROOT/'video-agent/production-v2'));import graphics as g
WORK=Path('/workspace/work/comparing-redesign-render');WORK.mkdir(exist_ok=True)
MODEL=Path('/workspace/work/kokoro-multi-lang-v1_0')
g.BG='#F1F8FF';g.TEAL='#008B8B';g.GOLD='#BF6500';g.EMPTY='#E5EFF8';g.INK='#17324D';g.MUTED='#465C73'
RATES={'question':.94,'term':.87,'discovery':.94,'misconception':.88,'recap':.90,'explanation':.90}
def run(args):subprocess.run(list(map(str,args)),check=True,capture_output=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def stamp(t):
 m=round(t*1000);return f'{m//3600000:02}:{m//60000%60:02}:{m//1000%60:02}.{m%1000:03}'
def render(c,path,partition=1):
 g.draw({'title':'Comparing Fractions','topic':'fractions','section':'meaning'},c,path,1)
 im=Image.open(path).convert('RGB');d=ImageDraw.Draw(im)
 if c.get('hide'):
  d.rectangle((1550,440,1780,815),fill='white')
 if c.get('concrete'):
  for j,r in enumerate(c['rows']):
   y=490+j*170;cell=1260/r['d']
   for k in range(r['d']):
    x=260+k*cell;colour=('#744126' if j==0 else '#A65C22') if k<r['n'] else '#F0DEC8'
    d.rounded_rectangle((x+2,y,x+cell-2,y+62),radius=5,fill=colour,outline='#5E361F',width=2)
    if k<r['n']:d.line((x+14,y+13,x+cell-14,y+13),fill='#C3956E',width=2)
 elif c.get('subdivide'):
  # Preserve the exact shaded length. Only new partition lines grow into view.
  for j,r in enumerate(c['rows']):
   old=c['subdivide'][j];new=r['d'];y=490+j*170
   if old==new:continue
   d.rectangle((260,y,1520,y+58),fill=g.EMPTY)
   if r['n']:d.rectangle((260,y,260+1260*r['n']/new,y+58),fill=g.TEAL if r['colour']=='teal' else g.GOLD)
   for k in range(1,old):
    x=round(260+1260*k/old);d.line((x,y,x,y+58),fill=('white' if k/old<r['n']/new else '#6D899D'),width=3)
   for k in range(1,new):
    x=round(260+1260*k/new);d.line((x,y,x,y+round(58*partition)),fill=('white' if k<r['n'] else '#6D899D'),width=3)
   d.line((260,y,260,y+58),fill=g.INK,width=4);d.line((1520,y,1520,y+58),fill=g.INK,width=4)
 if not c.get('concrete') and not c.get('subdivide'):
  for j,r in enumerate(c['rows']):
   y=490+j*170
   for k in range(1,r['d']):
    x=round(260+1260*k/r['d']);d.line((x,y,x,y+58),fill='white' if k<r['n'] else '#6D899D',width=3)
 if c.get('annotation'):
  if c['annotation']=='both':
   g.text(d,'Numerator: parts chosen',1110,275,32,g.INK,maxw=620);d.line((1085,296,1010,296),fill=g.TEAL,width=3)
  g.text(d,'Denominator: parts in the whole',1110,365,30,g.INK,maxw=650);d.line((1085,384,1010,384),fill=g.TEAL,width=3)
 if c.get('recap'):
  for title,eq,y in [('Same denominator',[[3,4],'>',[2,4]],285),('Same numerator',[[1,2],'>',[1,4]],475),('Different denominators',[[1,2],'<',[2,3]],665)]:
   g.text(d,title,420,y+45,37,g.INK,maxw=600)
   # Reuse stacked notation; familiar examples are intentionally small in number.
   x=1060
   for t in eq:
    if isinstance(t,list):g.fraction(d,t,x,y+5,49);x+=105
    else:g.text(d,t,x,y+30,50,g.TEAL);x+=100
 im.save(path)
def main():
 (OUT/'storyboard.json').write_text(json.dumps(C,indent=2,ensure_ascii=False)+'\n')
 (OUT/'transcript.md').write_text('# Comparing Fractions — redesigned lesson\n\n'+'\n\n'.join('## '+c['chapter']+'\n\n'+c['text']+(f'\n\n[Thinking time: {c["pause"]} seconds.]' if c['pause']>=3 else '') for c in C)+'\n')
 tts=sherpa_onnx.OfflineTts(sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(kokoro=sherpa_onnx.OfflineTtsKokoroModelConfig(model=str(MODEL/'model.onnx'),voices=str(MODEL/'voices.bin'),tokens=str(MODEL/'tokens.txt'),data_dir=str(MODEL/'espeak-ng-data'),lexicon=str(MODEL/'lexicon-us-en.txt')),num_threads=3),max_num_sentences=1))
 sr=tts.sample_rate;audio=[];timeline=[];clips=[];total=0;previous=None;vtt=['WEBVTT\n']
 for i,c in enumerate(C):
  speed=RATES[c.get('tone','explanation')];key=hashlib.sha256(json.dumps([c['text'],3,speed]).encode()).hexdigest();wav=WORK/(key+'.wav')
  if not wav.exists():
   generated=tts.generate(c['text'],sid=3,speed=speed);sf.write(wav,generated.samples,sr,subtype='PCM_16')
  a,rate=sf.read(wav,dtype='float32');assert rate==sr and np.sqrt(np.mean(a*a))>.005 and np.max(np.abs(a))<1
  pauseframes=math.ceil(c['pause']*30);speechframes=math.ceil(len(a)/sr*30);frames=speechframes+pauseframes;count=round(frames*sr/30)
  start=total/sr;end=(total+len(a))/sr;audio.append(np.pad(a,(0,count-len(a))));total+=count
  timeline.append(dict(scene=i,stage=c['stage'],chapter=c['chapter'],start=start,speech_end=end,pause_start=start+speechframes/30,end=total/sr,pause_seconds=pauseframes/30,rate=speed,text=c['text'],audio_sha256=sha(wav)))
  vtt.append(f'{stamp(start)} --> {stamp(end)}\n{c["text"]}\n')
  final=WORK/f'{i:02}.png';render(c,final);im=Image.open(final).convert('RGB');entries=[]
  # Purposeful subdivision grows new boundaries without changing coloured quantities.
  animframes=60 if c.get('subdivide') else 12
  for k in range(animframes):
   target=WORK/f'{i:02}-anim-{k:02}.png'
   if c.get('subdivide'):
    render(c,target,(k+1)/animframes)
    if previous and k<12:Image.blend(previous,Image.open(target).convert('RGB'),(k+1)/12).save(target)
   else:(Image.blend(previous,im,(k+1)/12) if previous else im).save(target)
   entries.append(f"file '{target}'\nduration {1/30:.9f}\n")
  entries.append(f"file '{final}'\nduration {(speechframes-animframes)/30:.9f}\n")
  if c['pause']>=3:
   # Clearly signposted intentional thinking interval, never a failed audio segment.
   for k in range(pauseframes):
    p=WORK/f'{i:02}-think-{k//30:02}.png'
    if k%30==0:
     hold=im.copy();d=ImageDraw.Draw(hold);left=math.ceil((pauseframes-k)/30);unit='second' if left==1 else 'seconds';g.text(d,f'Thinking time · {left} {unit}',960,845,34,g.GOLD,True);hold.save(p)
    entries.append(f"file '{p}'\nduration {1/30:.9f}\n")
  else:entries.append(f"file '{final}'\nduration {pauseframes/30:.9f}\n")
  entries.append(f"file '{final}'\n");listing=WORK/f'{i:02}.txt';listing.write_text(''.join(entries));clip=WORK/f'{i:02}.mp4'
  if not clip.exists():run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',listing,'-vf','fps=30,format=yuv420p','-frames:v',frames,'-c:v','libx264','-preset','veryfast','-crf','21','-threads','3',clip])
  clips.append(clip);previous=im;print(f'{i+1}/{len(C)} {c["stage"]}: {len(a)/sr:.2f}s speech + {pauseframes/30:.2f}s processing',flush=True)
 listing=WORK/'clips.txt';listing.write_text(''.join(f"file '{p}'\n" for p in clips));sf.write(WORK/'narration.wav',np.concatenate(audio),sr,subtype='PCM_16')
 output=OUT/'Comparing_Fractions_Redesigned_Prototype.mp4'
 run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',listing,'-i',WORK/'narration.wav','-map','0:v','-map','1:a','-c:v','copy','-af','loudnorm=I=-18:TP=-2:LRA=9','-c:a','aac','-b:a','160k','-ar','48000','-movflags','+faststart','-shortest',output])
 (OUT/'timeline.json').write_text(json.dumps(timeline,indent=2)+'\n');(OUT/'captions.vtt').write_text('\n'.join(vtt));print(f'FINISHED {total/sr:.2f}s',flush=True)
if __name__=='__main__':main()
