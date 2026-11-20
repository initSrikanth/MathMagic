"""Freeze technically verified pending bundles in the existing topic checkpoint.
This never calls promote_media, registers an approved player, or changes a lesson.
The unchanged release gate continues to reject unapproved MP4 publication.
"""
from pathlib import Path
import json,shutil,hashlib
import soundfile as sf
HERE=Path(__file__).parent;ROOT=HERE.resolve().parents[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 state=json.loads((HERE/'checkpoint.json').read_text());assert state['rendered']==5 and state['integrated']==0
 for i,row in enumerate(state['lessons'],1):
  assert row['status']=='TECHNICALLY_VERIFIED_PENDING_APPROVAL' and row['approval_status']=='PENDING'
  if row.get('bundle_sha256'):
   assert all(sha(row[k])==h for k,h in row['bundle_sha256'].items());continue
  folder=Path(row['video']).parent;out=HERE/'review'/f'lesson{i}';out.mkdir(parents=True,exist_ok=True)
  sources={'video':folder/'final.partial.mp4','captions':folder/'captions.vtt','transcript':folder/'transcript.txt','poster':folder/'poster.jpg','quality_evidence':folder/'qa.json','timings':folder/'timeline.json','asr_evidence':folder/'recognition.json','ocr_evidence':folder/'frame-ocr.json'}
  names={'video':f'Statistics_Lesson{i:02}_REVIEW_1080p.mp4','captions':'captions.vtt','transcript':'transcript.txt','poster':'poster.jpg','quality_evidence':'qa.json','timings':'timeline.json','asr_evidence':'recognition.json','ocr_evidence':'frame-ocr.json'}
  hashes={}
  for key,source in sources.items():
   target=out/names[key];assert source.exists();shutil.copy2(source,target);row[key]=str(target.relative_to(ROOT) if target.is_absolute() else target);hashes[key]=sha(target)
  assert hashes['video']==row['video_sha256'];row['bundle_sha256']=hashes
  for n in ['narration','narration-native']:
   pcm,sr=sf.read(folder/(n+'.wav'),dtype='int16');target=out/(n+'.flac');sf.write(target,pcm,sr,subtype='PCM_16');back,rate=sf.read(target,dtype='int16');assert rate==sr and (back==pcm).all();row[n.replace('-','_')+'_source']=str(target);row[n.replace('-','_')+'_source_sha256']=sha(target)
  row['publication_status']='BLOCKED_PENDING_EXACT_BYTE_FULL_AUDIOVISUAL_APPROVAL';row['reviewer']=None;row['review_date']=None
 state.update(status='FIVE_REVIEW_BUNDLES_PACKAGED_NOT_PUBLISHED',media_registration_status='PENDING_APPROVAL_CHECKSUM_BOUND_IN_EXISTING_TOPIC_CHECKPOINT',blockers=['Full exact-byte human listening/viewing for accent, expressiveness, pedagogical quality and flagged intervals.','No lesson integration or production media registration until existing approval and release gates pass.'])
 (HERE/'checkpoint.json').write_text(json.dumps(state,indent=2)+'\n')
if __name__=='__main__':main()
