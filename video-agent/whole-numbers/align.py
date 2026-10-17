"""Actual provider word clock or local two-pass acoustic alignment; never estimate speech timing."""
import json,re,subprocess,sys
from pathlib import Path
sys.path.insert(0,'/workspace/work/audio-tools')
from pocketsphinx import Decoder
ROOT=Path(__file__).parent
norm=lambda s:re.findall(r'[a-z0-9]+',s.lower())
def acoustic(source,script):
 pcm=subprocess.check_output(['ffmpeg','-v','error','-i',str(source),'-map','0:a:0','-f','s16le','-ar','16000','-ac','1','pipe:1'])
 # Analysis-only trailing context helps the aligner retain the last word.
 # This buffer is never written to narration or passed to the compositor.
 pcm=pcm+b'\0'*32000
 dec=Decoder(samprate=16000,loglevel='ERROR');words=norm(script)
 for w in set(words):
  if dec.lookup_word(w)is None:
   custom={'hundredths':'HH AH N D R AH D TH S','thousandths':'TH AW Z AH N D TH S','tenths':'T EH N TH S'}
   assert w in custom,('Missing pronunciation',w);dec.add_word(w,custom[w],update=True)
 dec.set_align_text(' '.join(words));dec.start_utt();dec.process_raw(pcm,full_utt=True);dec.end_utt();dec.set_alignment();dec.start_utt();dec.process_raw(pcm,full_utt=True);dec.end_utt()
 result=[dict(word=re.sub(r'\(\d+\)$','',w.name),start=w.start/100,end=(w.start+w.duration)/100)for w in dec.get_alignment()if not w.name.startswith(('<','[','+'))]
 if [x['word']for x in result]!=words:
  import difflib
  diff=list(difflib.SequenceMatcher(a=words,b=[x['word']for x in result]).get_opcodes());print('Alignment token differences',[(tag,words[a:b],[x['word']for x in result[c:d]])for tag,a,b,c,d in diff if tag!='equal'],flush=True)
  (ROOT/'qa'/'alignment-diagnostic.json').write_text(json.dumps(result,indent=2))
  raise ValueError('Incomplete alignment')
 return result

def main():
 lessons=json.loads((ROOT/'lessons.json').read_text())
 for p in lessons:
  source=ROOT/'sources'/f'{p["id"]}-original.{"mp4"if p["method"]=="avatar"else"mp3"}'
  if not source.exists():continue
  script=(ROOT/f'{p["id"]}.txt').read_text();file=ROOT/'sources'/f'{p["id"]}-words.json'
  if p['method']=='speech':
   data=json.loads(file.read_text());ws=[]
   for x in data['word_timestamps']:
    if x['word'].startswith('<'):continue
    parts=norm(x['word']);assert len(parts)==1,(x,parts)
    ws.append(dict(word=parts[0],start=x['start'],end=x['end']))
   assert [x['word']for x in ws]==norm(script),'Provider narration mismatches script'
   method='actual HeyGen word timestamps'
  else:
   cached=ROOT/'sources'/f'{p["id"]}-acoustic.json'
   if not cached.exists():cached.write_text(json.dumps(acoustic(source,script),indent=2))
   ws=json.loads(cached.read_text());method='PocketSphinx 5.0.4 two-pass acoustic alignment'
  offset=0;boards=[]
  for sc in p['scenes']:
   tokens=norm(sc['narration']);part=ws[offset:offset+len(tokens)];assert [w['word']for w in part]==tokens
   events=[]
   for row in sc['rows']:
    cue=norm(row['cue']);idx=next(k for k in range(len(tokens))if tokens[k:k+len(cue)]==cue)
    events.append({**row,'at':part[idx]['start']})
   boards.append({**sc,'start':part[0]['start'],'speech_end':part[-1]['end'],'events':events});offset+=len(tokens)
  probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(source)]));duration=float(probe['format']['duration'])
  for i,b in enumerate(boards):b['end']=boards[i+1]['start']if i+1<len(boards)else duration
  report=dict(lesson=p['id'],method=method,words=ws,boards=boards,duration=duration,source=str(source),all_script_words_verified=True)
  (ROOT/'sources'/f'{p["id"]}-alignment.json').write_text(json.dumps(report,indent=2)+'\n')
  print(p['id'],len(ws),'words;',duration,'seconds;',method,flush=True)
if __name__=='__main__':main()
