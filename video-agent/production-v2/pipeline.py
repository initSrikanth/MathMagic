#!/usr/bin/env python3
"""Resumable, CPU-only production. State is distinct from deployment evidence."""
import argparse
import datetime as dt
import hashlib
import html
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import urllib.request
from content import LESSONS, HERE, ROOT

STATE=HERE/'manifest.json'
UTC=dt.timezone.utc
MODEL_SHA='10ff414106a038ce7e9e0126c6461e4dc8a86efaa89dc91d2009d69fe635e339'
VOICES_SHA='a372c67b056ef0b695c375d39b99630d23fb07ad4c8d87aa32a19a62fca523ad'
SPEED=.84
VOICE_ID=7  # bf_emma, British English female; Kokoro v0.19 upstream mapping.

def now(): return dt.datetime.now(UTC)
def iso(t): return t.isoformat()
def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()
def json_hash(v): return hashlib.sha256(json.dumps(v,sort_keys=True).encode()).hexdigest()
def save(path,v):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+'.tmp'); tmp.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n'); tmp.replace(path)
def command(args,**kwargs): return subprocess.run(list(map(str,args)),check=True,timeout=600,**kwargs)
def git(*args): return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def initial():
    return dict(schema=2,interval_hours=5,last_batch_started=None,next_batch_due=None,active_batch=None,
                last_successful_batch=None,errors=[],limitations=['Local Kokoro bf_emma neural speech; perceived expressiveness and pronunciation have not been human-certified.','Only existing six-topic curriculum is catalogued; no future-year topics are inferred.'],lessons={})
def load(): return json.loads(STATE.read_text()) if STATE.exists() else initial()
def initialise(m):
    assert len(LESSONS)==30 and len({l['id'] for l in LESSONS})==30
    for l in LESSONS:
        page=ROOT/(l['topic']+'.html')
        assert re.search(r'<section\b[^>]*\bid="'+re.escape(l['section'])+'"',page.read_text()), l['id']
        m['lessons'].setdefault(l['id'],dict(topic=l['topic'],lesson=l['title'],section=l['section'],video_filename='videos/'+l['file']+'.mp4',production_status='pending',commit_sha=None,deployment_status='pending',reason='Missing explainer or requested narration/palette/structure revision.'))
    return m

def next_check(value):
    if not value: return None
    due_time=dt.datetime.fromisoformat(value)
    check=due_time.replace(minute=17,second=0,microsecond=0)
    return iso(check if check>=due_time else check+dt.timedelta(hours=1))

def summary(m):
    entries=list(m['lessons'].values()); rendered=sum(e['production_status'] in ['verified','integrated'] for e in entries)
    deployed=sum(e['deployment_status']=='verified_live' for e in entries)
    return dict(total_videos_required=len(entries),videos_successfully_rendered=rendered,videos_committed=sum(bool(e.get('commit_sha')) for e in entries),videos_deployed_and_verified_live=deployed,remaining_videos=len(entries)-deployed,last_successful_batch=m['last_successful_batch'],next_scheduled_batch=next_check(m['next_batch_due']),next_batch_eligible=m['next_batch_due'],errors_or_blockers=m['errors'],limitations=m['limitations'])
def persist(m):
    save(STATE,m); save(HERE/'status.json',summary(m))
    s=summary(m)
    (HERE/'STATUS.md').write_text('# MathMagic production status\n\n'+'\n'.join(f'- {k.replace("_"," ")}: {v}' for k,v in s.items() if k!='limitations')+'\n\nScheduled events may be delayed by GitHub. A due time is an earliest eligible time, not a guaranteed start.\n\n'+'\n'.join('- '+v for v in m['limitations'])+'\n')

def due(m,t=None):
    t=t or now()
    if all(e['deployment_status']=='verified_live' for e in m['lessons'].values()): return False
    return not m.get('next_batch_due') or t>=dt.datetime.fromisoformat(m['next_batch_due'])

