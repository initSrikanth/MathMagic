"""Statistics release preparation; exact-byte human approval is always required to apply."""
from pathlib import Path
import hashlib,json,re,html
ROOT=Path(__file__).resolve().parents[2]
CHECKPOINT=ROOT/'video-agent/statistics/checkpoint.json'
APPROVAL=ROOT/'video-agent/statistics/approval.json'
PLAYER_JS='js/statistics-video.js?v=1';PLAYER_CSS='css/statistics-video.css?v=1'
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read_state():return json.loads(CHECKPOINT.read_text())
def flag_ids(row):
 qa=json.loads((ROOT/row['quality_evidence']).read_text());items=[('static',f)for f in qa['static_scene_review_flags']]+[('fast',f)for f in qa['rushed_reveal_flags']]
 n=row['id'].removeprefix('statistics-lesson');return [f'L{n}-{kind}-{i+1}' for i,(kind,_) in enumerate(items)]
def verify_candidates():
 s=read_state();assert s['topic']=='statistics' and len(s['lessons'])==5
 assert [r['id']for r in s['lessons']]==['statistics-lesson'+str(i)for i in range(1,6)]
 for r in s['lessons']:
  for key,expected in r['bundle_sha256'].items():
   p=(ROOT/r[key]).resolve();assert p.is_relative_to((ROOT/'video-agent/statistics/review').resolve()),'Statistics asset path escaped review directory'
   assert digest(p)==expected,'Statistics integrity mismatch: '+r[key]
  assert digest(ROOT/r['video'])==r['video_sha256']
  q=json.loads((ROOT/r['quality_evidence']).read_text());assert q['sha256']==r['video_sha256'] and q['full_decode'] and q['caption_timing_valid'] and q['caption_transcript_text_match'] and q['meaningful_narration_seconds']>=300
  assert q['clipping_fraction']<.001 and q['audio_rms']>.008
 return s

def require_approval(state=None,approval=None):
 s=state or verify_candidates()
 policy=json.loads((ROOT/'video-agent/video-production-contract.json').read_text()).get('statistics_release_authorisation',{})
 assert policy.get('conditional_authorisation') is True and policy.get('topic')=='statistics' and policy.get('requires_full_human_audio_and_video_review') is True,'Statistics conditional release authority required'
 if approval is None:
  if not APPROVAL.exists():raise RuntimeError('STATISTICS RELEASE BLOCKED: full human audiovisual approval has not been recorded.')
  approval=json.loads(APPROVAL.read_text())
 if approval.get('approved') is not True:raise RuntimeError('STATISTICS RELEASE BLOCKED: five exact-byte full human audiovisual approvals are still pending. Generation permission does not authorise publication.')
 assert approval.get('player_assets')=={p:digest(ROOT/p) for p in ['js/statistics-video.js','css/statistics-video.css']},'Player assets changed since human review'
 assert approval.get('topic')=='statistics' and len(approval.get('videos',[]))==5,'Approval must cover exactly five Statistics files'
 for r,a in zip(s['lessons'],approval['videos']):
  assert a.get('id')==r['id'] and a.get('video_sha256')==r['video_sha256'],'Approval is not bound to the exact video'
  assert a.get('bundle_sha256')==r['bundle_sha256'],'Approval sidecars changed'
  assert all(isinstance(a.get(k),str) and a[k].strip() for k in ['reviewer','reviewed_at','evidence_record']),'Actual reviewer, date and evidence record required'
  assert re.match(r'^\d{4}-\d{2}-\d{2}',a['reviewed_at']),'Actual review date required'
  for k in ['full_audio_listened','full_video_viewed','accent_and_expressiveness_approved','pedagogy_approved','mobile_legibility_approved']:
   assert a.get(k)is True,'Human review missing: '+k
  resolutions=a.get('flag_resolutions',{});assert set(resolutions)==set(flag_ids(r)) and all(isinstance(v,str)and v.strip() for v in resolutions.values()),'Every flagged interval requires recorded human resolution'
 return approval

