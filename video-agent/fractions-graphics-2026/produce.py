"""One resumable five-lesson job. Offline speech only; no batch workflows/APIs."""
import json,sys,hashlib,math,re,subprocess,os,time,textwrap
from pathlib import Path
import numpy as np
import soundfile as sf
import sherpa_onnx
from PIL import Image
from lessons import LESSONS
from graphics import draw
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
WORK=Path(os.environ.get('FRACTIONS_RENDER_WORK','/workspace/fractions-five-work/render'));WORK.mkdir(parents=True,exist_ok=True)
MODEL=Path(os.environ.get('FRACTIONS_TTS_MODEL','/workspace/fractions-five-work/kokoro-multi-lang-v1_0'))
VOICE=31 # Kokoro v1.0 hf_alpha, existing female Hindi speaker, English phonemes.
RATES={'hook':.94,'goal':.91,'criteria':.92,'prediction':.92,'question':.92,'answer':.94,'misconception':.88,'recap':.91,'explanation':.90}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,data):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
def run(args):
 r=subprocess.run(list(map(str,args)),capture_output=True,text=True)
 if r.returncode:raise RuntimeError(r.stderr[-6000:])
 return r

def stamp(t,comma=False):
 n=round(t*1000);return f'{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02}'+(',' if comma else '.')+f'{n%1000:03}'
def synthesis(tts,l,folder):
 sr=tts.sample_rate;pcm=[];total=0;events=[];captions=[]
 for i,c in enumerate(l['beats']):
  start=total/sr;speed=RATES.get(c['role'],.90)
  for sentence in re.split(r'(?<=[.!?])\s+(?=[A-Z])',c['text']):
   key=hashlib.sha256(json.dumps([sentence,VOICE,speed,sha(MODEL/'voices.bin')]).encode()).hexdigest();wav=folder/(key+'.wav')
   if not wav.exists():
    a=tts.generate(sentence,sid=VOICE,speed=speed);assert a.sample_rate==sr and len(a.samples)>sr*.15
    sf.write(wav,a.samples,sr,subtype='PCM_16')
   a,rate=sf.read(wav,dtype='float32');assert rate==sr and np.isfinite(a).all() and np.sqrt(np.mean(a*a))>.005
   assert np.mean(np.abs(a)>.999)<.0001,'Speech clipping'
   captions.append(dict(start=total/sr,end=(total+len(a))/sr,text=sentence,source_sha256=sha(wav)))
   pcm.append(a);total+=len(a)
   # Brief natural sentence handoff, never narration stretching or pitch effects.
   gap=np.zeros(round(.12*sr),dtype='float32');pcm.append(gap);total+=len(gap)
  speech_end=(total-round(.12*sr))/sr
  pause=5 if c['role']=='question' else c.get('pause',.35)
  # The sentence handoff already supplies .12s of this declared processing interval.
  n=max(0,round((pause-.12)*sr));pcm.append(np.zeros(n,dtype='float32'));total+=n
  end_frame=math.ceil(total/sr*30);extra=end_frame*sr//30-total
  pcm.append(np.zeros(extra,dtype='float32'));total+=extra
  events.append(dict(index=i,start=start,speech_end=speech_end,end=total/sr,role=c['role'],chapter=c['chapter'],pause=pause,speed=speed,graphic=c))
 narration=HERE/'audio'/(l['slug']+'.flac');narration.parent.mkdir(exist_ok=True);sf.write(narration,np.concatenate(pcm),sr,format='FLAC',subtype='PCM_16')
 timeline=dict(duration=total/sr,sample_rate=sr,events=events,captions=captions,narration_sha256=sha(narration),alignment='Measured generated-sentence PCM sample intervals; no estimated word times.',voice_id=VOICE,voice='Kokoro v1.0 hf_alpha',language='English phonemes with native female Hindi speaker embedding',rates=RATES)
 save(HERE/'timings'/(l['slug']+'.json'),timeline);return timeline,narration

