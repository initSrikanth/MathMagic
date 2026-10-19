"""Replace just the existing Fractions video resources after all finals exist."""
from pathlib import Path
import hashlib
import html
import json
import re
from lessons import LESSONS

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent

def resources(text):
    result=[]
    for m in re.finditer(r'<div class="video-resource"[^>]*>',text):
        depth=1
        for tag in re.finditer(r'</?div\b[^>]*>',text[m.end():]):
            depth+= -1 if tag.group().startswith('</') else 1
            if depth==0:
                result.append((m.start(),m.end()+tag.end(),text[m.start():m.end()+tag.end()]))
                break
    return result

def main():
    p=ROOT/'fractions.html'; original=p.read_text()
    blocks=resources(original)
    assert len(blocks)==6, 'Expected five core players and the legacy LCM extension'
    core=[b for b in blocks if 'id="mathmagic-lcm-extension"' not in b[2]]
    assert len(core)==5
    replacements=[]
    for lesson,b in zip(LESSONS,core):
        stem='videos/'+lesson['file']; mp4=ROOT/(stem+'.mp4')
        assert mp4.exists() and mp4.read_bytes()[4:8]==b'ftyp'
        assert (ROOT/(stem+'_poster.jpg')).exists()
        prefix=b[2].split('<div class="video-frame">')[0]
        status='<p id="mathmagic-comparing-status" role="status" hidden></p>' if lesson['id']=='comparing' else ''
        transcript=''.join('<p>'+html.escape(c['text'])+'</p>' for c in lesson['beats'])
        player=(f'{prefix}<div class="video-frame"><video id="mathmagic-{lesson["id"]}-video" '
                f'controls playsinline preload="metadata" poster="{stem}_poster.jpg" style="width:100%;height:100%;object-fit:contain;background:#0D172B" '
                f'aria-label="MathMagic - {html.escape(lesson["title"])}">'
                f'<source src="{stem}.mp4" type="video/mp4">'
                f'<track kind="captions" src="{stem}.vtt" srclang="en-AU" label="English">'
                f'Your browser cannot play this video. <a href="{stem}.mp4">Open the lesson video</a>.'
                f'</video>{status}</div><a href="{stem}.mp4" target="_blank" rel="noopener noreferrer">'
                f'Open the {html.escape(lesson["title"])} video ↗</a>'
                f'<small>MathMagic animated explainer • MP4 • English captions available</small>'
                f'<details><summary>Read the video transcript</summary>{transcript}</details></div>')
        replacements.append((b[0],b[1],player))
    old=next(b for b in blocks if 'id="mathmagic-lcm-extension"' in b[2])
    cues=json.loads((HERE/'addsub-timing.json').read_text())
    start=next(c['start'] for c in cues if c['chapter']=='Extension: least common multiple')
    path='videos/'+LESSONS[3]['file']+'.mp4'
    extension=(f'<div class="video-resource" id="mathmagic-lcm-extension">'
        '<h3>Extension: Finding the Lowest Common Multiple (LCM)</h3>'
        '<p>Find shared multiples, rename fractions and add equal-sized parts. '
        'This extension is included in the Adding &amp; Subtracting Fractions video above.</p>'
        f'<a href="{path}#t={start:.2f}" target="_blank" rel="noopener noreferrer">Open the LCM extension chapter ↗</a></div>')
    replacements.append((old[0],old[1],extension))
    final=original
    for start,end,replacement in sorted(replacements,reverse=True): final=final[:start]+replacement+final[end:]
    assert len(re.findall(r'<video\b',final))==5
    assert 'feature/video-production-agent' not in final and 'scrimba.com' not in final
    # Byte-level proof: all content outside the six resource wrappers is untouched.
    stripped_before=original
    for start,end,_ in sorted(replacements,reverse=True): stripped_before=stripped_before[:start]+'__VIDEO_RESOURCE__'+stripped_before[end:]
    stripped_after=final
    for start,end,_ in reversed(resources(final)): stripped_after=stripped_after[:start]+'__VIDEO_RESOURCE__'+stripped_after[end:]
    assert stripped_before==stripped_after
    p.write_text(final)
    proof=dict(preserved_content_sha256=hashlib.sha256(stripped_after.encode()).hexdigest(),
               scope='Only six video-resource wrappers changed; five new players plus an LCM chapter link',
               javascript_css_auth_quizzes_and_lesson_content='unchanged byte for byte')
    (HERE/'integration.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps(proof,indent=2))

if __name__=='__main__': main()
