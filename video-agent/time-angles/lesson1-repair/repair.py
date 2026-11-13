"""PR59 Lesson 1 correction candidate; no synthesis, publication or other lesson edits.

Run from any directory. Requires existing FFmpeg, numpy and Pillow only.
Reuses exact decoded source speech, recovered acoustic word times and the existing
clock primitives. All cuts use the source's natural pauses, at 30fps/48kHz boundaries.
Original media and historical evidence are immutable. Full perceptual QA is pending.
"""
import ast
import contextlib
import copy
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import textwrap
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SOURCE = ROOT / 'videos/MathMagic_Time_Angles_01_Reading_Time_and_Duration_EXTENDED.mp4'
OUT = ROOT / 'videos/Time_Angles_01_Reading_Time_and_Duration_REPAIRED.mp4'
HISTORY = ROOT / 'video-agent/time-angles/accessibility/lesson1-historical.json'
FPS, SR = 30, 48000
BG, INK, TEAL, ORANGE = '#FFF9EE', '#17354D', '#00747C', '#A64C08'
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
W, H = 1920, 1080
# Repeated half-past demonstration, repeated duration/comparison explanations,
# and the redundant branded final challenge. All core methods/examples remain.
OMIT = {17, 18, 19, 23, 28, 36}

def run(args):
    return subprocess.check_output(list(map(str, args)), stderr=subprocess.PIPE)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def stamp(t):
    ms = round(t * 1000)
    return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02}.{ms%1000:03}'

def primitives():
    # Parse only proven graphics helpers; never import a synthesis entry point.
    tree = ast.parse((ROOT/'video-agent/time-angles/render_video1.py').read_text())
    funcs = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in ('font', 'txt', 'clock', 'timefmt')]
    ns = dict(math=math, ImageFont=ImageFont, FONT=FONT, INK=INK, TEAL=TEAL, ORANGE=ORANGE)
    exec(compile(ast.Module(body=funcs, type_ignores=[]), '<existing-clock-primitives>', 'exec'), ns)
    return ns['clock']

CLOCK = primitives()

def txt(d, text, x, y, size=48, colour=INK):
    d.text((x, y), text, font=ImageFont.truetype(FONT, size), fill=colour, anchor='mm')

def word_at(u, phrase):
    wanted = re.findall(r"[a-z]+(?:'[a-z]+)?", phrase.lower())
    words = u['words']
    for j in range(len(words)-len(wanted)+1):
        if [w['word'] for w in words[j:j+len(wanted)]] == wanted:
            return words[j]['start']
    raise ValueError('Missing acoustic cue: '+phrase)