def render(l,folder,timeline,narration):
 graphics_hash=sha(HERE/'graphics.py');clips=[];previous=None;previous_cue=None
 for event in timeline['events']:
  i=event['index'];c=event['graphic'];frames=round(event['end']*30)-round(event['start']*30);speechframes=math.ceil((event['speech_end']-event['start'])*30);thinking=c.get('pause',0)>=3 or c['role']=='question';fingerprint=hashlib.sha256((graphics_hash+json.dumps([c,previous_cue,frames,speechframes],sort_keys=True)).encode()).hexdigest()[:12];base=folder/f'{i:02}-{fingerprint}';clip=base.with_suffix('.mp4');final=folder/f'{i:02}-final.png'
  draw(l,c,final,1,previous_cue);im=Image.open(final).convert('RGB')
  if not clip.exists():
   listing=[];animation=24 if c.get('rows') or c.get('line') else 12
   for j in range(animation):
    p=folder/f'{i:02}-anim-{j:02}.png';draw(l,c,p,(j+1)/animation,previous_cue)
    if previous and j<10:Image.blend(previous,Image.open(p).convert('RGB'),(j+1)/10).save(p)
    listing.append(f"file '{p}'\nduration {1/30:.9f}\n")
   hold=(speechframes if thinking else frames)-animation;assert hold>=0
   listing.append(f"file '{final}'\nduration {hold/30:.9f}\n")
   if thinking:
    remain=frames-speechframes;k=0
    while remain:
     n=min(30,remain);p=folder/f'{i:02}-think-{k}.png';draw(l,c,p,1,previous_cue,math.ceil(remain/30));listing.append(f"file '{p}'\nduration {n/30:.9f}\n");remain-=n;k+=1
   listing.append(f"file '{final}'\n");text=base.with_suffix('.txt');text.write_text(''.join(listing))
   temp=base.with_suffix('.partial.mp4');run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',text,'-vf','fps=30,format=yuv420p','-frames:v',frames,'-c:v','libx264','-preset','veryfast','-crf','20','-threads','3',temp]);temp.replace(clip)
  previous=im;previous_cue=c;clips.append(clip);print(f'{l["slug"]}: rendered {i+1}/{len(timeline["events"])}',flush=True)
 out=ROOT/l['file'];out.parent.mkdir(parents=True,exist_ok=True)
 vtt=['WEBVTT',''];srt=[]
 for i,c in enumerate(timeline['captions'],1):
  vtt += [f'{stamp(c["start"])} --> {stamp(c["end"])} line:1% position:50% align:center size:88%','\n'.join(textwrap.wrap(c['text'],48)),'']
  srt += [str(i),f'{stamp(c["start"],True)} --> {stamp(c["end"],True)}','\n'.join(textwrap.wrap(c['text'],48)),'']
 out.with_suffix('.vtt').write_text('\n'.join(vtt));srtpath=folder/'captions.srt';srtpath.write_text('\n'.join(srt));(out.parent/(out.name+'_transcript.txt')).write_text('\n\n'.join(c['text'] for c in timeline['captions'])+'\n')
 listing=folder/'clips.txt';listing.write_text(''.join(f"file '{p}'\n" for p in clips));dest=out.with_suffix('.mp4');temp=folder/'final.partial.mp4'
 run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',listing,'-i',narration,'-i',srtpath,'-map','0:v:0','-map','1:a:0','-map','2:s:0','-c:v','copy','-af','loudnorm=I=-17:TP=-2:LRA=9','-c:a','aac','-b:a','160k','-ar','48000','-c:s','mov_text','-metadata:s:s:0','language=eng','-movflags','+faststart','-metadata','title='+l['title'],temp]);temp.replace(dest)
 run(['ffmpeg','-v','error','-y','-ss',timeline['events'][5]['start'],'-i',dest,'-frames:v','1','-vf','scale=1280:720',out.parent/(out.name+'_poster.jpg')])
 actual_duration=float(json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','json',str(dest)]))['format']['duration'])
 return dict(id=l['slug'],section=l['section'],title=l['title'],src=str(dest.relative_to(ROOT)),captions=str(out.with_suffix('.vtt').relative_to(ROOT)),transcript=str((out.parent/(out.name+'_transcript.txt')).relative_to(ROOT)),poster=str((out.parent/(out.name+'_poster.jpg')).relative_to(ROOT)),duration=actual_duration,narration_duration=timeline['duration'],caption_cues=len(timeline['captions']),bytes=dest.stat().st_size,sha256=sha(dest),audio=str(narration.relative_to(ROOT)),audio_sha256=sha(narration),status='rendered',presenter=False)

def main():
 save(HERE/'scripts.json',LESSONS)
 manifest=dict(schema=1,status='producing',scope='Five graphics-only Fractions lessons; separate approved LCM extension unchanged.',engine='Kokoro v1.0 / sherpa-onnx 1.12.26',speaker='hf_alpha',speaker_id=VOICE,voice_note='Native female Hindi voice embedding with English lexicon. No accent/pitch filters or post-generation speech retiming.',listening_review='not_performed',synthesis_cost=0,visual_source='Python mathematical primitives only; no video footage or faces.',models={p.name:sha(p) for p in [MODEL/'model.onnx',MODEL/'voices.bin']},lessons=[])
 save(HERE/'manifest.json',manifest)
 config=sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(kokoro=sherpa_onnx.OfflineTtsKokoroModelConfig(model=str(MODEL/'model.onnx'),voices=str(MODEL/'voices.bin'),tokens=str(MODEL/'tokens.txt'),data_dir=str(MODEL/'espeak-ng-data'),lexicon=str(MODEL/'lexicon-us-en.txt')),num_threads=3),max_num_sentences=1)
 tts=sherpa_onnx.OfflineTts(config);assert tts.num_speakers>VOICE and tts.sample_rate==24000
 for l in LESSONS:
  folder=WORK/l['slug'];folder.mkdir(exist_ok=True);timeline,narration=synthesis(tts,l,folder);print(l['slug']+': narration complete '+str(round(timeline['duration'],2))+'s',flush=True)
  manifest['lessons'].append(render(l,folder,timeline,narration));save(HERE/'manifest.json',manifest)
 manifest['status']='rendered_pending_qa';save(HERE/'manifest.json',manifest)
 print('ALL FIVE RENDERED',flush=True)
if __name__=='__main__':main()
