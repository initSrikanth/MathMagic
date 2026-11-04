"""Register only a validated authorised topic, retaining immutable old media."""
import pathlib as _vq_pathlib, sys as _vq_sys
_vq_root=next(p for p in _vq_pathlib.Path(__file__).resolve().parents if (p/'video-agent/video-production-contract.json').is_file())
_vq_sys.path.insert(0,str(_vq_root/'tools/video-quality'))
from guard import enforce as _vq_enforce
_vq_enforce()
import os,re
from pathlib import Path
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[1];TOPIC=os.environ.get('MATHMAGIC_TOPIC','whole-numbers')
p=ROOT/'tests/external-video-pattern.test.js';s=p.read_text()
if 'const year5Batches=' not in s:
 anchor='const newFractions=new Map(fractionsBatch.lessons.map(l=>[l.src,l]));'
 s=s.replace(anchor,anchor+'''\n// Explicitly authorised, independently verified graphics-only topic replacements.
const year5Batches=[
  ['whole-numbers.html',require('../video-agent/year5-graphics-2026/whole-numbers/manifest.json'),require('../video-agent/year5-graphics-2026/whole-numbers/previous-integrations.json')]
];
for(const [,batch,backup] of year5Batches){
 assert.strictEqual(batch.lessons.length,5);
 for(const [src,expected] of Object.entries(backup.assets)){
  const bytes=fs.readFileSync(src);assert.strictEqual(bytes.length,expected.bytes,'Previous approved media size changed: '+src);
  assert.strictEqual(crypto.createHash('sha256').update(bytes).digest('hex'),expected.sha256,'Previous approved media changed: '+src);
 }
}
const newVerified=new Map([...newFractions,...year5Batches.flatMap(([,batch])=>batch.lessons.map(l=>[l.src,l]))]);''')
 start=s.index('const approvedVideos=new Map([');end=s.index('\n]);',start)+4
 s=s[:start]+'''const approvedVideos=new Map([
  ['videos/MathMagic_Finding_LCM_FINAL_1080p.mp4','videos/MathMagic_Finding_LCM_FINAL_1080p.mp4'],
  ...fractionsBatch.lessons.map(l=>[l.src,l.src]),
  ...year5Batches.flatMap(([,batch])=>batch.lessons.map(l=>[l.src,l.src]))
]);'''+s[end:]
 s=s.replace('if(newFractions.has(src)){const expected=newFractions.get(src);','if(newVerified.has(src)){const expected=newVerified.get(src);')
 anchor="  if(file==='fractions.html'){"
 s=s.replace(anchor,"""  const topicBatch=year5Batches.find(([page])=>page===file);
  if(topicBatch){
   assert.strictEqual(videos.length,5,'Five distinct validated core videos required: '+file);
   for(const expected of topicBatch[1].lessons){
    const section=h.match(new RegExp('<section id="'+expected.section+'"[^>]*>([\\\\s\\\\S]*?)</section>'));
    assert(section&&section[1].includes('src="'+expected.src+'"'),'Wrong lesson video: '+file+' '+expected.section);
   }
  }
"""+anchor)
else:
 entry=f"  ['{TOPIC}.html',require('../video-agent/year5-graphics-2026/{TOPIC}/manifest.json'),require('../video-agent/year5-graphics-2026/{TOPIC}/previous-integrations.json')]"
 assert entry not in s
 s=s.replace('const year5Batches=[','const year5Batches=[\n'+entry+',')
p.write_text(s)
