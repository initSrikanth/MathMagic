"""Integrate only authorised existing-media corrections; preserve every old file and all non-player HTML."""
import json,re,os,copy,html,hashlib,subprocess,sys,importlib.util
from pathlib import Path
from contract import ROOT,REGISTER,branded
from brand_only_candidates import stamp
CACHE=Path('/workspace/video-correction-cache');OUT=ROOT/'video-agent/video-corrections-35'
spec=importlib.util.spec_from_file_location('cards',ROOT/'video-agent/fractions-graphics-2026/integrate.py');cards=importlib.util.module_from_spec(spec);spec.loader.exec_module(cards)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def seconds(s):
 h,m,s=map(float,s.split(':'));return h*3600+m*60+s

def parse_vtt(path):
 out=[]
 for block in Path(path).read_text().strip().split('\n\n')[1:]:
  lines=block.splitlines();at=next((i for i,l in enumerate(lines) if ' --> ' in l),None)
  if at is None:continue
  a,b=lines[at].split(' --> ');z=b.split(' ',1);out.append(dict(start=seconds(a),end=seconds(z[0]),settings=(' '+z[1]) if len(z)>1 else '',lines=lines[at+1:]))
 return out

def main():
 OUT.mkdir(exist_ok=True);(OUT/'scripts').mkdir(exist_ok=True);(OUT/'evidence').mkdir(exist_ok=True)
 if (OUT/'release.json').exists():
  prior=json.loads((OUT/'release.json').read_text())['replacements']
  if len(prior)==32 and all((ROOT/c['replacement']['mp4']).exists() and sha(ROOT/c['replacement']['mp4'])==c['replacement']['sha256'] and c['replacement']['mp4'] in (ROOT/c['page']).read_text() for c in prior):
   print('All32 scoped corrections already integrated; preserving existing outputs and metadata.');return
 db=json.loads(REGISTER.read_text());old=json.loads((CACHE/'brandfree-review/manifest.json').read_text());replacements=[];pages={};batches={};backups=[]
 for r in db['records']:
  c=next((x for x in old['results'] if x['number']==r['number']),None);visual=r['number'] in [14,15]
  if not c and not visual:continue
  origin=ROOT/r['mp4'];assert sha(origin)==r['expected_sha256'];name=origin.stem+('-model-corrected' if visual else '-brandfree');folder=ROOT/'videos/quality-corrections'/r['topic'];folder.mkdir(parents=True,exist_ok=True);final=folder/(name+'.mp4')
  source=CACHE/'visual-finals'/f"{r['number']:02}-model-corrected.mp4" if visual else CACHE/Path(c['candidate']).relative_to('video-agent/remediation-35')
  if not final.exists():os.link(source,final)
  data=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',final]));duration=float(data['format']['duration']);audio=next(s for s in data['streams'] if s['codec_type']=='audio')
  if visual:
   script=json.loads((ROOT/r['script']).read_text());evidence=json.loads(source.with_suffix('.json').read_text());evidence['output']=str(final.relative_to(ROOT));evidence['voice_review']='UNVERIFIED';typ='mathematical_visual_only'
   script['scoped_visual_correction']={'frame_interval':evidence['corrected_frame_interval'],'model':'Midpoint number line' if r['number']==14 else 'Equal ten-cell bars','renderer':'tools/video-quality/model_correction_previews.py:render_frame'}
  else:
   script=json.loads(source.with_suffix('.json').read_text());evidence=copy.deepcopy(c);evidence['candidate']=str(final.relative_to(ROOT));typ='branding_only'
  scriptpath=OUT/'scripts'/f"{r['number']:02}.json";scriptpath.write_text(json.dumps(script,indent=2)+'\n');assert not any(branded(x['text']) for x in script['beats'])
  caption=parse_vtt(ROOT/r['captions']);kept=[]
  for cap in caption:
   if branded(' '.join(cap['lines'])):continue
   shift=3.1 if r['number']==4 and cap['start']>=222 else 0
   if cap['start']-shift>=duration:continue
   kept.append(dict(cap,start=cap['start']-shift,end=min(cap['end']-shift,duration)))
  vtt=final.with_suffix('.vtt');vtt.write_text('WEBVTT\n\n'+'\n\n'.join(stamp(x['start'])+' --> '+stamp(x['end'])+x['settings']+'\n'+'\n'.join(x['lines']) for x in kept)+'\n')
  transcript=final.with_name(final.stem+'_transcript.txt');transcript.write_text('\n\n'.join(' '.join(x['lines']) for x in kept)+'\n');assert not branded(vtt.read_text()) and not branded(transcript.read_text())
  evidencepath=OUT/'evidence'/f"{r['number']:02}.json";evidence.update(final_status='VERIFIED_SCOPED_CORRECTION',full_quality_status='UNVERIFIED',accent_status='UNVERIFIED',deployed=False);evidencepath.write_text(json.dumps(evidence,indent=2)+'\n')
  replacement=dict(mp4=str(final.relative_to(ROOT)),sha256=sha(final),bytes=final.stat().st_size,captions=str(vtt.relative_to(ROOT)),transcript=str(transcript.relative_to(ROOT)),poster=r['poster'],script=str(scriptpath.relative_to(ROOT)),duration=duration,caption_cues=len(kept),audio_duration=float(audio.get('duration',duration)))
  record=dict(number=r['number'],topic=r['topic'],lesson=r['lesson'],section=r['lesson_section'],page=r['page'],type=typ,status='VERIFIED_SCOPED_CORRECTION',original={k:r[k] for k in ['mp4','expected_sha256','expected_bytes','captions','transcript','poster','script']},replacement=replacement,voice=r['voice'],narration_regenerated=False,pitch_speed_changed=False,accent_status='UNVERIFIED',full_quality_status='UNVERIFIED',evidence=str(evidencepath.relative_to(ROOT)),deployment={'status':'READY','url':'https://initsrikanth.github.io/MathMagic/'+replacement['mp4']})
  replacements.append(record);r['correction']=record;r['active_media']=replacement;r['correction_status']='VERIFIED_SCOPED_CORRECTION_READY';r['full_quality_status']='UNVERIFIED';r['accent_status']='UNVERIFIED';r['perceptual_checks_passed']=False
  page=pages.setdefault(r['page'],{'before':(ROOT/r['page']).read_text(),'replacements':[]});matches=[x for x in cards.Cards(page['before']).cards if x[0]==r['lesson_section'] and r['mp4'] in page['before'][x[1]:x[2]]];assert len(matches)==1,(r['number'],matches);section,a,b=matches[0];oldcard=page['before'][a:b];newcard=oldcard.replace(r['mp4'],replacement['mp4']).replace(r['captions'],replacement['captions'])
  # Only the video card transcript is changed; lesson prose, controls and layout are preserved byte-for-byte.
  newcard=re.sub(r'(<details[^>]*>\s*<summary[^>]*>.*?</summary>).*?(</details>)',lambda m:m[1]+''.join('<p>'+html.escape(' '.join(x['lines']))+'</p>' for x in kept)+m[2],newcard,flags=re.S)
  page['replacements'].append((a,b,newcard));backups.append(dict(number=r['number'],page=r['page'],section=section,card=oldcard,original=record['original']))
  # Existing strict media manifests remain authoritative, with explicit scoped rather than full-quality status.
  manifest=r['manifest'];batch=batches.setdefault(manifest,json.loads((ROOT/manifest).read_text()));ls=batch['lessons'];entry=next((x for x in ls if x.get('section')==r['lesson_section']),None);assert entry is not None,(manifest,r['lesson_section']);entry['original_release']=copy.deepcopy(entry)
  entry.update(src=replacement['mp4'],captions=replacement['captions'],transcript=replacement['transcript'],bytes=replacement['bytes'],sha256=replacement['sha256'],duration=duration,narration_duration=replacement['audio_duration'],caption_cues=len(kept),status='verified_scoped_correction',verification_scope=typ,full_quality_status='UNVERIFIED',accent_status='UNVERIFIED',correction_record=r['number'],correction_evidence=record['evidence'])
 for name,page in pages.items():
  after=page['before']
  for a,b,value in sorted(page['replacements'],reverse=True):after=after[:a]+value+after[b:]
  def stripped(s):
   for section,a,b in sorted(cards.Cards(s).cards,key=lambda x:x[1],reverse=True):s=s[:a]+f'[PLAYER:{section}]'+s[b:]
   return s
  assert stripped(after)==stripped(page['before']),name+' non-player content changed';(ROOT/name).write_text(after)
 for name,batch in batches.items():(ROOT/name).write_text(json.dumps(batch,indent=2,ensure_ascii=False)+'\n')
 assert len(replacements)==32 and sum(x['type']=='branding_only' for x in replacements)==30
 (OUT/'release.json').write_text(json.dumps(dict(schema=1,authorisation='Founder explicitly authorises objectively verified branding-only and independent mathematical/visual corrections without waiting for unrelated accent review.',scope='32 scoped corrections, all35 core lessons retained',full_quality_status='UNVERIFIED',new_topic_production='SUSPENDED',replacements=replacements),indent=2)+'\n');(OUT/'rollback.json').write_text(json.dumps({'base_commit':'26ea21a58568d798e17232a7582c9e765f565f15','original_files_preserved':True,'players':backups},indent=2)+'\n');REGISTER.write_text(json.dumps(db,indent=2,ensure_ascii=False)+'\n');print('Integrated32 scoped corrections;30branding,2models; all originals and non-player lesson bytes preserved.')
if __name__=='__main__':main()
