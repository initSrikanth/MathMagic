"""Two isolated review prototypes; never calls production integration or APIs."""
import sys,json,subprocess,hashlib,math
from pathlib import Path
import numpy as np
import soundfile as sf
import sherpa_onnx
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'video-agent/production-v2'))
import graphics as g
g.BG='#F1F8FF';g.TEAL='#008B8B';g.GOLD='#BF6500';g.EMPTY='#E5EFF8';g.INK='#17324D';g.MUTED='#465C73'
OUT=Path(__file__).parent; WORK=Path('/workspace/work/premium-render');WORK.mkdir(exist_ok=True)
MODEL=Path('/workspace/work/kokoro-multi-lang-v1_0')
def row(n,d,label,colour='teal'):return dict(n=n,d=d,label=label,colour=colour)
def cue(chapter,text,eq,rows,note,pause=0):return dict(chapter=chapter,text=text,equation=eq,rows=rows,note=note,pause=pause)
C=[
cue('Which would you choose?', 'Imagine two equal-sized chocolate bars. You can have three quarters of one bar, or one half of the other. Which gives you more chocolate? Keep your prediction in mind. We will use pictures to explain how to compare fractions, even when their numbers look quite different.',[[3,4],'?', [1,2]],[row(3,4,'Three quarters'),row(1,2,'One half','gold')],'Always compare equal-sized wholes.'),
cue('Equal parts matter','First, check the wholes. Both bars must represent the same amount of chocolate. Otherwise, a small fraction of a giant bar could be larger than a big fraction of a tiny bar. Our models use equal-sized wholes, so the comparison is fair.',[[3,4],'?', [1,2]],[row(3,4,'Same whole length'),row(1,2,'Same whole length','gold')],'Same whole • Equal parts within each whole'),
cue('Same denominator: compare the shaded parts','Look at three quarters and two quarters. The denominator is four in both fractions. It tells us that each whole is divided into four equal parts. Because the parts have the same size, we can compare how many are shaded.',[[3,4],'?', [2,4]],[row(3,4,'Three equal parts shaded'),row(2,4,'Two equal parts shaded','gold')],'Denominator: how many equal parts make one whole.'),
cue('Three quarters is greater','Three quarter-sized pieces cover more of the bar than two quarter-sized pieces. So, three quarters is greater than two quarters. This comparison sign opens towards the larger fraction. With equal denominators, the larger numerator tells us which fraction is greater.',[[3,4],'>',[2,4]],[row(3,4,'Greater shaded amount'),row(2,4,'Smaller shaded amount','gold')],'Equal denominators → compare numerators.'),
cue('Same numerator: think about piece size','Now compare one third with one sixth. Each fraction has a numerator of one, so we are choosing just one piece from each bar. But these pieces are different sizes. Look carefully at how the same whole has been divided.',[[1,3],'?', [1,6]],[row(1,3,'One of three equal parts'),row(1,6,'One of six equal parts','gold')],'Both numerators are one.'),
cue('More parts means smaller pieces','Dividing the bar into six equal parts makes smaller pieces than dividing it into three equal parts. One third is therefore greater than one sixth. When positive fractions have the same numerator, the smaller denominator gives the greater fraction. The picture helps explain why.',[[1,3],'>',[1,6]],[row(1,3,'Fewer, larger parts'),row(1,6,'More, smaller parts','gold')],'Same numerator → compare the sizes of the parts.'),
cue('Different denominators: make equal-sized parts','Return to our chocolate choice: three quarters or one half. We cannot simply compare three with one, because quarters and halves are different-sized parts. Instead, let us describe both amounts using the same-sized pieces. Watch the half-bar model.',[[3,4],'?', [1,2]],[row(3,4,'Three quarters'),row(1,2,'One half','gold')],'Different denominators → find equal-sized parts.'),
cue('One half is two quarters','Divide each half into two equal pieces. The whole now has four equal parts. The shaded half covers two of those quarters. Nothing has been added or taken away. One half and two quarters are equivalent fractions: different names for exactly the same amount.',[[1,2],'=',[2,4]],[row(3,4,'Three quarters stays visible'),row(2,4,'The same half, divided into quarters','gold')],'Same shaded length • Smaller equal parts'),
cue('A common denominator makes comparison clear','We can also write this by multiplying the numerator and denominator of one half by two. That gives two quarters. Four is now a common denominator, so both fractions describe quarter-sized pieces. We changed the way we named the amount, not its value.',[[1,2],'=',[2,4]],[row(3,4,'Three quarters'),row(2,4,'One × two; two × two','gold')],'Multiply numerator and denominator by the same number.'),
cue('Our chocolate question: solved','Now the comparison is clear. Three quarters is greater than two quarters, and two quarters equals one half. So three quarters is greater than one half. If the original bars are the same size, choosing three quarters gives you more chocolate. Does that match your prediction?',[[3,4],'>',[2,4],'=',[1,2]],[row(3,4,'Three quarters: the larger amount'),row(2,4,'Two quarters: the same as one half','gold')],'Equivalent fractions let us compare like-sized parts.'),
cue('Your turn: which fraction is greater?','Try one yourself. Which is greater: two thirds or five sixths? Think about how you could divide the thirds into smaller equal parts. Use the two models to help you. Take a few seconds to decide before the answer appears.',[[2,3],'?', [5,6]],[row(2,3,'Two thirds'),row(5,6,'Five sixths','gold')],'Think: how many sixths have the same value as two thirds?',5),
cue('Two thirds is four sixths','Each third can be split into two sixths. Two shaded thirds become four shaded sixths. So two thirds equals four sixths. Compare four sixths with five sixths: five sixths has one more sixth shaded, so it is greater.',[[2,3],'=',[4,6],'<',[5,6]],[row(4,6,'Four sixths: the same as two thirds'),row(5,6,'Five sixths: one extra sixth','gold')],'Two thirds is less than five sixths.'),
cue('Three strategies to remember','Here are your three comparison strategies. With equal denominators, compare the numerators. With equal numerators, think about the size of the pieces. With different denominators, use equivalent fractions to make equal-sized parts. Always check that your wholes are equal. A clear picture can help you explain your answer.',[[3,4],'>',[2,4]],[row(3,4,'Equal wholes make fair comparisons'),row(2,4,'Explain your reasoning','gold')],'Equal denominators • Equal numerators • Equivalent fractions')
]
assert all(0<=r['n']<=r['d'] for c in C for r in c['rows'])
from fractions import Fraction as F
assert F(3,4)>F(2,4)==F(1,2) and F(1,3)>F(1,6) and F(2,3)==F(4,6)<F(5,6)
(OUT/'script.json').write_text(json.dumps(C,indent=2))
def run(args):subprocess.run(list(map(str,args)),check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
def stamp(t):
 m=round(t*1000);return f'{m//3600000:02}:{m//60000%60:02}:{m//1000%60:02}.{m%1000:03}'
def main():
 tts=sherpa_onnx.OfflineTts(sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(kokoro=sherpa_onnx.OfflineTtsKokoroModelConfig(model=str(MODEL/'model.onnx'),voices=str(MODEL/'voices.bin'),tokens=str(MODEL/'tokens.txt'),data_dir=str(MODEL/'espeak-ng-data'),lexicon=str(MODEL/'lexicon-us-en.txt')+','+str(MODEL/'lexicon-zh.txt')),num_threads=3),max_num_sentences=4))
 sr=tts.sample_rate
 for voice,sid in [('A',3),('B',26)]:
  folder=WORK/voice;folder.mkdir(exist_ok=True);audio=[];timeline=[];clips=[];total=0;previous=None;vtt=['WEBVTT\n']
  for i,c in enumerate(C):
   wav=folder/f'{i:02}.wav'
   if not wav.exists():
    a=tts.generate(c['text'],sid=sid,speed=.94);sf.write(wav,a.samples,sr,subtype='PCM_16')
   a,rate=sf.read(wav,dtype='float32');assert rate==sr and np.sqrt(np.mean(a*a))>.005
   # Only the explicitly requested challenge adds a long pause. No speech is stretched.
   extra=c['pause'] if c['pause'] else .20
   frames=math.ceil((len(a)/sr+extra)*30); count=round(frames/30*sr)
   audio.append(np.pad(a,(0,count-len(a))));start=total/sr;end=(total+len(a))/sr;total+=count
   timeline.append(dict(scene=i,chapter=c['chapter'],start=start,speech_end=end,end=total/sr,thinking_pause=c['pause'],text=c['text']))
   # Captions break at complete sentences, times allocated within a measured speech segment.
   # Segment timings are real; no word alignment is claimed.
   vtt.append(f'{stamp(start)} --> {stamp(end)}\n{c["text"]}\n')
   final=folder/f'{i:02}.png';g.draw({'title':'Comparing Fractions'},c,final,1);im=Image.open(final).convert('RGB')
   entries=[]
   for k in range(10):
    p=folder/f'{i:02}-transition-{k:02}.png'
    # Blend only graphics; audio remains continuous, untouched.
    blend=Image.blend(previous,im,(k+1)/10) if previous else im
    blend.save(p);entries.append(f"file '{p}'\nduration {1/30:.9f}\n")
   entries.append(f"file '{final}'\nduration {(frames-10)/30:.9f}\nfile '{final}'\n")
   listing=folder/f'{i:02}.txt';listing.write_text(''.join(entries));clip=folder/f'{i:02}.mp4'
   if not clip.exists():run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',listing,'-vf','fps=30,format=yuv420p','-frames:v',frames,'-c:v','libx264','-preset','veryfast','-crf','21','-threads','3',clip])
   clips.append(clip);previous=im
   print(f'Voice {voice}: scene {i+1}/{len(C)}, speech {len(a)/sr:.2f}s',flush=True)
  narration=folder/'narration.wav';sf.write(narration,np.concatenate(audio),sr,subtype='PCM_16')
  listing=folder/'clips.txt';listing.write_text(''.join(f"file '{p}'\n" for p in clips))
  output=OUT/f'Comparing_Fractions_Prototype_Voice_{voice}.mp4'
  run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',listing,'-i',narration,'-map','0:v','-map','1:a','-c:v','copy','-af','loudnorm=I=-18:TP=-2:LRA=9','-c:a','aac','-b:a','160k','-ar','48000','-movflags','+faststart','-shortest',output])
  (OUT/f'Voice_{voice}.timeline.json').write_text(json.dumps(timeline,indent=2));(OUT/f'Voice_{voice}.vtt').write_text('\n'.join(vtt))
  print(f'FINISHED {output.name} {total/sr:.2f}s',flush=True)
if __name__=='__main__':main()
