"""Focused media, exact arithmetic, sample-clock and model-identity checks."""
import json,subprocess,hashlib,wave
from pathlib import Path
from fractions import Fraction as F
import numpy as np
P=Path(__file__).parent
report={'scope':'Two review prototypes only; no website/production operations.','mathematics':{'same_denominator':F(3,4)>F(2,4),'same_numerator':F(1,3)>F(1,6),'equivalence':F(1,2)==F(2,4),'challenge':F(2,3)==F(4,6)<F(5,6)},'videos':{},'limitations':['No direct perceptual listening: human naturalness, warmth, pronunciation and intonation require reviewer judgement.','Cue timing follows measured narration segments, not word-level forced alignment.','American English and British English speakers, not specifically Australian voices.','Captions are narration-segment transcripts; not word-level captions.']}
assert all(report['mathematics'].values())
for v in 'AB':
 p=P/f'Comparing_Fractions_Prototype_Voice_{v}.mp4'
 meta=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]));video=next(s for s in meta['streams'] if s['codec_type']=='video');audio=next(s for s in meta['streams'] if s['codec_type']=='audio')
 assert (video['width'],video['height'],video['r_frame_rate'],video['codec_name'],audio['codec_name'])==(1920,1080,'30/1','h264','aac')
 subprocess.run(['ffmpeg','-v','error','-i',str(p),'-f','null','-'],check=True,capture_output=True)
 raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-map','0:a','-ac','1','-ar','24000','-f','f32le','-']);a=np.frombuffer(raw,dtype='<f4');assert np.isfinite(a).all() and np.max(np.abs(a))<.999
 timeline=json.loads((P/f'Voice_{v}.timeline.json').read_text());assert len(timeline)==13
 for i,s in enumerate(timeline):
  if i:assert abs(timeline[i-1]['end']-s['start'])<1/24000
  speech=a[round(s['start']*24000):round(s['speech_end']*24000)];assert np.sqrt(np.mean(speech**2))>.008
 challenge=timeline[10];assert challenge['thinking_pause']==5 and challenge['end']-challenge['speech_end']>=5
 assert timeline[11]['start']==challenge['end']
 assert abs(float(meta['format']['duration'])-timeline[-1]['end'])<.1
 block=2400; rms=np.sqrt(np.mean(a[:len(a)//block*block].reshape(-1,block)**2,axis=1)); silent=rms<.0015
 runs=[]; begin=None
 for k,quiet in enumerate(list(silent)+[False]):
  if quiet and begin is None:begin=k
  if not quiet and begin is not None:
   if (k-begin)*.1>=2:runs.append((begin*.1,k*.1))
   begin=None
 unexpected=[r for r in runs if not (r[0]>=challenge['speech_end']-1 and r[1]<=challenge['end']+.5)]
 assert not unexpected, ('Unplanned long silence',unexpected)
 report['videos'][v]={'file':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'duration':float(meta['format']['duration']),'full_decode':'passed','unexpected_silence_over_two_seconds':unexpected,'audible_every_narration_segment':True,'peak_dBFS':float(20*np.log10(np.max(np.abs(a)))),'challenge_pause_seconds':challenge['end']-challenge['speech_end'],'cue_alignment':'continuous sample clock, frame-rounded only at segment boundaries','format':'1080p30 H264 yuv420p / AAC, faststart'}
assert report['videos']['A']['sha256']!=report['videos']['B']['sha256']
from PIL import Image,ImageColor
script=json.loads((P/'script.json').read_text())
for i,c in enumerate(script):
 fa=Path(f'/workspace/work/premium-render/A/{i:02}.png');fb=Path(f'/workspace/work/premium-render/B/{i:02}.png')
 assert fa.read_bytes()==fb.read_bytes(), 'Visual mismatch between voices'
 im=Image.open(fa)
 for j,r in enumerate(c['rows']):
  for k in range(r['d']):
   x=round(260+(k+.5)*1260/r['d']);y=490+j*170+29
   expected='#008B8B' if r['colour']=='teal' else '#BF6500'
   if k>=r['n']:expected='#E5EFF8'
   assert im.getpixel((x,y))==ImageColor.getrgb(expected), (i,j,k)
report['visuals']={'identical_cue_images_for_both_voices':True,'shaded_cell_pixel_checks':'passed for every cell of every fraction bar','visual_inspection':'all 13 cues, plus encoded challenge before/after reveal and ending; proper stacked fractions and no branding'}
model=Path('/workspace/work/kokoro-multi-lang-v1_0')
# Each distinct speaker has a separate 510×1×256 float32 style table.
voices=np.memmap(model/'voices.bin',mode='r',dtype='float32').reshape(-1,510,1,256)
assert not np.array_equal(voices[3],voices[26]);report['speaker_identity']={'engine':'Kokoro v1.0 / sherpa-onnx 1.12.26','A':'af_heart, speaker 3, American English female','B':'bm_george, speaker 26, British English male','different_style_embeddings':True,'synthesis_speed':.94,'post_synthesis_pitch_or_speed_changes':False,'models':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [model/'model.onnx',model/'voices.bin']}}
(P/'qa-results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
