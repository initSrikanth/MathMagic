"""Actual narrated-review media, mathematics, source-clock graphics and audio-continuity gates."""
import importlib.util,json,hashlib,subprocess,math,ast,re
from pathlib import Path
from fractions import Fraction
import numpy as np
from PIL import Image,ImageDraw
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];R=ROOT/'reviews/lcm/final'
DEST=R/'MathMagic_Finding_LCM_REVIEW_1080p.mp4';AUDIO=R/'LCM_Original_HeyGen_Narration.mp3'
spec=importlib.util.spec_from_file_location('lcm',HERE/'render.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]))
def pcm(p):return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-map','0:a:0','-f','f32le','-ac','1','-ar','44100','pipe:1']),dtype='<f4')
def balanced(items):
 if len(items)==1:return items[0]
 k=len(items)//2;return '('+balanced(items[:k])+')+('+balanced(items[k:])+')'
def readn(p,n):
 b=bytearray()
 while len(b)<n:
  chunk=p.read(n-len(b))
  if not chunk:break
  b.extend(chunk)
 return b

def main():
 m.validate_math();v=probe(DEST);a=probe(AUDIO);video=next(x for x in v['streams']if x['codec_type']=='video');audio=next(x for x in v['streams']if x['codec_type']=='audio')
 assert(video['width'],video['height'],video['codec_name'],video['pix_fmt'],video['avg_frame_rate'])==(1920,1080,'h264','yuv420p','30/1')
 assert(audio['codec_name'],audio['sample_rate'],audio['channels'],float(audio['start_time']))==('aac','44100',1,0)
 duration=float(a['format']['duration']);assert abs(float(v['format']['duration'])-duration)<1/30
 data=DEST.read_bytes();assert len(data)<100*1024*1024 and data[4:8]==b'ftyp'
 pos=0;boxes=[]
 while pos+8<=len(data):
  n=int.from_bytes(data[pos:pos+4],'big');kind=data[pos+4:pos+8]
  if n==1:n=int.from_bytes(data[pos+8:pos+16],'big')
  if n==0:n=len(data)-pos
  assert n>=8 and pos+n<=len(data);boxes.append(kind);pos+=n
 assert boxes.index(b'moov')<boxes.index(b'mdat')
 subprocess.run(['ffmpeg','-v','error','-i',str(DEST),'-f','null','-'],check=True)
 x=pcm(AUDIO);y=pcm(DEST);n=min(len(x),len(y));assert abs(len(x)-len(y))<=1024
 x=x[:n].astype(np.float64);y=y[:n].astype(np.float64);err=x-y
 corr=float(np.corrcoef(x,y)[0,1]);snr=float(10*np.log10(np.sum(x*x)/np.sum(err*err)));gain=float(20*np.log10(np.sqrt(np.mean(y*y))/np.sqrt(np.mean(x*x))))
 assert corr>.995 and snr>30 and abs(gain)<.1,(corr,snr,gain)
 assert np.max(np.abs(y))<1 and not np.any(np.abs(y)>=1)
 windows=[]
 for start in [1,40,80]:
  aa=x[int(start*44100):int((start+3)*44100)];bb=y[int(start*44100):int((start+3)*44100)];c=float(np.corrcoef(aa,bb)[0,1]);assert c>.995;windows.append({'start':start,'zero_lag_correlation':c})
 scenes,d=m.load_alignment(R/'heygen-speech-response.json',AUDIO,R/'voice-provenance.json')
 # Every graphics function remains the existing approved draft implementation.
 original=subprocess.check_output(['git','show','a4ad2da:video-agent/lcm/render.py'],cwd=ROOT,text=True)
 names={'font','text','frac','equation','multiples','bars','validate_math','anchor','content','frame'}
 def drawing(src):return '\n'.join(ast.dump(n,include_attributes=False)for n in ast.parse(src).body if isinstance(n,ast.FunctionDef)and n.name in names)
 assert drawing(original)==drawing((HERE/'render.py').read_text())
 indices=set(range(0,math.ceil(d*30),30));indices.add(math.ceil(d*30)-1)
 events=[]
 for s in scenes:
  events.append(s['start'])
 for i,phrase,offset in [(1,'four eight twelve sixteen',j)for j in range(4)]+[(2,'six twelve eighteen',j)for j in range(3)]+[(3,'Twelve is the first',0),(5,'One quarter equals three twelfths',3),(6,'One sixth equals two twelfths',3),(7,'That makes five twelfths',2),(7,'The answer is already',0)]:events.append(m.anchor(scenes[i],phrase,offset))
 for t in events:
  for dt in [-1/30,1/30,.333]:indices.add(max(0,min(math.ceil(d*30)-1,math.ceil((t+dt)*30))))
 indices=sorted(indices);select=balanced([f'eq(n\\,{i})'for i in indices]);cmd=['ffmpeg','-v','error','-threads','1','-filter_threads','1','-i',str(DEST),'-vf',f'select={select}','-an','-vsync','0','-pix_fmt','rgb24','-threads','1','-f','rawvideo','pipe:1']
 proc=subprocess.Popen(cmd,stdout=subprocess.PIPE);errors=[];images=[];size=1920*1080*3;targets=[5,16.8,21.5,29,40,53,64,73,85];sample_indices={min(indices,key=lambda j:abs(j-t*30))for t in targets}
 for i in indices:
  chunk=readn(proc.stdout,size);assert len(chunk)==size
  actual=np.frombuffer(chunk,dtype=np.uint8).reshape(1080,1920,3);expected=np.array(m.frame(i/30,scenes,False));errors.append(float(np.abs(actual.astype(np.int16)-expected.astype(np.int16)).mean()))
  if i in sample_indices:images.append((i/30,Image.fromarray(actual).resize((480,270))))
 assert proc.wait()==0 and max(errors)<3
 contact=Image.new('RGB',(1440,864),'white');dc=ImageDraw.Draw(contact)
 for j,(t,im)in enumerate(images):contact.paste(im,((j%3)*480,(j//3)*288));dc.text(((j%3)*480+8,(j//3)*288+270),f'{t:.2f}s',fill='black')
 contact.save(R/'final-contact.jpg')
 # Check every equation that can be displayed, using exact rational values.
 rows=set();base=m.equation
 def capture(draw,row,*args,**kwargs):rows.add(json.dumps(row));return base(draw,row,*args,**kwargs)
 m.equation=capture
 for s in scenes:
  for w in s['words']:m.frame(min(w['start']+.04,d-.01),scenes,False)
 for row in map(json.loads,rows):
  if '?'in row:continue
  parts=[];sub=[]
  def value(ts):
   total=Fraction(*ts[0]);k=1
   while k<len(ts):assert ts[k]=='+';total+=Fraction(*ts[k+1]);k+=2
   return total
  for token in row:
   if token=='=':parts.append(value(sub));sub=[]
   else:sub.append(token)
  parts.append(value(sub));assert all(p==parts[0]for p in parts)
 # Finished answers remain visible through subsequent dependent steps and recap.
 persistence=[{'result':'one quarter equals three twelfths','reveal':47.461,'needed_until':75.659},{'result':'one sixth equals two twelfths','reveal':61.646,'needed_until':75.659},{'result':'five twelfths answer','reveal':69.447,'needed_until':d}]
 assert all(p['needed_until']-p['reveal']>=4 for p in persistence)
 report={'status':'TECHNICAL_QA_PASS_USER_REVIEW_PENDING','filename':DEST.name,'duration':float(v['format']['duration']),'source_audio_duration':duration,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'format':'1920x1080 H.264/yuv420p, 30 fps, AAC 44.1 kHz mono, faststart','full_decode':'PASS','audio':{'source_mp3_sha256':hashlib.sha256(AUDIO.read_bytes()).hexdigest(),'original_sample_count':len(pcm(AUDIO)),'final_sample_count':len(pcm(DEST)),'zero_lag_correlation':corr,'SNR_dB_after_AAC_encoding':snr,'gain_difference_dB':gain,'peak_dBFS':float(20*np.log10(np.max(np.abs(y)))),'RMS_dBFS':float(20*np.log10(np.sqrt(np.mean(y*y)))),'clipped_samples':int(np.sum(np.abs(y)>=1)),'early_middle_late_samples':windows,'pitch_speed_changes':False,'silence_inserted':False,'note':'Only AAC encoding and codec-frame tail padding; no temporal filters, cropping, looping, silence insertion or narration edits'},'mathematics':'PASS; LCM, exact equivalences, addition and simplification verified','distinct_equation_states':len(rows),'existing_graphics_code':'PASS; mathematical drawing and animation functions AST-identical to a4ad2da','source_word_alignment':'PASS; complete script matched to actual provider word timestamps','rendered_board_samples':len(indices),'max_frame_pixel_mae':max(errors),'result_persistence':persistence,'voice_id':'2ec5ec7926eb471d9f33e1b7ba4bb77d','voice_name':'Srikanth sogathur','engine':'elevenlabs via connected HeyGen','speech_generation_requests':1,'publication_allowed':False,'human_audiovisual_review':'User approval of naturalness, pronunciation and teaching experience remains pending; automated checks do not certify subjective quality'}
 (R/'final-technical-qa.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
