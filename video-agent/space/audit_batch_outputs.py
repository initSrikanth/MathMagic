"""Independent final-byte/sidecar audit and actual encoded scene sampling.
Does not render, synthesize, approve perception, upload, merge or deploy.
"""
from pathlib import Path
import json,subprocess,re,hashlib,sys
import numpy as np
import soundfile as sf
from PIL import Image
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).parent
sys.path.insert(0,str(ROOT/'tools/video-quality'))
from contract import branded
OUT=Path('/workspace/output/space-review')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def audit():
 state=json.loads((HERE/'batch-manifest.json').read_text());records=[]
 for lesson,e in state['lessons'].items():
  if e.get('status')!='TECHNICALLY_VERIFIED':continue
  path=Path(e['output']);prefix=path.with_suffix('');t=json.loads(Path(str(prefix)+'_timing.json').read_text());qa=e['qa']
  assert sha(path)==e['sha256']==qa['sha256']
  caps=t['captions'];assert all(0<=c['start']<c['end']<=t['duration']+.001 for c in caps)
  assert all(a['end']<=b['start']+.002 for a,b in zip(caps,caps[1:]))
  transcript=Path(str(prefix)+'_transcript.txt').read_text();assert ' '.join(transcript.split())==' '.join(' '.join(c['text']for c in caps).split())
  recognition=json.loads(Path(str(prefix)+'_recognition.json').read_text());assert len(recognition)==20
  assert not branded(transcript) and not any(branded(r['recognised'])for r in recognition)
  assert t['voice_id']==31 and len(t['pauses'])==3 and all(abs(end-start-5)<1e-8 for start,end,_ in t['pauses'])
  assert qa['full_decode'] and qa['blank_frame_candidates']==0 and qa['audio_rms']>.008 and qa['clipping_fraction']<.001
  assert qa['full_audio_listened'] is False and qa['full_video_viewed'] is False
  frames=sorted(set(round((c['start']+.1)*30)for c in t['cues'])|set(round((c['speech_end']-.1)*30)for c in t['cues']))
  sheet=OUT/(path.stem+'_encoded_scenes.jpg')
  if not sheet.exists():
   select='select='+ '+'.join(f'eq(n\\,{n})'for n in frames)+',scale=480:270'
   raw=subprocess.check_output(['ffmpeg','-v','error','-threads','1','-i',str(path),'-an','-vf',select,'-vsync','0','-pix_fmt','rgb24','-f','rawvideo','-'])
   a=np.frombuffer(raw,np.uint8).reshape(-1,270,480,3);assert len(a)==len(frames)
   im=Image.new('RGB',(1920,270*((len(a)+3)//4)),'white')
   for i,tile in enumerate(a):im.paste(Image.fromarray(tile),((i%4)*480,(i//4)*270))
   im.save(sheet,quality=90)
  short=[dict(start=c['start'],end=c['end'],text=c['text'])for c in caps if c['end']-c['start']<.9]
  rapid=[dict(scene=c['index'],at=event['at'],visible_seconds=c['end']-event['at'],text=event['text'],timing_reason=event['reason'])for c in t['cues']for event in c['board_events']if c['end']-event['at']<.9]
  pcm,sr=sf.read(Path(str(prefix)+'_narration.flac'),dtype='float32');samples_per_window=sr//10
  bins=pcm[:len(pcm)//samples_per_window*samples_per_window].reshape(-1,samples_per_window)
  quiet=np.sqrt(np.mean(bins*bins,axis=1))<.001
  gaps=[];start=None
  for i,is_quiet in enumerate(quiet):
   if is_quiet and start is None:start=i
   if (not is_quiet or i==len(quiet)-1)and start is not None:
    if i-start>=15:gaps.append(dict(start=start/10,end=i/10,overlaps_declared_prediction=any(a-.5<=(start+i)/20<=b+.5 for a,b,_ in t['pauses'])))
    start=None
  assert all(g['overlaps_declared_prediction']for g in gaps), 'Unexpected long source silence'

  rec=dict(lesson=lesson,sha256=e['sha256'],output=str(path),duration=t['duration'],technical_status='PASS',caption_intervals_valid=True,caption_transcript_match=True,offline_recognition_brand_scan='PASS',decoded_frame_count=qa['decoded_frames'],encoded_scene_samples=len(frames),encoded_scene_sheet=str(sheet),flags=dict(extended_static_intervals=qa['extended_static_intervals'],short_caption_intervals=short,rapid_board_reveal_flags=rapid,long_silent_intervals=gaps,word_timing='Approximate ASR emissions, not certified forced alignment'),perceptual_status='UNVERIFIED',publication_status='BLOCKED',sidecar_hashes={p.name:sha(p)for p in OUT.glob(path.stem+'_*')if p.suffix in ['.flac','.json','.txt','.vtt','.jpg']})
  records.append(rec)
 report=dict(rendered=len(records),all_nine_rendered=len(records)==9,technical_results=records,perceptual_reviews_completed=0,published=0,paid_calls=0,external_gates=['Full listening and temporal viewing by an audio-capable evaluator of the exact SHA-256 bytes, with reviewer identity/date. Check accent, pronunciation, expressiveness, pace, pedagogy, caption/audio/visual synchronisation and all timing flags.','Real Safari/iOS and real-device mobile legibility/control/caption QA before release.','Live Firebase verification requires authorised network scope and an approved test identity. Inspect deployed rules, Auth/approval isolation, own/cross-UID progress, save/restore across sessions/devices and revocation. Emulator fixture results do not certify deployed services.','Recover and verify the preserved original representative MP4 from its prior external storage; its source/manifest/hash remain unchanged.'])
 (OUT/'final-audit.json').write_text(json.dumps(report,indent=2)+'\n');print('AUDITED',len(records),'rendered outputs; listening remains UNVERIFIED')
 return report
if __name__=='__main__':audit()
