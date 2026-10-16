"""Offline LCM graphics. Draft has no audio; final requires verified original clone audio and real word timestamps.
No network, TTS, HeyGen or publishing calls. Never pad/stretch narration.
"""
import argparse,json,re,math,hashlib,subprocess
from functools import lru_cache
from pathlib import Path
from fractions import Fraction
from PIL import Image,ImageDraw,ImageFont
HERE=Path(__file__).resolve().parent;REPO=HERE.parents[1]
LESSON=json.loads((HERE/'lesson.json').read_text())
NAVY='#19334e';BLUE='#187f9d';TEAL='#087e81';GREY='#e4f0f4';ORANGE='#a85b04'
@lru_cache(100)
def font(n,bold=False):return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans'+('-Bold'if bold else '')+'.ttf',n)
def text(d,x,y,s,n=42,bold=False,fill=NAVY):
 assert '/'not in str(s),'Slash notation prohibited in graphics'
 d.text((x,y),str(s),font=font(n,bold),anchor='mm',fill=fill)
def frac(d,x,y,v,scale=1):
 n,den=v;assert den>0
 f=font(round(82*scale),True);w=max(d.textlength(str(n),font=f),d.textlength(str(den),font=f))+18*scale
 text(d,x,y-53*scale,n,round(82*scale),True);text(d,x,y+53*scale,den,round(82*scale),True)
 d.line((x-w/2,y,x+w/2,y),fill=NAVY,width=max(2,round(4*scale)))
def equation(d,row,y,scale=1,count=None):
 widths=[145 if isinstance(t,list)else 80 for t in row];s=min(scale,1580/sum(widths));x=960-sum(widths)*s/2
 for idx,(t,w) in enumerate(zip(row,widths)):
  if count is not None and idx>=count:x+=w*s;continue
  cx=x+w*s/2
  if isinstance(t,list):frac(d,cx,y,t,s)
  else:text(d,cx,y,t,round(48*s),True)
  x+=w*s

def multiples(d,y,den,values,count,highlight=False):
 text(d,400,y,f'Multiples of {den}',42,True)
 for i,n in enumerate(values):
  if i>=count:break
  x=800+i*200
  if highlight and n==12:d.rounded_rectangle((x-76,y-54,x+76,y+54),radius=20,fill='#d4eeeb',outline=TEAL,width=4)
  text(d,x,y,n,64,True,TEAL if highlight and n==12 else NAVY)
 if count>=len(values):text(d,1680,y,'…',52)

def bars(d,y,a,b,total,fill=BLUE):
 # Equal-sized wholes, exact numerator/denominator partitions.
 x=445;w=1030;h=55
 d.rectangle((x,y,x+w,y+h),fill=GREY)
 d.rectangle((x,y,x+w*a/b,y+h),fill=fill)
 for k in range(1,total):d.line((x+w*k/total,y,x+w*k/total,y+h),fill=NAVY,width=2)
 d.rectangle((x,y,x+w,y+h),outline=NAVY,width=3)

def words(s):return re.findall(r'[a-z0-9]+',s.lower())
def validate_math():
 assert math.lcm(4,6)==12
 assert Fraction(1,4)==Fraction(3,12) and Fraction(1,6)==Fraction(2,12)
 assert Fraction(1,4)+Fraction(1,6)==Fraction(5,12)
 assert math.gcd(5,12)==1
 assert Fraction(1*3,4*3)==Fraction(1,4) and Fraction(1*2,6*2)==Fraction(1,6)
 assert all('/'not in s['narration']for s in LESSON['scenes'])
 return True