def maths():
    # Preserve and execute all original exact-rational fraction checks.
    import importlib.util
    spec=importlib.util.spec_from_file_location('fraction_checks',HERE.parent/'fractions-local/produce.py')
    mod=importlib.util.module_from_spec(spec)
    sys.path.insert(0,str(HERE.parent/'fractions-local')); spec.loader.exec_module(mod); sys.path.pop(0)
    mod.maths()
    from fractions import Fraction as Q
    assert Q(9,4)==2+Q(1,4) and Q(2,3)-Q(1,6)==Q(1,2) and Q(2,3)+Q(1,6)==Q(5,6)
    assert 2786+1457==4243 and 52000-27684==24316 and 406-178==228
    assert 6004-5997==7 and 398+257==655 and 502-498==4
    assert 3876+2142==6018 and 8032-3987==4045 and 4900+1900==6800
    assert 625+275==900 and 800-455==345 and 600-180==420
    assert 1248+375==1623 and 900-675==225 and 820-586==234
    assert 324*8==2592 and 426*7==2982 and 203*4==812
    assert 246*13==3198 and 315*24==7560 and 102*12==1224
    assert 1536==256*6 and 2184==312*7 and 816==204*4
    assert divmod(67,8)==(8,3) and Q(23,4)==Q('5.75') and math.ceil(31/5)==7
    assert 70*24==1680 and 398*21==8358 and 80*18==1440
    assert Q('4.680')>Q('4.607') and Q('.62')>Q('.599') and Q('2.450')>Q('2.405')
    assert Q(1,2)==Q('.5')==Q(50,100) and Q(3,4)==Q('.75') and Q(1,5)==Q('.2')
    assert Q(8,10)>Q(75,100) and 738%6==0 and 1245%5==0 and 1245%9!=0 and 312%4==0
    factors=lambda n:[d for d in range(1,n+1) if n%d==0]
    assert factors(24)==[1,2,3,4,6,8,12,24]
    assert factors(36)==[1,2,3,4,6,9,12,18,36]
    assert factors(40)==[1,2,4,5,8,10,20,40]
    assert set(factors(18))&set(factors(30))=={1,2,3,6}
    for l in LESSONS:
        assert l['beats'][0]['role']=='opening' and l['beats'][-1]['role']=='recap'
        assert any(b.get('pause')==4 and b['role']=='question' for b in l['beats'])
        for b in l['beats']:
            for r in b.get('rows',[]): assert r['d']>0 and 0<=r['n']<=4*r['d']
    return {'exact_arithmetic':'passed','lessons':len(LESSONS),'curriculum_scope':'Existing Year 5 topic boundaries; foundations/extension retained as labelled in lesson text.'}

def vtt_time(t):
    ms=round(t*1000); return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02}.{ms%1000:03}'

def synthesise(l,folder,model,deadline):
    import numpy as np
    import soundfile as sf
    import sherpa_onnx
    assert sha(model/'model.onnx')==MODEL_SHA and sha(model/'voices.bin')==VOICES_SHA
    key=json_hash(dict(lesson=l,voice=VOICE_ID,speed=SPEED,model=MODEL_SHA,format=2))
    timeline=folder/'timeline.json'
    if timeline.exists():
        old=json.loads(timeline.read_text())
        if old.get('input_hash')==key and (folder/'narration.wav').exists() and sha(folder/'narration.wav')==old['narration_sha256']: return old
    tts=sherpa_onnx.OfflineTts(sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(kokoro=sherpa_onnx.OfflineTtsKokoroModelConfig(model=str(model/'model.onnx'),voices=str(model/'voices.bin'),tokens=str(model/'tokens.txt'),data_dir=str(model/'espeak-ng-data')),num_threads=2),max_num_sentences=1))
    assert tts.sample_rate==24000
    sr=24000; samples=[]; total=0; captions=[]; cues=[]; pauses=[]
    for i,b in enumerate(l['beats']):
        start=total/sr
        # Real sentence sample boundaries; no fabricated word timestamps.
        sentences=re.split(r'(?<=[.!?])\s+(?=[A-Z])',b['text'])
        for sentence in sentences:
            if time.monotonic()>deadline: raise TimeoutError('Batch deadline reached during synthesis; cached sentences retained.')
            h=json_hash([sentence,VOICE_ID,SPEED,MODEL_SHA]); wav=folder/(h+'.wav')
            if not wav.exists():
                a=tts.generate(sentence,sid=VOICE_ID,speed=SPEED)
                assert a.sample_rate==sr and len(a.samples)>sr*.15
                temporary=wav.with_suffix('.partial.wav')
                sf.write(temporary,a.samples,sr,subtype='PCM_16'); temporary.replace(wav)
            a,rate=sf.read(wav,dtype='float32'); assert rate==sr
            assert np.sqrt(np.mean(a*a))>.008, f'Quiet narration: {l["id"]}'
            assert np.mean(np.abs(a)>.999)<.001, 'Clipped narration'
            captions.append(dict(start=total/sr,end=(total+len(a))/sr,text=sentence))
            samples.append(a); total+=len(a)
            pause=.65 if sentence.endswith('?') else .22
            if sentence==sentences[-1]: pause=b.get('pause',.65)
            pauses.append([total/sr,total/sr+pause,'think time' if pause==4 else 'sentence pause'])
            pad=np.zeros(round(sr*pause),dtype=np.float32); samples.append(pad); total+=len(pad)
        cues.append(dict(index=i,start=start,end=total/sr,lesson_progress=(i+1)/len(l['beats']),**b))
    narration=folder/'narration.wav'; sf.write(narration,np.concatenate(samples),sr,subtype='PCM_16')
    result=dict(input_hash=key,cues=cues,captions=captions,pauses=pauses,duration=total/sr,narration_sha256=sha(narration),voice='Kokoro v0.19 bf_emma',voice_id=VOICE_ID,speed=SPEED,sample_rate=sr,alignment='Measured PCM sample boundaries of each generated sentence; no word alignment claimed.')
    save(timeline,result)
    return result

