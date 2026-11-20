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
 qa_path.write_text(json.dumps(qa,indent=2)+'\n');print(row['id'],'static flags',len(qa['static_scene_review_flags']),'rapid flags',len(qa['rushed_reveal_flags']))
if __name__=='__main__':
 s=json.loads((HERE/'checkpoint.json').read_text())
 for row in s['lessons']:
  assert row['status']=='TECHNICALLY_VERIFIED_PENDING_APPROVAL';audit(row)
