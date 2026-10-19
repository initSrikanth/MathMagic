"""Bounded media verification and frame review sheets for the five new films."""
import argparse
import json
import math
import subprocess
from pathlib import Path
from difflib import SequenceMatcher
import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw
from lessons import LESSONS
from produce import maths, digest, HERE, REPO, save

def capture(args): return subprocess.check_output(list(map(str,args)))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--work-dir',type=Path,required=True)
    ap.add_argument('--asr-dir',type=Path,required=True)
    ap.add_argument('--only',choices=[l['id'] for l in LESSONS]); args=ap.parse_args()
    import sherpa_onnx
    recognizer=sherpa_onnx.OfflineRecognizer.from_nemo_ctc(
        str(args.asr_dir/'model.int8.onnx'),str(args.asr_dir/'tokens.txt'),num_threads=1)
    report=HERE/'media-verification.json'
    evidence=json.loads(report.read_text()) if report.exists() else {}
    review=args.work_dir/'review';review.mkdir(exist_ok=True)
    for l in LESSONS:
        if args.only and args.only!=l['id']: continue
        p=REPO/'videos'/(l['file']+'.mp4')
        if evidence.get(l['id'],{}).get('sha256')==digest(p):
            print(f'REUSE verified {l["id"]}',flush=True);continue
        meta=json.loads(capture(['ffprobe','-v','error','-show_format','-show_streams','-of','json',p]))
        v=next(s for s in meta['streams'] if s['codec_type']=='video')
        a=next(s for s in meta['streams'] if s['codec_type']=='audio')
        assert (v['width'],v['height'],v['codec_name'],v['pix_fmt'])==(1920,1080,'h264','yuv420p')
        assert a['codec_name']=='aac' and v['avg_frame_rate']=='30/1'
        subprocess.run(['ffmpeg','-hide_banner','-v','error','-xerror','-i',str(p),'-f','null','-'],check=True)
        pcm=np.frombuffer(capture(['ffmpeg','-v','error','-i',p,'-vn','-ac','1','-ar','22050','-f','f32le','-']),dtype=np.float32)
        rms=20*math.log10(float(np.sqrt(np.mean(pcm**2))))
        peak=float(np.max(np.abs(pcm)))
        assert rms>-35 and peak>.1 and float(np.mean(np.abs(pcm)>.999))<.001
        timeline=json.loads((args.work_dir/l['id']/'timeline.json').read_text()); cues=timeline['cues']
        assert abs(float(v['duration'])-timeline['duration'])<.1
        speech=[]
        for i in [0,len(cues)//2,len(cues)-1]:
            cue=cues[i]; start=int(cue['start']*22050);end=int(cue['end']*22050)
            stream=recognizer.create_stream();stream.accept_waveform(22050,pcm[start:end]);recognizer.decode_stream(stream)
            text=stream.result.text
            score=SequenceMatcher(None,cue['text'].lower(),text.lower()).ratio()
            assert score>.45, f'Check narration {l["id"]} cue {i}: {text}'
            speech.append(dict(cue=i,expected=cue['text'],recognised=text,similarity=score))
        sheet=Image.new('RGB',(1920,math.ceil(len(cues)/4)*292),'#0D172B'); draw=ImageDraw.Draw(sheet)
        for i,cue in enumerate(cues):
            frame=review/f'{l["id"]}-{i:02}.jpg'
            t=min(cue['start']+2.1,cue['end']-.2)
            subprocess.run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',str(p),'-frames:v','1','-vf','scale=480:270',str(frame)],check=True)
            x=(i%4)*480;y=(i//4)*292
            sheet.paste(Image.open(frame),(x,y));draw.text((x+8,y+272),f'{i+1:02} | {cue["chapter"]}',fill='white')
        sheet.save(review/(l['id']+'-contact.jpg'),quality=94)
        evidence[l['id']]=dict(path=str(p.relative_to(REPO)),sha256=digest(p),bytes=p.stat().st_size,
            duration=float(v['duration']),dimensions=[1920,1080],fps=30,video='H.264 yuv420p',audio='AAC',
            audio_rms_dbfs=rms,audio_peak=peak,decode='complete, no errors',speech_samples=speech,
            frame_samples=len(cues),alignment='Measured cue sample boundaries; visual changes within one video frame',
            human_listening_review=False)
        print(f'PASS {l["id"]}: {v["duration"]}s, {rms:.1f} dBFS, speech recognised, full decode',flush=True)
        save(HERE/'media-verification.json',evidence)
    print(maths())

if __name__=='__main__': main()
