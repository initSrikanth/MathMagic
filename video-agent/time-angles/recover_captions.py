"""Recover sidecars from preserved MP4 audio; never import/execute a renderer.
Optional regeneration: pocketsphinx==5.0.4 (free local acoustic alignment), FFmpeg.
The scripts supply wording, NOT timestamps or independent proof of speech fidelity.
Listening remains mandatory; no synthesis, media edits or paid calls occur here.
"""
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess
import textwrap

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'video-agent/time-angles/accessibility'
TOKEN = re.compile(r"[a-z]+(?:'[a-z]+)?")

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def beats(path):
    return next(ast.literal_eval(n.value) for n in ast.parse(path.read_text()).body
                if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'BEATS' for t in n.targets))

def stamp(t):
    ms = round(t * 1000)
    return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02}.{ms%1000:03}'

def recover(n):
    from pocketsphinx import Decoder
    script = ROOT / f'video-agent/time-angles/render_video{n}.py'
    src = next(p for p in (ROOT/'videos').glob(f'MathMagic_Time_Angles_0{n}_*.mp4') if ('EXTENDED' in p.name) == (n == 1))
    script_beats = beats(script)
    blocked = n == 1
    if blocked:
        # GitHub history plus both independent ASRs identify the actual historical
        # wording. The current renderer script is NOT the published video's script.
        historical = subprocess.check_output(['git','show','c4d27ce^:video-agent/time-angles/render_video1.py'],cwd=ROOT,text=True)
        script_beats = next(ast.literal_eval(x.value) for x in ast.parse(historical).body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='BEATS' for t in x.targets))
    # Inspect AUDIO ONLY; do not wastefully decode or re-encode preserved video.
    command = ['ffmpeg', '-hide_banner', '-i', str(src), '-vn', '-af', 'silencedetect=noise=-42dB:d=0.65', '-f', 'null', '-']
    detection = subprocess.run(command, check=True, capture_output=True, text=True).stderr
    gaps = [(float(e)-float(d), float(e)) for e,d in re.findall(r'silence_end: ([\d.]+) \| silence_duration: ([\d.]+)', detection)]
    assert len(gaps) == len(script_beats), 'Ambiguous utterance recovery; stop rather than estimate timings'
    assert all(0.9 < e-s < 1.5 or 4.9 < e-s < 5.5 for s,e in gaps[:-1]), 'Unexpected pause structure'
    raw = subprocess.check_output(['ffmpeg','-v','error','-i',str(src),'-vn','-ar','16000','-ac','1','-f','s16le','-'])
    duration = len(raw)/32000
    decoder = Decoder(lm=None, logfn='/dev/null')
    # CMU phoneme pronunciations for the four curriculum words absent in its bundled dictionary.
    for word, phones in {'protractor':'P R OW T R AE K T ER','protractors':'P R OW T R AE K T ER Z',
                         'anticlockwise':'AE N T IY K L AA K W AY Z','skateboarder':'S K EY T B AO R D ER','mathmagic':'M AE TH M AE JH IH K'}.items():
        decoder.add_word(word, phones, update=True)
    utterances = []; cues = []; flags = []
    for i, beat in enumerate(script_beats):
        start = gaps[i-1][1] if i else 0.0
        end = gaps[i][0]
        text = beat[1]
        tokens = TOKEN.findall(text.lower())
        assert all(decoder.lookup_word(w) for w in tokens), 'Missing pronunciation; no fabricated alignment'
        decoder.set_align_text(' '.join(tokens))
        decoder.start_utt(); decoder.process_raw(raw[round(start*16000)*2:round((end+0.15)*16000)*2], full_utt=True); decoder.end_utt()
        assert decoder.hyp() is not None, f'No alignment: lesson {n} utterance {i} {start}-{end}: {text}'
        segments = [s for s in decoder.seg() if not s.word.startswith('<')]
        assert [re.sub(r'\(\d+\)$','',s.word) for s in segments] == tokens, f'Alignment incomplete: {n}/{i}'
        words = [{'word':w, 'start':round(start+s.start_frame/100,3), 'end':round(start+(s.end_frame+1)/100,3)} for w,s in zip(tokens,segments)]
        assert all(w['end']>w['start'] for w in words)
        utterances.append({'role':beat[0], 'text':text, 'start':round(start,3), 'speech_end':round(end,3), 'words':words})
        # Preserve original punctuation/case. Split only on aligned words; no equal-time interpolation.
        original = list(re.finditer(r"[A-Za-z]+(?:'[A-Za-z]+)?[^A-Za-z]*", text))
        assert len(original) == len(words)
        group = 0
        for j in range(len(words)):
            visible = ''.join(m[0] for m in original[group:j+1]).strip()
            punctuation = bool(re.search(r'[.!?;:]\s*$', original[j][0]))
            next_len = len(visible) + (len(original[j+1][0]) if j+1 < len(words) else 0)
            if j == len(words)-1 or next_len > 76 or (punctuation and j-group >= 3) or words[j]['end']-words[group]['start'] > 4.5:
                a = words[group]['start']; b = min(duration, words[j]['end']+0.18, words[j+1]['start'] if j+1<len(words) else end+0.25)
                cue = {'start':a,'end':round(b,3),'text':visible,'utterance':i,'first_word':group,'last_word':j}
                cues.append(cue)
                if len(visible)/(b-a) > 17: flags.append({'cue':len(cues), 'flag':'reading_speed_over_17_cps','cps':round(len(visible)/(b-a),1)})
                if b-a < 0.8: flags.append({'cue':len(cues),'flag':'under_0.8_seconds'})
                group = j+1
    assert all(0 <= c['start'] < c['end'] <= duration for c in cues)
    assert all(a['end'] <= b['start'] for a,b in zip(cues,cues[1:]))
    stem = src.with_suffix('')
    transcript = OUT/'lesson1-historical-transcript.txt' if blocked else stem.with_name(stem.name+'_transcript.txt')
    vtt = OUT/'lesson1-historical-captions.vtt' if blocked else src.with_suffix('.vtt')
    transcript.write_text('\n\n'.join(b[1] for b in script_beats)+'\n')
    vtt.write_text('WEBVTT\n\n'+'\n\n'.join(f'{i}\n{stamp(c["start"])} --> {stamp(c["end"])}\n'+textwrap.fill(c['text'],width=42,break_long_words=False,break_on_hyphens=False) for i,c in enumerate(cues,1))+'\n')
    info = {'schema':1,'video':str(src.relative_to(ROOT)),'video_sha256':sha(src),'script':str(script.relative_to(ROOT)), 'script_sha256':sha(script), 'wording_source':'c4d27ce^:video-agent/time-angles/render_video1.py' if blocked else str(script.relative_to(ROOT)),
            'captions':str(vtt.relative_to(ROOT)),'captions_sha256':sha(vtt),'transcript':str(transcript.relative_to(ROOT)),'transcript_sha256':sha(transcript),
            'method':'Actual decoded audio silence boundaries plus PocketSphinx 5.0.4 CMU-en-US acoustic forced word alignment of saved renderer wording; 10ms frame resolution.',
            'limitations':'Forced alignment does not independently transcribe or prove words were spoken. Accent, speech fidelity and ambiguous spans require exact-video listening. No synthesis or video modification.',
            'listening_review':'not_performed','status':'BLOCKED_BRANDED_SOURCE' if blocked else 'ALIGNED_REVIEW_REQUIRED','duration':duration,'utterances':utterances,'cues':cues,'review_flags':flags}
    OUT.mkdir(exist_ok=True)
    (OUT/(f'lesson{n}-historical.json' if blocked else f'lesson{n}.json')).write_text(json.dumps(info,indent=2)+'\n')
    print(f'Lesson {n}: {len(utterances)} audio-bound utterances, {len(cues)} cues, {len(flags)} reading flags; listening NOT performed',flush=True)

if __name__ == '__main__':
    for n in range(1,6): recover(n)