def load_alignment(path,audio,provenance):
 p=json.loads(provenance.read_text())
 assert p['provider']=='ElevenLabs' and p['verified_clone_name']==LESSON['voice']['clone_name']
 assert p['verified_voice_id']==p['approved_voice_id'] and p['verified_voice_id']
 assert p['actual_settings']==p['approved_settings'] and p['model_id']
 assert p['audio_sha256']==hashlib.sha256(audio.read_bytes()).hexdigest()
 info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-of','json',str(audio)]));duration=float(info['format']['duration'])
 data=json.loads(path.read_text());data=data.get('normalized_alignment')or data.get('alignment')or data
 chars=data['characters'];starts=data['character_start_times_seconds'];ends=data['character_end_times_seconds']
 assert len(chars)==len(starts)==len(ends) and starts==sorted(starts)
 joined=''.join(chars);records=[];pos=0;bounds=[]
 for ch,a,b in zip(chars,starts,ends):
  bounds.extend([(a,b)]*len(ch))
 for m in re.finditer(r'[a-z0-9]+',joined.lower()):records.append({'word':m.group(),'start':bounds[m.start()][0],'end':bounds[m.end()-1][1]})
 expected=words(' '.join(s['narration']for s in LESSON['scenes']));assert [x['word']for x in records]==expected,'Actual narration must match the full script'
 cursor=0;scenes=[]
 for scene in LESSON['scenes']:
  n=len(words(scene['narration']));ws=records[cursor:cursor+n];cursor+=n
  scenes.append(dict(scene=scene,start=ws[0]['start'],end=ws[-1]['end'],words=ws))
 # All source audio is retained, including any natural initial/trailing pauses.
 scenes[0]['start']=0
 for i in range(len(scenes)-1):scenes[i]['end']=scenes[i+1]['start']
 scenes[-1]['end']=duration
 return scenes,duration

def draft_timeline():
 scenes=[];cursor=0
 for scene in LESSON['scenes']:
  tokens=words(scene['narration']);length=scene['draft_seconds'];step=length/len(tokens)
  scenes.append(dict(scene=scene,start=cursor,end=cursor+length,words=[dict(word=w,start=cursor+j*step,end=cursor+(j+1)*step)for j,w in enumerate(tokens)]));cursor+=length
 return scenes,cursor

def anchor(scene,phrase,offset=0):
 target=words(phrase);hay=[w['word']for w in scene['words']];hits=[i for i in range(len(hay)-len(target)+1)if hay[i:i+len(target)]==target]
 assert len(hits)==1,(scene['scene']['id'],phrase,hits)
 return scene['words'][hits[0]+offset]['start']

def content(t,scenes):
 im=Image.new('RGB',(1920,1080),'white');d=ImageDraw.Draw(im)
 i=max(k for k,s in enumerate(scenes)if t>=s['start']);scene=scenes[i];sid=scene['scene']['id']
 text(d,960,190,['The smallest shared positive multiple','Start with the multiples of four','Now list multiples of six','Choose the first shared positive number','Use equal-sized parts','Rename one quarter','Rename one sixth','Add the numerators; keep twelve','Shared multiples → smallest → rename → calculate'][i],38)
 if i<=3:
  n4=0 if i==0 else 4;n6=0 if i<2 else 3
  if i==1:
   n4=sum(t>=anchor(scene,'four eight twelve sixteen',j)for j in range(4))
  if i==2:n6=sum(t>=anchor(scene,'six twelve eighteen',j)for j in range(3))
  if i==0:
   text(d,960,340,'Lowest Common Multiple',70,True);text(d,960,455,'LCM',108,True)
   text(d,960,640,'A positive multiple shared by both numbers',43)
   text(d,960,730,'Choose the smallest one',50,True)
  else:
   shared=i==3 and t>=anchor(scene,'Twelve is the first')
   multiples(d,365,4,[4,8,12,16],n4,shared)
   multiples(d,540,6,[6,12,18],n6,shared)
   if shared:text(d,960,780,'LCM of 4 and 6 = 12',72,True,TEAL)
 else:
  if i==4:
   equation(d,[[1,4],'+',[1,6],'=','?'],360)
   text(d,960,600,'4 × 3 = 12        6 × 2 = 12',58,True)
   text(d,960,770,'Common denominator: 12',52,True,TEAL)
  elif i==5:
   text(d,960,285,'Multiply numerator and denominator by 3',37)
   equation(d,[[1,4],'=',[3,12]],430,count=3 if t>=anchor(scene,'One quarter equals three twelfths',3)else 1)
   bars(d,675,1,4,12)
   text(d,960,805,'Same amount, smaller equal parts',42,True)
  elif i==6:
   equation(d,[[1,4],'=',[3,12]],320,.75)
   text(d,960,480,'Multiply numerator and denominator by 2',37)
   row=[[1,6],'=',[2,12]]
   equation(d,row,620,count=3 if t>=anchor(scene,'One sixth equals two twelfths',3)else 1);bars(d,810,1,6,12)
  elif i==7:
   equation(d,[[1,4],'=',[3,12]],300,.68)
   equation(d,[[1,6],'=',[2,12]],475,.68)
   row=[[3,12],'+',[2,12],'=',[5,12]]
   equation(d,row,700,.9,count=5 if t>=anchor(scene,'That makes five twelfths',2)else 3)
   if t>=anchor(scene,'The answer is already'):text(d,960,905,'Already in simplest form',37,True,TEAL)
  else:
   equation(d,[[1,4],'+',[1,6],'=',[5,12]],355)
   text(d,960,600,'Any common denominator can work',46,True)
   text(d,960,710,'The LCM usually keeps the numbers smaller',43,True,TEAL)
 return im

