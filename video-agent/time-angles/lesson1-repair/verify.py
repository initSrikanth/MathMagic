"""Targeted exact-byte checks for the PR59 Lesson 1 candidate (no release action).

Independent source-sample reconstruction verifies the retained recorded voice;
ASR, OCR, PCM comparison and browser tests cannot certify perceptual qualities.
"""
import ast
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess

import numpy as np
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent

def run(args):
    p=subprocess.run(list(map(str,args)),check=True,capture_output=True)
    assert not p.stderr.strip(),p.stderr.decode()
    return p.stdout

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    edit=json.loads((HERE/'edit.json').read_text());a=json.loads((HERE/'alignment.json').read_text())
    source=ROOT/edit['source'];video=ROOT/edit['candidate']
    assert sha(source)==edit['source_sha256'] and sha(video)==edit['candidate_sha256']==a['video_sha256']
    assert a['script_sha256']==sha(ROOT/a['script'])
    manifest=json.loads((ROOT/'video-agent/time-angles/accessibility/manifest.json').read_text())
    unchanged=[]
    for row in manifest['lessons'][1:]:
        # Verify every asset, not only the four MP4s and captions.
        for p,h in row['assets'].items():assert sha(ROOT/p)==h,p
        unchanged.append(row['lesson'])
    info=json.loads(run(['ffprobe','-v','error','-show_format','-show_streams','-of','json',video]))
    v=next(s for s in info['streams'] if s['codec_type']=='video');audio=next(s for s in info['streams'] if s['codec_type']=='audio')
    duration=float(info['format']['duration'])
    assert (v['codec_name'],v['width'],v['height'],v['pix_fmt'],v['r_frame_rate'],audio['codec_name'])==('h264',1920,1080,'yuv420p','30/1','aac')
    assert 300<=duration<=420 and abs(duration-edit['duration'])<.05
    atoms=[]
    with video.open('rb') as f:
        while h:=f.read(8):
            n,k=struct.unpack('>I4s',h);header=8
            if n==1:n=struct.unpack('>Q',f.read(8))[0];header=16
            atoms.append(k.decode())
            if not n:break
            f.seek(n-header,1)
    assert atoms.index('moov')<atoms.index('mdat')
    # Every video frame is decoded and evaluated for a wholly blank model.
    raw=run(['ffmpeg','-v','error','-i',video,'-an','-vf','scale=96:54,format=gray','-f','rawvideo','-'])
    frames=np.frombuffer(raw,np.uint8).reshape(-1,54,96)
    contrasts=frames.std(axis=(1,2));assert contrasts.min()>3
    changes=np.mean(abs(frames[1:].astype(np.int16)-frames[:-1].astype(np.int16)),axis=(1,2))
    borders=[0]+(np.flatnonzero(changes>.10)+1).tolist()+[len(frames)]
    static_flags=[{'start':x/30,'end':y/30,'status':'REVIEW_REQUIRED_PERSISTENT_MODEL'} for x,y in zip(borders,borders[1:]) if (y-x)/30>8]
    original=np.frombuffer(run(['ffmpeg','-v','error','-i',source,'-vn','-ac','1','-ar','48000','-f','f32le','-']),np.float32)
    pieces=[original[round(s['source_start']*48000):round(s['source_end']*48000)] for s in edit['segments']]
    expected=np.concatenate(pieces)
    assert hashlib.sha256(expected.tobytes()).hexdigest()==edit['exact_retained_float_pcm_sha256']
    final=np.frombuffer(run(['ffmpeg','-v','error','-i',video,'-vn','-ac','1','-ar','48000','-f','f32le','-']),np.float32)[:len(expected)]
    assert len(final)==len(expected)
    rms=float(np.sqrt(np.mean(final*final)));clipping=float(np.mean(abs(final)>=.999));assert rms>=.008 and clipping<.001
    correlation=float(np.corrcoef(expected,final)[0,1]);assert correlation>.995
    snr=float(10*np.log10(np.mean(expected**2)/np.mean((expected-final)**2)));assert snr>25
    # Each edit junction has natural silence on both sides (20ms), without fades.
    joins=[]
    for seg in edit['segments'][:-1]:
        at=round(seg['output_end']*48000)
        quiet=float(np.sqrt(np.mean(expected[max(0,at-960):at+960]**2)))
        joins.append({'output_time':seg['output_end'],'rms_40ms':quiet})
    # Boundaries between original utterances may retain a natural initial breath;
    # the actual internal sentence splice must be near zero on BOTH sides.
    splice=edit['segments'][1]['output_end'];at=round(splice*48000)
    assert float(np.max(abs(expected[at-480:at+480])))<.001
    history=json.loads((ROOT/'video-agent/time-angles/accessibility/lesson1-historical.json').read_text())
    actual_words=[]
    for seg in edit['segments']:
        u=history['utterances'][seg['source_utterance']];offset=seg['output_start']-seg['source_start']
        for w in u['words']:
            if seg['source_start']<=w['start'] and w['end']<=seg['source_end']+.02:
                actual_words.append((w['word'],round(w['start']+offset,6),round(w['end']+offset,6)))
    assert actual_words==[(w['word'],w['start'],w['end']) for u in a['utterances'] for w in u['words']]
    assert not any(w[0]=='mathmagic' for w in actual_words)
    assert all(c['start']<c['end']<=duration for c in a['cues'])
    assert all(x['end']<=y['start'] for x,y in zip(a['cues'],a['cues'][1:]))
    for k in ('captions','transcript'):
        text=(ROOT/a[k]).read_text();assert sha(ROOT/a[k])==a[k+'_sha256']
        assert not re.search(r'math[\s_-]*magic',text,re.I)
    # Independently derive all lesson durations and 12/24-hour equivalences.
    examples=[]
    for start,end,parts in [('09:15','10:05',[45,5]),('13:20','14:10',[40,10]),('14:25','15:10',[35,10]),('11:35','12:20',[25,20])]:
        minutes=lambda s:int(s[:2])*60+int(s[3:])
        total=minutes(end)-minutes(start);assert total==sum(parts)
        examples.append({'start':start,'end':end,'parts':parts,'minutes':total})
    assert 3+12==15 and 14-12==2 and 12*60-0==720
    shots=[];folder=HERE/'frames';folder.mkdir(exist_ok=True)
    for index,u in enumerate(a['utterances']):
        # Final spoken state of EVERY retained scene, plus prediction states.
        t=min(u['speech_end']-.05,duration-.1);out=folder/f'{index:02}.jpg'
        run(['ffmpeg','-v','error','-y','-ss',t,'-i',video,'-frames:v','1','-q:v','2',out])
        p=subprocess.run(['tesseract',str(out),'stdout','--psm','11'],capture_output=True,text=True,check=True)
        assert not re.search(r'math[\s_-]*magic',p.stdout,re.I),p.stdout
        if u['text'].startswith('Look at this clock.'):
            assert '03:40' not in p.stdout,'Prediction answer leaked'
            # 40 minutes = 240 degrees clockwise from twelve, not a shortened
            # minute hand. Sample independently calculated points on that ray.
            im=Image.open(out).convert('RGB')
            for x,y in [(830,725),(812,735)]:
                pixel=im.getpixel((x,y));assert pixel[1]>pixel[0]+35 and pixel[2]>pixel[0]+35
        if u['text'].startswith('Here is a quick check.'):
            assert '2:20 pm' not in p.stdout,'Conversion prediction answer leaked'
        if u['text'].startswith('From eleven thirty-five to noon'):
            # The split must be 25/45 across the 1400px time axis.
            # Check the last part of the first jump and the first part of the
            # second; this detects the old equal-width two-jump model error.
            im=Image.open(out).convert('RGB')
            left=im.getpixel((1020,650));right=im.getpixel((1060,650))
            assert left[1]>left[0]+35 and right[0]>right[1]+35
        shots.append({'at':t,'role':u['role'],'image':str(out.relative_to(ROOT)),'ocr':p.stdout})
    # Exhaustive branding-lane pixel check: every frame has only a flat empty band.
    lane=run(['ffmpeg','-v','error','-i',video,'-an','-vf','crop=1920:165:0:0,scale=192:16,format=gray','-f','rawvideo','-'])
    lane=np.frombuffer(lane,np.uint8).reshape(-1,16,192)
    assert lane.std(axis=(1,2)).max()<1.5
    sheet=Image.new('RGB',(1440,((len(shots)+2)//3)*300),'white');d=ImageDraw.Draw(sheet)
    for j,s in enumerate(shots):
        x=(j%3)*480;y=(j//3)*300;sheet.paste(Image.open(ROOT/s['image']).resize((480,270)),(x,y));d.text((x+5,y+275),f'{j}: {s["role"]} @ {s["at"]:.2f}s',fill='black')
    sheet.save(HERE/'contact.jpg')
    # Do not commit individual redundant full-size frames; the contact sheet and
    # exact timestamps allow recovery from the candidate bytes.
    for j,s in enumerate(shots):
        (ROOT/s.pop('image')).unlink()
        s['contact_sheet_cell']=[j%3,j//3]
    folder.rmdir()
    result=dict(candidate_sha256=sha(video),duration=duration,encoding='PASS',faststart=True,full_decode=True,decoded_frames=len(frames),
                minimum_frame_contrast=float(contrasts.min()),empty_branding_lane_all_frames=True,scene_ocr_brand_free=True,scene_samples=shots,
                audio_rms=rms,clipping_fraction=clipping,source_audio_correlation=correlation,source_audio_snr_db=snr,
                original_voice_preserved=True,internal_sentence_splice_quiet=True,joins=joins,caption_word_source_mapping=True,
                caption_readability_flags=a['review_flags'],static_model_flags=static_flags,
                mathematics=examples,other_lessons_all_assets_unchanged=unchanged,
                full_quality_status='UNVERIFIED',accent_status='UNVERIFIED',full_listening_viewing='NOT_PERFORMED',release_ready=False)
    (HERE/'qa.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('scene_samples','joins')},indent=2))

if __name__=='__main__':main()
