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
OUT=ROOT/"videos"/"MathMagic_Time_Angles_04_Measuring_Angles.mp4"
MODEL=Path(os.environ.get("KOKORO_MODEL","/workspace/fractions-five-work/kokoro-multi-lang-v1_0"))
W,H=1920,1080
BG="#FFF9EE";INK="#17354D";TEAL="#008A94";ORANGE="#B85A10";MUTED="#6A8398"
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BEATS=[["hook","Two students draw different-looking angles and both say theirs is bigger. How could we settle their argument fairly?","angle",75],["introduction","Today we are learning to measure and draw angles with a protractor.","angle",75],["goal","Our learning goal is to measure and draw angles with a protractor.","angle",75],["criteria","Success criteria: align the vertex, find the zero baseline and read the correct degree scale.","angle",75],["explanation","An angle is the amount of turning between two rays meeting at a vertex. The length of the rays does not change the angle.","angle",45],["explanation","A full turn is three hundred and sixty degrees, a half turn is one hundred and eighty, and a quarter turn is ninety.","angle",90],["question","Look at this angle. Is it acute, right, obtuse or straight? Pause for five seconds and decide.","angle",60],["answer","Sixty degrees is smaller than ninety degrees, so this is an acute angle.","angle",60],["explanation","A right angle is ninety degrees. It looks like the corner of a square.","angle",90],["question","An angle is one hundred and twenty degrees. Is it acute or obtuse? Compare it with ninety degrees.","angle",120],["answer","One hundred and twenty is greater than ninety and less than one hundred and eighty, so the angle is obtuse.","angle",120],["misconception","An angle with longer arms is not necessarily larger. We measure the amount of turning, not the length of the lines.","angle",120],["explanation","When measuring with a protractor, place the centre at the vertex and align one arm with the zero-degree baseline.","angle",75],["question","If the angle looks narrower than a right angle, should you read seventy-five or one hundred and five degrees?","angle",75],["answer","Seventy-five degrees is the sensible measurement because it is less than ninety degrees.","angle",75],["explanation","Always check which protractor scale begins at zero along your starting arm. The two scales count in opposite directions.","angle",140],["question","Two adjacent angles lie on a straight line. One is forty degrees. What is the other angle?","angle",140],["answer","A straight angle is one hundred and eighty degrees. Subtract forty to get one hundred and forty degrees.","angle",140],["explanation","To draw an angle, draw the first ray, mark the required number of degrees from zero and connect the mark to the vertex.","angle",55],["question","A robot makes two quarter turns in the same direction. How many degrees has it turned altogether?","angle",180],["answer","Ninety plus ninety equals one hundred and eighty degrees, which is a half turn.","angle",180],["explanation","Angles are measured in degrees, not centimetres. A small drawing and a large drawing can show exactly the same turn.","angle",60],["explanation","Imagine a door opening. A small opening makes an acute angle, while a door opened square to the wall makes a right angle.","angle",90],["explanation","A turn of thirty degrees is one third of a right angle. Three such turns add up to ninety degrees.","angle",30],["explanation","A turn of one hundred and fifty degrees is close to a straight angle, but thirty degrees short of one hundred and eighty.","angle",150],["explanation","Use benchmarks to estimate. Compare the angle with ninety degrees before reading a protractor scale.","angle",110],["explanation","If your measurement says forty degrees but the drawing looks wider than a right angle, check whether you used the wrong scale.","angle",140],["explanation","When drawing an angle, keep the ruler steady and make sure both rays begin at the same vertex.","angle",75],["explanation","Explain your answer using the size of the turn. This is stronger than simply saying the angle looks big.","angle",120],["explanation","Before using a protractor, predict whether the angle is less than or greater than ninety degrees. Your prediction can catch a wrong-scale reading.","angle",90],["explanation","The centre mark must sit exactly on the vertex. If it is moved away, the protractor markings no longer measure the intended angle.","angle",90],["explanation","Some protractors number clockwise and anticlockwise at once. Find the zero aligned with the starting ray before following the numbers.","angle",90],["explanation","Suppose your first ray points left. Begin with the zero on the left, rather than automatically reading from the right-hand scale.","angle",90],["explanation","An angle of thirty degrees is much smaller than a right angle. Use this comparison when checking your drawing.","angle",90],["explanation","An angle of one hundred and sixty degrees is almost straight. It is twenty degrees away from a straight angle.","angle",90],["explanation","If you draw a sixty-degree angle and measure it again, your answer should be close to sixty degrees. Small pencil errors may matter.","angle",90],["explanation","For an independent check, draw an angle measuring one hundred and ten degrees. Predict its type before touching the protractor.","angle",90],["recap","Explain the steps to someone else: estimate the angle, align the baseline, read the correct scale and check the angle type.","angle",90],["recap","Your challenge is to find three angles in your classroom, classify them and explain your reasoning.","angle",120]]
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
 txt(d,"MEASURING ANGLES",960,210,45,MUTED)
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
  raise SystemExit(f"Rejecting video: duration {seconds:.1f}s, required 300-900s")
 print(f"Rendered and duration-verified: {OUT} ({seconds:.1f}s)")
if __name__=="__main__":main()
