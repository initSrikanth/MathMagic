"""Install only finished, verified owner-authorised narration replacements."""
import json,hashlib,shutil,sys,copy,importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/video-quality'))
from narration_release import verify
spec=importlib.util.spec_from_file_location('cards',ROOT/'video-agent/fractions-graphics-2026/integrate.py');cards=importlib.util.module_from_spec(spec);spec.loader.exec_module(cards)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 dbpath=ROOT/'docs/video-quality-audit-35.json';db=json.loads(dbpath.read_text());out=Path(__file__).parent;releases=[];pages={};batches={}
 for r in db['records'][10:30]:
  folder=out/str(r['number']);evpath=folder/'candidate.json'
  if not evpath.exists():continue
  if r.get('narration_replacement'):releases.append(r['narration_replacement']);continue
  e=json.loads(evpath.read_text());s=r.get('active_media') or dict(mp4=r['mp4'],sha256=r['expected_sha256'],bytes=r['expected_bytes'],captions=r['captions'],transcript=r['transcript'],poster=r['poster'],script=r['script'],duration=r['duration'])
  assert e['source']==s['mp4'] and e['source_sha256']==s['sha256']
  dest=ROOT/'videos/hf-alpha'/r['topic'];dest.mkdir(parents=True,exist_ok=True);f=dest/(Path(s['mp4']).stem+'-hf-alpha.mp4');source=folder/e['file'];assert sha(source)==e['sha256'];shutil.copy2(source,f)
  cap=f.with_suffix('.vtt');cap.write_bytes((folder/'Multiply_Efficiently_HFAlpha_Narration_Review_1080p.vtt').read_bytes());txt=f.with_name(f.stem+'_transcript.txt');txt.write_bytes((ROOT/s['transcript']).read_bytes())
  t=dict(s,mp4=str(f.relative_to(ROOT)),sha256=sha(f),bytes=f.stat().st_size,captions=str(cap.relative_to(ROOT)),transcript=str(txt.relative_to(ROOT)),duration=e['duration'])
  c=dict(number=r['number'],page=r['page'],section=r['lesson_section'],previous=s,replacement=t,evidence=str(evpath.relative_to(ROOT)),owner_authorised=True,perceptual_status='UNVERIFIED',deployed=False)
  r['narration_replacement']=c;verify([r]);r['active_media']=t;r['previous_voice']=r['voice'];r['voice']=e['voice'];r['accent_status']='UNVERIFIED';r['full_quality_status']='UNVERIFIED';releases.append(c)
  h=pages.setdefault(r['page'],(ROOT/r['page']).read_text());matches=[(a,b) for section,a,b in cards.Cards(h).cards if section==r['lesson_section'] and s['mp4'] in h[a:b]];assert len(matches)==1,(r['number'],matches);a,b=matches[0];card=h[a:b];assert s['mp4'] in card
  newcard=card.replace(s['mp4'],t['mp4']).replace(s['captions'],t['captions']).replace(s['transcript'],t['transcript']);pages[r['page']]=h[:a]+newcard+h[b:]
  manifest=r['manifest'];batch=batches.setdefault(manifest,json.loads((ROOT/manifest).read_text()));entry=next(x for x in batch['lessons'] if x['section']==r['lesson_section']);entry['previous_narration_release']=copy.deepcopy(entry)
  entry.update(src=t['mp4'],captions=t['captions'],transcript=t['transcript'],bytes=t['bytes'],sha256=t['sha256'],duration=t['duration'],status='verified_owner_authorised_narration',perceptual_status='UNVERIFIED',voice=e['voice'])
 for name,h in pages.items():
  before=(ROOT/name).read_text()
  def strip(s):
   for section,a,b in sorted(cards.Cards(s).cards,key=lambda x:x[1],reverse=True):s=s[:a]+f'[PLAYER:{section}]'+s[b:]
   return s
  assert strip(h)==strip(before);(ROOT/name).write_text(h)
 for name,batch in batches.items():(ROOT/name).write_text(json.dumps(batch,indent=2)+'\n')
 dbpath.write_text(json.dumps(db,indent=2)+'\n');(out/'release.json').write_text(json.dumps(dict(owner_authorisation='Explicit owner directive: approved hf_alpha profile; replace existing20 without another sample approval.',per_video_perceptual_status='UNVERIFIED',replacements=releases),indent=2)+'\n');print('Integrated',len(releases),'verified replacements')
if __name__=='__main__':main()
