"""Deterministic 1080p teaching boards on the original narration clock.
Teacher frames and original audio advance continuously at native speed.
"""
import argparse,json,math,subprocess,re,hashlib
from pathlib import Path
from functools import lru_cache
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).parent;REPO=ROOT.parents[1]
NAVY='#19334e';TEAL='#087e81';BLUE='#187f9d';GREY='#e4f0f4';ORANGE='#a85b04'
@lru_cache(100)
def font(size,bold=False):return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans'+('-Bold'if bold else '')+'.ttf',size)
def label(d,x,y,s,size=44,bold=False,color=NAVY,maxwidth=None):
 assert '/'not in s,'No slash fractions in student graphics'
 while maxwidth and d.textlength(s,font=font(size,bold))>maxwidth:size-=1
 assert size>=24,('Unreadable text',s,size)
 d.text((x,y),s,font=font(size,bold),fill=color,anchor='mm')
def positions(avatar):return (690,1845)if avatar else(180,1740)
def table(d,m,y,left,right):
 cols=len(m['digits']);w=(right-left)/cols;h=150
 for i,(dig,name)in enumerate(zip(m['digits'],m['labels'])):
  x=left+i*w;highlight=i==m.get('highlight',-1)
  d.rounded_rectangle((x+3,y,x+w-3,y+h),radius=12,fill='#d4eeeb'if highlight else GREY,outline=TEAL if highlight else '#c2dbe2',width=3)
  for n,line in enumerate(name.split('\n')):label(d,x+w/2,y+28+n*30,line,26,True,maxwidth=w-12)
  label(d,x+w/2,y+110,dig,62,True,color=TEAL if highlight else NAVY)
def line(d,m,y,left,right,t):
 a,b=m['start'],m['end'];d.line((left,y,right,y),fill=NAVY,width=4)
 for i in range(11):
  x=left+(right-left)*i/10;d.line((x,y-14,x,y+14),fill=NAVY,width=3)
  if i%2==0 or m['decimals']==3:label(d,x,y+45,f'{a+(b-a)*i/10:.{m["decimals"]}f}',36,maxwidth=(right-left)/10-4)
 if m.get('mark')is None:return
 x=left+(right-left)*(m['mark']-a)/(b-a)
 # The moving indicator is a graphic only; it never changes narration timing.
 d.ellipse((x-10,y-10,x+10,y+10),fill=TEAL)
 label(d,x,y-45,f'{m["mark"]:.3f}',38,True,color=TEAL)

def content(p,al,t):
 avatar=p['method']=='avatar';left,right=positions(avatar);cx=(left+right)/2
 board=max((b for b in al['boards']if b['start']<=t),key=lambda b:b['start'],default=al['boards'][0])
 im=Image.new('RGB',(1920,1080),'#f6f6fc');d=ImageDraw.Draw(im)
 x0=644 if avatar else 70
 d.rounded_rectangle((x0,38,1887 if avatar else 1850,1046),radius=35,fill='white',outline='#d3e4ec',width=5)
 label(d,cx,106,'MathMagic • Whole Numbers & Place Value',32,True,color=TEAL,maxwidth=right-left)
 label(d,cx,182,p['title'],42,True,maxwidth=right-left)
 label(d,cx,270,board['heading'],39,True,maxwidth=right-left)
 model=board.get('model')
 if model:
  if model['type']=='place':table(d,model,330,left,right)
  else:
   model=dict(model)
   if p['id']=='lesson5' and board['heading']=='Zoom in to thousandths' and t<next(e['at']for e in board['events']if e['cue']=='Count seven'):model['mark']=None
   line(d,model,430,left+30,right-30,t)
 rowstart=570 if model else 400;step=110 if model else 120
 for idx,e in enumerate(board['events']):
  if t+1e-8<e['at']:continue
  # A short graphic-only reveal fade, never a speech/teacher hold.
  fade=min(1,max(0,(t-e['at'])/.18))
  color=tuple(round(255+(int(NAVY[j:j+2],16)-255)*fade)for j in (1,3,5))
  label(d,cx,rowstart+idx*step,e['text'],51,True,color=color,maxwidth=right-left)
 elapsed=(t-board['start'])/max(.001,board['end']-board['start']);n=al['boards'].index(board)
 # Retain a late-revealed strategy across the next board, without pausing speech.
 if n>0:
  prev=al['boards'][n-1]
  late=[e for e in prev['events']if prev['end']-e['at']<3 and t<e['at']+3]
  if late:
   label(d,cx,830,'Previous strategy',25,color=TEAL)
   label(d,cx,885,late[-1]['text'],36,True,maxwidth=right-left)
 for i in range(len(al['boards'])):
  xx=left+i*(right-left)/len(al['boards']);ww=(right-left)/len(al['boards'])-10
  d.rounded_rectangle((xx,1000,xx+ww,1008),radius=4,fill=TEAL if i<=n else GREY)
 label(d,cx,954,'Read the place • explain the value',27,color=TEAL,maxwidth=right-left)
 return im

