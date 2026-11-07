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
OUT=ROOT/"videos"/"MathMagic_Time_Angles_02_Timetables_and_Journeys.mp4"
MODEL=Path(os.environ.get("KOKORO_MODEL","/workspace/fractions-five-work/kokoro-multi-lang-v1_0"))
W,H=1920,1080
BG="#FFF9EE";INK="#17354D";TEAL="#008A94";ORANGE="#B85A10";MUTED="#6A8398"
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BEATS=[["hook","A family is planning a trip to the wildlife park. Three buses leave at different times. Which one arrives before the gates open?","journey",8,25,9,10],["introduction","Today we are learning to read timetables and calculate travel durations.","journey",8,25,9,10],["goal","Our learning goal is to read timetables and calculate travel durations.","journey",8,25,9,10],["criteria","Success criteria: read departure times, calculate elapsed time and choose a suitable journey.","journey",8,25,9,10],["explanation","Read the departure and arrival times from the same service on the timetable. Different rows can refer to different journeys.","timeline",8,25,9,10],["explanation","A timeline makes the journey visible. Begin at eight twenty-five, move to nine o'clock and then move to nine ten.","timeline",8,25,9,10],["question","How many minutes pass between eight twenty-five and nine ten? Estimate first, then calculate.","timeline",8,25,9,10],["answer","Thirty-five minutes to nine o'clock plus ten minutes to nine ten makes forty-five minutes.","timeline",8,25,9,10],["explanation","Twenty-four-hour time removes confusion between morning and afternoon. Thirteen fifteen means one fifteen in the afternoon.","conversion",13,15,14,5],["question","A train departs at thirteen fifteen and arrives at fourteen oh five. How long is the journey?","timeline",13,15,14,5],["answer","Forty-five minutes to fourteen hundred, then five more minutes. The journey lasts fifty minutes.","timeline",13,15,14,5],["misconception","Subtracting the minute numbers alone is a mistake when you cross an hour. Use the full timeline instead.","timeline",13,15,14,5],["explanation","For a deadline, consider arrival time, not just departure time. Arriving after an event begins may be too late.","journey",9,0,9,35],["question","You must arrive before ten. A service arrives at nine thirty-five. Does it meet the deadline?","timeline",9,35,10,0],["answer","Yes. Nine thirty-five is twenty-five minutes before ten, so the service meets the deadline.","timeline",9,35,10,0],["explanation","Remember to include walking and waiting time. Reaching the station exactly when the bus leaves is risky.","journey",9,20,10,5],["question","A bus departs at nine twenty and arrives at ten oh five. How many minutes does the trip take?","timeline",9,20,10,5],["answer","Forty minutes to ten o'clock, then five more minutes. The trip lasts forty-five minutes.","timeline",9,20,10,5],["explanation","Check that your answer is sensible. A journey crossing an hour can be longer than the difference between the minute digits.","timeline",9,20,10,5],["question","A train leaves at eleven thirty-five and arrives at twelve twenty. Calculate the duration using noon.","timeline",11,35,12,20],["answer","Twenty-five minutes to noon plus twenty minutes afterwards makes forty-five minutes.","timeline",11,35,12,20],["recap","Read the correct timetable entry, draw a timeline, cross the hour boundary and add the intervals.","timeline",11,35,12,20],
["explanation","Think about a school bus timetable. The departure time tells us when to be at the stop, while the arrival time tells us when we can reach our destination.","journey",8,25,9,10],
["explanation","If the bus is delayed, our original plan may no longer work. A good traveller checks whether there is enough time before an important appointment.","timeline",8,25,9,10],
["explanation","Try a different strategy. Instead of counting every minute, split the journey at the nearest whole hour and add the two intervals.","timeline",13,15,14,5],
["explanation","A journey from nine thirty-five to ten o'clock takes twenty-five minutes. We know this because sixty minus thirty-five equals twenty-five.","timeline",9,35,10,0],
["explanation","Check your answer by counting forward. Start at nine thirty-five, add twenty-five minutes, and you should reach ten o'clock.","timeline",9,35,10,0],
["explanation","If you have to change buses, calculate the waiting time between the first arrival and the second departure. That wait is part of the whole trip.","timeline",9,20,10,5],
["explanation","Estimate before you calculate. A journey from eleven thirty-five to twelve twenty must be shorter than an hour, because twelve thirty-five would be one hour later.","timeline",11,35,12,20],
["explanation","You can explain your thinking with words, numbers or a timeline. The strongest answer shows where each interval comes from.","timeline",11,35,12,20]]
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
 txt(d,"TIMETABLES AND JOURNEYS",960,210,45,MUTED)
 title={"hook":"The mystery of the bus journey","introduction":"Today we are learning…","goal":"Today's Learning Goal","criteria":"Success Criteria","explanation":"Let's investigate","question":"Your turn — predict","prediction":"Think before calculating","answer":"Reveal and explain","misconception":"Spot the mistake","conversion":"12-hour and 24-hour time","recap":"What have we learned?"}.get(role,"Explore the mathematics")
 txt(d,title,960,292,59,INK)
 if kind=="angle":
  deg=args[0];cx,cy=960,690;r=290
  d.ellipse((cx-r,cy-r,cx+r,cy+r),outline="#D7E6E8",width=4)
  d.line((cx,cy,cx+r,cy),fill=TEAL,width=15)
  a=-math.radians(deg*p)
  d.line((cx,cy,cx+r*math.cos(a),cy+r*math.sin(a)),fill=ORANGE,width=15)
  d.ellipse((cx-13,cy-13,cx+13,cy+13),fill=INK)
  txt(d,f"{deg} degrees",960,1020,62,INK)
 elif kind=="clock":
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
 if not 300 <= seconds <= 900:
  OUT.unlink(missing_ok=True)
  raise SystemExit(f"Rejecting video: duration {seconds:.1f}s, required 300-600s")
 print(f"Rendered and duration-verified: {OUT} ({seconds:.1f}s)")
if __name__=="__main__":main()
