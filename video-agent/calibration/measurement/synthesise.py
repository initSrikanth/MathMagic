import pathlib as _vq_pathlib, sys as _vq_sys
_vq_root=next(p for p in _vq_pathlib.Path(__file__).resolve().parents if (p/'video-agent/video-production-contract.json').is_file())
_vq_sys.path.insert(0,str(_vq_root/'tools/video-quality'))
from guard import enforce as _vq_enforce
_vq_enforce()
from pathlib import Path
import json,time,hashlib
import sherpa_onnx,numpy as np,soundfile as sf
ROOT=Path(__file__).parent;model=ROOT/'kokoro-multi-lang-v1_0'
segments=[
 ('hook',"Could this ribbon really be nine centimetres long? Look closely! It starts at two, not zero.",1.00),
 ('goal',"Today, let's learn to measure the distance between the marks, rather than just reading the last number.",1.00),
 ('predict',"Before we calculate, what length do you predict? Follow the spaces with your finger, and keep your answer in mind.",.94),
 ('trace',"Now trace from two to nine. Each equal space is one centimetre. We count seven spaces altogether!",.96),
 ('calculate',"Nine minus two equals seven. So, the ribbon is seven centimetres long. Did your prediction match?",.98),
 ('recap',"Great thinking! Moving the ruler cannot stretch the ribbon. Check the start, count the intervals, then explain your answer.",1.00)]
p=model.as_posix()+'/'
tts=sherpa_onnx.OfflineTts(sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(kokoro=sherpa_onnx.OfflineTtsKokoroModelConfig(model=p+'model.onnx',voices=p+'voices.bin',tokens=p+'tokens.txt',data_dir=p+'espeak-ng-data',lang='en'),num_threads=2),max_num_sentences=8))
audios=[];cues=[];cursor=0;start=time.monotonic()
for name,text,speed in segments:
 out=ROOT/(name+'.wav')
 if out.exists():samples,sr=sf.read(out,dtype='float32')
 else:
  a=tts.generate(text,sid=31,speed=speed);samples=np.array(a.samples);sr=a.sample_rate;sf.write(out,samples,sr,subtype='PCM_16')
 cues.append(dict(name=name,text=text,start=cursor,end=cursor+len(samples)/sr,speed=speed));cursor+=len(samples)/sr;audios.append(samples);print(name,round(len(samples)/sr,2),flush=True)
a=np.concatenate(audios);sf.write(ROOT/'narration.wav',a,sr,subtype='PCM_16')
report=dict(model='Kokoro v1.0 multilingual ONNX',voice='hf_alpha',speaker_id=31,voice_language='Hindi female embedding, English phonemization: experimental cross-language candidate',licence='Apache-2.0 bundled model licence',sample_rate=sr,duration=cursor,elapsed_seconds=time.monotonic()-start,inserted_silence_samples=0,postprocessing_pitch_or_speed=False,cues=cues,model_sha256=hashlib.sha256((model/'model.onnx').read_bytes()).hexdigest(),rms=float(np.sqrt(np.mean(a*a))),clipping_fraction=float(np.mean(abs(a)>.999)))
(ROOT/'timing.json').write_text(json.dumps(report,indent=2));(ROOT/'transcript.txt').write_text('\n\n'.join(x['text'] for x in cues)+'\n');print('TOTAL',cursor,'RUNTIME',report['elapsed_seconds'],flush=True)
