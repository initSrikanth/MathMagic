"""Enforce video release rules when a PR changes active media, not documentation candidates."""
import json,re,subprocess,sys,ast,importlib.util
from pathlib import Path
from contract import ROOT,load,assert_release,assert_scoped_correction_release,assert_owner_approved_space_release,branded,rendered_texts,overlay_brand_literals
from math_check import inspect as inspect_math
from narration_release import verify as verify_narration
from registry import load_registry,legacy_inventory,check_history,assert_releasable
c=load();db=json.loads((ROOT/'docs/video-quality-audit-35.json').read_text());records=db['records']
media_registry=load_registry();legacy_inventory(records,media_registry['index'])
assert len({r['mp4'] for r in records})==len(records)
for name in json.loads((Path(__file__).parent/'guarded-entries.json').read_text()):
 tree=ast.parse((ROOT/name).read_text());assert any(isinstance(x,ast.Call) and isinstance(x.func,ast.Name) and x.func.id=='_vq_enforce' for x in ast.walk(tree)),name
parser_spec=importlib.util.spec_from_file_location('video_cards',ROOT/'video-agent/fractions-graphics-2026/integrate.py');parser_module=importlib.util.module_from_spec(parser_spec);parser_spec.loader.exec_module(parser_module)
for overlay in {r['graphics_source'] for r in records}:assert not overlay_brand_literals((ROOT/overlay).read_text()), 'Prohibited branding in rendered overlay source: '+overlay
base=sys.argv[1] if len(sys.argv)>1 else None
if not base:
 print('Contract and production-entry guards valid; no release requested. Library compliance is NOT asserted.');sys.exit(0)
changed=set(subprocess.check_output(['git','diff','--name-only',base,'HEAD'],cwd=ROOT,text=True).splitlines());selected=[]
for r in records:
 media={r[k] for k in ['mp4','captions','transcript','poster']};candidate=r.get('narration_replacement',{}).get('replacement',r.get('correction',{}).get('replacement',r.get('candidate',{})));media.update(v for k,v in candidate.items() if k in ['mp4','captions','transcript','poster'])
 player_changed=False
 if r['page'] in changed:
  before=subprocess.check_output(['git','show',base+':'+r['page']],cwd=ROOT,text=True);after=(ROOT/r['page']).read_text();players=lambda h:[h[a:b] for section,a,b in parser_module.Cards(h).cards if section==r['lesson_section']]
  player_changed=players(before)!=players(after)
 if media&changed or player_changed:selected.append(r)
known=set(media_registry['files'])
space=None
if (ROOT/'video-agent/space/release.json').exists():
 space=assert_owner_approved_space_release()
 known.update(r[k]for r in space['lessons']for k in ['src','captions','transcript','poster'])
 print('Verified10 checksum-bound Space assets with the recorded owner attestation; independent audiovisual, Safari and live Firebase verification is not claimed.')
unknown=[f for f in changed if f.lower().endswith('.mp4') and f not in known]
assert not unknown,'Unaudited new/replacement media under production hold: '+repr(unknown)
trusted=check_history(media_registry,base)
assert_releasable(media_registry,changed,trusted=trusted)
if selected:
 for r in selected:
  target=dict(r,**r.get('narration_replacement',{}).get('replacement',r.get('correction',{}).get('replacement',r.get('candidate',{}))));script=json.loads((ROOT/target['script']).read_text())
  if isinstance(script,list):script=next(x for x in script if x.get('slug',x.get('id'))==r['script_key'])
  assert not any(branded(t,c) for t in rendered_texts(script)),r['lesson']+' branded script/overlay'
  inspect_math(script)
  for field in ['captions','transcript']:assert not branded((ROOT/target[field]).read_text(),c),r['lesson']+' branded '+field
  if not r.get('correction'):
   voice=target.get('voice',r['voice']);assert voice.get('name',voice.get('voice'))==c['approved_voice']['voice'] and voice.get('speaker_id')==c['approved_voice']['speaker_id'],r['lesson']+' voice mismatch'
 narrated=[r for r in selected if r.get('narration_replacement')]
 if narrated:verify_narration(narrated)
 scoped=[r for r in selected if r.get('correction') and not r.get('narration_replacement')];full=[r for r in selected if not r.get('correction') and not r.get('narration_replacement')]
 if scoped:assert_scoped_correction_release(scoped)
 if full:assert_release(full)
 print('Verified owner-authorised narration replacements:',len(narrated),'; scoped corrections:',len(scoped),'; full-quality releases:',len(full),'. Scoped corrections do not approve accent or full perceptual quality.')
elif space:print('Owner-approved Space release verified. Independent audiovisual/Safari/live Firebase checks remain unverified; all unrelated production holds remain.')
else:print('Source/audit-only changes; production hold remains. No video is declared compliant.')
