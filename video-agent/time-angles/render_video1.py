"""MathMagic Time and Angles 1: Kokoro hf_alpha, animated clocks and timelines.
Run from repository root: python video-agent/time-angles/render_video1.py
Requires sherpa-onnx, Pillow, numpy, soundfile, ffmpeg, and Kokoro v1.0 model.
Set KOKORO_MODEL to the directory containing model.onnx, voices.bin, tokens.txt.
No fallback voice is permitted.
"""
import os, math, re, json, subprocess, tempfile, wave
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import sherpa_onnx
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"videos"/"MathMagic_Time_Angles_01_Reading_Time_and_Duration_EXTENDED.mp4"
MODEL=Path(os.environ.get("KOKORO_MODEL","/workspace/fractions-five-work/kokoro-multi-lang-v1_0"))
W,H=1920,1080
BG="#FFF9EE";INK="#17354D";TEAL="#008A94";ORANGE="#B85A10";MUTED="#6A8398"
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BEATS=[
("hook","Imagine you are waiting for a bus. It leaves at nine fifteen and reaches your destination at ten oh five. You glance at the clock and wonder, how long did the journey really take? Could it be ten minutes? Or is there something we are missing? Let us find out together.","journey",9,15,10,5),
("introduction","Today we are learning how to read time and calculate duration. By the end of this lesson, you will be able to solve our bus mystery yourself.","journey",9,15,10,5),
("goal","Our learning goal is to read time accurately, calculate elapsed time, and explain our thinking using clocks and timelines.","clock",9,15),
("criteria","By the end, you can read the hour and minute hands, calculate a duration that crosses the hour, and check your answer with a timeline.","clock",9,15),
("explanation","Start with the minute hand. Each large step around the clock is five minutes. The minute hand at three means fifteen minutes past the hour.","clock",9,15),
("explanation","Now find the short hour hand. It sits a little after nine, because fifteen minutes of the ninth hour have passed. This clock shows nine fifteen.","clock",9,15),
("question","Look at this clock. What time does it show? Read the minute hand first, then the hour hand. Give yourself five seconds to decide.","clock",3,40),
("answer","The minute hand points to eight, or forty minutes. The hour hand is between three and four. It is three forty, not eight fifteen.","clock",3,40),
("explanation","Let's return to our bus journey. It begins at nine fifteen and finishes at ten oh five. We can make the calculation easier by jumping to the next hour.","journey",9,15,10,5),
("prediction","From nine fifteen to ten o'clock, how many minutes pass? You could count in fives, or subtract fifteen from sixty.","timeline",9,15,10,0),
("answer","Forty-five minutes pass between nine fifteen and ten o'clock. That is our first part of the journey.","timeline",9,15,10,0),
("explanation","Then the bus travels another five minutes, from ten o'clock to ten oh five. We add the two parts: forty-five plus five equals fifty minutes.","journey",9,15,10,5),
("misconception","A common mistake is to subtract fifteen from five and say the journey took ten minutes. That ignores the change of hour. A timeline makes the missing minutes visible.","journey",9,15,10,5),
("explanation","Now let's read twenty-four-hour time. Nine fifteen in the morning is written zero nine fifteen. Three forty in the afternoon is written fifteen forty.","conversion",9,15,15,40),
("explanation","For afternoon times after twelve, add twelve to the hour. Three plus twelve equals fifteen. The minutes do not change.","conversion",3,40,15,40),
("question","A movie begins at thirteen twenty and ends at fourteen ten. Before I reveal the answer, estimate: is the duration closer to thirty minutes or one hour?","timeline",13,20,14,10),
("answer","From thirteen twenty to fourteen hundred is forty minutes. Another ten minutes takes us to fourteen ten. The total is fifty minutes.","timeline",13,20,14,10),
("explanation","Here is a useful trick. A clock has sixty minutes, but only twelve large numbers. Each jump between two neighbouring numbers represents five minutes. Start at twelve and count five, ten, fifteen, twenty, twenty-five, and thirty.","clock",6,30),
("question","Take a look at this clock showing six thirty. Before you hear my answer, point to the minute hand. Why does it point to six instead of thirty? Pause and think about what each large number represents.","clock",6,30),
("answer","The long minute hand points to six, which represents thirty minutes. The shorter hour hand is halfway between six and seven. Half past six is written six thirty. We never read the number under the minute hand as the minutes directly.","clock",6,30),
("explanation","We can also use the word quarter. A quarter of sixty minutes is fifteen minutes. When the minute hand points to three, it is quarter past the hour. When it points to nine, it is quarter to the next hour.","clock",9,45),
("question","This clock shows nine forty-five. Is that quarter past nine, or quarter to ten? Look closely at where the shorter hour hand is moving. Give yourself five seconds to decide.","clock",9,45),
("answer","It is quarter to ten. Forty-five minutes have already passed since nine o'clock, and fifteen minutes remain until ten. The hour hand is nearly at ten. That is why we say quarter to ten.","clock",9,45),
("explanation","To calculate a duration, we are not looking for the difference between two clock numbers. We want the amount of time that actually passes. A number line or timeline shows each part of the journey clearly.","timeline",9,15,10,5),
("explanation","Think of ten o'clock as a friendly stopping point. First travel from nine fifteen to ten o'clock. Then travel from ten o'clock to ten oh five. We can add the two durations because the parts do not overlap.","timeline",9,15,10,5),
("question","Try another example. A swimming lesson begins at two twenty-five and finishes at three ten. How many minutes until three o'clock? Then how many more minutes until three ten? Work it out before the explanation.","timeline",14,25,15,10),
("answer","From two twenty-five to three o'clock is thirty-five minutes. From three o'clock to three ten is another ten minutes. Thirty-five plus ten equals forty-five minutes. The swimming lesson lasts forty-five minutes.","timeline",14,25,15,10),
("misconception","Check the reasonableness of your answer. If an activity begins before three o'clock and finishes just after three o'clock, a duration of five minutes is too short. Estimate first, then calculate to catch mistakes.","timeline",14,25,15,10),
("explanation","Now let us compare morning and afternoon times. A digital clock may show three forty in the afternoon, while a twenty-four-hour clock shows fifteen forty. Both represent exactly the same moment.","conversion",3,40,15,40),
("question","Here is a quick check. If a sports match starts at fourteen twenty, what time is that on a twelve-hour clock? Think about subtracting twelve from the hour. The minutes should stay exactly the same.","conversion",14,20,2,20),
("answer","Fourteen minus twelve equals two, so fourteen twenty is two twenty in the afternoon. Notice that we did not subtract twelve from the minutes. The twenty minutes remain twenty minutes.","conversion",14,20,2,20),
("explanation","Be careful around midday. Twelve noon is twelve hundred in twenty-four-hour time. Midnight is zero hundred. These two moments are twelve hours apart, even though both may be written as twelve on a twelve-hour clock.","conversion",12,0,0,0),
("question","Here is our final independent challenge. A train leaves at eleven thirty-five and reaches its destination at twelve twenty. How long does it travel? Draw a timeline with noon as the middle stop and solve each part.","timeline",11,35,12,20),
("answer","From eleven thirty-five to noon is twenty-five minutes. From noon to twelve twenty is another twenty minutes. Twenty-five plus twenty equals forty-five minutes. The train journey takes forty-five minutes.","timeline",11,35,12,20),
("recap","To check your understanding, explain the method to someone else. Read the clock hands, choose a helpful hour boundary, count each jump, and add the minutes. If your answer seems surprising, draw the timeline again.","timeline",11,35,12,20),
("recap","Today you read clock hands, crossed an hour boundary, and converted between twelve-hour and twenty-four-hour time. Remember: count the time between the two moments, not just the numbers on the clock.","journey",9,15,10,5),
("recap","Your challenge: a train departs at eleven thirty-five and arrives at twelve twenty. Draw a timeline, find the duration, and explain each jump. Then try the MathMagic practice.","timeline",11,35,12,20),
]
def font(sz):return ImageFont.truetype(FONT,sz)
def txt(d,s,x,y,size=50,fill=INK,anchor="mm"):
 d.text((x,y),s,font=font(size),fill=fill,anchor=anchor)
