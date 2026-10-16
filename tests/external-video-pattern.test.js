const fs=require('fs'),assert=require('assert');
const modules=['fractions.html','whole-numbers.html','addition-subtraction.html','decimals-percentages.html','multiplication-division.html','factors-multiples.html'];
const crypto=require('crypto');
// Approved MathMagic replacements count as the same lesson coverage, not extra
// coverage. Keep the established 14-resource / five-Fractions-lesson minimums.
const approvedVideos=new Map([
  ['videos/MathMagic_Comparing_Fractions_FINAL.mp4','videos/MathMagic_Comparing_Fractions_FINAL.mp4'],
  ['https://raw.githubusercontent.com/initSrikanth/MathMagic/feature/video-production-agent/videos/MathMagic_Equivalent_Fractions_FINAL.mp4','https://github.com/initSrikanth/MathMagic/raw/refs/heads/feature/video-production-agent/videos/MathMagic_Equivalent_Fractions_FINAL.mp4'],
  ['videos/MathMagic_Mixed_Numbers_FINAL.mp4','videos/MathMagic_Mixed_Numbers_FINAL.mp4'],
  ['videos/MathMagic_Adding_Subtracting_Fractions_CORRECTED_1080p.mp4','videos/MathMagic_Adding_Subtracting_Fractions_CORRECTED_1080p.mp4']
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
      assert(bytes.length>0&&bytes.subarray(4,8).toString()==='ftyp',src+' must be a real MP4, not a missing file or LFS pointer');
      if(src==='videos/MathMagic_Adding_Subtracting_Fractions_CORRECTED_1080p.mp4'){
        assert.strictEqual(crypto.createHash('sha256').update(bytes).digest('hex'),'48ef9512c531cc6450ee22048152dad4e6d3ab757b74bf88eacc639df27358db','Adding and Subtracting Fractions must preserve the approved corrected MP4 bytes');
      }
      if(src==='videos/MathMagic_Mixed_Numbers_FINAL.mp4'){
        assert.strictEqual(crypto.createHash('sha256').update(bytes).digest('hex'),'92c831fce1d463b7a369511098a1a5eff47a8756d840e5fe52f510dc3f7cdc56','Mixed Numbers must preserve the approved MP4 bytes');
      }
    }
    mathmagicVideos++;
  }
  if(file==='fractions.html'){
    for(const id of ['meaning','equivalent','mixed','addsub','problems']){
      const lesson=h.match(new RegExp('<section id="'+id+'"[^>]*>([\\s\\S]*?)</section>'));
      assert(lesson,'Missing Fractions lesson '+id);
      const players=lesson[1].match(/<(?:iframe|video)\b/gi)||[];
      assert.strictEqual(players.length,1,'Each Fractions lesson must retain exactly one original explainer: '+id);
      if(id==='mixed')assert(lesson[1].includes('src="videos/MathMagic_Mixed_Numbers_FINAL.mp4"'),'Mixed Numbers must use its approved local MP4');
    }
    assert(scrimba.length+videos.length>=5,'Expected the five Fractions lessons to use original MathMagic explainers');
  }
}
assert(youtubeEmbeds+scrimbaEmbeds+mathmagicVideos>=14,'Expected established MathMagic embedded-video coverage');
assert.strictEqual(seenVideos.size,approvedVideos.size,'All approved MathMagic MP4 replacements must remain present');
console.log('MathMagic video pattern passed across '+modules.length+' modules with '+youtubeEmbeds+' YouTube, '+scrimbaEmbeds+' Scrimba and '+mathmagicVideos+' approved MP4 players');
