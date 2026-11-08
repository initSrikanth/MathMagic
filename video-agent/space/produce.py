"""Representative Space video using the approved existing native renderer and voice.
Output stays outside the production tree until mandatory perceptual QA passes.
"""
from pathlib import Path
import importlib.util,sys,json,copy,hashlib,subprocess,time
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).parent
sys.path.insert(0,str(ROOT/'video-agent/production-v2'));sys.path.insert(0,str(ROOT/'tools/video-quality'))
import measurement_quality as q
from contract import assert_generation_allowed,load
sp=importlib.util.spec_from_file_location('space_lesson',HERE/'lesson1.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
sp=importlib.util.spec_from_file_location('space_drawing',HERE/'graphics.py');g=importlib.util.module_from_spec(sp);sp.loader.exec_module(g)
import numpy as np,soundfile as sf,sherpa_onnx
WORK=Path('/workspace/space-video-work/lesson1');MODEL=Path('/workspace/voice-calibration/kokoro-multi-lang-v1_0');ASR=q.ASR
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 WORK.mkdir(parents=True,exist_ok=True)
 if (WORK/'qa.json').exists() and (WORK/'final.partial.mp4').exists():
  old=json.loads((WORK/'qa.json').read_text())
  if old.get('sha256')==sha(WORK/'final.partial.mp4') and old.get('script_sha256')==sha(HERE/'lesson1.py') and old.get('graphics_source_sha256')==sha(HERE/'graphics.py') and old.get('repair_source_sha256')==sha(HERE/'repair_visuals.py'):
   print('Completed representative preserved; mandatory listening remains unresolved.');return
 if not (WORK/'timeline.json').exists() and (HERE/'lesson1_timing.json').exists() and (HERE/'lesson1_narration.flac').exists():
  pcm,sr=sf.read(HERE/'lesson1_narration.flac');sf.write(WORK/'narration.wav',pcm,sr,subtype='PCM_16');cached=json.loads((HERE/'lesson1_timing.json').read_text());cached['narration_sha256']=sha(WORK/'narration.wav');q.save(WORK/'timeline.json',cached)
 l=copy.deepcopy(m.LESSON);l['drawing_sha256']=sha(HERE/'graphics.py');profile=load()['approved_voice'];assert_generation_allowed('space_production',[l],profile)
 assert sha(MODEL/'model.onnx')==profile['model_sha256'] and sha(MODEL/'voices.bin')==profile['voices_sha256']
 assert 'Apache License' in (MODEL/'LICENSE').read_text()
 q.save(HERE/'manifest.json',dict(expected_lessons=10,representative='space-lesson1',status='GENERATING_REPRESENTATIVE',script_sha256=sha(HERE/'lesson1.py'),graphics_sha256=sha(HERE/'graphics.py'),voice=profile,paid_calls=0,perceptual_status='BLOCKED_NO_AUDIO_INPUT',outputs_stay_outside_production_tree=True))
 for kind in ['cube','prism','pyramid']:g.mesh(kind)
 q.MODEL=MODEL
 import repair_visuals as visual
 q.picture=lambda l,c,folder,p,elapsed,previous:visual.frame(l,c,folder,p,elapsed) if c['index'] in [23,26,27] else g.picture(l,c,folder,p,elapsed,previous)
 tts=sherpa_onnx.OfflineTts(sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(kokoro=sherpa_onnx.OfflineTtsKokoroModelConfig(model=str(MODEL/'model.onnx'),voices=str(MODEL/'voices.bin'),tokens=str(MODEL/'tokens.txt'),data_dir=str(MODEL/'espeak-ng-data'),lang='en'),num_threads=2)))
 rec=sherpa_onnx.OfflineRecognizer.from_transducer(tokens=str(ASR/'tokens.txt'),encoder=str(ASR/'encoder-epoch-99-avg-1.int8.onnx'),decoder=str(ASR/'decoder-epoch-99-avg-1.int8.onnx'),joiner=str(ASR/'joiner-epoch-99-avg-1.int8.onnx'),num_threads=2)
 t=q.synth(l,WORK,tts,rec)
 if not t.get('declared_prediction_pauses'):
  pcm,sr=sf.read(WORK/'narration.wav',dtype='float32');chunks=[];shift=0;pauses=[]
  for c in t['cues']:
   start,end=c['start'],c['end'];chunks.append(pcm[round(start*sr):round(end*sr)])
   for k in ['start','end','motion_start','motion_end','reveal_at']:c[k]+=shift
   c['speech_end']=c['end']
   for w in c['words']:w['start']+=shift
   for e in c['board_events']:e['at']+=shift
   for cap in t['captions']:
    if not cap.get('_shifted') and start<=cap['start']<end:cap['start']+=shift;cap['end']+=shift;cap['_shifted']=True
   if c['role']=='question':chunks.append(np.zeros(sr*5,dtype='float32'));c['end']+=5;pauses.append([c['speech_end'],c['end'],'authorised five-second prediction']);shift+=5
  for cap in t['captions']:cap.pop('_shifted',None)
  sf.write(WORK/'narration.wav',np.concatenate(chunks),sr,subtype='PCM_16');t.update(duration=t['duration']+shift,narration_sha256=sha(WORK/'narration.wav'),pauses=pauses,declared_prediction_pauses=True)
  q.save(WORK/'timeline.json',t)
 assert t['duration']>=300,'Substantive narration is shorter than five minutes; do not pad.'
 q.save(HERE/'manifest.json',dict(expected_lessons=10,representative='space-lesson1',status='RENDERING_REPRESENTATIVE',duration=t['duration'],timeline=str(WORK/'timeline.json'),voice=profile,paid_calls=0,perceptual_status='BLOCKED_NO_AUDIO_INPUT'))
 final=q.render(l,WORK,t)
 if (WORK/'visual-repair.json').exists():final=visual.repair(final,t,l)
 qa=q.p.verify(final,t,WORK/'narration.wav');qa.update(perceptual_status='BLOCKED_NO_AUDIO_INPUT',published=False,voice=profile,minimum_five_minutes=t['duration']>=300,declared_prediction_pauses=t['pauses'],graphics_source_sha256=sha(HERE/'graphics.py'),repair_source_sha256=sha(HERE/'repair_visuals.py'))
 q.save(WORK/'qa.json',qa);q.save(HERE/'manifest.json',dict(expected_lessons=10,completed_local_representatives=1,published=0,status='AWAITING_MANDATORY_PERCEPTUAL_REVIEW',qa=qa,output=str(final),timeline=str(WORK/'timeline.json'),voice=profile,paid_calls=0));sf.write(WORK/'narration.flac',*sf.read(WORK/'narration.wav'),subtype='PCM_16');print('REPRESENTATIVE_RENDERED',qa,flush=True)
if __name__=='__main__':main()
