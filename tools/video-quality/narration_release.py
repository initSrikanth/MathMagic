"""Validate the owner's explicitly authorised existing-20 voice replacement scope."""
import json,hashlib,subprocess
from contract import ROOT,load,branded
from brand_only_candidates import packets
from integrate_scoped_corrections import parse_vtt

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify(rows):
 profile=load()['approved_voice']
 for r in rows:
  c=r['narration_replacement'];s=c['previous'];t=c['replacement'];e=json.loads((ROOT/c['evidence']).read_text())
  assert 11<=r['number']<=30 and c['owner_authorised'] is True
  assert c['perceptual_status']=='UNVERIFIED'
  assert sha(ROOT/s['mp4'])==s['sha256'] and sha(ROOT/t['mp4'])==t['sha256']
  assert e['voice']['voice']==profile['voice']=='hf_alpha' and e['voice']['speaker_id']==profile['speaker_id']==31
  for k in ['model_sha256','voices_sha256']:assert e['voice'][k]==profile[k]
  assert e['video_packets_identical'] and not e['audio_pitch_shift'] and not e['audio_time_stretch']
  assert packets(ROOT/t['mp4'],'v:0')==packets(ROOT/s['mp4'],'v:0')
  assert e['max_caption_end_error']<=.101 and e['clipping_fraction']<.001 and e['final_rms']>.005
  for k in ['captions','transcript']:assert (ROOT/t[k]).read_bytes()==(ROOT/s[k]).read_bytes() and not branded((ROOT/t[k]).read_text())
  caps=parse_vtt(ROOT/t['captions']);assert len(caps)==len(e['events'])
  for a,b in zip(caps,e['events']):assert ' '.join(a['lines'])==b['text'] and abs(a['start']-b['caption_start'])<.001
  assert len(caps)>10 and max(x['end'] for x in caps)<=t['duration']+.05
  v=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(ROOT/t['mp4'])]));video=next(x for x in v['streams'] if x['codec_type']=='video');audio=next(x for x in v['streams'] if x['codec_type']=='audio')
  assert (video['codec_name'],video['width'],video['height'],video['pix_fmt'],audio['codec_name'])==('h264',1920,1080,'yuv420p','aac')
 return True
