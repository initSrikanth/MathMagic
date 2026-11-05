"""Two low-resolution, original-audio scene corrections; not full replacements or release approval."""
import json,sys,hashlib,subprocess,copy,math
from pathlib import Path
from fractions import Fraction
from contract import ROOT,REGISTER,branded,assert_preservation_edit_allowed
sys.path.insert(0,str(ROOT/'video-agent/production-v2'))
from graphics import draw,text,fraction,equation,INK,TEAL,GOLD,EMPTY,MUTED
from PIL import Image,ImageDraw
OUT=ROOT/'video-agent/remediation-35/model-previews'
def ramp(t,a,b):return max(0,min(1,(t-a)/(b-a)))
def render_frame(n,markers,t,imbase,timing,start,burn_captions=True):
 im=imbase.copy();d=ImageDraw.Draw(im);d.rectangle((120,260,1800,960),fill='white')
 if n==14:
  equation(d,[[1,2],'=','0.5','=','50%'],330)
  y=620;left=240;span=1440;p=ramp(t,0,.6);d.line((left,y,left+span*p,y),fill=MUTED,width=6)
  for x,label in [(left,'0'),(left+span,'1')]:d.line((x,y-20,x,y+20),fill=INK,width=4);text(d,label,x,y+45,44,INK,True)
  at=markers['midpoint'];p=ramp(t,at,at+.55)
  if p>0:
   x=left+span/2;d.line((left,y-55,left+span/2*p,y-55),fill=GOLD,width=7);d.ellipse((x-14*p,y-14*p,x+14*p,y+14*p),fill=TEAL);fraction(d,[1,2],x-30,y-160,45,TEAL);text(d,'0.5 = 50%',x,y+60,44,TEAL,True)
  note='Same whole, same midpoint, different names'
 else:
  for y,numerator,label,a,b,col in [(440,5,'One half = 0.5 = 50%',markers['half'],markers['half_shaded']+.55,TEAL),(650,4,'0.4 = 40%',markers['zero_point_four'],markers['four_shaded']+.6,GOLD)]:
   p=ramp(t,a,b);text(d,label,280,y-65,40,col)
   # Continuous filling, exactly 5/10 and 4/10 of equal wholes at the end.
   for cell in range(10):
    x=280+cell*126;d.rectangle((x,y,x+126,y+70),fill=EMPTY)
    amount=max(0,min(1,numerator*p-cell))
    if amount:d.rectangle((x,y,x+126*amount,y+70),fill=col)
    d.rectangle((x,y,x+126,y+70),outline='white',width=3)
   d.rectangle((280,y,1540,y+70),outline=INK,width=3)
  if t>=markers['equal_wholes']:text(d,'50% ? 40%',960,815,53,TEAL,True)
  note='Equal wholes and equal tenths make a fair comparison'
 # Captions use original narration timing and a separate reserved lower band.
 cap=next((c['text'] for c in timing['captions'] if c['start']<=start+t<c['end']),None)
 if cap and burn_captions:
  words=cap.split();lines=[];line=''
  for word in words:
   if len(line)+len(word)>95:lines.append(line);line=word
   else:line=(line+' '+word).strip()
  if line:lines.append(line)
  d.rounded_rectangle((110,890,1810,985),radius=12,fill='#143D3B')
  for j,s in enumerate(lines[:2]):text(d,s,960,905+34*j,29,'white',True)
 elif burn_captions:text(d,note,960,915,32,MUTED,True)
 return im

def preview(n,scene):
 r=json.loads(REGISTER.read_text())['records'][n-1];l=json.loads((ROOT/r['script']).read_text());timing=json.loads((ROOT/r['timing']).read_text());cue=timing['cues'][scene];start,end=cue['start'],cue['end'];duration=end-start
 assert_preservation_edit_allowed(r,l);OUT.mkdir(exist_ok=True);name=f'{n:02}-model-original-audio';video=OUT/(name+'.mp4');ev=OUT/(name+'.json')
 if video.exists() and ev.exists():print('Existing preview preserved',n);return
 assert Fraction(1,2)==Fraction('.5')==Fraction(50,100) and Fraction(4,10)==Fraction(40,100)
 # Actual full-audio recognition produced these word starts. ASR timing uncertainty is retained in evidence.
 markers=({'fifty_percent':64.0430832713445-start,'all_three_names':65.36308332379659-start,'midpoint':67.16308327611287-start,'between_zero_one':67.72308321889241-start} if n==14 else {'half':74.8848749332428-start,'half_shaded':75.16487490463257-start,'zero_point_four':76.564875-start,'four_shaded':77.28487502861023-start,'equal_wholes':78.92487465667725-start})
 base=copy.deepcopy(cue);base.update(board=[' '],equation=[],rows=[],line=None,note='');still=OUT/(name+'-base.png');draw(l,base,still,1);imbase=Image.open(still).convert('RGB');fps=12;count=math.ceil(duration*fps)
 audio=OUT/(name+'-audio.m4a');subprocess.run(['ffmpeg','-v','error','-y','-i',str(ROOT/r['mp4']),'-ss',str(start),'-t',str(duration),'-vn','-c:a','aac','-b:a','160k',str(audio)],check=True)
 ff=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','854x480','-r',str(fps),'-i','-','-i',str(audio),'-t',str(duration),'-c:v','libx264','-preset','veryfast','-crf','21','-pix_fmt','yuv420p','-c:a','copy','-movflags','+faststart',str(video)],stdin=subprocess.PIPE)
 for i in range(count):
  im=render_frame(n,markers,i/fps,imbase,timing,start)
  if i in (0,count//2,count-1):im.save(OUT/(name+f'-frame-{i:03}.png'))
  ff.stdin.write(im.resize((854,480),Image.Resampling.LANCZOS).tobytes())
 ff.stdin.close();assert ff.wait()==0;subprocess.run(['ffmpeg','-v','error','-i',str(video),'-f','null','-'],check=True)
 caps=[dict(c,start=max(0,c['start']-start),end=min(duration,c['end']-start)) for c in timing['captions'] if c['start']<end and c['end']>start]
 from brand_only_candidates import stamp
 video.with_suffix('.vtt').write_text('WEBVTT\n\n'+'\n\n'.join(stamp(c['start'])+' --> '+stamp(c['end'])+'\n'+c['text'] for c in caps)+'\n');video.with_name(video.stem+'-transcript.txt').write_text(cue['text']+'\n')
 ev.write_text(json.dumps(dict(number=n,scene=scene,source=r['mp4'],source_sha256=r['expected_sha256'],source_interval=[start,end],preview=str(video.relative_to(ROOT)),sha256=hashlib.sha256(video.read_bytes()).hexdigest(),native_narration=True,voice_regenerated=False,pitch_speed_changed=False,timing_method='Existing full-audio ASR word starts, approximate rather than forced alignment; conceptual perceptual review required',word_offsets=markers,mathematical_models='14: midpoint 1/2 = 0.5 = 50%; 15: equal ten-cell bars, 5/10 and 4/10',prediction_answer_hidden=True,full_decode=True,resolution=[854,480],status='UNVERIFIED_SCENE_PREVIEW_ONLY',deployed=False),indent=2)+'\n');still.unlink();audio.unlink();print('Original-audio animated model preview',n,flush=True)
if __name__=='__main__':
 for n,scene in [(14,5),(15,6)]:preview(n,scene)
