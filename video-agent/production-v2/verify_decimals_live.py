"""TLS-verified published HTML/assets, hashes and actual HTTP byte-range checks."""
import os,json,urllib.request,urllib.error,hashlib,concurrent.futures,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];P=Path(__file__).resolve().parent
TOPIC=os.environ.get('MATHMAGIC_TOPIC','decimals-percentages')
RELEASE='decimals-release.json' if TOPIC=='decimals-percentages' else TOPIC+'-release.json'
BASE='https://initsrikanth.github.io/MathMagic/'
CACHE=Path('/workspace/pr46-live-cache') if TOPIC=='decimals-percentages' else Path('/workspace')/(TOPIC+'-live-cache');CACHE.mkdir(parents=True,exist_ok=True)
def fetch(relative):
 relative=relative.split('?')[0];assert '..' not in Path(relative).parts
 path=CACHE/relative;path.parent.mkdir(parents=True,exist_ok=True)
 with urllib.request.urlopen(urllib.request.Request(BASE+relative,headers={'Cache-Control':'no-cache'}),timeout=60) as response:
  data=response.read();status=response.status;headers=dict(response.headers)
 path.write_bytes(data);return data,status,headers

def main():
 m=json.loads((P/RELEASE).read_text());page,status,_=fetch(TOPIC+'.html');text=page.decode();assert status==200
 def check(e):
  assert 'src="'+e['src']+'"' in text
  data,status,headers=fetch(e['src']);assert status==200 and len(data)==e['bytes'] and hashlib.sha256(data).hexdigest()==e['sha256']
  assert 'video/mp4' in headers.get('Content-Type',headers.get('content-type',''))
  req=urllib.request.Request(BASE+e['src'],headers={'Range':'bytes=0-1023'})
  with urllib.request.urlopen(req,timeout=60) as response:assert response.status==206 and response.read()==data[:1024]
  cc,_,_=fetch(e['captions']);tr,_,_=fetch(e['transcript']);fetch(e['poster'])
  assert cc==(ROOT/e['captions']).read_bytes() and tr==(ROOT/e['transcript']).read_bytes()
  return dict(src=e['src'],url=BASE+e['src'],http=200,bytes=len(data),sha256=e['sha256'],range=206,mime='video/mp4',captions_transcript_exact=True)
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(check,m['lessons']))
 for path in ['css/'+TOPIC+'.css','js/'+TOPIC+'.js']:
  content,_,_=fetch(path);assert content==(ROOT/path).read_bytes()
 report=dict(passed=True,source='Actual published GitHub Pages responses, TLS verification enabled',videos=results)
 (CACHE/'verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