def board(i, u, beat, t):
    role, _, kind, *args = beat
    im = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(im)
    txt(d, 'READING TIME AND DURATION', 960, 210, 44)
    title = {'hook':'The mystery of the bus journey', 'introduction':'Today we are learning…',
             'goal':'Our learning goal', 'criteria':'Three things you can do',
             'question':'Your turn — think first', 'prediction':'Think before calculating',
             'answer':'Reveal and explain', 'misconception':'Spot the mistake', 'recap':'What have we learned?'}.get(role, "Let's investigate")
    txt(d, title, 960, 292, 58)
    if role in ('goal', 'criteria'):
        rows = ['Read time accurately', 'Find how much time passes', 'Explain with clocks and timelines'] if role=='goal' else ['Read the hour and minute hands', 'Calculate across an hour', 'Check using a timeline']
        triggers = ['read time', 'calculate elapsed', 'explain'] if role=='goal' else ['read the hour', 'calculate a duration', 'check your answer']
        for j,(label,trigger) in enumerate(zip(rows,triggers)):
            if t >= word_at(u, trigger): txt(d, f'{j+1}.  {label}', 960, 460+j*145, 57, TEAL)
    elif kind=='conversion':
        # No arrow between unrelated times or noon/midnight. Answers are withheld
        # in the 14:20 prediction; revealed only in the following answer beat.
        rows = {
            13:[('9:15 am', '09:15', 'Morning'), ('3:40 pm', '15:40', 'Afternoon')],
            14:[('3:40 pm', '15:40', '3 + 12 = 15; minutes stay 40')],
            29:[('14:20', '?', 'What is the 12-hour time?')],
            30:[('14:20', '2:20 pm', '14 − 12 = 2; minutes stay 20')],
            31:[('12:00 noon', '12:00', 'Midday'), ('12:00 midnight', '00:00', 'Start of a new day')],
        }[i]
        for j,(left,right,label) in enumerate(rows):
            y = 490+j*260 if len(rows)>1 else 580
            txt(d,left,520,y,72,TEAL); txt(d,'=',960,y,70)
            reveal = i not in (13,14,30,31) or t >= word_at(u, {13:'written zero',14:'equals fifteen',30:'equals two',31:'twelve hundred'}[i])
            if i==13 and j==1: reveal=t>=word_at(u,'written fifteen')
            if i==31 and j==1: reveal=t>=word_at(u,'zero hundred')
            txt(d,right if reveal else '…',1400,y,72,ORANGE)
            txt(d,label,960,y+100,42)
        if i==31: txt(d,'Noon and midnight are 12 hours apart.',960,980,43)
    elif kind=='clock':
        h,m=args; CLOCK(d,960,650,280,h,m,1)
        # Digital answer hidden when the task is to read the hands.
        if i!=6: txt(d,f'{h:02}:{m:02}',960,990,60,TEAL)
        if i==6: txt(d,'What time do the hands show?',960,990,47)
        if i in (4,5,7,20,21,22):
            highlight='Minute hand' if i in (4,7,20) else 'Hour hand'
            txt(d,highlight,360 if highlight=='Minute hand' else 1540,450,40,TEAL)
    else:
        h1,m1,h2,m2=args; start=h1*60+m1; end=h2*60+m2
        if kind=='journey' and i not in (11,12,35):
            CLOCK(d,510,640,210,h1,m1,1); CLOCK(d,1410,640,210,h2,m2,1)
            for x,h,m,label in ((510,h1,m1,'Departure'),(1410,h2,m2,'Arrival')):
                txt(d,f'{h:02}:{m:02}',x,920,54,TEAL); txt(d,label,x,975,35)
        else:
            x0,x1,y=260,1660,650; mid=min((start//60+1)*60,end)
            xpos=lambda minute:x0+(x1-x0)*(minute-start)/(end-start)
            marks=[start]+([mid] if mid<end else [])+[end]
            d.line((x0,y,x1,y),fill='#CADBDE',width=12)
            for minute in marks:
                x=xpos(minute); d.ellipse((x-13,y-13,x+13,y+13),fill=INK)
                # A five-minute last jump occupies only 140px. Stagger its
                # endpoint label so 10:00 and 10:05 cannot touch on a phone.
                stagger=minute==end and len(marks)>2 and xpos(end)-xpos(mid)<220
                if stagger:d.line((x,y+20,x,y+120),fill=INK,width=3)
                txt(d,f'{minute//60:02}:{minute%60:02}',x,y+(155 if stagger else 85),47)
            # Explicit segment counts follow the actual recorded explanation.
            reveal = role in ('answer','recap') or i in (11,24)
            if reveal:
                parts=[(start,mid,TEAL)]+([(mid,end,ORANGE)] if mid<end else [])
                for j,(a,b,col) in enumerate(parts):
                    phrase = {10:'Forty-five minutes',11:'another five',16:'Another ten',24:'Then travel',26:'another ten',33:'another twenty'}.get(i)
                    onset=u['words'][0]['start'] if j==0 else (word_at(u,phrase) if phrase else u['words'][0]['start'])
                    if i==11 and j==0: onset=u['words'][0]['start']
                    p=max(0,min(1,(t-onset)/1.0))
                    if p:
                        d.line((xpos(a),y,xpos(a)+(xpos(b)-xpos(a))*p,y),fill=col,width=16)
                        if p>=1: txt(d,f'+{b-a} min',(xpos(a)+xpos(b))/2,y-95,46,col)
                if role in ('answer','recap') or i==11:
                    phrase={11:'equals fifty',16:'total is fifty',26:'equals forty',33:'equals forty'}.get(i)
                    onset=word_at(u,phrase) if phrase else u['words'][0]['start']+1
                    if t>=onset:txt(d,f'{mid-start}'+(f' + {end-mid}' if mid<end else '')+f' = {end-start} minutes',960,900,65,TEAL)
            elif role in ('question','prediction'):txt(d,'Draw your jumps. How many minutes?',960,900,46)
            elif role=='misconception':txt(d,'Cross the hour; count both parts.',960,900,48)
    return im

def make_cues(utterances, duration):
    cues=[];flags=[]
    for i,u in enumerate(utterances):
        original=list(re.finditer(r"[A-Za-z]+(?:'[A-Za-z]+)?[^A-Za-z]*",u['text']))
        words=u['words']; assert len(words)==len(original)
        group=0
        for j in range(len(words)):
            visible=''.join(m[0] for m in original[group:j+1]).strip()
            next_len=len(visible)+(len(original[j+1][0]) if j+1<len(words) else 0)
            punctuation=bool(re.search(r'[.!?;:]\s*$',original[j][0]))
            if j==len(words)-1 or next_len>76 or (punctuation and j-group>=3) or words[j]['end']-words[group]['start']>4.5:
                a=words[group]['start'];b=min(duration, words[j]['end']+.18,words[j+1]['start'] if j+1<len(words) else u['speech_end']+.25)
                c=dict(start=round(a,3),end=round(b,3),text=visible,utterance=i,first_word=group,last_word=j);cues.append(c)
                if len(visible)/(b-a)>17:flags.append(dict(cue=len(cues),flag='reading_speed_over_17_cps',cps=round(len(visible)/(b-a),1)))
                if b-a<.8:flags.append(dict(cue=len(cues),flag='under_0.8_seconds'))
                group=j+1
    return cues,flags

def main():
    history=json.loads(HISTORY.read_text());assert sha(SOURCE)==history['video_sha256']
    tree=ast.parse((ROOT/'video-agent/time-angles/render_video1.py').read_text())
    beats=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='BEATS' for t in n.targets))
    original=history['utterances']; segments=[]; utterances=[];elapsed=0
    pcm=np.frombuffer(run(['ffmpeg','-v','error','-i',SOURCE,'-vn','-ac','1','-ar',SR,'-f','f32le','-']),np.float32)
    audio=[]
    cache=ROOT/'work/time-angles-lesson1-repair-cache';cache.mkdir(parents=True,exist_ok=True)
    key=cache/'recipe.json'
    recipe={'renderer':sha(Path(__file__)), 'source':sha(SOURCE), 'alignment':sha(HISTORY),
            'primitives':sha(ROOT/'video-agent/time-angles/render_video1.py')}
    if key.exists():
        assert json.loads(key.read_text())==recipe, 'Stale scratch graphics; remove work/time-angles-lesson1-repair-cache before rerendering changed source.'
    else:key.write_text(json.dumps(recipe,indent=2)+'\n')
    with contextlib.nullcontext(cache) as tmp:
        work=Path(tmp); clips=[]
        for i,u in enumerate(original):
            if i in OMIT:continue
            a=math.floor(u['start']*FPS); b=math.floor((original[i+1]['start'] if i+1<len(original) else history['duration'])*FPS)
            # A cut before an omitted utterance must be INSIDE the natural quiet
            # gap, not at its silence-detector end (which can contain word onset).
            if i+1 in OMIT:b-=6
            ranges=[(a,b)] if i!=1 else [(a,695),(899,b)] # 23.1667–29.9667: measured near-zero sentence boundaries.
            local=[]
            for first,last in ranges:
                p,q=first/FPS,last/FPS;length=(last-first)/FPS; offset=elapsed-p
                words=[dict(w,start=round(w['start']+offset,6),end=round(w['end']+offset,6)) for w in u['words'] if p<=w['start'] and w['end']<=q+.02]
                assert words
                # Exact samples; no speed/pitch effects, crossfade, gain or inserted silence.
                audio.append(pcm[first*(SR//FPS):last*(SR//FPS)].copy())
                segments.append(dict(source_utterance=i,source_start=p,source_end=q,output_start=elapsed,output_end=elapsed+length))
                local.extend(words);elapsed+=length
            v=copy.deepcopy(u);v['start']=segments[-len(ranges)]['output_start'];v['speech_end']=local[-1]['end'];v['words']=local
            if i==1:v['text']='Today we are learning how to read time and calculate duration. By the end, you will be able to solve our bus mystery yourself.'
            utterances.append(v)
            # Generate only necessary replacement graphics, retaining clock/journey
            # source models in the other scenes; no narrator/model download needed.
            repair=beats[i][2] in ('timeline','conversion') or i in (2,3,6,11,12,35)
            framefiles=[];dur=sum((y-x)/FPS for x,y in ranges)
            if repair:
                # 10fps semantic animation; duplicate frames to the delivery 30fps.
                nframes=round(dur*FPS)
                for f in range(0,nframes,3):
                    t=u['start']+f/FPS
                    path=work/f'{i:02}-{f:05}.png'
                    if not path.exists():board(i,u,beats[i],t).save(path)
                    framefiles.append((path,min(3,nframes-f)/FPS))
            else:
                path=work/f'{i:02}-source.png'
                if not path.exists():
                    run(['ffmpeg','-v','error','-y','-ss',u['start']+1,'-i',SOURCE,'-frames:v','1',path])
                    im=Image.open(path).convert('RGB');d=ImageDraw.Draw(im)
                    # Proven branding is entirely in this otherwise empty band.
                    d.rectangle((0,0,W,165),fill=BG);im.save(path)
                framefiles=[(path,dur)]
            listing=work/f'{i:02}.txt';listing.write_text(''.join(f"file '{p}'\nduration {d:.9f}\n" for p,d in framefiles)+f"file '{framefiles[-1][0]}'\n")
            clip=work/f'{i:02}.mp4'
            cached_frames=0
            if clip.exists():
                try:cached_frames=int(run(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=nb_frames','-of','csv=p=0',clip]).strip())
                except (ValueError,subprocess.CalledProcessError):pass
            if cached_frames!=round(dur*FPS):
                run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',listing,'-vf','fps=30,format=yuv420p','-frames:v',round(dur*FPS),'-c:v','libx264','-threads','2','-preset','veryfast','-crf','21',clip])
            clips.append(clip); print(f'Lesson 1 scene {i}: {dur:.2f}s; graphics '+('corrected' if repair else 'source model reused'),flush=True)
        expected=np.concatenate(audio);assert len(expected)==round(elapsed*SR)
        wav=work/'speech.wav'
        with wave.open(str(wav),'wb') as f:
            f.setnchannels(1);f.setsampwidth(2);f.setframerate(SR);f.writeframes((np.clip(expected,-1,1)*32767).astype('<i2').tobytes())
        listing=work/'clips.txt';listing.write_text(''.join(f"file '{p}'\n" for p in clips))
        run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',listing,'-i',wav,'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','160k','-movflags','+faststart','-t',elapsed,OUT])
    cues,flags=make_cues(utterances,elapsed)
    transcript=OUT.with_name(OUT.stem+'_transcript.txt');transcript.write_text('\n\n'.join(u['text'] for u in utterances)+'\n')
    captions=OUT.with_suffix('.vtt');captions.write_text('WEBVTT\n\n'+'\n\n'.join(f'{i}\n{stamp(c["start"])} --> {stamp(c["end"])} line:1% position:50% size:90%\n'+textwrap.fill(c['text'],42,break_long_words=False,break_on_hyphens=False) for i,c in enumerate(cues,1))+'\n')
    run(['ffmpeg','-v','error','-y','-ss','1','-i',OUT,'-frames:v','1','-q:v','2',OUT.with_suffix('.jpg')])
    alignment=dict(schema=1,video=str(OUT.relative_to(ROOT)),video_sha256=sha(OUT),script=str(Path(__file__).relative_to(ROOT)),script_sha256=sha(Path(__file__)),
                   wording_source=str(HISTORY.relative_to(ROOT)),captions=str(captions.relative_to(ROOT)),captions_sha256=sha(captions),transcript=str(transcript.relative_to(ROOT)),transcript_sha256=sha(transcript),
                   method='Exact 30fps/48kHz source cuts; retained PocketSphinx acoustic word times shifted by the exact retained-sample offsets. No interpolated word timing.',
                   limitations='Source recognition and alignment are imperfect. Full listening, speech fidelity, accent, temporal visual quality and mobile readability remain unverified.',
                   listening_review='not_performed',status='ALIGNED_REVIEW_REQUIRED',duration=elapsed,utterances=utterances,cues=cues,review_flags=flags)
    (HERE/'alignment.json').write_text(json.dumps(alignment,indent=2)+'\n')
    proof=dict(schema=1,source=str(SOURCE.relative_to(ROOT)),source_sha256=sha(SOURCE),candidate=str(OUT.relative_to(ROOT)),candidate_sha256=sha(OUT),
               duration=elapsed,segments=segments,omitted_source_utterances=sorted(OMIT),internal_cut=[695/FPS,899/FPS],
               narration_regenerated=False,pitch_speed_changed=False,inserted_silence=False,voice='preserved original Kokoro hf_alpha / speaker 31 recording',
               exact_retained_float_pcm_sha256=hashlib.sha256(expected.tobytes()).hexdigest(),full_quality_status='UNVERIFIED',accent_status='UNVERIFIED',release_ready=False)
    (HERE/'edit.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(f'Rendered Lesson 1 candidate: {elapsed:.3f}s; {len(cues)} cues; {len(flags)} readability flags. NOT RELEASE APPROVAL.')

if __name__=='__main__':main()