def player(row,i):
 title=json.loads((ROOT/row['script']).read_text())['title'];e=html.escape
 text=(ROOT/row['transcript']).read_text();paragraphs=''.join('<p>'+e(p)+'</p>' for p in text.split('\n\n') if p.strip())
 return f'''<aside class="video-resource statistics-player" data-statistics-video="{row['id']}"><h3 id="video-heading-{i}">{e(title)}</h3><div class="statistics-video-stage"><video id="statistics-video-{i}" tabindex="0" controls playsinline preload="metadata" aria-labelledby="video-heading-{i}" aria-describedby="video-help-{i}" poster="{row['poster']}"><source src="{row['video']}" type="video/mp4"><track kind="captions" src="{row['captions']}" srclang="en" label="English"><a href="{row['video']}">Open the {e(title)} video</a></video></div><button type="button" data-video-toggle aria-controls="statistics-video-{i}">Play video</button><p data-video-status role="status"></p><button type="button" data-caption-toggle aria-pressed="false" aria-controls="captions-{i}">Show captions</button><div id="captions-{i}" class="statistics-caption-panel" role="region" aria-label="Video captions" hidden><p data-caption-text>Captions appear here during speech.</p></div><p id="video-help-{i}">Use the video controls to play, pause or open fullscreen. Captions appear below the picture; fullscreen uses native captions.</p><p><a href="{row['video']}">Open or download the video</a> • <a href="{row['captions']}">Caption file</a> • <a href="{row['transcript']}">Transcript file</a></p><details><summary>Read the video transcript</summary>{paragraphs}</details></aside>'''

def integrated_html(state=None):
 s=state or verify_candidates();page=(ROOT/'statistics.html').read_text()
 for i,row in enumerate(s['lessons'],1):
  pattern=r'<aside class="video-pending">.*?</aside>';start=page.index(f'<section id="lesson{i}"');end=page.index('</section>',start);section=page[start:end]
  if 'data-statistics-video='in section:raise RuntimeError('Statistics players already present; inspect before rewriting.')
  section,count=re.subn(pattern,lambda _:player(row,i),section,count=1,flags=re.S);assert count==1,'Expected one pending video card per lesson';page=page[:start]+section+page[end:]
 page=page.replace('</head>',f'<link rel="stylesheet" href="{PLAYER_CSS}"></head>').replace('</body>',f'<script src="{PLAYER_JS}"></script></body>')
 return page

def prepare():
 s=verify_candidates();page=integrated_html(s)
 preview=ROOT/'video-agent/statistics/review/integration-preview.html'
 preview.write_text(page.replace('<head>','<head><base href="../../../">',1).replace('<main class="course-shell"','<p class="release-preview-note">Integration preview — pending full human approval; not a published lesson player.</p><main class="course-shell"',1))
 return preview

def apply():
 s=verify_candidates();approval=require_approval(s)
 page=integrated_html(s);(ROOT/'statistics.html').write_text(page)
 # Registration remains in the existing topic checkpoint; approval evidence is separate.
 s['integrated']=5
 for row,review in zip(s['lessons'],approval['videos']):
  row.update(status='APPROVED_FOR_INTEGRATION',approval_status='APPROVED',perceptual_review='HUMAN_APPROVED_EXACT_BYTES',reviewer=review['reviewer'],review_date=review['reviewed_at'])
 s.update(status='APPROVED_REGISTERED_PENDING_DEPLOYMENT',checkpoint='Five checksum-bound human approvals recorded; complete players integrated; deployment still pending.',human_approval_status='APPROVED_ALL_FIVE',media_registration_status='APPROVED_EXACT_BYTE_HUMAN_RECORD',human_approval_record='video-agent/statistics/approval.json',blockers=['Final-head required checks, authorised merge/Pages deployment and live verification.'])
 s.setdefault('release_preparation',{}).update(production_players_integrated=5,approval_granted=True)
 CHECKPOINT.write_text(json.dumps(s,indent=2)+'\n')
 return ROOT/'statistics.html'

def assert_integrated_release():
 s=verify_candidates();require_approval(s);page=(ROOT/'statistics.html').read_text()
 assert s.get('integrated')==5 and s.get('human_approval_status')=='APPROVED_ALL_FIVE','Approved registration required'
 assert page.count('data-statistics-video=')==5 and 'class="video-pending"'not in page,'Complete five-player integration required'
 for row in s['lessons']:
  assert f'data-statistics-video="{row["id"]}"' in page
  assert all(f'src="{row[k]}"' in page for k in ['video','captions']) and f'poster="{row["poster"]}"' in page
 assert PLAYER_JS in page and PLAYER_CSS in page
 return s

if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--prepare',action='store_true');ap.add_argument('--apply',action='store_true');a=ap.parse_args();assert a.prepare!=a.apply,'Choose --prepare or --apply'
 print(prepare() if a.prepare else apply())
