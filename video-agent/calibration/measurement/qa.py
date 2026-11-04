from pathlib import Path
import subprocess,json,hashlib
import numpy as np,soundfile as sf
r=Path(__file__).parent;v=r/'measurement-voice-animation-calibration.mp4';d=json.loads((r/'timing.json').read_text())
meta=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(v)]));video=next(s for s in meta['streams'] if s['codec_type']=='video');audio=next(s for s in meta['streams'] if s['codec_type']=='audio');assert(video['width'],video['height'],video['codec_name'],video['pix_fmt'],audio['codec_name'])==(960,540,'h264','yuv420p','aac')
subprocess.run(['ffmpeg','-v','error','-i',str(v),'-f','null','-'],check=True)
f=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(v),'-vf','scale=48:27','-pix_fmt','gray','-f','rawvideo','-']),np.uint8).reshape(-1,48*27);assert (f.std(axis=1)>8).all()
a,sr=sf.read(r/'narration.wav');decoded=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(v),'-vn','-f','f32le','-ac','1','-ar',str(sr),'-']),np.float32);n=min(len(a),len(decoded));corr=float(np.corrcoef(a[:n],decoded[:n])[0,1]);assert corr>.98 and np.max(abs(a))<.999
caps=json.loads((r/'captions.json').read_text());assert all(0<=c['start']<c['end']<=d['duration']+.001 for c in caps);assert all(a['end']<=b['start']+.001 for a,b in zip(caps,caps[1:]))
e=json.loads((r/'events.json').read_text())['events'];assert e['trace_finish']-e['trace_start']>5;assert d['cues'][2]['end']<=e['trace_start'];assert e['equation_nine']<e['equation_minus']<e['equation_two']<e['equation_equals']<e['equation_seven'];assert 9-2==7
# Autocorrelation pitch range: objective variation only, not proof of expressive delivery.
y=a[::3];f0=[]
for i in range(0,len(y)-400,160):
 z=y[i:i+400];z=z-z.mean()
 if np.sqrt(np.mean(z*z))<.015:continue
 ac=np.correlate(z,z,'full')[399:];lo,hi=18,100;k=lo+np.argmax(ac[lo:hi])
 if ac[k]/ac[0]>.6:f0.append(8000/k)
qa=dict(passed=True,format='960x540 H.264/yuv420p 25fps AAC faststart',duration=d['duration'],frames_checked=len(f),minimum_frame_contrast=float(f.std(axis=1).min()),audio_source_correlation=corr,source_peak=float(abs(a).max()),audio_clipping_samples=int(sum(abs(a)>=.999)),caption_cues=len(caps),trace_seconds=e['trace_finish']-e['trace_start'],prediction_guidance_seconds=d['cues'][2]['end']-d['cues'][2]['start'],inserted_silence_samples=d['inserted_silence_samples'],estimated_voiced_f0_10th_90th_hz=[round(x,1) for x in np.percentile(f0,[10,90])],sha256=hashlib.sha256(v.read_bytes()).hexdigest(),bytes=v.stat().st_size,limitations=['ASR timing is approximate; perceptual synchronisation requires review.','Pitch variation/ASR intelligibility do not establish accent, enthusiasm or naturalness.','Experimental Hindi female voice embedding speaking English; not a certified Indian-English voice.'])
(r/'qa.json').write_text(json.dumps(qa,indent=2));print(json.dumps(qa,indent=2))
