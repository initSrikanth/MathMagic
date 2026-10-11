const fs=require('fs'),assert=require('assert');
const modules=['fractions.html','whole-numbers.html','addition-subtraction.html','decimals-percentages.html','multiplication-division.html','factors-multiples.html'];
let youtubeEmbeds=0,scrimbaEmbeds=0;
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
}
assert(youtubeEmbeds+scrimbaEmbeds>=14,'Expected established MathMagic embedded-video coverage');
assert(scrimbaEmbeds>=5,'Expected the five Fractions lessons to use original MathMagic explainers');
console.log('MathMagic video pattern passed across '+modules.length+' modules with '+youtubeEmbeds+' YouTube and '+scrimbaEmbeds+' Scrimba embeds');
