"""One decoded-picture review audit; report flags rather than inventing approvals."""
from pathlib import Path
import json,subprocess,hashlib
import numpy as np
HERE=Path(__file__).parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def audit(row):
 video=Path(row['video']);qa_path=Path(row['quality_evidence']);qa=json.loads(qa_path.read_text());assert qa['sha256']==sha(video)
 raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(video),'-an','-vf','fps=5,scale=96:54','-pix_fmt','gray','-f','rawvideo','-']);frames=np.frombuffer(raw,dtype=np.uint8).reshape(-1,96*54);delta=np.mean(abs(frames[1:].astype(np.int16)-frames[:-1].astype(np.int16)),axis=1);events=[0]+[(int(i)+1)/5 for i in np.flatnonzero(delta>.4)]+[len(frames)/5]
 qa['decoded_picture_audit']={'method':'5fps decoded 96x54 luma, mean absolute adjacent difference >0.4 is a change','timing_resolution_seconds':.2,'sampled_frames':len(frames),'limitations':'Compression noise/very small changes can affect detection; sampled pictures do not replace full viewing.'}
 qa['static_scene_review_flags']=[{'start':a,'end':b,'seconds':b-a,'status':'PENDING_HUMAN_REVIEW','reason':'Decoded picture remains substantially unchanged >8s; review persistence and teaching purpose.'} for a,b in zip(events,events[1:]) if b-a>8]
 qa['rushed_reveal_flags']=[{'start':a,'end':b,'seconds':b-a,'status':'PENDING_HUMAN_REVIEW','reason':'Decoded visual state lasts <0.9s; review whether this is meaningful focus or an unwanted flash.'} for a,b in zip(events,events[1:]) if .19<b-a<.9]
 audio=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(video),'-vn','-ac','1','-ar','24000','-f','f32le','-']),dtype='<f4')
 windows=audio[:len(audio)//2400*2400].reshape(-1,2400);quiet=np.sqrt(np.mean(windows**2,axis=1))<.001;runs=[];start=None
 for i,v in enumerate(list(quiet)+[False]):
  if v and start is None:start=i
  if not v and start is not None:
   if i-start>=15:
    a,b=start/10,i/10;planned=any(x-.3<=(a+b)/2<=y+.3 for x,y,_ in qa['planned_prediction_pauses']);runs.append({'start':a,'end':b,'planned_prediction_opportunity':planned,'status':'PLANNED' if planned else 'PENDING_HUMAN_REVIEW'})
   start=None
 qa['silence_over_1_5_seconds']=runs
 qa['unplanned_silence_flags']=[r for r in runs if not r['planned_prediction_opportunity']]
 qa_path.write_text(json.dumps(qa,indent=2)+'\n');print(row['id'],'static flags',len(qa['static_scene_review_flags']),'rapid flags',len(qa['rushed_reveal_flags']))
if __name__=='__main__':
 s=json.loads((HERE/'checkpoint.json').read_text())
 for row in s['lessons']:
  assert row['status']=='TECHNICALLY_VERIFIED_PENDING_APPROVAL';audit(row)
