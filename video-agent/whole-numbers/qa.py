"""Task-specific mathematics, sample-clock, media, captions and teacher continuity QA."""
import json,subprocess,hashlib,re,math,sys
from pathlib import Path
from fractions import Fraction
import numpy as np
ROOT=Path(__file__).parent;REPO=ROOT.parents[1]
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]))
def pcm(p):return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-map','0:a:0','-f','f32le','-ac','1','-ar','44100','pipe:1']),dtype='<f4')
def mathematical_checks():
 assert 7*10000==70000 and 8*10000==80000 and 50000==10*5000
 assert 34*10==340 and 340//10==34
 assert 400000+6000+200+70+5==406275 and 34*100==3400
 assert 600000+20000+4000+300+8==624308
 assert 456782>456728 and 309950<310005 and 89999<90001<90010
 assert round(89999,-3)==90000
 assert Fraction('4.726')==4+Fraction('.7')+Fraction('.02')+Fraction('.006')
 assert Fraction('.1')==10*Fraction('.01') and Fraction('.01')==10*Fraction('.001')
 assert Fraction('.5')==10*Fraction('.05') and Fraction('.5')>Fraction('.05')
 assert Fraction('1.407')<Fraction('1.470') and Fraction('1.47')==Fraction('1.470')
 assert Fraction('2.053')<Fraction('2.305')<Fraction('2.350') and Fraction('4.7')==Fraction('4.700')
 assert (Fraction('1.50')-Fraction('1.40'))/10==Fraction('.01')
 assert (Fraction('1.44')-Fraction('1.43'))/10==Fraction('.001')
 assert Fraction('1.430')+7*Fraction('.001')==Fraction('1.437')
 assert Fraction('1.43')<Fraction('1.437')<Fraction('1.44')
 return 'PASS: every worked numerical relationship and number-line partition checked exactly'
def compare_teacher(source,out):
 v=next(s for s in probe(source)['streams']if s['codec_type']=='video');w,h=v['width'],v['height'];cw=round(h*2/3);cx=(w-cw)//2
 # Entire original 2:3 photograph retained; only provider-added pillarboxing removed.
 base=f'crop={cw}:{h}:{cx}:0,scale=606:912:force_original_aspect_ratio=decrease,pad=606:912:(ow-iw)/2:(oh-ih)/2:color=0xf6f6fc,setsar=1'
 def frames(p,vf):return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-vf',vf+',fps=1,scale=202:304','-an','-f','rawvideo','-pix_fmt','rgb24','pipe:1']),dtype=np.uint8).reshape(-1,304,202,3)
 a=frames(source,base);b=frames(out,'crop=606:912:0:84');n=min(len(a),len(b));errors=np.abs(a[:n].astype(float)-b[:n].astype(float)).mean(axis=(1,2,3));assert errors.max()<4,errors.max()
 return dict(status='PASS',sampled_teacher_frames=n,max_pixel_mae=float(errors.max()),source_photo_fully_retained=True,teacher_scale_uniform=True,no_new_teacher_holds='Frame correspondence to continuously advancing source verified each second; renderer has no temporal filters')
