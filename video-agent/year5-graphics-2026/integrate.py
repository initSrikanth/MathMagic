"""Scoped native-player integration using the approved Fractions card parser."""
import json,re,html,hashlib,subprocess,os,importlib.util
from pathlib import Path
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[1];TOPIC=os.environ.get('MATHMAGIC_TOPIC','whole-numbers');P=BASE/TOPIC
sp=importlib.util.spec_from_file_location('approved_card_parser',BASE.parent/'fractions-graphics-2026/integrate.py');old=importlib.util.module_from_spec(sp);sp.loader.exec_module(old);Cards=old.Cards
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 import pathlib as _vq_pathlib, sys as _vq_sys
 _vq_root=next(p for p in _vq_pathlib.Path(__file__).resolve().parents if (p/'video-agent/video-production-contract.json').is_file())
 _vq_sys.path.insert(0,str(_vq_root/'tools/video-quality'))
 from guard import enforce as _vq_enforce
 _vq_enforce()
 m=json.loads((P/'manifest.json').read_text());assert len(m['lessons'])==5 and all(e['status']=='verified' for e in m['lessons'])
 page=ROOT/(TOPIC+'.html');before=page.read_text();sections={e['section'] for e in m['lessons']};cards=[c for c in Cards(before).cards if c[0] in sections];assert len(cards)==5
 backup=dict(base_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),cards={},assets={});replace={}
 for section,a,b in cards:
  card=before[a:b];backup['cards'][section]=card
  for src in re.findall(r'(?:src|href|poster)="(videos/[^"]+)"',card):
   src=src.split('#')[0];f=ROOT/src
   if f.is_file():backup['assets'][src]=dict(bytes=f.stat().st_size,sha256=sha(f))
  entry=next(e for e in m['lessons'] if e['section']==section);assert sha(ROOT/entry['src'])==entry['sha256'];t=html.escape(entry['title']);transcript=''.join('<p>'+html.escape(c['text'])+'</p>' for c in json.loads((P/'timings'/(entry['id']+'.json')).read_text())['captions'])
  match=re.search(r'\bid="([^"]+)"',card.split('>')[0]);cid=match[1] if match else 'mathmagic-'+TOPIC+'-'+section
  replace[section]=f'<aside class="video-resource mathmagic-owned-video" id="{cid}" data-year5-graphics="{entry["id"]}"><h3>MathMagic: {t}</h3><div class="video-frame"><video controls playsinline preload="metadata" poster="{entry["poster"]}" aria-label="MathMagic - {t}" style="width:100%;height:100%;object-fit:contain;background:#FFF9EE"><source src="{entry["src"]}" type="video/mp4"><track kind="captions" src="{entry["captions"]}" srclang="en" label="English" default>Your browser cannot play this video. <a href="{entry["src"]}">Download the lesson video</a>.</video></div><a class="resource-link" href="{entry["src"]}" target="_blank" rel="noopener noreferrer">Open the {t} lesson video</a><details><summary>Read the {t} video transcript</summary>{transcript}</details></aside>'
 after=before
 for sec,a,b in sorted(cards,key=lambda c:c[1],reverse=True):after=after[:a]+replace[sec]+after[b:]
 def strip(s):
  for sec,a,b in sorted([c for c in Cards(s).cards if c[0] in sections],key=lambda c:c[1],reverse=True):s=s[:a]+'[VIDEO:'+sec+']'+s[b:]
  return s
 assert strip(before)==strip(after),'Non-media content changed'
 (P/'previous-integrations.json').write_text(json.dumps(backup,indent=2,ensure_ascii=False)+'\n');page.write_text(after);m['status']='release_ready';(P/'manifest.json').write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n');print('Five verified players integrated; non-media bytes preserved.')
if __name__=='__main__':main()
