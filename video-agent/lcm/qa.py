"""Actual rendered-draft checks; explicitly does not certify absent speech."""
import importlib.util,json,hashlib,subprocess
from pathlib import Path
import numpy as np
from PIL import Image
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];DEST=ROOT/'reviews/lcm/MathMagic_LCM_SILENT_GRAPHICS_DRAFT_1080p.mp4'
spec=importlib.util.spec_from_file_location('lcm',HERE/'render.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def main():
 m.validate_math();info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(DEST)]));v=next(x for x in info['streams']if x['codec_type']=='video')
 assert(v['width'],v['height'],v['codec_name'],v['pix_fmt'],v['avg_frame_rate'])==(1920,1080,'h264','yuv420p','30/1')
 assert not any(x['codec_type']=='audio'for x in info['streams'])
 data=DEST.read_bytes();assert len(data)<100*1024*1024 and data[4:8]==b'ftyp'
 i=0;boxes=[]
 while i+8<=len(data):
  n=int.from_bytes(data[i:i+4],'big');kind=data[i+4:i+8]
  if n==1:n=int.from_bytes(data[i+8:i+16],'big')
  if n==0:n=len(data)-i
  assert n>=8 and i+n<=len(data);boxes.append(kind);i+=n
 assert boxes.index(b'moov')<boxes.index(b'mdat')
 subprocess.run(['ffmpeg','-v','error','-i',str(DEST),'-f','null','-'],check=True)
 scenes,d=m.draft_timeline();assert float(info['format']['duration'])==d==80
 cmd=['ffmpeg','-v','error','-threads','1','-filter_threads','1','-i',str(DEST),'-vf','select=not(mod(n\\,30))','-an','-vsync','0','-pix_fmt','rgb24','-threads','1','-f','rawvideo','pipe:1']
 proc=subprocess.Popen(cmd,stdout=subprocess.PIPE);errors=[];size=1920*1080*3
 for t in range(80):
  chunk=bytearray()
  while len(chunk)<size:
   b=proc.stdout.read(size-len(chunk))
   if not b:break
   chunk.extend(b)
  assert len(chunk)==size
  a=np.frombuffer(chunk,dtype=np.uint8).reshape(1080,1920,3);b=np.array(m.frame(t,scenes));errors.append(float(np.abs(a.astype(np.int16)-b.astype(np.int16)).mean()))
 assert proc.wait()==0 and max(errors)<3
 report={'status':'SILENT_GRAPHICS_DRAFT_QA_PASS_NOT_A_NARRATED_FINAL','filename':DEST.name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'duration':80,'size':[1920,1080],'fps':30,'full_decode':'PASS','faststart':'PASS','exact_mathematics':'PASS','rendered_frame_samples':80,'max_frame_pixel_mae':max(errors),'fraction_renderer':'Stacked numerator, horizontal bar, denominator; runtime slash-text rejection','voice_verification':'BLOCKED: no ElevenLabs connection/secret/provider voice configuration','audio_quality':'NOT RUN: no narration exists','narration_synchronisation':'NOT RUN: draft uses illustrative timings; final mode requires actual timestamps','user_approval':'PENDING','publication_allowed':False,'heygen_calls':0,'credits_spent':0}
 (ROOT/'reviews/lcm/technical-qa.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
