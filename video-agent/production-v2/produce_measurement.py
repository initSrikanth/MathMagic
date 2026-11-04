#!/usr/bin/env python3
"""One manual five-lesson batch using the existing offline producer; legacy scheduling is untouched."""
import json,time,re,subprocess,sys,fcntl,hashlib
from pathlib import Path
import numpy as np,soundfile as sf
import pipeline as p
from measurement_content import LESSONS
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];WORK=Path('/workspace/measurement-render');STATE=HERE/'measurement-manifest.json'
sys.path.insert(0,str(ROOT/'tests'));from importlib.util import spec_from_file_location,module_from_spec
sp=spec_from_file_location('measurement_math',ROOT/'tests/validate-measurement.py');checks=module_from_spec(sp);sp.loader.exec_module(checks)
def persist(m):p.save(STATE,m)
def run():
 WORK.mkdir(exist_ok=True);lock=(WORK/'production.lock').open('w');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 maths=checks.content();m=json.loads(STATE.read_text()) if STATE.exists() else dict(topic='measurement',base_commit=p.git('rev-parse','HEAD'),maths=maths,lessons={},paid_calls=0,automation='manual only; legacy workflows unchanged')
 deadline=time.monotonic()+220*60
 for l in LESSONS:
  l['graphics_source_sha256']=p.sha(HERE/'measurement_graphics.py');key=l['id'];folder=WORK/key;folder.mkdir(exist_ok=True)
  e=m['lessons'].setdefault(key,{});script_hash=p.json_hash(l);p.save(HERE/'scripts'/(key+'.json'),l)
  if e.get('status')=='verified':
   assert e['script_sha256']==script_hash and p.sha(ROOT/('videos/'+l['file']+'.mp4'))==e['qa']['sha256'];continue
  e.update(status='synthesising',script_sha256=script_hash,voice=dict(model='Kokoro v0.19',voice='bf_emma',speaker=7,speed=p.SPEED,model_sha256=p.MODEL_SHA,paid_calls=0));persist(m)
  t=p.synthesise(l,folder,Path('/workspace/mathmagic-offline-models/kokoro-en-v0_19'),deadline);p.save(HERE/'timings'/(key+'.json'),t)
  e['status']='rendering';persist(m);final=p.render(l,folder,t,deadline);qa=p.verify(final,t,folder/'narration.wav');p.verify_sidecars(l,folder,t)
  raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(final),'-an','-vf','scale=32:18','-pix_fmt','gray','-f','rawvideo','-']);frames=np.frombuffer(raw,dtype=np.uint8).reshape(-1,576);std=frames.std(axis=1);assert float(std.min())>3,'Blank/flat frame detected'
  clips=(folder/'clips.txt').read_text().splitlines();assert len(clips)==len(set(clips))==12
  for a,b in zip(t['cues'],t['cues'][1:]):assert abs(a['end']-b['start'])<1/24000
  qa.update(blank_frames=0,frames_checked=len(frames),minimum_frame_contrast=float(std.min()),unique_scenes=12)
  p.promote_media(l,folder,qa);samples,rate=sf.read(folder/'narration.wav',dtype='int16');audio=HERE/'audio'/(key+'.flac');sf.write(audio,samples,rate,format='FLAC',subtype='PCM_16');same,same_rate=sf.read(audio,dtype='int16');assert rate==same_rate and np.array_equal(samples,same)
  e.update(status='verified',qa=qa,narration_sha256=t['narration_sha256'],source_audio=str(audio.relative_to(ROOT)),source_audio_sha256=p.sha(audio));persist(m);print(key+': verified',flush=True)
 assert len(m['lessons'])==5 and all(e['status']=='verified' for e in m['lessons'].values())
 release=dict(topic='measurement',source_commit=m['base_commit'],lessons=[]);page=ROOT/'measurement.html';html=page.read_text()
 for l in LESSONS:
  e=m['lessons'][l['id']];stem='videos/'+l['file'];t=json.loads((HERE/'timings'/(l['id']+'.json')).read_text());info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-of','json',ROOT/(stem+'.mp4')]))
  release['lessons'].append(dict(id=l['id'],section=l['section'],title=l['title'],src=stem+'.mp4',captions=stem+'.vtt',transcript=stem+'_transcript.txt',poster=stem+'_poster.jpg',bytes=e['qa']['bytes'],sha256=e['qa']['sha256'],duration=float(info['format']['duration']),narration_duration=t['duration'],caption_cues=len(t['captions']),caption_language='en-GB',status='verified',presenter=False,source_audio=e['source_audio'],source_audio_sha256=e['source_audio_sha256']))
  pattern=r'<aside class="video-resource" data-measurement-pending="'+l['section']+r'">.*?</aside>'
  html,n=re.subn(pattern,lambda _:p.wrapper(l).replace('<video controls','<video tabindex="0" controls'),html,flags=re.S)
  assert n==1 or html.count('data-mathmagic-v2="'+l['id']+'"')==1
 assert 'data-measurement-pending' not in html;page.write_text(html);p.save(HERE/'measurement-release.json',release);p.save(HERE/'measurement-previous-integrations.json',dict(base_commit=m['base_commit'],cards={},assets={},reason='New Year 5 topic; no prior players replaced.'));m['integrated']=True;persist(m);print('PASS: five verified media bundles integrated; no previous media changed.',flush=True)
if __name__=='__main__':run()
