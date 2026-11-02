"""Freeze only this validated five-video release for strict media/browser checks."""
import json,hashlib,subprocess,importlib.util,re,tempfile,argparse
from pathlib import Path
from content import LESSONS,HERE,ROOT
from pipeline import sha,json_hash,verify_sidecars
SECTIONS=['place','compare','percent','connect','apply']
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--work-dir',type=Path,default=ROOT/'work/production-v2');args=ap.parse_args()
 m=json.loads((HERE/'manifest.json').read_text());lessons=[l for l in LESSONS if l['topic']=='decimals-percentages'];assert [l['section'] for l in lessons]==SECTIONS
 assert m['active_batch']['lessons']==[l['id'] for l in lessons]
 release=dict(source_commit=m['active_batch']['rollback_sha'],topic='decimals-percentages',lessons=[])
 for l in lessons:
  e=m['lessons'][l['id']];assert e['production_status']=='integrated' and e['script_sha256']==json_hash(l) and e['qa']['result']=='passed' and e['qa']['full_decode']
  src=e['video_filename'];p=ROOT/src;assert sha(p)==e['qa']['sha256'] and p.stat().st_size==e['qa']['bytes']
  t=json.loads((HERE/'timings'/(l['id']+'.json')).read_text())
  stem=src[:-4];captions=stem+'.vtt';transcript=stem+'_transcript.txt';poster=stem+'_poster.jpg'
  assert all((ROOT/f).is_file() for f in [captions,transcript,poster]);assert (ROOT/transcript).read_text()=='\n\n'.join(b['text'] for b in l['beats'])+'\n'
  with tempfile.TemporaryDirectory() as tmp:
   folder=Path(tmp)
   for name,f in [('captions.vtt',captions),('transcript.txt',transcript),('poster.jpg',poster)]: (folder/name).symlink_to(ROOT/f)
   verify_sidecars(l,folder,t)
  info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-of','json',p]))
  import soundfile as sf,numpy as np
  original=args.work_dir/l['id']/'narration.wav';samples,rate=sf.read(original,dtype='int16');assert rate==t['sample_rate'] and sha(original)==t['narration_sha256']
  audio=HERE/'audio'/(l['id']+'.flac');audio.parent.mkdir(exist_ok=True);sf.write(audio,samples,rate,format='FLAC',subtype='PCM_16');decoded,decoded_rate=sf.read(audio,dtype='int16');assert decoded_rate==rate and np.array_equal(samples,decoded)
  release['lessons'].append(dict(id=l['id'],section=l['section'],title=l['title'],src=src,captions=captions,transcript=transcript,poster=poster,bytes=p.stat().st_size,sha256=sha(p),duration=float(info['format']['duration']),narration_duration=t['duration'],caption_cues=len(t['captions']),caption_language='en-GB',status='verified',presenter=False,source_audio=str(audio.relative_to(ROOT)),source_audio_sha256=sha(audio)))
 (HERE/'decimals-release.json').write_text(json.dumps(release,indent=2)+'\n')
 backup_path=HERE/'decimals-previous-integrations.json'
 if not backup_path.exists():
  text=subprocess.check_output(['git','show',m['active_batch']['rollback_sha']+':decimals-percentages.html'],text=True)
  spec=importlib.util.spec_from_file_location('approved_cards',HERE.parent/'fractions-graphics-2026/integrate.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
  backup=dict(base_commit=m['active_batch']['rollback_sha'],cards={sec:'' for sec in SECTIONS},assets={})
  for sec,a,b in mod.Cards(text).cards:
   if sec not in SECTIONS:continue
   card=text[a:b];backup['cards'][sec]=card
   for f in re.findall(r'(?:src|href|poster)="(videos/[^"]+)"',card):
    if (ROOT/f).is_file():backup['assets'][f]=dict(bytes=(ROOT/f).stat().st_size,sha256=sha(ROOT/f))
  backup_path.write_text(json.dumps(backup,indent=2)+'\n')
 print('Five exact-script videos frozen for release, with previous embeds retained.')
if __name__=='__main__':main()
