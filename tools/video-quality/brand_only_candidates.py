#!/usr/bin/env python3
"""Cut only branded final sentences of existing approved-profile videos; packet-copy review candidates, never publish."""
import json,re,sys,subprocess,hashlib,copy
from pathlib import Path
import numpy as np
from contract import ROOT,REGISTER,assert_generation_allowed,branded
OUT=ROOT/'video-agent/remediation-35/brandfree-review'
def cmd(args):return subprocess.check_output(list(map(str,args)))
def packets(path,stream):
 d=json.loads(cmd(['ffprobe','-v','error','-select_streams',stream,'-show_packets','-show_entries','packet=data_hash','-show_data_hash','sha256','-of','json',path]));return [p['data_hash'] for p in d['packets']]
def stamp(t):
 ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02}.{ms%1000:03}'
def run():
 db=json.loads(REGISTER.read_text());assert db.get('automated_evidence_complete') and len(db['records'])==35
 OUT.mkdir(parents=True,exist_ok=True);results=json.loads((OUT/'manifest.json').read_text())['results'] if (OUT/'manifest.json').exists() else [];done={r['number'] for r in results}
 for r in db['records']:
  if r['voice'].get('name')!='hf_alpha' or r['number'] in done:continue
  source=ROOT/r['mp4'];t=json.loads((ROOT/r['timing']).read_text());caps=t['captions'];bad=[c for c in caps if branded(c['text'])];assert len(bad)==1
  if bad[0]!=caps[-1]:
   (OUT/(str(r['number'])+'-blocked.json')).write_text(json.dumps({'number':r['number'],'status':'BLOCKED','reason':'Branded sentence is followed by an optional LCM notice. A prefix cut would remove unrelated curriculum guidance; preserve it and require a reviewed internal edit.'},indent=2)+'\n');continue
  authored=json.loads((ROOT/r['script']).read_text());authored=next(v for v in authored if v.get('slug',v.get('id'))==r['script_key']) if isinstance(authored,list) else authored
  def remove_phrase(v):
   if isinstance(v,dict):return {k:remove_phrase(x) for k,x in v.items()}
   if isinstance(v,list):return [remove_phrase(x) for x in v]
   return v.replace(' '+bad[0]['text'],'').replace(bad[0]['text'],'') if isinstance(v,str) else v
  clean=remove_phrase(copy.deepcopy(authored));clean['topic']=r['topic'];assert not branded(clean['beats'][-1]['text']);assert clean['beats'][-1]['text'].strip().endswith(('.', '!', '?'))
  assert_generation_allowed('remediation_candidate',[clean],r['voice'])
  audio=np.frombuffer(cmd(['ffmpeg','-v','error','-i',source,'-vn','-ac','1','-ar','24000','-f','f32le','-']),np.float32);sr=24000;at=bad[0]['start'];start=max(0,int((at-.75)*sr));stop=int((at+.10)*sr);quiet=[]
  for i in range(start,stop,240):
   if np.sqrt(np.mean(audio[i:i+240]**2))<.003:quiet.append(i/sr)
  groups=[]
  for x in quiet:
   if groups and abs(x-groups[-1][-1]-.01)<.001:groups[-1].append(x)
   else:groups.append([x])
  safe=[g for g in groups if len(g)>=6];assert safe,(r['number'],'No safe natural phrase boundary; do not cut blindly')
  g=safe[-1];cut=(g[0]+g[-1])*.5;folder=OUT/r['topic'];folder.mkdir(exist_ok=True);out=folder/(r['lesson_section']+'-brandfree-review.mp4')
  if not out.exists():cmd(['ffmpeg','-v','error','-y','-i',source,'-t',f'{cut:.6f}','-map','0:v:0','-map','0:a:0','-c','copy','-movflags','+faststart',out])
  else:assert abs(float(json.loads(cmd(['ffprobe','-v','error','-show_format','-of','json',out]))['format']['duration'])-cut)<.15
  subprocess.run(['ffmpeg','-v','error','-i',out,'-f','null','-'],check=True)
  proof={}
  for stream in ['v:0','a:0']:
   original=packets(source,stream);kept=packets(out,stream);assert kept==original[:len(kept)],'Encoded packet identity changed';proof[stream]={'packets_kept':len(kept),'original_packets':len(original),'exact_original_prefix':True}
  tail=np.frombuffer(cmd(['ffmpeg','-v','error','-i',out,'-vn','-ac','1','-ar','24000','-f','f32le','-']),np.float32)[-1200:];assert len(tail) and np.sqrt(np.mean(tail*tail))<.004,'Ending is not quiet'
  cc=[dict(c,end=min(c['end'],cut)) for c in caps[:-1] if c['start']<cut];assert all(c['end']>c['start'] for c in cc)
  stem=out.with_suffix('');vtt=stem.with_suffix('.vtt');vtt.write_text('WEBVTT\n\n'+'\n\n'.join(stamp(c['start'])+' --> '+stamp(c['end'])+'\n'+c['text'] for c in cc)+'\n');transcript=stem.with_name(stem.name+'-transcript.txt');transcript.write_text('\n\n'.join(b['text'] for b in clean['beats'])+'\n');script=stem.with_suffix('.json');script.write_text(json.dumps(clean,indent=2)+'\n');assert not branded(vtt.read_text()) and not branded(transcript.read_text())
  result={'number':r['number'],'lesson':r['lesson'],'source':r['mp4'],'source_sha256':r['expected_sha256'],'candidate':str(out.relative_to(ROOT)),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'bytes':out.stat().st_size,'cut_seconds':cut,'removed_caption':bad[0],'packet_copy_proof':proof,'narration_regenerated':False,'pitch_speed_changed':False,'enthusiasm_changed':False,'natural_silence_cut_interval':[g[0],g[-1]+.01],'caption_brand_free':True,'transcript_brand_free':True,'deployed':False,'final_status':'UNVERIFIED','release_status':'BLOCKED_FULL_PERCEPTUAL_AND_ENHANCED_ENTHUSIASM_REVIEW'};results.append(result);(OUT/'manifest.json').write_text(json.dumps({'purpose':'Review only, no live replacement','results':results},indent=2)+'\n');print('CANDIDATE',r['number'],r['lesson'],'no re-encoding',flush=True)
 (OUT/'manifest.json').write_text(json.dumps({'purpose':'Review only, no live replacement','results':results},indent=2)+'\n')
if __name__=='__main__':run()
