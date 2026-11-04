"""Review-candidate automated evidence; never claim perceptual quality or publish."""
from pathlib import Path
import json,re,hashlib,subprocess,sys
import numpy as np
from contract import ROOT,branded,rendered_texts
from brand_only_candidates import cmd,OUT

def seconds(s):
 h,m,s=map(float,s.split(':'));return h*3600+m*60+s

def run():
 m=json.loads((OUT/'manifest.json').read_text());assert len(m['results'])==30;rec=None
 for r in m['results']:
  p=ROOT/r['candidate'];sha=hashlib.sha256(p.read_bytes()).hexdigest();assert sha==r['sha256']
  if r.get('candidate_automated_evidence',{}).get('sha256')==sha:continue
  f=json.loads(cmd(['ffprobe','-v','error','-show_format','-show_streams','-of','json',p]));v=next(x for x in f['streams'] if x['codec_type']=='video');a=next(x for x in f['streams'] if x['codec_type']=='audio');duration=float(f['format']['duration'])
  assert (v['codec_name'],v['width'],v['height'],v['pix_fmt'],a['codec_name'])==('h264',1920,1080,'yuv420p','aac')
  # Reuse successful full decode and packet identity from composition, bound to exact candidate hash.
  assert r.get('packet_copy_proof') or (r['number']==4 and r.get('video_prefix_exact_original_packets')==6471)
  audio=np.frombuffer(cmd(['ffmpeg','-v','error','-i',p,'-vn','-ac','1','-ar','16000','-f','f32le','-']),np.float32);rms=float(np.sqrt(np.mean(audio*audio)));clip=float(np.mean(abs(audio)>=.999));assert rms>.008 and clip<.001
  vtt=p.with_suffix('.vtt').read_text();transcript=p.with_name(p.stem+'-transcript.txt').read_text();script=json.loads(p.with_suffix('.json').read_text());assert not branded(vtt) and not branded(transcript) and not any(branded(s) for s in rendered_texts(script))
  cues=[]
  for block in vtt.strip().split('\n\n')[1:]:
   lines=block.splitlines();x,y=lines[0].split(' --> ');cues.append((seconds(x),seconds(y),' '.join(lines[1:])))
  assert all(0<=x<y<=duration+.1 for x,y,s in cues);assert all(x[1]<=y[0]+.01 for x,y in zip(cues,cues[1:]))
  norm=lambda s:re.sub(r'\s+',' ',s).strip();assert norm(' '.join(c[2] for c in cues))==norm(transcript)
  chunks=[audio[i:i+320] for i in range(0,len(audio)-320,320)];quiet=[np.sqrt(np.mean(c*c))<.004 for c in chunks];runs=[];start=None
  for i,q in enumerate(quiet+[False]):
   if q and start is None:start=i
   if not q and start is not None:
    if (i-start)*.02>=1.5:runs.append([start*.02,i*.02])
    start=None
  # Do not repeat the 14 saved ASR checks; recognise only endings with no prior evidence.
  if 'ending_asr' not in r:
   if rec is None:
    import sherpa_onnx
    model=Path('/workspace/voice-calibration/sherpa-onnx-zipformer-small-en-2023-06-26');rec=sherpa_onnx.OfflineRecognizer.from_transducer(tokens=str(model/'tokens.txt'),encoder=str(model/'encoder-epoch-99-avg-1.int8.onnx'),decoder=str(model/'decoder-epoch-99-avg-1.int8.onnx'),joiner=str(model/'joiner-epoch-99-avg-1.int8.onnx'),num_threads=2)
   stream=rec.create_stream();stream.accept_waveform(16000,audio[-160000:]);rec.decode_stream(stream);r['ending_asr']=stream.result.text;r['ending_review_note']='Actual ending recognised locally, not listening or proof of accent/enthusiasm.'
  assert not branded(r['ending_asr']),r['ending_asr']
  r['candidate_automated_evidence']=dict(sha256=sha,duration=duration,encoding={'video':v['codec_name'],'width':v['width'],'height':v['height'],'pixel_format':v['pix_fmt'],'audio':a['codec_name']},audio_rms=rms,clipping_fraction=clip,silence_flags_seconds=runs,caption_timing_valid=True,caption_transcript_text_match=True,sidecars_brand_free=True,perceptual_review='UNVERIFIED',deployed=False)
  (OUT/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');print('CANDIDATE QA',r['number'],'PASS automated only',flush=True)
 print('Thirty brand-edited candidates verified automatically. Full perceptual/voice gates remain BLOCKED.')
if __name__=='__main__':run()
