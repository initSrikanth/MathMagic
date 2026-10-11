const fs=require('fs'),assert=require('assert');
const htmlFiles=fs.readdirSync('.').filter(f=>f.endsWith('.html'));
let embeds=0;
for(const file of htmlFiles){
  const h=fs.readFileSync(file,'utf8');
  const frames=[...h.matchAll(/<iframe\b[^>]*src="([^"]*scrimba\.com\/explain\/[^"]+)"[^>]*>/gi)];
  for(const m of frames){
    embeds++;
    assert(/^https:\/\/scrimba\.com\/explain\//.test(m[1]),file+' Scrimba embed must use https://scrimba.com/explain/');
    assert(/loading="lazy"/i.test(m[0]),file+' Scrimba embed must lazy-load');
    assert(/title="[^"]+"/i.test(m[0]),file+' Scrimba embed needs an accessible title');
    assert(/allowfullscreen/i.test(m[0]),file+' Scrimba embed must support fullscreen');
    const guide=(m[1].match(/scrimba\.com\/explain\/([^?"#]+)/)||[])[1];
    assert(guide,file+' Scrimba embed needs a guide id');
    assert(new RegExp('<a\\b[^>]*href="https://scrimba\\.com/explain/'+guide+'"','i').test(h),file+' needs a visible fallback Scrimba guide link');
  }
}
console.log('MathMagic Scrimba explainer embed audit passed for '+embeds+' current embed(s)');