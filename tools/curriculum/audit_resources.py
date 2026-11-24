"""Inventory actual Year 5 lesson/media bytes. Optional --live is read-only.
No authentication bypass, media generation or approval mutation.
"""
from pathlib import Path
from html.parser import HTMLParser
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import argparse, hashlib, json, subprocess, urllib.request
ROOT=Path(__file__).resolve().parents[2]
PAGES=['whole-numbers','fractions','decimals-percentages','addition-subtraction','multiplication-division','factors-multiples','measurement','time-angles','space-lessons','statistics']
class Inventory(HTMLParser):
    def __init__(self):
        super().__init__(); self.section=None; self.videos=[]; self.ids=[]; self.sidecars=[]
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if a.get('id'): self.ids.append(a['id'])
        if tag=='section': self.section=a.get('id')
        if tag=='video': self.videos.append({'lesson':self.section,'poster':a.get('poster'),'controls':'controls' in a,'playsinline':'playsinline' in a,'captions':None})
        if tag=='source' and self.videos: self.videos[-1]['path']=a.get('src')
        if tag=='track' and self.videos: self.videos[-1]['captions']=a.get('src')
        if tag=='a' and 'transcript' in a.get('href','').lower(): self.sidecars.append(a['href'])
def sha(data): return hashlib.sha256(data).hexdigest()
def local():
    pages=[]; assets={}
    for page in PAGES:
        path=ROOT/(page+'.html'); data=path.read_bytes(); p=Inventory();p.feed(data.decode())
        rows=[]
        for v in p.videos:
            name=v.get('path'); f=ROOT/name
            if name not in assets:
                probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(f)]))
                assets[name]={'path':name,'sha256':sha(f.read_bytes()),'bytes':f.stat().st_size,'duration':float(probe['format']['duration']),'streams':[{k:s[k] for k in ['codec_name','width','height','pix_fmt'] if k in s} for s in probe['streams']]}
            rows.append(v)
        sidecars=set(p.sidecars+[v[k] for v in rows for k in ['poster','captions'] if v[k]])
        # Existing core players expose matching transcripts inline and as sibling files.
        for v in rows:
            stem=Path(v['path']).with_suffix(''); candidate=str(stem)+'_transcript.txt'
            if (ROOT/candidate).exists():sidecars.add(candidate)
        for name in sorted(sidecars):
            f=ROOT/name
            assets[name]={'path':name,'sha256':sha(f.read_bytes()),'bytes':f.stat().st_size}
        pages.append({'path':page+'.html','sha256':sha(data),'lesson_ids':[i for i in p.ids if i.startswith('lesson') or i in ['meaning','equivalent','mixed','addsub','problems','place','compare','percent','connect','apply']],'videos':rows,'sidecars':sorted(sidecars)})
    return {'audited_on':datetime.now(timezone.utc).isoformat(),'baseline_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'method':'Actual HTML, local media SHA-256/ffprobe and caption/transcript inspection; no new full audiovisual review or decode certification.','pages':pages,'assets':list(assets.values())}
def live(report):
    origin='https://initsrikanth.github.io/MathMagic/'
    def get(row):
        try:
            req=urllib.request.Request(origin+row['path'],headers={'User-Agent':'MathMagic-curriculum-audit'})
            with urllib.request.urlopen(req,timeout=45) as r:
                h=hashlib.sha256(); size=0
                while chunk:=r.read(1024*1024):h.update(chunk);size+=len(chunk)
                return {'path':row['path'],'status':r.status,'content_type':r.headers.get('Content-Type'),'bytes':size,'sha256':h.hexdigest(),'matches_local':h.hexdigest()==row['sha256']}
        except Exception as e:return {'path':row['path'],'error':str(e),'matches_local':False}
    with ThreadPoolExecutor(max_workers=4) as pool:report['live']=list(pool.map(get,report['pages']+report['assets']))
    report['live_limitations']='Public byte retrieval only; no real Google sign-in, approved-user Firebase write/rules/App Check, external-provider playback, physical iOS or full listening/viewing claimed.'
    return report
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--live',action='store_true');ap.add_argument('--output',required=True);a=ap.parse_args();r=local()
    if a.live:r=live(r)
    Path(a.output).write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps({'pages':len(r['pages']),'assets':len(r['assets']),'videos':sum(len(p['videos']) for p in r['pages']),'live_matches':sum(x.get('matches_local',False) for x in r.get('live',[])),'live_failures':[x for x in r.get('live',[]) if not x['matches_local']]}))
