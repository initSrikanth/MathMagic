import json,re,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[2];out=R/'docs/video-quality-audit-35.json';records=[];exceptions=[]
config=[('fractions','fractions.html','video-agent/fractions-graphics-2026/manifest.json'),('whole-numbers','whole-numbers.html','video-agent/year5-graphics-2026/whole-numbers/manifest.json'),('decimals-percentages','decimals-percentages.html','video-agent/production-v2/decimals-release.json'),('addition-subtraction','addition-subtraction.html','video-agent/production-v2/addition-subtraction-release.json'),('multiplication-division','multiplication-division.html','video-agent/production-v2/multiplication-division-release.json'),('factors-multiples','factors-multiples.html','video-agent/production-v2/factors-multiples-release.json'),('measurement','measurement.html','video-agent/production-v2/measurement-release.json')]
legacy=json.loads((R/'video-agent/production-v2/manifest.json').read_text())['lessons'];seen=set()
for topic,page,manifest in config:
 m=json.loads((R/manifest).read_text());h=(R/page).read_text();expected=[]
 assert len(m['lessons'])==5
 for l in m['lessons']:
  src=l['src'];assert src not in seen;seen.add(src);expected.append(src)
  section=re.search(r'<section\b[^>]*id="'+l['section']+r'"[^>]*>(.*?)</section>',h,re.S);assert section and ('src="'+src+'"') in section[1],(topic,l['section'])
  if topic in ['fractions','whole-numbers']:
   base=Path(manifest).parent;sf=base/'scripts.json';scriptall=json.loads((R/sf).read_text());script=next(s for s in scriptall if s.get('slug',s.get('id'))==l['id']);tf=base/'timings'/(l['id']+'.json');producer='video-agent/fractions-graphics-2026/produce.py' if topic=='fractions' else 'video-agent/year5-graphics-2026/produce.py';graphics='video-agent/fractions-graphics-2026/graphics.py' if topic=='fractions' else 'video-agent/year5-graphics-2026/graphics.py';voice=dict(model=m['engine'],name=m['speaker'],speaker_id=m['speaker_id'],note=m['voice_note']);audio=l['audio'];voice['native_rates']=json.loads((R/tf).read_text()).get('rates')
  else:
   sf=Path('video-agent/production-v2/scripts')/(l['id']+('-calibrated' if topic=='measurement' else '')+'.json');script=json.loads((R/sf).read_text());tf=Path('video-agent/production-v2/timings')/(l['id']+'.json');producer='video-agent/production-v2/'+('measurement_quality.py' if topic=='measurement' else 'pipeline.py');graphics='video-agent/production-v2/'+('measurement_graphics.py' if topic=='measurement' else 'graphics.py');voice=m.get('voice') or legacy[l['id']]['voice'];audio=l['source_audio']
  ts=json.loads((R/tf).read_text());beats=script['beats'];brand=[]
  for c in ts['captions']:
   if re.search(r'math\s*magic',c['text'],re.I):brand.append(dict(start=c['start'],end=c['end'],text=c['text'],evidence='Actual-narration caption/source text; audio ASR confirmation pending'))
  status_voice='PASS_CONFIG_ONLY' if voice.get('name')=='hf_alpha' else 'FAIL_CONFIG'
  attributes={k:dict(status='UNVERIFIED',evidence='Requires actual full listening/viewing; automated evidence does not certify this attribute.') for k in ['accent_and_voice_consistency','clarity_expressiveness_pacing','mathematics_and_curriculum','goal_and_three_criteria','constructivist_sequence','examples_and_misconception','prediction_and_thinking_time','animation_progressive_reveals','sentence_and_concept_sync','readability_cognitive_load','caption_accuracy_timing','transcript_accuracy','audio_loudness_clipping_silence_transitions','closing_reflection','published_integrity_mobile_playback','increased_natural_enthusiasm']}
  attributes['spoken_branding']=dict(status='FAIL' if brand else 'UNVERIFIED',evidence=brand)
  attributes['onscreen_branding']=dict(status='UNVERIFIED',evidence='Actual-frame/OCR inspection pending')
  if topic=='measurement':attributes['accent_and_voice_consistency']['evidence']='Owner reports all five current videos have excellent audio delivery; preserve it. New enthusiasm requirement still needs perceptual verification.'
  if topic=='multiplication-division':attributes['accent_and_voice_consistency']=dict(status='FAIL',evidence='Owner reports British accent; actual producer provenance is bf_emma, British female, speaker 7.')
  paths=[src,l['captions'],l['transcript'],l['poster'],str(sf),str(tf),audio,producer,graphics]
  missing=[p for p in paths if not(R/p).is_file()]
  defects=[dict(code='BRAND_IN_NARRATION_CAPTIONS_TRANSCRIPT',start=x['start'],end=x['end'],detail=x['text']) for x in brand]
  if status_voice=='FAIL_CONFIG':defects.append(dict(code='UNAPPROVED_BRITISH_VOICE_PROFILE',start=0,end=l['duration'],detail='bf_emma, speaker 7. Replace narration with approved profile; perceptual review remains mandatory.'))
  rates=voice.get('native_rates');silence=ts.get('pauses',[])
  r=dict(number=len(records)+1,topic=topic,lesson=l['title'],lesson_section=l['section'],page=page,published_url='https://initsrikanth.github.io/MathMagic/'+src,mp4=src,expected_bytes=l['bytes'],expected_sha256=l['sha256'],duration=l['duration'],voice=voice,voice_profile_check=status_voice,manifest=manifest,script=str(sf),script_key=l['id'],timing=str(tf),captions=l['captions'],transcript=l['transcript'],poster=l['poster'],source_audio=audio,producer=producer,graphics_source=graphics,cached_assets_hint={'measurement':'/workspace/measurement-quality-render','multiplication-division':'/workspace/multiplication-render','factors-multiples':'/workspace/factors-render','addition-subtraction':'/workspace/addition-render','decimals-percentages':'/workspace/pr46-render'}.get(topic,'/workspace/fractions-five-work or /workspace/year5-graphics-work'),missing_assets=missing,attributes=attributes,defects=defects,required_correction=['Remove prohibited branding without disturbing satisfactory audio','Use approved female voice where profile is defective','Perceptually verify modest additional enthusiasm without faster/louder speech','Review all mandatory visual/teaching/audio attributes before PASS'],verification_evidence={},final_status='FAIL' if defects or missing else 'UNVERIFIED',release_status='BLOCKED_PERCEPTUAL_REVIEW',scene_count=len(beats))
  records.append(r)
 extras=set(re.findall(r'<source\b[^>]*src="([^"]+)"',h))-set(expected)
 for x in extras:exceptions.append(dict(page=page,src=x,classification='Existing LCM extension, outside the 35 core placements' if 'Finding_LCM' in x else 'UNEXPECTED_PLAYER'))
