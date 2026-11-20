"""One objective graphics correction pass; preserve native audio and good clips."""
from pathlib import Path
import json,copy,shutil,datetime
import produce as p
q=p.q

def repair(i):
 state=json.loads((p.HERE/'checkpoint.json').read_text());row=state['lessons'][i-1]
 if row.get('objective_graphics_correction'):
  assert p.sha(row['video'])==row['video_sha256'];print('PRESERVED_CORRECTED',i,flush=True);return
 folder=Path(row['video']).parent;old=copy.deepcopy(row);assert row['status']=='TECHNICALLY_VERIFIED_PENDING_APPROVAL';before=p.sha(folder/'narration.wav');native=p.sha(folder/'narration-native.wav')
 archive=folder/'before-objective-graphics-correction';archive.mkdir(exist_ok=True)
 for name in ['final.partial.mp4','qa.json','timeline.json','captions.vtt','transcript.txt','poster.jpg','render-key.json']:
  if not (archive/name).exists():shutil.copy2(folder/name,archive/name)
 t=json.loads((folder/'timeline.json').read_text());key=json.loads((folder/'render-key.json').read_text())['key']
 if i in [1,2]:t=p.measured_events({},t);affected=[n for n,c in enumerate(t['cues']) if c['role'] not in ['learning_goal','success_criteria','thinking_pause']]
 elif i==3:affected=[n for n,c in enumerate(t['cues']) if c['parent_index'] in [6,7]]
 else:
  t=p.measured_events({},t);affected=[n for n,c in enumerate(t['cues']) if c['parent_index']==9]
 for n in affected:
  clip=folder/f'quality-{n:02}-{key[:10]}.mp4'
  if clip.exists():clip.replace(archive/clip.name)
 # Existing renderer reuses all unaffected compressed clips. Invalidating only
 # its completion marker forces a single corrected assembly, never synthesis.
 (folder/'render-key.json').unlink();l=p.prepare(i);q.picture=p.g.picture;p.g.CACHE.clear();q.save(folder/'timeline.json',t);final=q.render(l,folder,t)
 assert p.sha(folder/'narration.wav')==before and p.sha(folder/'narration-native.wav')==native
 qa=p.qa_extra(l,t,folder,final,q.p.verify(final,t,folder/'narration.wav'));q.p.verify_sidecars(l,folder,t)
 qa['objective_graphics_correction']={'reason':'Sentence-local/cached board timing could expose a future summary briefly; parent-word events now persist.' if i in [1,2] else 'Removed overlapping duplicate comparison heading.' if i==3 else 'Delay the numerical summary in the additional investigation example until its actual spoken result.','previous_video_sha256':old['video_sha256'],'corrected_clips':len(affected),'unchanged_narration_sha256':before,'unchanged_native_narration_sha256':native,'speech_regenerated':False,'speech_pitch_or_time_changed':False,'previous_outputs_preserved_outside_website':True}
 q.save(folder/'qa.json',qa);row.update(video_sha256=p.sha(final),quality_evidence=str(folder/'qa.json'),objective_graphics_correction=qa['objective_graphics_correction']);p.persist(state);print('CORRECTED_REVIEW_CANDIDATE',i,row['video_sha256'],flush=True)
if __name__=='__main__':
 for i in [1,2,3,4,5]:repair(i)
