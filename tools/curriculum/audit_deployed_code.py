"""Read-only deployed script/style audit against the recorded resource baseline.
Run from the repository root; preserves authentication and TLS verification.
"""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
import json,hashlib,urllib.request,subprocess
root=Path(__file__).resolve().parents[2];baseline=json.loads((root/'docs/year5/resource-audit.json').read_text())['baseline_commit'];paths=set()
class P(HTMLParser):
 def handle_starttag(self,t,aa):
  a=dict(aa);url=a.get('src') if t=='script' else a.get('href') if t=='link' and a.get('rel')=='stylesheet' else None
  if url and not urlsplit(url).scheme:paths.add(url)
for name in ['whole-numbers','fractions','decimals-percentages','addition-subtraction','multiplication-division','factors-multiples','measurement','time-angles','space-lessons','statistics']:
 P().feed(subprocess.check_output(['git','show',baseline+':'+name+'.html'],cwd=root,text=True))
def get(url):
 data=subprocess.check_output(['git','show',baseline+':'+urlsplit(url).path],cwd=root);expected=hashlib.sha256(data).hexdigest()
 with urllib.request.urlopen('https://initsrikanth.github.io/MathMagic/'+url,timeout=35) as r:remote=r.read();return {'url':url,'status':r.status,'bytes':len(remote),'sha256':hashlib.sha256(remote).hexdigest(),'baseline_sha256':expected,'matches_baseline':hashlib.sha256(remote).hexdigest()==expected}
with ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(get,sorted(paths)))
out={'baseline_commit':baseline,'checked_on':datetime.now(timezone.utc).isoformat(),'method':'Fetch actual versioned script and stylesheet URLs from all 10 baseline lesson pages; compare to exact baseline Git blobs. Functions deployment/Google sign-in/App Check are not verified.','resources':rows}
(root/'docs/year5/deployed-code-audit.json').write_text(json.dumps(out,indent=2)+'\n');print(len(rows),'resources;',sum(r['matches_baseline'] for r in rows),'hash matches; failures',[r for r in rows if not r['matches_baseline']])