assert len(records)==len(seen)==35
payload=dict(schema=1,baseline_commit='d31afb5dfae6f87564e0aaddc24c7ccb0af4acf3',scope='Exactly 35 core placements across seven Year 5 topics; approved LCM extension recorded separately',new_topic_development='SUSPENDED',new_video_production='SUSPENDED except scoped remediation after audit',perceptual_review_limitation='No available audio-listening/full-video perceptual tool. ASR, OCR, metadata and image samples cannot certify accent, enthusiasm or full teaching quality.',unexpected_or_extra_placements=exceptions,records=records)
if out.exists():
 previous=json.loads(out.read_text());assert len(previous['records'])==35
 assert {(r['mp4'],r['page'],r['lesson_section']) for r in previous['records']}=={(r['mp4'],r['page'],r['lesson_section']) for r in records}, 'Published placement inventory changed; preserve/review the existing audit before rebasing.'
 print('Existing audit retained; all 35 actual source placements match.')
else:out.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n')
print('35 placements; brand-script violations',sum(bool(r['attributes']['spoken_branding']['evidence']) for r in records),'British-profile mismatches',sum(r['voice_profile_check']=='FAIL_CONFIG' for r in records),'missing assets',sum(len(r['missing_assets']) for r in records),'extras',exceptions)
