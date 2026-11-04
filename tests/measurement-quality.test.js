// Contract for the founder-approved offline voice calibration and this five-video correction.
const fs=require('fs'),assert=require('assert'),crypto=require('crypto');
const root='video-agent/production-v2/',manifest=require('../'+root+'measurement-quality-manifest.json'),release=require('../'+root+'measurement-release.json'),calibration=require('../video-agent/calibration/measurement/timing.json');
for(const [key,file] of Object.entries({producer:'measurement_quality.py',graphics:'graphics.py',measurement_graphics:'measurement_graphics.py'}))assert.strictEqual(manifest.source_fingerprints[key],crypto.createHash('sha256').update(fs.readFileSync(root+file)).digest('hex'));
assert.strictEqual(manifest.voice.name,'hf_alpha');assert.strictEqual(manifest.voice.speaker_id,31);assert.strictEqual(manifest.voice.model_sha256,calibration.model_sha256);assert.strictEqual(manifest.paid_calls,0);assert.strictEqual(release.lessons.length,5);assert(manifest.integrated);
for(const l of release.lessons){
 const e=manifest.lessons[l.id],t=JSON.parse(fs.readFileSync(root+'timings/'+l.id+'.json'));
 const prior=JSON.parse(fs.readFileSync(root+'scripts/'+l.id+'.json')),current=JSON.parse(fs.readFileSync(root+'scripts/'+l.id+'-calibrated.json'));
 assert.strictEqual(current.beats.length,12);for(let i=0;i<12;i++){assert.deepStrictEqual(current.beats[i].board,prior.beats[i].board,'Mathematical working must stay unchanged');if(current.beats[i].role!=='question')assert.strictEqual(current.beats[i].text,prior.beats[i].text);else{assert(current.beats[i].text.startsWith(prior.beats[i].text));const expected={...current.beats.find(c=>c.role==='answer').model,reveal:false};assert.deepStrictEqual(current.beats[i].model,expected);}}
 assert.strictEqual(e.status,'verified');assert.strictEqual(e.qa.blank_frames,0);assert.strictEqual(e.qa.late_safe_reveals,0,'Unresolved mathematical reveal requires review');assert.strictEqual(e.qa.inserted_silence_samples,0);assert.strictEqual(e.qa.native_mathematical_animation_fps,25);assert(e.qa.audio_correlation>.98);assert.strictEqual(t.inserted_silence_samples,0);assert.strictEqual(t.audio_postprocessing,false);assert.deepStrictEqual(t.pauses,[]);assert.strictEqual(t.cues.length,12);assert(l.src.includes('_V3_'));assert.strictEqual(crypto.createHash('sha256').update(fs.readFileSync(l.src)).digest('hex'),l.sha256);
 for(const c of t.cues){
  assert(c.end>c.start);assert(c.words.length);assert(c.motion_end>c.motion_start);assert(c.words.every(w=>w.start>=c.start&&w.start<c.end));assert(c.board_events.every(e=>e.at>=c.start&&e.at<c.end));
  if(c.role==='question'){assert(c.text.includes('keep your prediction in mind'));assert(c.model,'Prediction needs its actual mathematical model');assert.strictEqual(c.model.reveal,false);}
 }
 assert.strictEqual(t.captions.map(c=>c.text).join(' ').replace(/\s+/g,' '),t.cues.map(c=>c.text).join(' ').replace(/\s+/g,' '));
 assert(t.captions.every((c,i)=>c.start>=0&&c.end>c.start&&c.end<=t.duration+.001&&(!i||c.start>=t.captions[i-1].end-.001)));
}
console.log('PASS: five calibrated voice bundles, protected voice identity, native continuous audio, timed mathematical reveals, prediction models and actual-narration captions.');