def clock(d,cx,cy,r,h,m,progress):
 d.ellipse((cx-r,cy-r,cx+r,cy+r),fill="#FFFFFF",outline=INK,width=8)
 for k in range(60):
  a=math.radians(k*6-90);inner=r-(35 if k%5==0 else 16)
  d.line((cx+inner*math.cos(a),cy+inner*math.sin(a),cx+(r-7)*math.cos(a),cy+(r-7)*math.sin(a)),fill=INK,width=5 if k%5==0 else 2)
 for k in range(1,13):
  a=math.radians(k*30-90);txt(d,str(k),cx+(r-76)*math.cos(a),cy+(r-76)*math.sin(a),39)
 ah=math.radians((h%12+m/60)*30-90);am=math.radians(m*6-90)
 d.line((cx,cy,cx+r*.53*math.cos(ah),cy+r*.53*math.sin(ah)),fill=INK,width=17)
 d.line((cx,cy,cx+r*.76*math.cos(am)*progress,cy+r*.76*math.sin(am)*progress),fill=TEAL,width=11)
 d.ellipse((cx-12,cy-12,cx+12,cy+12),fill=ORANGE)
def timefmt(h,m):return f"{h:02d}:{m:02d}"
def draw(beat,p,path):
 role,spoken,kind,*args=beat
 im=Image.new("RGB",(W,H),BG);d=ImageDraw.Draw(im)
 txt(d,"READING TIME AND DURATION",960,210,45,MUTED)
 title={"hook":"The mystery of the bus journey","introduction":"Today we are learning…","goal":"Today's Learning Goal","criteria":"Success Criteria","explanation":"Let's investigate","question":"Your turn — predict","prediction":"Think before calculating","answer":"Reveal and explain","misconception":"Spot the mistake","conversion":"12-hour and 24-hour time","recap":"What have we learned?"}.get(role,"Explore the mathematics")
 txt(d,title,960,292,59,INK)
 if kind=="clock":
  h,m=args;clock(d,960,650,310,h,m,p)
  txt(d,timefmt(h,m),960,1000,60,TEAL)
 elif kind in ("journey","timeline"):
  h1,m1,h2,m2=args;start=h1*60+m1;end=h2*60+m2
  if kind=="journey":
   clock(d,510,640,210,h1,m1,1);clock(d,1410,640,210,h2,m2,p)
   txt(d,timefmt(h1,m1),510,920,54,TEAL);txt(d,timefmt(h2,m2),1410,920,54,ORANGE)
   txt(d,"Departure",510,970,35,MUTED);txt(d,"Arrival",1410,970,35,MUTED)
  else:
   x0,x1,y=260,1660,650
   d.line((x0,y,x1,y),fill="#D7E6E8",width=16)
   d.line((x0,y,x0+(x1-x0)*p,y),fill=TEAL,width=16)
   mid=(start//60+1)*60
   marks=[(start,timefmt(h1,m1)),(end,timefmt(h2,m2))]
   if start<mid<end:marks.insert(1,(mid,timefmt(mid//60,0)))
   for t,label in marks:
    x=x0+(x1-x0)*(t-start)/(end-start)
    d.ellipse((x-14,y-14,x+14,y+14),fill=ORANGE if t==end else TEAL)
    txt(d,label,x,y+75,46)
   if role in ("answer","recap"):
    txt(d,f"{end-start} minutes",960,880,72,TEAL)
 elif kind=="conversion":
  h1,m1,h2,m2=args
  txt(d,timefmt(h1,m1),620,620,110,TEAL)
  txt(d,"→",960,620,100,INK)
  txt(d,timefmt(h2,m2),1300,620,110,ORANGE)
  txt(d,"12-hour / 24-hour comparison",960,820,43,MUTED)
 im.save(path)
def run(cmd):subprocess.run(cmd,check=True,stdout=subprocess.DEVNULL)
def main():
 for p in ("model.onnx","voices.bin","tokens.txt","espeak-ng-data","lexicon-us-en.txt"):
  if not (MODEL/p).exists():raise SystemExit(f"Missing Kokoro asset: {MODEL/p}. No voice substitution allowed.")
 cfg=sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(kokoro=sherpa_onnx.OfflineTtsKokoroModelConfig(model=str(MODEL/"model.onnx"),voices=str(MODEL/"voices.bin"),tokens=str(MODEL/"tokens.txt"),data_dir=str(MODEL/"espeak-ng-data"),lexicon=str(MODEL/"lexicon-us-en.txt")),num_threads=3),max_num_sentences=1)
 tts=sherpa_onnx.OfflineTts(cfg);assert tts.num_speakers>31
 OUT.parent.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory() as tmp:
  work=Path(tmp);audio=[];clips=[];cues=[];elapsed=0.
  for i,beat in enumerate(BEATS):
   speech=tts.generate(beat[1],sid=31,speed=.91)
   assert speech.sample_rate==24000
   a=np.asarray(speech.samples,dtype=np.float32)
   assert len(a)>24000 and np.sqrt(np.mean(a*a))>.005
   pause=5.0 if beat[0] in ("question","prediction") else 1.0
   audio.append(a);audio.append(np.zeros(int(pause*24000),dtype=np.float32))
   duration=len(a)/24000+pause;frames=math.ceil(duration*30)
   cues.append(dict(start=elapsed,end=elapsed+duration,text=beat[1],role=beat[0]));elapsed+=duration
   # Real mathematical motion: minute hands and timeline segments reveal progressively.
   n=18;listing=[]
   for j in range(n):
    frame=work/f"{i:02}-{j:02}.png";draw(beat,(j+1)/n,frame)
    listing.append(f"file '{frame}'\nduration {1/30:.8f}\n")
   still=work/f"{i:02}-still.png";draw(beat,1,still)
   listing.append(f"file '{still}'\nduration {(frames-n)/30:.8f}\nfile '{still}'\n")
   concat=work/f"{i:02}.txt";concat.write_text("".join(listing))
   clip=work/f"{i:02}.mp4"
   run(["ffmpeg","-v","error","-y","-f","concat","-safe","0","-i",str(concat),"-vf","fps=30,format=yuv420p","-frames:v",str(frames),"-c:v","libx264","-preset","veryfast","-crf","21",str(clip)])
   clips.append(clip)
  from scipy.io import wavfile
  wav=work/"narration.wav";wavfile.write(wav,24000,np.concatenate(audio))
  video_list=work/"all.txt";video_list.write_text("".join(f"file '{p}'\n" for p in clips))
  run(["ffmpeg","-v","error","-y","-f","concat","-safe","0","-i",str(video_list),"-i",str(wav),"-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac","-b:a","160k","-ar","48000","-af","loudnorm=I=-17:TP=-2:LRA=9","-movflags","+faststart","-shortest",str(OUT)])
  (OUT.with_suffix(".json")).write_text(json.dumps(cues,indent=2))
 probe=subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",str(OUT)],text=True)
 seconds=float(probe.strip())
 if not 300 <= seconds <= 600:
  OUT.unlink(missing_ok=True)
  raise SystemExit(f"Rejecting video: duration {seconds:.1f}s, required 300-600s")
 print(f"Rendered and duration-verified: {OUT} ({seconds:.1f}s)")
if __name__=="__main__":main()