def frame(p,al,t):
 im=content(p,al,t);b=max((b for b in al['boards']if b['start']<=t),key=lambda b:b['start'],default=al['boards'][0]);start=b['start']
 if start>0 and start<=t<start+.24:
  old=content(p,al,start-.001);im=Image.blend(old,im,(t-start)/.24)
 return im

def main():
 ap=argparse.ArgumentParser();ap.add_argument('lesson');ap.add_argument('--frames-only',action='store_true');args=ap.parse_args()
 p=next(x for x in json.loads((ROOT/'lessons.json').read_text())if x['id']==args.lesson);al=json.loads((ROOT/'sources'/f'{args.lesson}-alignment.json').read_text());source=Path(al['source']);dest=REPO/'videos'/f'MathMagic_{p["slug"]}_1080p.mp4'
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(source)]));v=next((s for s in probe['streams']if s['codec_type']=='video'),None)
 fps=v['avg_frame_rate']if v else'30';f=float(eval(fps,{'__builtins__':{}},{}));total=math.ceil(al['duration']*f)
 samples=[]
 for n,b in enumerate(al['boards']):
  t=min(b['end']-.05,max(b['start']+.3,max(e['at']for e in b['events'])+.3));img=frame(p,al,t);path=ROOT/'qa'/f'{args.lesson}-board-{n+1}.jpg';img.save(path,quality=95);samples.append(str(path))
 if args.frames_only:return
 cmd=['ffmpeg','-v','error','-y','-threads','2','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r',fps,'-i','pipe:0','-i',str(source)]
 if v:
  # The 16:9 provider output pillarboxes the complete 2:3 photo.
  # Remove only the synthetic side padding, keeping the entire original photo.
  sw,sh=v['width'],v['height'];corew=round(sh*2/3);corex=(sw-corew)//2
  assert corew<=sw
  vf=f'[1:v]crop={corew}:{sh}:{corex}:0,scale=606:912:force_original_aspect_ratio=decrease,pad=606:912:(ow-iw)/2:(oh-ih)/2:color=0xf6f6fc,setsar=1[t];[0:v][t]overlay=0:84:shortest=1[v]'
  assert not any(x in vf for x in ['setpts','tpad','atempo','loop'])
  cmd+=['-filter_complex',vf,'-map','[v]','-map','1:a:0','-c:a','copy']
 else:cmd+=['-map','0:v:0','-map','1:a:0','-c:a','aac','-b:a','192k']
 cmd+=['-c:v','libx264','-threads','2','-preset','fast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(dest.with_suffix('.working.mp4'))]
 (ROOT/'qa'/f'{args.lesson}-render-command.json').write_text(json.dumps(cmd,indent=2)+'\n')
 proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
 try:
  for n in range(total):
   proc.stdin.write(frame(p,al,n/f).tobytes())
   if n%900==0:print(args.lesson,n,total,flush=True)
 finally:proc.stdin.close()
 assert proc.wait()==0,'Render failed'
 dest.with_suffix('.working.mp4').replace(dest)
 (ROOT/'qa'/f'{args.lesson}-render.json').write_text(json.dumps(dict(filename=dest.name,bytes=dest.stat().st_size,sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),frames=total,fps=fps,source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),source_duration=al['duration'],pitch_speed_changes=False,silence_inserted=False,teacher_cropped=False),indent=2)+'\n')
 print('RENDERED',dest,flush=True)
if __name__=='__main__':main()
