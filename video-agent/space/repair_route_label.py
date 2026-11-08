"""Repair the coincident start/return display label in lesson5, after the batch.
Re-encode one scene; preserve every AAC and all other H.264 packets and old files.
"""
from pathlib import Path
import json,copy,math,subprocess,shutil
import produce_batch as b
import batch_graphics as g
ROOT=b.ROOT;HERE=b.HERE;OUT=b.OUT;WORK=b.WORK
EXPECTED='e8b14d7557d8e9bea7c2f8aa96b8183d2bb463a96b058a555de04b75e5543f04'
sha=b.sha

def packet_hashes(path,stream):
 info=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams',stream,'-show_packets','-show_entries','packet=data_hash','-show_data_hash','sha256','-of','json',str(path)]))
 return [x['data_hash']for x in info['packets']]

def main():
 state=json.loads(b.STATE.read_text());assert state['rendered_this_batch']==9,'Finish all nine renders first'
 entry=state['lessons']['space-lesson5'];target=Path(entry['output']);folder=WORK/'lesson5';repair=WORK/'lesson5-label-repair';repair.mkdir(exist_ok=True)
 receipt=repair/'receipt.json'
 if receipt.exists():
  proof=json.loads(receipt.read_text());assert sha(target)==proof['new_sha256']==entry['sha256'];print('Existing verified label repair preserved');return
 assert sha(target)==entry['sha256']==EXPECTED
 stem=target.stem;history=HERE/'review-media/history/lesson5-before-label-repair';history.mkdir(parents=True,exist_ok=True)
 for src in OUT.glob(stem+'*'):
  if src.is_file():shutil.copyfile(src,history/src.name)
 original=history/target.name
 t=json.loads((folder/'timeline.json').read_text());l=json.loads((OUT/(stem+'_script.json')).read_text());old_t=copy.deepcopy(t);old_l=copy.deepcopy(l)
 cue=t['cues'][18];assert cue['model']['labels']==['Start','Turn','Return'] and cue['model']['points']==[[2,2],[5,2],[2,2]]
 cue['model']['labels']=['Home','Turn',''];l['beats'][18]['model']['labels']=['Home','Turn','']
 assert [c['text']for c in l['beats']]==[c['text']for c in old_l['beats']]
 frames=round(cue['end']*30)-round(cue['start']*30);clip=repair/'cue18-corrected.mp4'
 if not clip.exists():
  cmd=['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','25','-i','pipe:0','-an','-vf','fps=30,format=yuv420p','-frames:v',str(frames),'-c:v','libx264','-preset','veryfast','-crf','23','-threads','2',str(clip.with_suffix('.partial.mp4'))]
  proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
  try:
   for j in range(math.ceil(frames/30*25)):
    elapsed=min(cue['end']-cue['start']-.001,j/25)
    proc.stdin.write(g.picture(l,cue,folder,0,elapsed,[]).tobytes())
  finally:proc.stdin.close()
  assert proc.wait()==0;clip.with_suffix('.partial.mp4').replace(clip)
 clips=[Path(line.split("'",2)[1])for line in (folder/'clips.txt').read_text().splitlines()];assert len(clips)==20;clips[18]=clip
 listing=repair/'clips.txt';listing.write_text(''.join(f"file '{p}'\n"for p in clips))
 video=repair/'video.mp4';candidate=repair/'candidate.mp4'
 b.q.p.command(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',listing,'-an','-c:v','copy',video])
 b.q.p.command(['ffmpeg','-v','error','-y','-i',video,'-i',original,'-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart',candidate])
 old_a,new_a=packet_hashes(original,'a:0'),packet_hashes(candidate,'a:0');assert old_a==new_a
 old_v,new_v=packet_hashes(original,'v:0'),packet_hashes(candidate,'v:0');start=round(cue['start']*30);end=round(cue['end']*30)
 assert len(old_v)==len(new_v) and old_v[:start]==new_v[:start] and old_v[end:]==new_v[end:]
 qa=b.technical(candidate,folder,t,l)
 proof=dict(old_sha256=EXPECTED,new_sha256=qa['sha256'],cue_index=18,old_labels=['Start','Turn','Return'],new_labels=['Home','Turn',''],newly_encoded_frames=frames,total_video_frames=len(new_v),aac_packet_count=len(old_a),all_audio_packets_preserved=True,all_other_video_packets_preserved=True,caption_transcript_unchanged=True,original_preserved=str(original.relative_to(ROOT)),repair_source_sha256=sha(Path(__file__)),perceptual_status='UNVERIFIED')
 qa['label_repair']=proof
 # Publish only to the review output/manifest, never a student player or main.
 shutil.copyfile(candidate,target);assert sha(target)==qa['sha256']
 b.q.save(folder/'timeline.json',t);b.q.save(OUT/(stem+'_timing.json'),t);b.q.save(OUT/(stem+'_script.json'),l);b.q.save(OUT/(stem+'_qa.json'),qa)
 entry.update(sha256=qa['sha256'],bytes=qa['bytes'],qa=qa,script_sha256=b.q.p.json_hash(l),label_repair=proof);b.q.save(b.STATE,state);b.q.save(receipt,proof);b.q.save(OUT/'lesson5-label-repair.json',proof)
 (OUT/'SHA256SUMS').write_text(''.join(f"{e['sha256']}  {Path(e['output']).name}\n"for e in state['lessons'].values()))
 # The old encoded sheets remain in history. Force samples from the new bytes.
 for suffix in ['_encoded_scenes.jpg','_encoded_scenes_examples.jpg']:
  p=OUT/(stem+suffix)
  if p.exists():p.unlink()
 print('REPAIRED one scene:',frames,'frames; all original audio and other video packets preserved',flush=True)
if __name__=='__main__':main()
