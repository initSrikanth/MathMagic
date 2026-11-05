const fs=require('fs'),assert=require('assert');
const modules=['measurement.html','fractions.html','whole-numbers.html','addition-subtraction.html','decimals-percentages.html','multiplication-division.html','factors-multiples.html'];
const crypto=require('crypto');
// Approved MathMagic replacements count as the same lesson coverage, not extra
// coverage. The LCM extension and two additional Whole Numbers lesson players
// add three resources beyond the original coverage. The other three Whole Numbers
// players replace the removed Math Antics embeds. Keep the 14-resource minimum.
// Five new graphics-only replacements explicitly authorised in this production mission.
const fractionsBatch=require('../video-agent/fractions-graphics-2026/manifest.json');
const correctionRelease=require('../video-agent/video-corrections-35/release.json');
const scopedCorrections=new Map(correctionRelease.replacements.map(c=>[c.replacement.mp4,c]));
const previousMedia=require('../video-agent/fractions-graphics-2026/previous-integrations.json');
assert.strictEqual(fractionsBatch.lessons.length,5);
const newFractions=new Map(fractionsBatch.lessons.map(l=>[l.src,l]));
// Explicitly authorised, independently verified graphics-only topic replacements.
const year5Batches=[
  ['measurement.html',require('../video-agent/production-v2/measurement-release.json'),require('../video-agent/production-v2/measurement-previous-integrations.json')],
  ['factors-multiples.html',require('../video-agent/production-v2/factors-multiples-release.json'),require('../video-agent/production-v2/factors-multiples-previous-integrations.json')],
  ['multiplication-division.html',require('../video-agent/production-v2/multiplication-division-release.json'),require('../video-agent/production-v2/multiplication-division-previous-integrations.json')],
  ['addition-subtraction.html',require('../video-agent/production-v2/addition-subtraction-release.json'),require('../video-agent/production-v2/addition-subtraction-previous-integrations.json')],
  ['decimals-percentages.html',require('../video-agent/production-v2/decimals-release.json'),require('../video-agent/production-v2/decimals-previous-integrations.json')],
  ['whole-numbers.html',require('../video-agent/year5-graphics-2026/whole-numbers/manifest.json'),require('../video-agent/year5-graphics-2026/whole-numbers/previous-integrations.json')]
];
for(const [,batch,backup] of year5Batches){
 assert.strictEqual(batch.lessons.length,5);
 for(const [src,expected] of Object.entries(backup.assets)){
  const bytes=fs.readFileSync(src);assert.strictEqual(bytes.length,expected.bytes,'Previous approved media size changed: '+src);
  assert.strictEqual(crypto.createHash('sha256').update(bytes).digest('hex'),expected.sha256,'Previous approved media changed: '+src);
 }
}
const newVerified=new Map([...newFractions,...year5Batches.flatMap(([,batch])=>batch.lessons.map(l=>[l.src,l]))]);
for(const [src,record] of Object.entries(previousMedia.assets)){
 const bytes=fs.readFileSync(src);assert.strictEqual(bytes.length,record.bytes,'Previous media backup size changed: '+src);
 assert.strictEqual(crypto.createHash('sha256').update(bytes).digest('hex'),record.sha256,'Previous approved media changed: '+src);
}
// Original approved files remain immutable even though the active players changed.
for(const [src,hash] of [
 ['videos/MathMagic_Adding_Subtracting_Fractions_CORRECTED_1080p.mp4','48ef9512c531cc6450ee22048152dad4e6d3ab757b74bf88eacc639df27358db'],
 ['videos/MathMagic_Mixed_Numbers_FINAL.mp4','92c831fce1d463b7a369511098a1a5eff47a8756d840e5fe52f510dc3f7cdc56'],
 ['videos/MathMagic_Finding_LCM_FINAL_1080p.mp4','374bae53a7d727587b7940e2e302dcf30c528e17a964db914d2c8eb7107a3c00']
])assert.strictEqual(crypto.createHash('sha256').update(fs.readFileSync(src)).digest('hex'),hash);
const approvedVideos=new Map([
  ['videos/MathMagic_Finding_LCM_FINAL_1080p.mp4','videos/MathMagic_Finding_LCM_FINAL_1080p.mp4'],
  ...fractionsBatch.lessons.map(l=>[l.src,l.src]),
  ...year5Batches.flatMap(([,batch])=>batch.lessons.map(l=>[l.src,l.src]))
]);
let youtubeEmbeds=0,scrimbaEmbeds=0,mathmagicVideos=0;
const seenVideos=new Set();
for(const file of modules){
  const h=fs.readFileSync(file,'utf8');
  const youtube=[...h.matchAll(/<iframe\b[^>]*src="([^"]*youtube[^"]*)"[^>]*>/gi)];
  for(const m of youtube){
    youtubeEmbeds++;
    assert(m[1].includes('youtube-nocookie.com/embed/'),file+' must use the privacy-enhanced provider player');
    assert(/loading="lazy"/i.test(m[0]),file+' YouTube embed must lazy-load');
    assert(/title="[^"]+"/i.test(m[0]),file+' YouTube embed needs an accessible title');
    assert(/allowfullscreen/i.test(m[0]),file+' YouTube embed must support fullscreen');
    const id=(m[1].match(/\/embed\/([^?&"]+)/)||[])[1];
    assert(id,file+' embed needs a video id');
    assert(h.includes('youtube.com/watch?v='+id),file+' embed needs an original YouTube fallback link');
  }
  const scrimba=[...h.matchAll(/<iframe\b[^>]*src="([^"]*scrimba\.com\/explain\/[^"]+)"[^>]*>/gi)];
  for(const m of scrimba){
    scrimbaEmbeds++;
    assert(/^https:\/\/scrimba\.com\/explain\//.test(m[1]),file+' Scrimba embed must use the supported explainer URL');
    assert(/loading="lazy"/i.test(m[0]),file+' Scrimba embed must lazy-load');
    assert(/title="[^"]+"/i.test(m[0]),file+' Scrimba embed needs an accessible title');
    assert(/allowfullscreen/i.test(m[0]),file+' Scrimba embed must support fullscreen');
    const guide=(m[1].match(/scrimba\.com\/explain\/([^?"#]+)/)||[])[1];
    assert(guide,file+' Scrimba embed needs a guide id');
    assert(h.includes('https://scrimba.com/explain/'+guide),file+' needs a direct Scrimba fallback link');
  }
  const videos=[...h.matchAll(/<video\b([^>]*)>([\s\S]*?)<\/video>/gi)];
  for(const [,attrs,body] of videos){
    assert(/\bcontrols\b/i.test(attrs),file+' video needs native controls');
    assert(/\bplaysinline\b/i.test(attrs),file+' video must play inline on mobile');
    assert(/\bpreload="metadata"/i.test(attrs),file+' video must preload metadata only');
    assert(!/\bautoplay\b/i.test(attrs),file+' video must not autoplay');
    assert(/aria-label="MathMagic[^\"]+"/i.test(attrs),file+' video needs an accessible MathMagic name');
    assert(/width:100%/i.test(attrs),file+' video must be responsive');
    const source=body.match(/<source\b[^>]*src="([^"]+)"[^>]*type="video\/mp4"[^>]*>/i);
    assert(source,file+' video needs a typed MP4 source');
    const src=source[1],fallback=approvedVideos.get(src);
    assert(fallback,file+' unexpected video cannot replace approved lesson coverage: '+src);
    assert(!seenVideos.has(src),'Duplicate video cannot inflate resource coverage: '+src);
    seenVideos.add(src);
    assert(h.includes('href="'+fallback+'"'),file+' video needs a direct MP4 fallback link');
    if(!src.startsWith('https://')){
      const bytes=fs.readFileSync(src);
      if(newVerified.has(src)){const expected=newVerified.get(src);if(scopedCorrections.has(src)){const correction=scopedCorrections.get(src);assert.strictEqual(expected.status,'verified_scoped_correction');assert(['branding_only','mathematical_visual_only'].includes(correction.type));assert.strictEqual(correction.full_quality_status,'UNVERIFIED');assert.strictEqual(correction.accent_status,'UNVERIFIED');assert.strictEqual(correction.replacement.sha256,expected.sha256);assert.strictEqual(crypto.createHash('sha256').update(fs.readFileSync(correction.original.mp4)).digest('hex'),correction.original.expected_sha256,'Original correction backup changed');}else assert.strictEqual(expected.status,'verified');assert.strictEqual(expected.presenter,false);assert.strictEqual(bytes.length,expected.bytes);assert.strictEqual(crypto.createHash('sha256').update(bytes).digest('hex'),expected.sha256);}
      assert(bytes.length>0&&bytes.subarray(4,8).toString()==='ftyp',src+' must be a real MP4, not a missing file or LFS pointer');
      if(src==='videos/MathMagic_Adding_Subtracting_Fractions_CORRECTED_1080p.mp4'){
        assert.strictEqual(crypto.createHash('sha256').update(bytes).digest('hex'),'48ef9512c531cc6450ee22048152dad4e6d3ab757b74bf88eacc639df27358db','Adding and Subtracting Fractions must preserve the approved corrected MP4 bytes');
      }
      if(src==='videos/MathMagic_Finding_LCM_FINAL_1080p.mp4')assert.strictEqual(crypto.createHash('sha256').update(bytes).digest('hex'),'374bae53a7d727587b7940e2e302dcf30c528e17a964db914d2c8eb7107a3c00','LCM must preserve the approved MP4 bytes');
      if(src==='videos/MathMagic_Mixed_Numbers_FINAL.mp4'){
        assert.strictEqual(crypto.createHash('sha256').update(bytes).digest('hex'),'92c831fce1d463b7a369511098a1a5eff47a8756d840e5fe52f510dc3f7cdc56','Mixed Numbers must preserve the approved MP4 bytes');
      }
    }
    mathmagicVideos++;
  }
  const topicBatch=year5Batches.find(([page])=>page===file);
  if(topicBatch){
   assert.strictEqual(videos.length,5,'Five distinct validated core videos required: '+file);
   for(const expected of topicBatch[1].lessons){
    const section=h.match(new RegExp('<section id="'+expected.section+'"[^>]*>([\\s\\S]*?)</section>'));
    assert(section&&section[1].includes('src="'+expected.src+'"'),'Wrong lesson video: '+file+' '+expected.section);
   }
  }
  if(file==='fractions.html'){
    assert.strictEqual((h.match(/id="mathmagic-lcm-extension"/g)||[]).length,1);
    assert(h.includes('Extension: Finding the Lowest Common Multiple (LCM)'));
    assert(h.indexOf('id="mathmagic-lcm-extension"')>h.indexOf('id="mathmagic-addsub-video"'));
    for(const id of ['meaning','equivalent','mixed','addsub','problems']){
      const lesson=h.match(new RegExp('<section id="'+id+'"[^>]*>([\\s\\S]*?)</section>'));
      assert(lesson,'Missing Fractions lesson '+id);
      const players=lesson[1].match(/<(?:iframe|video)\b/gi)||[];
      assert.strictEqual(players.length,id==='addsub'?2:1,'Each lesson retains its core explainer, plus only the approved addsub extension: '+id);
      if(id==='addsub'){
        assert(lesson[1].includes('id="mathmagic-lcm-extension"'),'LCM extension belongs only in Adding and Subtracting');
        assert(lesson[1].includes('src="'+fractionsBatch.lessons.find(l=>l.section==='addsub').src+'"'),'Verified core Adding and Subtracting video must remain');
      }
      const expected=fractionsBatch.lessons.find(l=>l.section===id);assert(expected&&lesson[1].includes('src="'+expected.src+'"'),'Each section must use its matching verified graphics-only MP4: '+id);
    }
    assert(scrimba.length+videos.length>=5,'Expected the five Fractions lessons to use original MathMagic explainers');
  }
}
assert(youtubeEmbeds+scrimbaEmbeds+mathmagicVideos-3>=14,'Expected established MathMagic embedded-video coverage');
assert.strictEqual(seenVideos.size,approvedVideos.size,'All approved MathMagic MP4 replacements must remain present');
console.log('MathMagic video pattern passed across '+modules.length+' modules with '+youtubeEmbeds+' YouTube, '+scrimbaEmbeds+' Scrimba and '+mathmagicVideos+' approved MP4 players');
