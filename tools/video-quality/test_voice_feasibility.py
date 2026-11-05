"""One no-cost local feasibility probe; does not approve an accent or replace any lesson narration."""
import sys,json,time,hashlib,resource,importlib.metadata
from pathlib import Path
import numpy as np,soundfile as sf,sherpa_onnx
from contract import ROOT,load,assert_generation_allowed
OUT=ROOT/'video-agent/video-corrections-35/voice';MODEL=Path('/workspace/voice-calibration/kokoro-multi-lang-v1_0')
def main():
 OUT.mkdir(exist_ok=True);wav=OUT/'hf-alpha-feasibility.wav';meta=OUT/'feasibility.json'
 if wav.exists() and meta.exists():assert hashlib.sha256(wav.read_bytes()).hexdigest()==json.loads(meta.read_text())['audio_sha256'];print('Existing feasibility probe preserved');return
 text="Could one big multiplication become three smaller facts? Let's investigate! Three hundred and twenty-four times eight can be split into three hundred, twenty, and four, each multiplied by eight. Which part would you try first? Great thinking: every part matters."
 c=load();voice=c['approved_voice'];assert_generation_allowed('remediation_candidate',[{'topic':'multiplication-division','text':text}],voice)
 assert hashlib.sha256((MODEL/'model.onnx').read_bytes()).hexdigest()==voice['model_sha256'];assert hashlib.sha256((MODEL/'voices.bin').read_bytes()).hexdigest()==voice['voices_sha256'];licence=(MODEL/'LICENSE').read_text();assert 'Apache License' in licence and 'Version 2.0' in licence
 start=time.monotonic();tts=sherpa_onnx.OfflineTts(sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(kokoro=sherpa_onnx.OfflineTtsKokoroModelConfig(model=str(MODEL/'model.onnx'),voices=str(MODEL/'voices.bin'),tokens=str(MODEL/'tokens.txt'),data_dir=str(MODEL/'espeak-ng-data'),lang='en'),num_threads=2)));ready=time.monotonic();speech=tts.generate(text,sid=31,speed=1.0);runtime=time.monotonic()-ready;audio=np.asarray(speech.samples);gain=min(1.,.96/float(abs(audio).max()));audio=audio*gain;sf.write(wav,audio,speech.sample_rate,subtype='PCM_16');rms=float(np.sqrt(np.mean(audio**2)));clipping=float(np.mean(abs(audio)>=.999));assert rms>.008 and clipping<.001
 f0=[]
 for i in range(0,len(audio)-960,480):
  frame=audio[i:i+960];frame=frame-frame.mean()
  if np.sqrt(np.mean(frame*frame))<.025:continue
  ac=np.correlate(frame,frame,'full')[959:];lo,hi=round(speech.sample_rate/400),round(speech.sample_rate/80);lag=lo+int(np.argmax(ac[lo:hi]));
  if ac[lag]/(ac[0]+1e-12)>.6:f0.append(speech.sample_rate/lag)
 result={'model':voice,'engine':importlib.metadata.version('sherpa-onnx'),'speaker_mapping':'Local generate_voices_bin.py maps31 to hf_alpha; no identity imitation or cloning','licence':'Apache-2.0, actual installed LICENSE inspected','licence_sha256':hashlib.sha256(licence.encode()).hexdigest(),'offline':True,'paid_calls':0,'threads':2,'initialisation_seconds':ready-start,'generation_seconds':runtime,'duration':len(audio)/speech.sample_rate,'peak_process_rss_mib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,'sample_rate':speech.sample_rate,'rms':rms,'clipping_fraction':clipping,'native_speed':1.0,'headroom_gain':gain,'inserted_silence_samples':0,'pitch_or_time_effects':False,'audio_sha256':hashlib.sha256(wav.read_bytes()).hexdigest(),'f0_10_50_90_hz':np.percentile(f0,[10,50,90]).tolist() if f0 else None,'feasibility':'LOCAL_SYNTHESIS_WORKS','accent_status':'UNVERIFIED','expressiveness_status':'UNVERIFIED','limitation':'The same installed hf_alpha profile underlies the owner-praised Measurement narration. Successful synthesis and acoustic variation do not establish perceived Indian-English accent, naturalness or enthusiasm; actual listening remains necessary. No existing lesson voice was replaced.'}
 meta.write_text(json.dumps(result,indent=2)+'\n');(OUT/'transcript.txt').write_text(text+'\n');(OUT/'LICENSE.txt').write_text(licence);print('Local voice feasibility: generated',round(result['duration'],2),'seconds in',round(runtime,2),'seconds; accent UNVERIFIED, zero paid calls.')
if __name__=='__main__':main()