def render(l,folder,timeline,deadline):
    from graphics import draw
    clips=[]; render_key=json_hash([timeline['input_hash'],sha(HERE/'graphics.py'),2])
    for i,c in enumerate(timeline['cues']):
        if time.monotonic()>deadline: raise TimeoutError('Batch deadline reached; completed cue clips retained.')
        base=folder/f'cue-{i:02}-{render_key[:12]}'; clip=base.with_suffix('.mp4')
        # Absolute frame boundaries avoid accumulating audio/video drift.
        frames=round(c['end']*30)-round(c['start']*30)
        if not clip.exists():
            frames_dir=folder/f'frames-{i:02}'; frames_dir.mkdir(exist_ok=True)
            concat=[]
            for j in range(9):
                image=frames_dir/f'{j:02}.png'; draw(l,c,image,j/8)
                concat.extend([f"file '{image.as_posix()}'",f'duration {(.1 if j<8 else frames/30-.8):.9f}'])
            concat.append(f"file '{image.as_posix()}'")
            listing=frames_dir/'frames.txt'; listing.write_text('\n'.join(concat)+'\n')
            tmp=base.with_suffix('.partial.mp4')
            command(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',listing,'-vf','fps=30,format=yuv420p','-frames:v',frames,'-c:v','libx264','-preset','veryfast','-crf','23','-threads','2',tmp])
            tmp.replace(clip)
            # Only completed compressed intermediates belong in persisted caches.
            import shutil
            shutil.rmtree(frames_dir)
        clips.append(clip)
        print(f'{l["id"]}: graphics {i+1}/{len(timeline["cues"])}',flush=True)
    listing=folder/'clips.txt'; listing.write_text(''.join(f"file '{p.as_posix()}'\n" for p in clips))
    out=ROOT/'videos'; out.mkdir(exist_ok=True); final=out/(l['file']+'.mp4'); temp=folder/'final.partial.mp4'
    command(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',listing,'-i',folder/'narration.wav','-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','128k','-movflags','+faststart','-metadata','title='+l['title'],temp])
    assert temp.stat().st_size<90*1024**2, 'MP4 exceeds repository file budget'
    temp.replace(final)
    captions=['WEBVTT','']
    for c in timeline['captions']: captions.extend([f'{vtt_time(c["start"])} --> {vtt_time(c["end"])}',c['text'],''])
    (out/(l['file']+'.vtt')).write_text('\n'.join(captions))
    (out/(l['file']+'_transcript.txt')).write_text('\n\n'.join(b['text'] for b in l['beats'])+'\n')
    command(['ffmpeg','-v','error','-y','-ss','2','-i',final,'-frames:v','1','-vf','scale=1280:720',out/(l['file']+'_poster.jpg')])
    return final

def verify(final,timeline,narration):
    import numpy as np
    import soundfile as sf
    info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(final)]))
    v=next(s for s in info['streams'] if s['codec_type']=='video'); a=next(s for s in info['streams'] if s['codec_type']=='audio')
    assert (v['codec_name'],v['width'],v['height'],v['pix_fmt'],v['r_frame_rate'])==('h264',1920,1080,'yuv420p','30/1')
    assert a['codec_name']=='aac' and abs(float(v['duration'])-timeline['duration'])<.10
    command(['ffmpeg','-v','error','-xerror','-i',final,'-f','null','-'],stdout=subprocess.DEVNULL)
    pcm=subprocess.check_output(['ffmpeg','-v','error','-i',str(final),'-vn','-ac','1','-ar','24000','-f','f32le','-'])
    audio=np.frombuffer(pcm,dtype='<f4'); rms=float(np.sqrt(np.mean(audio*audio))); clipping=float(np.mean(np.abs(audio)>.999))
    assert rms>.008 and clipping<.001
    source,rate=sf.read(narration,dtype='float32'); assert rate==24000
    count=min(len(source),len(audio))
    correlation=float(np.corrcoef(source[:count],audio[:count])[0,1])
    assert correlation>.98, 'Encoded audio differs or is shifted from narration'
    # Compare each speech window to original PCM: catches missing, shifted or silent narration.
    for c in timeline['captions']:
        window=audio[round(c['start']*24000):round(c['end']*24000)]
        assert len(window)>0 and np.sqrt(np.mean(window*window))>.008, 'Unexpected silent speech window'
    # Long silence outside deliberate pauses or model sentence-edge breathing is a failure.
    silent=[]
    for i in range(0,len(audio)-2400,2400):
        if np.sqrt(np.mean(audio[i:i+2400]**2))<.001: silent.append(i/24000)
    runs=[]
    for t in silent:
        if runs and abs(t-runs[-1][-1]-.1)<.01: runs[-1].append(t)
        else: runs.append([t])
    for run in runs:
        if len(run)<20: continue
        midpoint=(run[0]+run[-1])*.5
        assert any(s-.4<=midpoint<=e+.4 for s,e,_ in timeline['pauses']), f'Unexpected silence at {midpoint}'
    with open(final,'rb') as f: head=f.read(1024*1024)
    assert b'moov' in head, 'Faststart missing'
    return dict(result='passed',sha256=sha(final),bytes=final.stat().st_size,duration=timeline['duration'],audio_rms=rms,clipping_fraction=clipping,audio_correlation=correlation,full_decode=True,format='1080p H.264/yuv420p 30fps, AAC, faststart',synchronisation='Exact sentence PCM clocks; graphics follow cue boundaries within one video frame.',perceptual_voice_review='Not human-certified')

