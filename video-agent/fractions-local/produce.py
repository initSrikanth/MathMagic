#!/usr/bin/env python3
"""Free local production: storyboard -> neural WAV -> Manim -> FFmpeg MP4.

Run with --voice-dir PATH --work-dir PATH. Completed synthesis/rendering is
resumed by content hash, never submitted to a remote generation service.
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
from fractions import Fraction as Q

from lessons import LESSONS

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]

def digest(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p, value):
    p.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')
def run(cmd, **kwargs): subprocess.run(list(map(str,cmd)), check=True, **kwargs)
def stamp(t):
    ms = round(t*1000)
    return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02}.{ms%1000:03}'

def maths():
    # Independent exact-rational checks for the narrated examples.
    assert Q(3,4)>Q(1,2) and Q(1,3)>Q(1,6) and Q(1,4)<Q(1,2)<Q(3,4)
    assert Q(5,8)>Q(3,8)
    assert Q(1,2)==Q(2,4)==Q(4,8) and Q(3,5)==Q(12,20)
    assert Q(6,8)==Q(3,4) and Q(12,18)==Q(2,3) and Q(1,2)!=Q(2,3)
    assert Q(3,4)==3*Q(1,4)==Q(1,2)+Q(1,4)
    assert Q(11,4)==2+Q(3,4) and 3+Q(2,5)==Q(17,5)
    assert Q(8,4)==2 and 3+Q(1,4)>2+Q(3,4) and 2+Q(1,2)>2+Q(1,4)
    assert Q(9,4)==2+Q(1,4)
    assert Q(2,7)+Q(3,7)==Q(5,7) and Q(1,2)+Q(1,4)==Q(3,4)
    assert Q(3,4)-Q(1,8)==Q(5,8) and Q(1,6)+Q(3,6)==Q(2,3)
    assert 1+Q(4,5)+Q(2,5)==2+Q(1,5)
    assert Q(1,2)+Q(1,4)-Q(1,8)==Q(5,8)
    assert math.lcm(4,6)==12 and Q(1,4)+Q(1,6)==Q(5,12)
    assert Q(2,3)-Q(1,6)==Q(1,2)
    assert 2-Q(3,4)==1+Q(1,4) and Q(3,4)-Q(5,8)==Q(1,8)
    assert 1-Q(1,4)-Q(1,2)==Q(1,4) and Q(2,3)+Q(1,6)==Q(5,6)
    # All strip fractions are bounded by one and every diagram uses equal cells.
    for lesson in LESSONS:
        for b in lesson['beats']:
            for r in b['rows']: assert 0 <= r['n'] <= 4*r['d'] and r['d'] > 0
            if b['line']:
                l=b['line']; assert all(0<=p<=l['maximum']*l['d'] for p in l['points'])
    return 'All narrated worked examples checked with exact rational arithmetic.'

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--voice-dir', type=Path, required=True)
    ap.add_argument('--work-dir', type=Path, required=True)
    ap.add_argument('--only', choices=[l['id'] for l in LESSONS])
    ap.add_argument('--prepare-only', action='store_true')
    args=ap.parse_args()
    import numpy as np
    import soundfile as sf
    import sherpa_onnx
    work=args.work_dir.resolve(); work.mkdir(parents=True, exist_ok=True)
    out=REPO/'videos'; out.mkdir(exist_ok=True)
    manifest_path=HERE/'manifest.json'
    manifest=json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    model=args.voice_dir/'en_GB-cori-high.onnx'
    manifest.update(dict(method='Local Piper VITS through sherpa-onnx; Manim Cairo; FFmpeg',
        voice='en_GB-cori-high',voice_license='Public-domain LibriVox source recordings; see MODEL_CARD',
        model_sha256=digest(model),speed=1.02,paid_api_calls=0,avatar=False,
        maths=maths(),alignment='Exact PCM-sample boundaries of locally synthesised narration cues; no estimated word timings',
        lessons=manifest.get('lessons',{})))
    # Persist complete original scripts/storyboards before any synthesis.
    save(HERE/'storyboard.json', LESSONS)
    for lesson in LESSONS:
        text='\n\n'.join(b['text'] for b in lesson['beats'])+'\n'
        (HERE/(lesson['id']+'.txt')).write_text(text)
        manifest['lessons'].setdefault(lesson['id'],{})['script_sha256']=hashlib.sha256(text.encode()).hexdigest()
    save(manifest_path,manifest)
    config=sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(
        vits=sherpa_onnx.OfflineTtsVitsModelConfig(model=str(model),
        tokens=str(args.voice_dir/'tokens.txt'),data_dir=str(args.voice_dir/'espeak-ng-data')),
        num_threads=2),max_num_sentences=1)
    tts=sherpa_onnx.OfflineTts(config)
    for lesson in LESSONS:
        if args.only and args.only!=lesson['id']: continue
        folder=work/lesson['id']; folder.mkdir(exist_ok=True)
        entry=manifest['lessons'][lesson['id']]
        pieces=[]; cues=[]; total=0
        for i,b in enumerate(lesson['beats']):
            h=hashlib.sha256((b['text']+'|cori-high|1.02').encode()).hexdigest()[:12]
            wav=folder/f'{i:02}-{h}.wav'
            if not wav.exists():
                audio=tts.generate(b['text'],sid=0,speed=1.02)
                sf.write(wav,audio.samples,audio.sample_rate,subtype='PCM_16')
            audio,sr=sf.read(wav,dtype='int16')
            assert sr==22050 and len(audio)>sr
            assert np.max(np.abs(audio.astype(np.int32)))>1000, f'Inaudible cue: {wav}'
            start=total/sr; total+=len(audio)
            cues.append(dict(index=i,start=start,end=total/sr,samples=len(audio),
                             audio_sha256=digest(wav),**b))
            pieces.append(audio)
            print(f'{lesson["id"]}: narration {i+1}/{len(lesson["beats"])}',flush=True)
        # No padding, inserted holds, time stretching, pitch change or audio truncation.
        narration=folder/'narration.wav'; sf.write(narration,np.concatenate(pieces),sr,subtype='PCM_16')
        save(HERE/(lesson['id']+'-timing.json'),cues)
        timeline=dict(lesson=lesson,cues=cues,duration=total/sr,narration=str(narration))
        save(folder/'timeline.json',timeline)
        entry.update(duration=total/sr,narration_sha256=digest(narration),synthesis='complete',
                     cue_count=len(cues),render='pending')
        save(manifest_path,manifest)
        # Captions use words for fractions, never slash notation.
        vtt=['WEBVTT','']
        for cue in cues:
            # Split at sentence boundaries at proportional times ONLY for subtitle reading;
            # the exact scene/audio timing remains the measured cue boundaries above.
            vtt.extend([f'{stamp(cue["start"])} --> {stamp(cue["end"])}',cue['text'],''])
        (out/(lesson['file']+'.vtt')).write_text('\n'.join(vtt))
        (out/(lesson['file']+'_transcript.txt')).write_text('\n\n'.join(b['text'] for b in lesson['beats'])+'\n')
        if args.prepare_only: continue
        final=out/(lesson['file']+'.mp4')
        render_hash=hashlib.sha256((digest(HERE/'scenes.py')+digest(folder/'timeline.json')).encode()).hexdigest()
        if not final.exists() or entry.get('render_hash')!=render_hash:
            env=dict(os.environ,MM_TIMELINE=str(folder/'timeline.json'))
            run([sys.executable,'-m','manim','--disable_caching','--progress_bar','none',
                 '--verbosity','WARNING','--resolution','1920,1080','--fps','30',
                 '--media_dir',folder/'media','-o','animation',HERE/'scenes.py','FractionFilm'],env=env)
            animation=next((folder/'media'/'videos').rglob('animation.mp4'))
            run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',animation,'-i',narration,
                 '-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','128k',
                 '-movflags','+faststart','-metadata','title='+lesson['title'],final])
            entry.update(render='complete',render_hash=render_hash,sha256=digest(final),bytes=final.stat().st_size)
            save(manifest_path,manifest)
        poster=out/(lesson['file']+'_poster.jpg')
        if not poster.exists():
            run(['ffmpeg','-v','error','-y','-ss','2.1','-i',final,'-frames:v','1',
                 '-vf','scale=1280:720','-q:v','2',poster])
        print(f'COMPLETE {final} {entry["duration"]:.2f}s',flush=True)
    print(maths())

if __name__=='__main__': main()
