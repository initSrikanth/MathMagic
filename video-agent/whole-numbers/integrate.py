"""Integrate only after all five final media checks pass. Never edit existing content."""
from pathlib import Path
import json,html,hashlib
ROOT=Path(__file__).parent;REPO=ROOT.parents[1]
def main():
 checks=json.loads((ROOT/'qa'/'all-media.json').read_text());assert len(checks)==5 and all(x['status']=='PASS'for x in checks)
 p=REPO/'whole-numbers.html';baseline=p.read_text();s=baseline
 for lesson in json.loads((ROOT/'lessons.json').read_text()):
  name=f'MathMagic_{lesson["slug"]}_1080p';id=lesson['id'];title=html.escape(lesson['title']);src=f'videos/{name}.mp4';file=REPO/src
  check=next(x for x in checks if x['lesson']==id);assert hashlib.sha256(file.read_bytes()).hexdigest()==check['sha256']
  assert f'id="mathmagic-wn-{id}"'not in s,'Already integrated: do not duplicate'
  transcript=(ROOT/f'{id}.txt').read_text();paras=''.join('<p>'+html.escape(x)+'</p>'for x in transcript.strip().split('\n\n'))
  card=f'<aside class="video-resource mathmagic-owned-video" id="mathmagic-wn-{id}"><h3>MathMagic explainer: {title}</h3><div class="video-frame"><video controls playsinline preload="metadata" style="width:100%;height:100%;object-fit:contain;background:#101827" aria-label="MathMagic - {title}"><source src="{src}" type="video/mp4"><track kind="captions" src="videos/{name}.vtt" srclang="en-AU" label="English">Your browser cannot play this video. <a href="{src}">Open this MathMagic lesson video</a>.</video></div><a class="resource-link" href="{src}" target="_blank" rel="noopener noreferrer">Open the MathMagic lesson video ↗</a><details><summary>Read the {title} video transcript</summary>{paras}</details></aside>'
  start=s.index('<section id="'+id+'"');end=s.index('</section>',start);chunk=s[start:end]
  # Retain original curated resources too; add the owned video before the first
  # original video resource, or before lesson navigation where none existed.
  anchor='<aside class="video-resource">'if '<aside class="video-resource">'in chunk else'<div class="lesson-nav">'
  assert chunk.count(anchor)==1;chunk=chunk.replace(anchor,card+anchor,1);s=s[:start]+chunk+s[end:]
  baseline_reconstructed=s
 # Prove that deleting only the five additive cards restores every baseline byte.
 import re
 restored=re.sub(r'<aside class="video-resource mathmagic-owned-video"[\s\S]*?</aside>','',s)
 assert restored==baseline
 p.write_text(s)
 m=json.loads((ROOT/'manifest.json').read_text());
 for lesson in m['lessons']:
  qa=next(x for x in checks if x['lesson']==lesson['id']);lesson['render']=json.loads((ROOT/'qa'/f'{lesson["id"]}-render.json').read_text())
  lesson.update(status='RENDERED_QA_PASS_INTEGRATED_PENDING_BROWSER_CI',mp4='videos/'+qa['filename'],sha256=qa['sha256'],bytes=qa['bytes'],duration=qa['duration'],caption_cues=qa['caption_cues'],qa='PASS_MEDIA_MATHEMATICS_ALIGNMENT',deployment='PENDING')
 (ROOT/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 print('Five additive players integrated; previous whole-numbers.html recovered exactly by removing only those cards.')
if __name__=='__main__':main()