def wrapper(l):
    stem='videos/'+l['file']; title=html.escape(l['title']); transcript=''.join('<p>'+html.escape(b['text'])+'</p>' for b in l['beats'])
    identity=' id="mathmagic-comparing-video"' if l['id']=='fractions-comparing' else ''
    status='<p id="mathmagic-comparing-status" role="status" hidden></p>' if identity else ''
    return (f'<aside class="video-resource" data-mathmagic-v2="{l["id"]}"><h3>MathMagic: {title}</h3><div class="video-frame">'
            f'<video{identity} controls playsinline preload="metadata" poster="{stem}_poster.jpg" aria-label="MathMagic - {title}" style="width:100%;height:100%;object-fit:contain;background:#FFF9EF">'
            f'<source src="{stem}.mp4" type="video/mp4"><track kind="captions" src="{stem}.vtt" srclang="en-GB" label="English">'
            f'<a href="{stem}.mp4">Open the lesson video</a></video>{status}</div>'
            f'<a href="{stem}.mp4">Open the {title} video</a><details><summary>Read the video transcript</summary>{transcript}</details></aside>')

def integrate(batch,m):
    # Replace only an existing media-resource wrapper in the matching section.
    # If no video exists, insert the new player; preserve every other byte.
    for lesson_id in batch:
        l=next(l for l in LESSONS if l['id']==lesson_id); e=m['lessons'][lesson_id]
        final=ROOT/e['video_filename']; assert e['qa']['sha256']==sha(final)
        page=ROOT/(l['topic']+'.html'); original=page.read_text()
        marker=f'data-mathmagic-v2="{l["id"]}"'
        if marker in original:
            assert 'src="'+e['video_filename']+'"' in original
            e['production_status']='integrated'; continue
        pattern=r'(<section\b[^>]*\bid="'+re.escape(l['section'])+r'"[^>]*>)(.*?)(</section>)'
        match=re.search(pattern,original,re.S); assert match, l['id']
        body=match.group(2); blocks=[]
        for opening in re.finditer(r'<(aside|div)\b[^>]*class="[^"]*\bvideo-resource\b[^"]*"[^>]*>',body):
            tag=opening.group(1); depth=1
            for token in re.finditer(r'</?'+tag+r'\b[^>]*>',body[opening.end():]):
                depth+=-1 if token.group().startswith('</') else 1
                if depth==0:
                    end=opening.end()+token.end()
                    if re.search(r'<(?:video|iframe)\b',body[opening.start():end]): blocks.append((opening.start(),end))
                    break
        assert len(blocks)<=1, 'Ambiguous existing players; integration refused'
        start,end=blocks[0] if blocks else (len(body),len(body))
        insert=wrapper(l)
        newbody=body[:start]+insert+body[end:]
        assert newbody[:start]==body[:start] and newbody[start+len(insert):]==body[end:]
        result=original[:match.start(2)]+newbody+original[match.end(2):]
        page.write_text(result)
        e.update(production_status='integrated',integration=dict(page=page.name,section=l['section'],preserved_original_sha256=hashlib.sha256(original.encode()).hexdigest(),replaced_wrapper_sha256=hashlib.sha256(body[start:end].encode()).hexdigest(),rollback_sha=m['active_batch']['rollback_sha']))


