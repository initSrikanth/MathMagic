"""Review-only sentence removal for inventory 4; retain the subsequent LCM notice."""
import copy,json,hashlib,subprocess,sys
from pathlib import Path
import numpy as np
from contract import ROOT,REGISTER,assert_preservation_edit_allowed,branded
from brand_only_candidates import packets,stamp,cmd,OUT

def run():
 db=json.loads(REGISTER.read_text());r=db['records'][3];manifest=OUT/'manifest.json';m=json.loads(manifest.read_text())
 if any(x['number']==4 for x in m['results']):print('Existing internal edit preserved');return
 source=ROOT/r['mp4'];timing=json.loads((ROOT/r['timing']).read_text());bad=[c for c in timing['captions'] if branded(c['text'])];assert len(bad)==1 and timing['captions'][-1]['text']=='The separate L C M video is optional extension work.'
 authored=json.loads((ROOT/r['script']).read_text());authored=next(l for l in authored if l.get('slug',l.get('id'))==r['script_key']) if isinstance(authored,list) else authored
 def clean(v):
  if isinstance(v,dict):return {k:clean(x) for k,x in v.items()}
  if isinstance(v,list):return [clean(x) for x in v]
  return v.replace(' '+bad[0]['text'],'').replace(bad[0]['text'],'') if isinstance(v,str) else v
 lesson=clean(copy.deepcopy(authored));assert_preservation_edit_allowed(r,lesson)
 # Frame-exact natural quiet boundaries, checked against decoded PCM below.
 a,b,end,key=218.9,222.0,226.4,215.7;sr=24000
 pcm=np.frombuffer(cmd(['ffmpeg','-v','error','-i',source,'-vn','-ac','1','-ar',sr,'-f','f32le','-']),np.float32)
 for cut in (a,b,end):assert np.sqrt(np.mean(pcm[round((cut-.025)*sr):round((cut+.025)*sr)]**2))<.004,'Not a natural quiet edit boundary'
 folder=OUT/'fractions';out=folder/'addsub-brandfree-review.mp4';tmp=folder/'internal-edit-cache';tmp.mkdir(exist_ok=True)
 prefix=tmp/'prefix.mp4';tail=tmp/'tail.mp4';joined=tmp/'joined.mp4'
 # B-frame DTS may precede a keyframe's PTS: -t alone includes packets from the next GOP.
 # Bound the exact packet count as well, so the copied prefix ends before that keyframe.
 cmd(['ffmpeg','-v','error','-y','-i',source,'-t',key,'-frames:v',round(key*30),'-an','-c:v','copy',prefix])
 vf=f'[0:v]split=2[x][y];[x]trim=0:{a-key},setpts=PTS-STARTPTS[p];[y]trim={b-key}:{end-key},setpts=PTS-STARTPTS[q];[p][q]concat=n=2:v=1:a=0[v]'
 cmd(['ffmpeg','-v','error','-y','-ss',key,'-i',source,'-filter_complex',vf,'-map','[v]','-an','-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-r','30','-video_track_timescale','15360',tail])
 listing=tmp/'concat.txt';listing.write_text(f"file '{prefix.resolve()}'\nfile '{tail.resolve()}'\n")
 cmd(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',listing,'-an','-c:v','copy',joined])
 af=f'[1:a]asplit=2[x][y];[x]atrim=0:{a},asetpts=PTS-STARTPTS[p];[y]atrim={b}:{end},asetpts=PTS-STARTPTS[q];[p][q]concat=n=2:v=0:a=1[a]'
 cmd(['ffmpeg','-v','error','-y','-i',joined,'-i',source,'-filter_complex',af,'-map','0:v:0','-map','[a]','-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart',out])
 decode=subprocess.run(['ffmpeg','-v','error','-i',out,'-f','null','-'],check=True,capture_output=True,text=True)
 assert not decode.stderr.strip(),decode.stderr
 frames=json.loads(cmd(['ffprobe','-v','error','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp_time','-of','json',out]))['frames']
 pts=[float(f['best_effort_timestamp_time']) for f in frames];assert all(y>x for x,y in zip(pts,pts[1:])), 'Non-monotonic frame PTS'
 assert len(frames)==round((end-(b-a))*30), 'Unexpected frame count at edit seam'
 orig=packets(source,'v:0');kept=packets(out,'v:0');n=round(key*30);assert kept[:n]==orig[:n],'Prefix video packets changed'
 cc=[]
 for c in timing['captions']:
  if c is bad[0]:continue
  shift=b-a if c['start']>=b else 0;cc.append(dict(c,start=c['start']-shift,end=min(c['end'],end)-shift))
 assert all(c['end']>c['start'] for c in cc)
 out.with_suffix('.vtt').write_text('WEBVTT\n\n'+'\n\n'.join(stamp(c['start'])+' --> '+stamp(c['end'])+'\n'+c['text'] for c in cc)+'\n')
 out.with_name(out.stem+'-transcript.txt').write_text('\n\n'.join(x['text'] for x in lesson['beats'])+'\n');out.with_suffix('.json').write_text(json.dumps(lesson,indent=2)+'\n')
 result=dict(number=4,lesson=r['lesson'],source=r['mp4'],source_sha256=r['expected_sha256'],candidate=str(out.relative_to(ROOT)),sha256=hashlib.sha256(out.read_bytes()).hexdigest(),bytes=out.stat().st_size,duration=end-(b-a),internal_removed_interval=[a,b],natural_quiet_boundaries_pcm_checked=True,optional_lcm_notice_preserved=True,video_prefix_exact_original_packets=n,video_tail_reencoded_seconds=end-key-(b-a),aac_reencoded=True,narration_regenerated=False,pitch_speed_changed=False,enthusiasm_changed=False,caption_brand_free=True,transcript_brand_free=True,deployed=False,final_status='UNVERIFIED',release_status='BLOCKED_FULL_PERCEPTUAL_AND_ENHANCED_ENTHUSIASM_REVIEW')
 m['results'].append(result);m['results'].sort(key=lambda x:x['number']);manifest.write_text(json.dumps(m,indent=2)+'\n')
 (OUT/'4-blocked.json').write_text(json.dumps({'number':4,'status':'INTERNAL_EDIT_PREPARED_REVIEW_BLOCKED','candidate':result['candidate'],'optional_lcm_notice_preserved':True,'perceptual_review':'UNVERIFIED'},indent=2)+'\n')
 # Delete only this tool's reproducible temporary copies; keep final and original media.
 for p in (prefix,tail,joined,listing):p.unlink()
 tmp.rmdir();print('Inventory 4 brand sentence removed; LCM notice preserved; 215.7 seconds video packets exact, only 7.6-second tail re-encoded. Review remains blocked.')
if __name__=='__main__':run()
