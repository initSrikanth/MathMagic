"""Normalise copied-prefix movie edits to the verified frame-count duration; no payload re-encoding."""
from pathlib import Path
import struct,math,json,subprocess,hashlib,sys
from brand_only_candidates import packets

def normalise(path,duration):
 p=Path(path);tmp=p.with_name(p.stem+'-timing.mp4');before={s:packets(p,s) for s in ['v:0','a:0']};old_sha=hashlib.sha256(p.read_bytes()).hexdigest()
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(p),'-map','0','-c','copy','-movflags','+faststart+negative_cts_offsets',str(tmp)],check=True)
 b=bytearray(tmp.read_bytes());scale=None;changes=[]
 def walk(start,end):
  nonlocal scale
  at=start
  while at+8<=end:
   size,typ=struct.unpack_from('>I4s',b,at);header=8
   if size==1:size=struct.unpack_from('>Q',b,at+8)[0];header=16
   if not size:size=end-at
   q=at+header;version=b[q]
   if typ==b'mvhd':scale=struct.unpack_from('>I',b,q+(20 if version else 12))[0]
   offset=None
   if typ==b'mvhd':offset=q+(24 if version else 16)
   elif typ==b'tkhd':offset=q+(28 if version else 20)
   elif typ==b'elst':
    assert struct.unpack_from('>I',b,q+4)[0]==1,'Only a single continuous prefix edit is supported';offset=q+8
   if offset is not None:
    fmt='>Q' if version else '>I';old=struct.unpack_from(fmt,b,offset)[0];new=min(old,math.ceil(duration*scale-1e-8))
    if old!=new:struct.pack_into(fmt,b,offset,new);changes.append({'box':typ.decode(),'old_ticks':old,'new_ticks':new,'timescale':scale})
   if typ in [b'moov',b'trak',b'mdia',b'edts']:walk(q,at+size)
   at+=size
 walk(0,len(b));assert changes;tmp.write_bytes(b)
 for s in before:assert packets(tmp,s)==before[s],'Encoded audio/video packet identity changed'
 dec=subprocess.run(['ffmpeg','-v','error','-i',str(tmp),'-f','null','-'],capture_output=True,text=True,check=True);assert not dec.stderr.strip(),dec.stderr
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-of','json',str(tmp)]));assert abs(float(probe['format']['duration'])-duration)<.002
 tmp.replace(p)  # Atomic replacement also preserves any hardlinked cache copy.
 return {'old_sha256':old_sha,'new_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'edits':changes,'all_h264_and_aac_packet_payloads_unchanged':True,'full_decode':True,'target_duration':duration,'reason':'WebKit used movie/edit-list duration while Chromium/ffprobe used frame-count duration. Normalise the movie window without encoding, stretching or changing narration.'}
if __name__=='__main__':
 root=Path(__file__).resolve().parents[2];rel=root/'video-agent/video-corrections-35/release.json';m=json.loads(rel.read_text());db=json.loads((root/'docs/video-quality-audit-35.json').read_text())
 for c in m['replacements']:
  if c['number'] not in [34,35]:continue
  p=root/c['replacement']['mp4'];existing=json.loads((root/c['evidence']).read_text())
  if existing.get('metadata_timing_correction') and hashlib.sha256(p.read_bytes()).hexdigest()==c['replacement']['sha256']:print('Existing timing correction preserved',c['number']);continue
  proof=normalise(p,c['replacement']['duration']);c['replacement']['sha256']=proof['new_sha256'];c['replacement']['bytes']=p.stat().st_size;e=root/c['evidence'];ev=json.loads(e.read_text());ev['metadata_timing_correction']=proof;ev['sha256']=proof['new_sha256'];ev['bytes']=p.stat().st_size;ev.pop('scoped_qa',None);e.write_text(json.dumps(ev,indent=2)+'\n')
  r=db['records'][c['number']-1];r['correction']=c;r['active_media']=c['replacement'];manifest=root/r['manifest'];batch=json.loads(manifest.read_text());l=next(x for x in batch['lessons'] if x['section']==r['lesson_section']);l['sha256']=proof['new_sha256'];l['bytes']=p.stat().st_size;manifest.write_text(json.dumps(batch,indent=2,ensure_ascii=False)+'\n');print('Metadata normalised',c['number'],'all encoded audio/video packets preserved')
 rel.write_text(json.dumps(m,indent=2)+'\n');(root/'docs/video-quality-audit-35.json').write_text(json.dumps(db,indent=2,ensure_ascii=False)+'\n')