def record_commits(m):
    for e in m['lessons'].values():
        if e['production_status'] in ['verified','integrated'] and not e.get('commit_sha'):
            try:
                tracked=git('ls-files','--',e['video_filename'])
                if tracked and git('status','--porcelain','--',e['video_filename'])=='':
                    e['commit_sha']=git('log','-1','--format=%H','--',e['video_filename'])
            except subprocess.CalledProcessError: pass

def live(m):
    record_commits(m)
    for lesson_id,e in m['lessons'].items():
        if e['production_status']!='integrated' or e['deployment_status']=='verified_live' or not e.get('commit_sha'): continue
        base='https://initsrikanth.github.io/MathMagic/'
        try:
            with urllib.request.urlopen(base+e['topic']+'.html',timeout=60) as r: page=r.read().decode()
            assert f'data-mathmagic-v2="{lesson_id}"' in page and f'src="{e["video_filename"]}"' in page
            h=hashlib.sha256(); size=0
            with urllib.request.urlopen(base+e['video_filename'],timeout=60) as r:
                assert r.status==200 and r.headers.get_content_type() in ['video/mp4','application/octet-stream']
                for chunk in iter(lambda:r.read(1024*1024),b''): h.update(chunk); size+=len(chunk)
            assert h.hexdigest()==e['qa']['sha256'] and size==e['qa']['bytes'], 'Live bytes differ from verified final'
            for suffix in ['.vtt','_transcript.txt','_poster.jpg']:
                with urllib.request.urlopen(base+e['video_filename'][:-4]+suffix,timeout=60) as r: assert r.status==200 and len(r.read())>0
            e.update(deployment_status='verified_live',live_verified_at=iso(now()),live_url=base+e['video_filename'])
            e.pop('deployment_error',None)
        except Exception as ex: e['deployment_error']=f'{type(ex).__name__}: {str(ex) or "Live page or media not available yet"}'
    batch=m.get('active_batch')
    if batch and all(m['lessons'][k]['deployment_status']=='verified_live' for k in batch['lessons']):
        m['last_successful_batch']=dict(id=batch['id'],lessons=batch['lessons'],completed=iso(now())); m['active_batch']=None
    if all(e['deployment_status']=='verified_live' for e in m['lessons'].values()): m['next_batch_due']=None
    m['errors']=[f'{k}: {e[key]}' for k,e in m['lessons'].items() for key in ['error','deployment_error'] if e.get(key)]
    persist(m)
    return not any(e.get('deployment_error') for e in m['lessons'].values())

