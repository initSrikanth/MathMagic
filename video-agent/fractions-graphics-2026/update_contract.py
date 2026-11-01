"""Authorised replacement contract; preserve strict checks and every old asset."""
from pathlib import Path
import re
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
def main():
 p=ROOT/'tests/external-video-pattern.test.js';s=p.read_text();start=s.index('const approvedVideos=new Map([');end=s.index('\n]);',start)+4
 old=s[start:end];pairs=re.findall(r"\['([^']+)','([^']+)'\]",old);kept=pairs[:5];assert len(kept)==5 and all('Fractions' not in pair[0] and 'LCM' not in pair[0] and 'Mixed_Numbers' not in pair[0] for pair in kept)
 literal=',\n'.join('  '+repr(list(pair)).replace(', ',",") for pair in kept+[('videos/MathMagic_Finding_LCM_FINAL_1080p.mp4','videos/MathMagic_Finding_LCM_FINAL_1080p.mp4')])
 new="""// Five new graphics-only replacements explicitly authorised in this production mission.
const fractionsBatch=require('../video-agent/fractions-graphics-2026/manifest.json');
const previousMedia=require('../video-agent/fractions-graphics-2026/previous-integrations.json');
assert.strictEqual(fractionsBatch.lessons.length,5);
const newFractions=new Map(fractionsBatch.lessons.map(l=>[l.src,l]));
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
"""+literal+",\n  ...fractionsBatch.lessons.map(l=>[l.src,l.src])\n]);"
 s=s[:start]+new+s[end:]
 s=s.replace("const bytes=fs.readFileSync(src);\n      assert(bytes.length>0", "const bytes=fs.readFileSync(src);\n      if(newFractions.has(src)){const expected=newFractions.get(src);assert.strictEqual(expected.status,'verified');assert.strictEqual(expected.presenter,false);assert.strictEqual(bytes.length,expected.bytes);assert.strictEqual(crypto.createHash('sha256').update(bytes).digest('hex'),expected.sha256);}\n      assert(bytes.length>0")
 s=s.replace("assert(lesson[1].includes('src=\"videos/MathMagic_Adding_Subtracting_Fractions_CORRECTED_1080p.mp4\"'),'Core Adding and Subtracting video must remain');", "assert(lesson[1].includes('src=\"'+fractionsBatch.lessons.find(l=>l.section==='addsub').src+'\"'),'Verified core Adding and Subtracting video must remain');")
 s=s.replace("if(id==='mixed')assert(lesson[1].includes('src=\"videos/MathMagic_Mixed_Numbers_FINAL.mp4\"'),'Mixed Numbers must use its approved local MP4');", "const expected=fractionsBatch.lessons.find(l=>l.section===id);assert(expected&&lesson[1].includes('src=\"'+expected.src+'\"'),'Each section must use its matching verified graphics-only MP4: '+id);")
 p.write_text(s)
 p=ROOT/'tests/e2e/fractions.spec.js';s=p.read_text();start=s.index("test('five original MathMagic explainers retain approved MP4 or Scrimba players");end=s.index("test('original explainer frames stay responsive",start)
 assert 'approved Mixed Numbers video' in s[start:end]
 new="""test('five graphics-only lessons retain their verified MP4 players', async ({page})=>{
 await openFractions(page);
 const batch=require('../../video-agent/fractions-graphics-2026/manifest.json');
 for(const l of batch.lessons){
  await page.locator('[data-screen="'+l.section+'"]').click();
  const card=page.locator('[data-fractions-graphics="'+l.id+'"]'),video=card.locator('video');
  await expect(video).toBeVisible();await expect(video.locator('source')).toHaveAttribute('src',l.src);
  await expect(video.locator('source')).toHaveAttribute('type','video/mp4');
  for(const attr of ['controls','playsinline'])await expect(video).toHaveAttribute(attr,'');
  await expect(video).toHaveAttribute('preload','metadata');await expect(video).not.toHaveAttribute('autoplay',/.*/);
  await expect(video).toHaveAttribute('aria-label','MathMagic - '+l.title);
  await expect(card.locator('.video-frame + a')).toHaveAttribute('href',l.src);
  await expect(page.locator('#'+l.section+' iframe')).toHaveCount(0);
 }
});

"""
 s=s[:start]+new+s[end:];p.write_text(s)
 p=ROOT/'tests/e2e/approved-addsub-video.spec.js'
 p.write_text("""const {test,expect}=require('@playwright/test');
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const batch=require('../../video-agent/fractions-graphics-2026/manifest.json');
const root=path.join(__dirname,'../..'),normal=s=>s.replace(/\\s+/g,' ').trim();
for(const l of batch.lessons)test('graphics-only '+l.title+' exact media, captions and responsive playback',async({page},testInfo)=>{
 const bytes=fs.readFileSync(path.join(root,l.src));expect(bytes.length).toBe(l.bytes);expect(crypto.createHash('sha256').update(bytes).digest('hex')).toBe(l.sha256);
 const first=await page.request.get('/'+l.src,{headers:{Range:'bytes=0-1023'}});
 expect(first.status()).toBe(206);expect(first.headers()['content-type']).toBe('video/mp4');expect(first.headers()['content-range']).toBe('bytes 0-1023/'+l.bytes);expect(Buffer.compare(await first.body(),bytes.subarray(0,1024))).toBe(0);
 expect((await page.request.get('/'+l.src,{headers:{Range:'bytes='+l.bytes+'-'}})).status()).toBe(416);
 // UI/media isolation; this does not test production Firebase or physical iOS.
 await page.route('**/js/fractions-auth.js*',r=>r.abort());await page.goto('/fractions.html');await page.evaluate(()=>document.body.classList.remove('auth-loading'));
 await page.locator('[data-screen="'+l.section+'"]').click();
 const card=page.locator('[data-fractions-graphics="'+l.id+'"]'),video=card.locator('video');
 await expect(video).toBeVisible();for(const a of ['controls','playsinline'])await expect(video).toHaveAttribute(a,'');
 await expect(video).toHaveAttribute('preload','metadata');await expect(video).not.toHaveAttribute('autoplay',/.*/);
 await expect.poll(()=>video.evaluate(v=>v.readyState)).toBeGreaterThanOrEqual(2);
 expect(await video.evaluate(v=>[v.videoWidth,v.videoHeight])).toEqual([1920,1080]);expect(await video.evaluate(v=>v.duration)).toBeCloseTo(l.duration,1);
 const track=video.locator('track[kind="captions"]');await expect(track).toHaveAttribute('srclang','en');await expect(track).toHaveAttribute('default','');
 await video.evaluate(v=>v.textTracks[0].mode='showing');await expect.poll(()=>video.evaluate(v=>v.textTracks[0].cues?.length||0)).toBe(l.caption_cues);
 expect(await video.evaluate(v=>Array.from(v.textTracks[0].cues).every(c=>c.line===1&&c.snapToLines===false))).toBeTruthy();
 const transcript=fs.readFileSync(path.join(root,l.transcript),'utf8');expect(normal(await video.evaluate(v=>Array.from(v.textTracks[0].cues,c=>c.text).join(' ')))).toBe(normal(transcript));
 await card.locator('summary').click();expect(normal((await card.locator('details p').allTextContents()).join(' '))).toBe(normal(transcript));
 for(const viewport of [{width:1440,height:1000},{width:768,height:1024},{width:390,height:844}]){
  await page.setViewportSize(viewport);await video.scrollIntoViewIfNeeded();await video.focus();await expect(video).toBeFocused();const box=await video.boundingBox();expect(box.x).toBeGreaterThanOrEqual(0);expect(box.x+box.width).toBeLessThanOrEqual(viewport.width+1);expect(Math.abs(box.width/box.height-16/9)).toBeLessThan(.01);
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1)).toBeTruthy();
  const timing=require('../../video-agent/fractions-graphics-2026/timings/'+l.id+'.json');const goal=timing.events.find(e=>e.role==='goal');
  await video.evaluate((v,t)=>{v.pause();v.currentTime=t},goal.start+1);await expect.poll(()=>video.evaluate(v=>!v.seeking&&v.readyState>=2)).toBeTruthy();
  if(viewport.width!==768)await video.screenshot({path:testInfo.outputPath(l.id+'-goal-'+viewport.width+'.png')});
  await video.evaluate(v=>{v.currentTime=0;return v.play()});await expect.poll(()=>video.evaluate(v=>v.currentTime)).toBeGreaterThan(.2);
  for(const t of [1,l.duration/2,l.duration-2]){await video.evaluate((v,t)=>{v.pause();v.currentTime=t},t);await expect.poll(()=>video.evaluate(v=>!v.seeking&&v.readyState>=2)).toBeTruthy();expect(await video.evaluate(v=>v.currentTime)).toBeCloseTo(t,1)}
 }
 await video.evaluate(v=>{v.currentTime=v.duration-.4;return v.play()});await expect.poll(()=>video.evaluate(v=>v.ended)).toBeTruthy();
 expect(l.presenter).toBe(false);
});
""")
 print('Updated authorised active-video contract; legacy files remain hash-protected, all five new players receive full playback/caption checks.')
if __name__=='__main__':main()
