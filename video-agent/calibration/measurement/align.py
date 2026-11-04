from pathlib import Path
import json,re,time
import numpy as np,soundfile as sf,sherpa_onnx
from scipy.signal import resample_poly
r=Path(__file__).parent;p=r/'sherpa-onnx-zipformer-small-en-2023-06-26'
t=time.monotonic();rec=sherpa_onnx.OfflineRecognizer.from_transducer(tokens=str(p/'tokens.txt'),encoder=str(p/'encoder-epoch-99-avg-1.int8.onnx'),decoder=str(p/'decoder-epoch-99-avg-1.int8.onnx'),joiner=str(p/'joiner-epoch-99-avg-1.int8.onnx'),num_threads=2)
d=json.loads((r/'timing.json').read_text());allwords=[]
for cue in d['cues']:
 a,sr=sf.read(r/(cue['name']+'.wav'),dtype='float32');s=rec.create_stream();s.accept_waveform(16000,resample_poly(a,2,3));rec.decode_stream(s);res=s.result;words=[]
 for token,timestamp in zip(res.tokens,res.timestamps):
  if token.startswith(('▁',' ')) or not words:words.append(dict(word=token.replace('▁','').strip().lower(),start=cue['start']+timestamp))
  else:words[-1]['word']+=token.lower()
 print(cue['name'],res.text,flush=True);allwords.extend(words)
(r/'words.json').write_text(json.dumps(dict(method='Independent offline Zipformer ASR token emission timestamps; approximate alignment, not human-certified word boundaries',runtime=time.monotonic()-t,words=allwords),indent=2))
# Independent transcript comparison: normalised word edit distance.
expected=re.findall(r"[a-z]+",' '.join(c['text'] for c in d['cues']).lower());observed=re.findall(r"[a-z]+",' '.join(w['word'] for w in allwords));dp=list(range(len(observed)+1))
for i,a in enumerate(expected,1):
 row=[i]
 for j,b in enumerate(observed,1):row.append(min(row[-1]+1,dp[j]+1,dp[j-1]+(a!=b)))
 dp=row
print('WER',dp[-1],len(expected),dp[-1]/len(expected));(r/'asr-qa.json').write_text(json.dumps(dict(word_errors=dp[-1],reference_words=len(expected),word_error_rate=dp[-1]/len(expected),limitations='ASR agreement measures intelligibility, not accent, warmth or subjective naturalness'),indent=2))