def batch_run(m,args):
    if not due(m) and not (args.resume_active and m.get('active_batch')): print('No production due.'); return
    started=now(); deadline=time.monotonic()+args.budget_minutes*60
    if not args.resume_active:
        m['last_batch_started']=iso(started); m['next_batch_due']=iso(started+dt.timedelta(hours=5))
    if not m.get('active_batch'):
        pending=[l['id'] for l in LESSONS if m['lessons'][l['id']]['production_status']!='integrated'][:5]
        if not pending:
            print('Rendering complete; live deployment verification remains.'); persist(m); return
        m['active_batch']=dict(id=started.strftime('%Y%m%dT%H%M%SZ'),lessons=pending,started=iso(started),rollback_sha=git('rev-parse','HEAD'))
    from importlib.metadata import version
    import platform
    m['runtime']=dict(python=platform.python_version(),packages={name:version(name) for name in ['sherpa-onnx','soundfile','numpy','Pillow']},ffmpeg=subprocess.check_output(['ffmpeg','-version'],text=True).splitlines()[0])
    persist(m); maths()
    for key in m['active_batch']['lessons']:
        e=m['lessons'][key]
        if e['production_status'] in ['verified','integrated']:
            assert sha(ROOT/e['video_filename'])==e['qa']['sha256'], 'Completed media bytes changed; explicit repair required'
            continue
        l=next(l for l in LESSONS if l['id']==key); folder=args.work_dir/key; folder.mkdir(parents=True,exist_ok=True)
        try:
            # Persist authored script/boards and voice provenance before synthesis.
            save(HERE/'scripts'/(key+'.json'),l)
            e.update(production_status='synthesising',script_sha256=json_hash(l),source_commit_sha=git('rev-parse','HEAD'),source_tree_dirty=bool(git('status','--porcelain')),producer_sha256=sha(HERE/'pipeline.py'),graphics_sha256=sha(HERE/'graphics.py'),voice=dict(model='Kokoro v0.19',name='bf_emma',speaker_id=VOICE_ID,speed=SPEED,model_sha256=MODEL_SHA,licence='Apache-2.0',paid_calls=0))
            persist(m)
            timeline=synthesise(l,folder,args.voice_dir,deadline)
            save(HERE/'timings'/(key+'.json'),timeline)
            e.update(production_status='rendering',duration=timeline['duration'],narration_sha256=timeline['narration_sha256']); persist(m)
            final=render(l,folder,timeline,deadline)
            e.update(qa=verify(final,timeline,folder/'narration.wav'),production_status='verified'); e.pop('error',None)
            persist(m)
        except Exception as ex:
            e['error']=f'{type(ex).__name__}: {ex}'; e['production_status']='incomplete'
            m['errors']=[f'{k}: {v["error"]}' for k,v in m['lessons'].items() if v.get('error')]; persist(m)
            raise
    assert all(m['lessons'][k]['production_status'] in ['verified','integrated'] for k in m['active_batch']['lessons'])
    total=sum(p.stat().st_size for p in (ROOT/'videos').glob('*.mp4'))
    assert total<800*1024**2, 'Repository MP4 budget exceeded; configure external media storage before continuing.'
    integrate(m['active_batch']['lessons'],m); m['errors']=[]; persist(m)


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('action',choices=['init','due','run','verify-live','maths'])
    ap.add_argument('--voice-dir',type=Path,default=Path('work/models/kokoro-en-v0_19'))
    ap.add_argument('--work-dir',type=Path,default=ROOT/'work/production-v2')
    ap.add_argument('--budget-minutes',type=int,default=220)
    ap.add_argument('--resume-active',action='store_true',help='Resume only the already selected batch; never select a new batch early.')
    args=ap.parse_args(); args.work_dir=args.work_dir.resolve(); args.voice_dir=args.voice_dir.resolve()
    if args.action=='maths': print(json.dumps(maths())); return
    lock=None
    if args.action=='run':
        import fcntl
        lockpath=ROOT/'work/production-v2.lock'; lockpath.parent.mkdir(parents=True,exist_ok=True)
        lock=lockpath.open('w')
        try: fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError: raise SystemExit('Another local production process holds the lock.')
    m=initialise(load())
    if args.action=='due': print('true' if due(m) else 'false'); return
    if args.action=='init': persist(m)
    elif args.action=='verify-live': sys.exit(0 if live(m) else 1)
    else:
        try: batch_run(m,args)
        except Exception as ex:
            m['errors']=list(dict.fromkeys(m.get('errors',[])+[f'{type(ex).__name__}: {ex}']))
            persist(m)
            raise
if __name__=='__main__': main()
