"""Replace exactly five owned player cards; never change lesson prose or LCM."""
import json,re,html,hashlib,subprocess
from pathlib import Path
from html.parser import HTMLParser
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
VOID={'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
class Cards(HTMLParser):
 def __init__(self,text):
  super().__init__(convert_charrefs=False);self.text=text;self.offsets=[0];self.stack=[];self.cards=[]
  for m in re.finditer('\n',text):self.offsets.append(m.end())
  self.feed(text)
 def pos(self):a,b=self.getpos();return self.offsets[a-1]+b
 def handle_starttag(self,tag,attrs):
  if tag in VOID:return
  attrs=dict(attrs);section=attrs.get('id') if tag=='section' else next((e['section'] for e in reversed(self.stack) if e['section']),None)
  self.stack.append(dict(tag=tag,start=self.pos(),section=section,card='video-resource' in attrs.get('class','').split() and attrs.get('id')!='mathmagic-lcm-extension'))
 def handle_endtag(self,tag):
  idx=next((i for i in range(len(self.stack)-1,-1,-1) if self.stack[i]['tag']==tag),None)
  if idx is None:return
  entry=self.stack[idx];self.stack=self.stack[:idx]
  if entry['card']:self.cards.append((entry['section'],entry['start'],self.pos()+len('</'+tag+'>')))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 import pathlib as _vq_pathlib, sys as _vq_sys
 _vq_root=next(p for p in _vq_pathlib.Path(__file__).resolve().parents if (p/'video-agent/video-production-contract.json').is_file())
 _vq_sys.path.insert(0,str(_vq_root/'tools/video-quality'))
 from guard import enforce as _vq_enforce
 _vq_enforce()
 manifest=json.loads((P/'manifest.json').read_text());assert manifest['status']=='verified_pending_integration' and len(manifest['lessons'])==5
 page=ROOT/'fractions.html';before=page.read_text();cards=Cards(before).cards;sections={e['section'] for e in manifest['lessons']};cards=[c for c in cards if c[0] in sections];assert len(cards)==5 and len({c[0] for c in cards})==5
 backup=dict(base_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),cards={},assets={})
 for section,start,end in cards:
  old=before[start:end];backup['cards'][section]=old
  for src in re.findall(r'(?:src|href|poster)="(videos/[^"]+)"',old):
   path=ROOT/src.split('#')[0]
   if path.is_file():backup['assets'][src.split('#')[0]]=dict(bytes=path.stat().st_size,sha256=sha(path))
 (P/'previous-integrations.json').write_text(json.dumps(backup,indent=2,ensure_ascii=False)+'\n')
 replacements={};ids={'meaning':'mathmagic-comparing-video','equivalent':'mathmagic-equivalent-video','mixed':'mathmagic-mixed-video','addsub':'mathmagic-addsub-video','problems':'mathmagic-problems-video'}
 for e in manifest['lessons']:
  assert sha(ROOT/e['src'])==e['sha256'];title=html.escape(e['title']);t=json.loads((P/'timings'/(e['id']+'.json')).read_text());transcript=''.join('<p>'+html.escape(c['text'])+'</p>' for c in t['captions'])
  card=f'<div class="video-resource fractions-graphics-resource" data-fractions-graphics="{e["id"]}"><h3>MathMagic: {title}</h3><div class="video-frame"><video id="{ids[e["section"]]}" controls playsinline preload="metadata" poster="{e["poster"]}" aria-label="MathMagic - {title}" style="width:100%;height:100%;object-fit:contain;background:#FFF9EE"><source src="{e["src"]}" type="video/mp4"><track kind="captions" src="{e["captions"]}" srclang="en" label="English" default>Your browser cannot play this video. <a href="{e["src"]}">Download the lesson video</a>.</video></div><a href="{e["src"]}">Open the {title} video</a><details><summary>Read the {title} transcript</summary>{transcript}</details>'
  if e['section']=='meaning':card+='<p id="mathmagic-comparing-status" hidden role="status"></p>'
  replacements[e['section']]=card+'</div>'
 after=before
 for section,start,end in sorted(cards,key=lambda x:x[1],reverse=True):after=after[:start]+replacements[section]+after[end:]
 # Compare every non-media byte, including the complete separate LCM card.
 def strip(text):
  result=text
  for section,start,end in sorted([c for c in Cards(text).cards if c[0] in sections],key=lambda x:x[1],reverse=True):result=result[:start]+'[PLAYER:'+section+']'+result[end:]
  return result
 assert strip(before)==strip(after),'Unrelated lesson content changed'
 page.write_text(after);manifest['status']='integrated_candidate';(P/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
 print('Five players integrated; all non-player bytes and separate LCM extension preserved.')
if __name__=='__main__':main()
