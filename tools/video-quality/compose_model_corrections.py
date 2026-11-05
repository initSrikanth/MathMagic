"""Replace only two missing-model scene GOPs at1080p; copy all original AAC and other video packets."""
import json,copy,sys,subprocess,hashlib,math
from pathlib import Path
from PIL import Image
from contract import ROOT,REGISTER,assert_preservation_edit_allowed
from brand_only_candidates import cmd,packets
from model_correction_previews import render_frame,draw
OUT=Path('/workspace/video-correction-cache/visual-finals')
def compose(n,scene):
 r=json.loads(REGISTER.read_text())['records'][n-1];source=ROOT/r['mp4'];lesson=json.loads((ROOT/r['script']).read_text());assert_preservation_edit_allowed(r,lesson)
 timing=json.loads((ROOT/r['timing']).read_text());cue=timing['cues'][scene];a,b=round(cue['start']*30),round(cue['end']*30);start,end=a/30,b/30
 evidence=json.loads((Path('/workspace/video-correction-cache/model-previews')/f'{n:02}-model-original-audio.json').read_text());markers=evidence['word_offsets'];OUT.mkdir(exist_ok=True)
 final=OUT/f'{n:02}-model-corrected.mp4';meta=final.with_suffix('.json')
 if final.exists() and meta.exists():assert hashlib.sha256(final.read_bytes()).hexdigest()==json.loads(meta.read_text())['sha256'];print('Existing final preserved',n);return
 key=json.loads(cmd(['ffprobe','-v','error','-select_streams','v:0','-skip_frame','nokey','-show_frames','-show_entries','frame=best_effort_timestamp_time','-of','json',source]))['frames'];keys={round(float(x['best_effort_timestamp_time'])*30) for x in key};assert a in keys and b in keys,'Use exact existing scene GOP boundaries'
 base=copy.deepcopy(cue);base.update(board=[' '],equation=[],rows=[],line=None,note='');png=OUT/f'{n}-base.png';draw(lesson,base,png,1);imbase=Image.open(png).convert('RGB');new=OUT/f'{n}-scene.mp4'
 ff=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','30','-i','-','-frames:v',str(b-a),'-an','-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-video_track_timescale','15360',str(new)],stdin=subprocess.PIPE)
 for i in range(b-a):
  t=(a+i)/30-cue['start'];im=render_frame(n,markers,t,imbase,timing,cue['start'],burn_captions=False)
  if i in (0,(b-a)//2,b-a-1):im.save(OUT/f'{n:02}-frame-{i:03}.png')
  ff.stdin.write(im.tobytes())
 ff.stdin.close();assert ff.wait()==0
 prefix=OUT/f'{n}-prefix.mp4';suffix=OUT/f'{n}-suffix.mp4';listing=OUT/f'{n}-concat.txt'
 cmd(['ffmpeg','-v','error','-y','-i',source,'-frames:v',a,'-an','-c:v','copy',prefix])
 cmd(['ffmpeg','-v','error','-y','-ss',f'{end+.000001:.9f}','-i',source,'-an','-c:v','copy',suffix])
 orig=packets(source,'v:0');assert packets(prefix,'v:0')==orig[:a],'Copied prefix mismatch';assert packets(suffix,'v:0')==orig[b:],'Copied suffix mismatch'
 listing.write_text(''.join(f"file '{p.resolve()}'\n" for p in [prefix,new,suffix]))
 cmd(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',listing,'-i',source,'-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart',final])
 decode=subprocess.run(['ffmpeg','-v','error','-i',final,'-f','null','-'],capture_output=True,text=True,check=True);assert not decode.stderr.strip(),decode.stderr
 frames=json.loads(cmd(['ffprobe','-v','error','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp_time','-of','json',final]))['frames'];pts=[float(f['best_effort_timestamp_time']) for f in frames];assert len(frames)==len(orig) and all(y>x for x,y in zip(pts,pts[1:]))
 assert packets(final,'a:0')==packets(source,'a:0'),'Original narration packets changed';vp=packets(final,'v:0');assert vp[:a]==orig[:a] and vp[b:]==orig[b:]
 result=dict(number=n,source=r['mp4'],source_sha256=r['expected_sha256'],output=str(final),sha256=hashlib.sha256(final.read_bytes()).hexdigest(),bytes=final.stat().st_size,scene=scene,corrected_frame_interval=[a,b],corrected_seconds=[start,end],original_audio_packets_exact=True,video_outside_scene_packets_exact=True,voice_regenerated=False,pitch_speed_changed=False,frame_count=len(frames),strict_frame_timestamps=True,decode_error_output='',word_offsets=markers,timing_method=evidence['timing_method'],mathematics=evidence['mathematical_models'],resolution=[1920,1080],caption_transcript_unchanged=True,accent_status='UNVERIFIED',full_quality_status='UNVERIFIED',scope='mathematical_visual_only')
 meta.write_text(json.dumps(result,indent=2)+'\n')
 for p in [png,new,prefix,suffix,listing]:p.unlink()
 print('FULL CORRECTION',n,'only',b-a,'scene frames encoded; all narration and other frames exact.',flush=True)
if __name__=='__main__':
 for n,scene in [(14,5),(15,6)]:compose(n,scene)