def frame(t,scenes,draft=True):
 im=Image.new('RGB',(1920,1080),'#f5f5fa');d=ImageDraw.Draw(im)
 d.rounded_rectangle((55,35,1865,1045),radius=32,fill='white',outline='#d3e4ec',width=4)
 text(d,960,100,LESSON['title'],52,True)
 c=content(t,scenes);i=max(k for k,s in enumerate(scenes)if t>=s['start']);start=scenes[i]['start']
 if i and t-start<.3:c=Image.blend(content(start-.001,scenes),c,max(0,(t-start)/.3))
 im.paste(c.crop((80,155,1840,955)),(80,155))
 if draft:text(ImageDraw.Draw(im),960,1000,'SILENT GRAPHICS DRAFT • narration unavailable • timing illustrative',27,True,ORANGE)
 return im

def main():
 p=argparse.ArgumentParser();p.add_argument('--draft',action='store_true');p.add_argument('--audio',type=Path);p.add_argument('--alignment',type=Path);p.add_argument('--provenance',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args();validate_math()
 if a.draft:
  assert not a.audio;scenes,duration=draft_timeline()
 else:
  if not all([a.audio,a.alignment,a.provenance]):raise SystemExit('BLOCKED: exact ElevenLabs clone audio, actual alignment and verified voice provenance required; no substitute voice or estimated final timing')
  scenes,duration=load_alignment(a.alignment,a.audio,a.provenance)
 cmd=['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','30','-i','pipe:0']
 if a.audio:cmd+=['-i',str(a.audio),'-map','0:v:0','-map','1:a:0','-c:a','aac','-b:a','192k']
 else:cmd+=['-an']
 cmd+=['-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(a.output)]
 a.output.parent.mkdir(exist_ok=True,parents=True);proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
 try:
  for n in range(math.ceil(duration*30)):
   proc.stdin.write(frame(n/30,scenes,a.draft).tobytes())
   if n%600==0:print(n,flush=True)
 finally:proc.stdin.close()
 if proc.wait():raise RuntimeError('Render failed')
 report={'status':'SILENT_DRAFT_NOT_NARRATED_NOT_PUBLICATION_READY'if a.draft else'REVIEW_CANDIDATE_HUMAN_APPROVAL_REQUIRED','seconds':duration,'fps':30,'size':[1920,1080],'bytes':a.output.stat().st_size,'sha256':hashlib.sha256(a.output.read_bytes()).hexdigest(),'actual_word_alignment':not a.draft,'teacher':None,'heygen_calls':0,'credits_spent':0,'scenes':scenes}
 a.output.with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k!='scenes'},indent=2))
if __name__=='__main__':main()
