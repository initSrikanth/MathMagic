import json,re,shutil
from pathlib import Path
ROOT=Path(__file__).parent;REPO=ROOT.parents[1]
norm=lambda s:re.findall(r'[a-z0-9]+',s.lower())
def stamp(s):
 ms=round(s*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02}.{ms%1000:03}'
def main():
 for p in json.loads((ROOT/'lessons.json').read_text()):
  a=ROOT/'sources'/f'{p["id"]}-alignment.json'
  if not a.exists():continue
  words=json.loads(a.read_text())['words'];script=(ROOT/f'{p["id"]}.txt').read_text();tokens=[];pos=0
  for s in script.split():
   count=len(norm(s));assert count;part=words[pos:pos+count];assert [w['word']for w in part]==norm(s);tokens.append(dict(text=s,start=part[0]['start'],end=part[-1]['end']));pos+=count
  groups=[];chunk=[]
  for token in tokens:
   if chunk and(len(' '.join(x['text']for x in chunk+[token]))>74 or len(chunk)>=10):groups.append(chunk);chunk=[]
   chunk.append(token)
   if token['text'].endswith(('.','?','!'))and len(chunk)>=4:groups.append(chunk);chunk=[]
  if chunk:groups.append(chunk)
  text='WEBVTT\n\n'
  for i,g in enumerate(groups):
   lines=['']
   for x in g:
    if len(lines[-1])+len(x['text'])+1>42:lines.append('')
    lines[-1]+=(' 'if lines[-1]else'')+x['text']
   text+=f'{i+1}\n{stamp(g[0]["start"])} --> {stamp(max(g[0]["start"]+.01,g[-1]["end"]))}\n'+ '\n'.join(lines)+'\n\n'
  name=f'MathMagic_{p["slug"]}_1080p';(REPO/'videos'/f'{name}.vtt').write_text(text);(REPO/'videos'/f'{name}_transcript.txt').write_text(script)
  assert norm(' '.join(t['text']for g in groups for t in g))==norm(script)
  print(p['id'],len(groups),'caption cues')
if __name__=='__main__':main()