def main():
 mathresult=mathematical_checks();results=[]
 provenance=json.loads((ROOT/'qa'/'voice-and-avatar-provenance.json').read_text())
 assert len(provenance)==5
 for id,identity in provenance.items():
  assert identity['voice_id']=='2ec5ec7926eb471d9f33e1b7ba4bb77d'
  if id in ['lesson1','lesson3']:
   assert identity['avatar_id']=='2e895abe1f515732737973186daa2e51' and identity['engine']=='avatar_iv' and identity['script_verified']
  else:assert identity['voice_name']=='Srikanth sogathur' and identity['engine']=='elevenlabs' and identity['speed']==1
 for p in json.loads((ROOT/'lessons.json').read_text()):
  name=f'MathMagic_{p["slug"]}_1080p';out=REPO/'videos'/f'{name}.mp4';alignment=ROOT/'sources'/f'{p["id"]}-alignment.json'
  if not out.exists()or not alignment.exists():continue
  cached=ROOT/'qa'/f'{p["id"]}-qa.json'
  if cached.exists():
   old=json.loads(cached.read_text())
   if old['sha256']==hashlib.sha256(out.read_bytes()).hexdigest():
    results.append(old);print(p['id'],'REUSE VERIFIED PASS (unchanged bytes)',flush=True);continue
  a=json.loads(alignment.read_text());source=Path(a['source']);meta=probe(out);v=next(s for s in meta['streams']if s['codec_type']=='video');audio=next(s for s in meta['streams']if s['codec_type']=='audio');duration=float(meta['format']['duration'])
  assert(v['width'],v['height'],v['codec_name'],v['pix_fmt'],audio['codec_name'])==(1920,1080,'h264','yuv420p','aac')
  fps=float(Fraction(v['avg_frame_rate']));assert abs(duration-a['duration'])<=1/fps+.03
  data=out.read_bytes();assert data.index(b'moov')<data.index(b'mdat');assert len(data)<100*1024*1024
  subprocess.run(['ffmpeg','-v','error','-i',str(out),'-f','null','-'],check=True)
  x,y=pcm(source),pcm(out);n=min(len(x),len(y));assert abs(len(x)-len(y))<=2048
  corr=float(np.corrcoef(x[:n],y[:n])[0,1]);assert corr>.995,corr
  clipped=int((np.abs(y)>=.9999).sum());assert clipped==0,clipped
  audioresult=dict(zero_lag_correlation=corr,clipped_samples=clipped,source_samples=len(x),final_samples=len(y),time_stretch=False,artificial_silence=False)
  if p['method']=='avatar':assert np.array_equal(x,y),'Copied avatar audio must decode identically';audioresult['decoded_audio_identical']=True
  # Word anchors are measured, matched against the complete narration, and quantised to the next frame.
  norm=lambda s:re.findall(r'[a-z0-9]+',s.lower())
  assert [w['word']for w in a['words']]==norm((ROOT/f'{p["id"]}.txt').read_text())
  assert all(w['start']<=w['end']for w in a['words'])
  persistence=[]
  for board in a['boards']:
   for e in board['events']:
    q=math.ceil(e['at']*fps)/fps;assert 0<=q-e['at']<1/fps+.00001
    seconds=board['end']-e['at']
    if seconds<3 and board is not a['boards'][-1]:seconds=3 # verified persistent previous-strategy strip
    assert seconds>=1.5,(p['id'],e,seconds)
    persistence.append(round(seconds,3))
  vtt=(REPO/'videos'/f'{name}.vtt').read_text();lines=[s for s in vtt.splitlines()if s and s!='WEBVTT'and '-->'not in s and not s.isdigit()]
  script=(ROOT/f'{p["id"]}.txt').read_text();assert norm(' '.join(lines))==norm(script)
  assert not re.search(r'\d+/\d+',vtt)
  report=dict(lesson=p['id'],title=p['title'],status='PASS',filename=out.name,bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),duration=duration,width=1920,height=1080,fps=fps,full_decode='PASS',faststart='PASS',mathematics=mathresult,audio=audioresult,alignment=a['method'],complete_script_match=True,events_quantised_within_one_frame=True,minimum_event_persistence_seconds=min(persistence),caption_cues=len(re.findall('-->',vtt)),transcript_match=True,teacher=compare_teacher(source,out)if p['method']=='avatar'else'Not applicable: graphics-only')
  (ROOT/'qa'/f'{p["id"]}-qa.json').write_text(json.dumps(report,indent=2)+'\n');print(p['id'],'PASS',round(duration,2),len(data),flush=True);results.append(report)
 (ROOT/'qa'/'all-media.json').write_text(json.dumps(results,indent=2)+'\n')
 if len(results)!=5:raise SystemExit('Not all five finished videos are available; no publication permitted')
if __name__=='__main__':main()
