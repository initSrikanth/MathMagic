"""Audit recovered caption assets, including the explicitly blocked historical video.
Never certifies speech fidelity, accent, teaching quality, production or live services.
"""
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parents[2]
MANIFEST='video-agent/time-angles/accessibility/manifest.json'

def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def tokens(text):return re.findall(r"[a-z]+(?:'[a-z]+)?",text.lower())

def verify():
    m=json.loads((ROOT/MANIFEST).read_text());assert m['schema']==1 and m['scope']=='existing_time_angles_accessibility_only'
    assert len(m['lessons'])==5
    html=(ROOT/'time-angles.html').read_text();result=[]
    for n,row in enumerate(m['lessons'],1):
        assert row['lesson']==n
        for path,expected in row['assets'].items():assert sha(path)==expected,'Changed evidence: '+path
        alignment=json.loads((ROOT/row['alignment']).read_text())
        assert alignment['video_sha256']==sha(row['video']) and alignment['script_sha256']==sha(alignment['script'])
        assert alignment['listening_review']=='not_performed','Machine evidence is not perceptual approval'
        text=(ROOT/alignment['transcript']).read_text();vtt=(ROOT/alignment['captions']).read_text()
        assert tokens(text)==tokens(' '.join(u['text']for u in alignment['utterances']))
        cues=alignment['cues'];assert len(cues)>40
        assert tokens(' '.join(c['text']for c in cues))==tokens(text),'Caption words omitted/repeated'
        media=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(ROOT/row['video'])]))
        duration=float(media['format']['duration']);v=next(s for s in media['streams']if s['codec_type']=='video');a=next(s for s in media['streams']if s['codec_type']=='audio')
        assert(v['width'],v['height'],v['codec_name'],v['pix_fmt'],a['codec_name'])==(1920,1080,'h264','yuv420p','aac')
        assert vtt.startswith('WEBVTT\n\n')
        blocks=vtt.strip().split('\n\n')[1:];assert len(blocks)==len(cues)
        def timestamp(s):
            h,m,s=map(float,s.split(':'));return h*3600+m*60+s
        for i,(block,cue)in enumerate(zip(blocks,cues)):
            lines=block.splitlines();start,end=map(timestamp,lines[1].split(' --> '))
            assert 0<=start<end<=duration+.03
            if i:assert start>=cues[i-1]['end']-.001
            assert abs(start-cue['start'])<.0011 and abs(end-cue['end'])<.0011
            assert tokens(' '.join(lines[2:]))==tokens(cue['text'])
            assert len(lines[2:])<=2 and max(map(len,lines[2:]))<=42
            words=alignment['utterances'][cue['utterance']]['words'];first=words[cue['first_word']];last=words[cue['last_word']]
            assert abs(first['start']-start)<.0011 and last['end']<=end+.0011
        section=re.search(r'<section id="lesson'+str(n)+r'".*?</section>',html,re.S)[0]
        assert 'src="'+row['video']+'"'in section
        branded=bool(re.search(r'math[\s_-]*magic',text+' '+vtt,re.I))
        if row['status']=='BLOCKED_BRANDED_SOURCE':
            assert n==1 and branded
            assert alignment['captions']not in html and alignment['transcript']not in html,'Blocked historical evidence cannot be integrated'
            assert alignment['wording_source']=='c4d27ce^:video-agent/time-angles/render_video1.py'
            assert row['frame_defect_evidence']in row['assets']
        else:
            assert not branded
            assert 'src="'+alignment['captions']+'"'in section and 'href="'+alignment['transcript']+'"'in section
            assert 'Read the transcript'in section
        result.append({'lesson':n,'video':row['video'],'sha256':sha(row['video']),'status':row['status'],'cues':len(cues),'review_flags':len(alignment['review_flags']),'perceptual_status':'UNVERIFIED'})
    return {'lessons':result,'integrated_caption_sets':sum(r['status']=='ALIGNED_REVIEW_REQUIRED'for r in result),
            'blocked_lessons':[r['lesson']for r in result if r['status'].startswith('BLOCKED')],
            'listening_review':'UNVERIFIED','human_review_required':True,'release_ready':False}

if __name__=='__main__':print(json.dumps(verify(),indent=2))
