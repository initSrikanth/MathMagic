"""Repair three confirmed model mismatches only; preserve every AAC packet and other clips."""
from pathlib import Path
import json,subprocess,math,hashlib,importlib.util,sys
from PIL import ImageDraw
HERE=Path(__file__).parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'tools/video-quality'));from brand_only_candidates import packets
s=importlib.util.spec_from_file_location('space_repair_base',HERE/'graphics.py');g=importlib.util.module_from_spec(s);s.loader.exec_module(g)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def polygon(d,points,faces,edges):
 for f in faces:d.polygon([points[i]for i in f],fill='#dceee7',outline=g.INK,width=3)
 for a,b in edges:d.line((*points[a],*points[b]),fill=g.INK,width=4)
def cylinder(d,x,y,p):
 d.rectangle((x-110,y-110,x+110,y+110),fill='#dceee7');d.ellipse((x-110,y+75,x+110,y+145),fill='#dceee7');d.arc((x-110,y+75,x+110,y+145),0,180,fill=g.INK,width=4);d.line((x-110,y-110,x-110,y+110),fill=g.INK,width=4);d.line((x+110,y-110,x+110,y+110),fill=g.INK,width=4);d.ellipse((x-110,y-145,x+110,y-75),fill='#ffe1b9',outline=g.INK,width=4)
 d.arc((x-110,y-145,x+110,y-75),-90,-90+360*p,fill=g.GOLD,width=7)
def frame(l,c,folder,p,elapsed):
 im=g.picture(l,c,folder,p,elapsed,[]);d=ImageDraw.Draw(im);d.rectangle((330,430,1590,1040),fill=g.BG);now=c['start']+elapsed
 if c['index']==23:
  points,faces,edges=g.mesh('prism');points=[(600+(x-960)*.75,690+(y-650)*.75)for x,y in points];polygon(d,points,faces[-3:],edges)
  points=[(1080,800),(1400,800),(1290,690),(1230,505)];faces=[[0,1,2],[0,1,3],[1,2,3],[2,0,3]];edges=[(0,1),(1,2),(2,0),(0,3),(1,3),(2,3)];polygon(d,points,faces,edges)
  g.text(d,'Triangular prism',600,465,40,g.TEAL,True);g.text(d,'Triangular pyramid',1240,465,40,g.TEAL,True)
  g.text(d,'Two matching ends',600,890,35,g.INK,True);g.text(d,'Four triangular faces',1240,890,35,g.INK,True)
 elif c['index']==26:
  cylinder(d,620,710,p);d.ellipse((1120,580,1380,840),fill='#bcded4',outline=g.INK,width=5);d.ellipse((1150,610,1190,650),fill='#e8f5ee');g.text(d,'Cylinder',620,465,42,g.TEAL,True);g.text(d,'Sphere',1250,465,42,g.TEAL,True)
  g.text(d,'Flat circular faces + curved surface',620,930,31,g.INK,True);g.text(d,'One curved surface',1250,930,31,g.INK,True)
 else:
  cylinder(d,960,700,p);g.text(d,'A curved boundary is not a row of vertices.',960,930,38,g.INK,True)
 return im

def repair(source,t,l):
 folder=Path(source).parent;meta=folder/'visual-repair.json';fingerprint=sha(Path(__file__))
 if meta.exists():
  e=json.loads(meta.read_text())
  if e['source_fingerprint']==fingerprint and sha(source)==e['sha256']:return source
 listing=(folder/'clips.txt').read_text().splitlines();assert len(listing)==32
 replacements={};indices=[23,26,27]
 for idx in indices:
  c=t['cues'][idx];frames=round(c['end']*30)-round(c['start']*30);n=math.ceil(frames/30*25);clip=folder/f'correct-model-{idx}-{fingerprint[:10]}.mp4'
  if not clip.exists():
   proc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','25','-i','pipe:0','-an','-vf','fps=30,format=yuv420p','-frames:v',str(frames),'-c:v','libx264','-preset','veryfast','-crf','23','-threads','2',str(clip)],stdin=subprocess.PIPE)
   for j in range(n):
    elapsed=min(c['end']-c['start']-.001,j/25);p=max(0,min(1,(c['start']+elapsed-c['motion_start'])/max(.1,c['speech_end']-c['motion_start'])));im=frame(l,c,folder,p,elapsed);proc.stdin.write(im.tobytes())
    if j==n//2:im.save(folder/f'correct-model-{idx}.png')
   proc.stdin.close();assert proc.wait()==0
  replacements[idx]=clip;listing[idx]=f"file '{clip}'";print('Repaired model scene',idx,flush=True)
 sequence=folder/'corrected-clips.txt';sequence.write_text('\n'.join(listing)+'\n');out=folder/'corrected.partial.mp4'
 subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(sequence),'-i',str(source),'-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart',str(out)],check=True)
 assert packets(out,'a:0')==packets(source,'a:0');original=packets(source,'v:0');new=packets(out,'v:0');assert len(original)==len(new)
 changed=set()
 for idx in indices:
  c=t['cues'][idx];changed.update(range(round(c['start']*30),round(c['end']*30)))
 assert all(a==b for i,(a,b)in enumerate(zip(original,new))if i not in changed)
 subprocess.run(['ffmpeg','-v','error','-i',str(out),'-f','null','-'],check=True)
 evidence=dict(source_fingerprint=fingerprint,sha256=sha(out),repaired_scenes=indices,encoded_scene_frames=len(changed),all_narration_packets_preserved=True,all_other_video_packets_preserved=True,caption_and_transcript_unchanged=True,perceptual_status='UNVERIFIED')
 out.replace(source);meta.write_text(json.dumps(evidence,indent=2)+'\n');return source
if __name__=='__main__':
 import importlib.util
 sp=importlib.util.spec_from_file_location('space_repair_lesson',HERE/'lesson1.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 folder=Path('/workspace/space-video-work/lesson1');repair(folder/'final.partial.mp4',json.loads((folder/'timeline.json').read_text()),m.LESSON)
