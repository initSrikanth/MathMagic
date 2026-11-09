const {test,expect}=require('@playwright/test');
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const release=require('../../video-agent/space/release.json');
const root=path.resolve(__dirname,'../..'),normal=s=>s.replace(/\s+/g,' ').trim();
// UI/media integration only. This route is a test fixture, not production auth.
test('Space: all ten owner-approved players, captions, transcripts and responsive playback',async({page})=>{
 test.setTimeout(120000);
 await page.route('**/js/space-auth.js',r=>r.fulfill({contentType:'application/javascript',body:"document.body.classList.remove('auth-loading');"}));
 await page.goto('/space-lessons.html');
 await expect(page.locator('section.lesson')).toHaveCount(10);
 await expect(page.locator('video')).toHaveCount(10);
 for(const l of release.lessons){
  const bytes=fs.readFileSync(path.join(root,l.src));expect(bytes.length).toBe(l.bytes);expect(crypto.createHash('sha256').update(bytes).digest('hex')).toBe(l.sha256);
  const first=await page.request.get('/'+l.src,{headers:{Range:'bytes=0-1023'}});expect(first.status()).toBe(206);expect(first.headers()['content-type']).toBe('video/mp4');expect(Buffer.compare(await first.body(),bytes.subarray(0,1024))).toBe(0);
  const section=page.locator('#'+l.section),card=section.locator('[data-space-video="'+l.id+'"]'),v=card.locator('video');await v.scrollIntoViewIfNeeded();await expect(v).toBeVisible();
  await expect(v).toHaveAttribute('controls','');await expect(v).toHaveAttribute('playsinline','');await expect(v).toHaveAttribute('preload','metadata');await expect(v).not.toHaveAttribute('autoplay',/.*/);
  await expect(v.locator('source')).toHaveAttribute('src',l.src);await expect(v.locator('track')).toHaveAttribute('src',l.captions);await expect(v.locator('track')).toHaveAttribute('srclang','en');
  await expect.poll(()=>v.evaluate(v=>v.readyState)).toBeGreaterThanOrEqual(2);expect(await v.evaluate(v=>[v.videoWidth,v.videoHeight])).toEqual([1920,1080]);expect(await v.evaluate(v=>v.duration)).toBeCloseTo(l.duration,1);
  await v.evaluate(v=>v.textTracks[0].mode='showing');await expect.poll(()=>v.evaluate(v=>v.textTracks[0].cues?.length||0)).toBe(l.caption_cues);
  expect(normal(await v.evaluate(v=>Array.from(v.textTracks[0].cues,c=>c.text).join(' ')))).toBe(normal(fs.readFileSync(path.join(root,l.transcript),'utf8')));
  await card.locator('summary').click();expect(normal((await card.locator('details p').allTextContents()).join(' '))).toBe(normal(fs.readFileSync(path.join(root,l.transcript),'utf8')));await card.locator('summary').click();
  for(const width of [1440,768,390]){await page.setViewportSize({width,height:900});await v.scrollIntoViewIfNeeded();const box=await v.boundingBox();expect(box.x).toBeGreaterThanOrEqual(0);expect(box.x+box.width).toBeLessThanOrEqual(width+1);expect(Math.abs(box.width/box.height-16/9)).toBeLessThan(.02);expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1)).toBe(true)}
  await v.focus();await v.press('Space');await expect.poll(()=>v.evaluate(v=>v.currentTime)).toBeGreaterThan(.2);expect(await v.evaluate(v=>v.muted)).toBe(false);
  for(const t of [l.duration/2,l.duration-.4]){await v.evaluate((v,t)=>{v.pause();v.currentTime=t},t);await expect.poll(()=>v.evaluate(v=>!v.seeking&&v.readyState>=2)).toBe(true)}
  await v.focus();await v.press('Space');await expect.poll(()=>v.evaluate(v=>v.ended)).toBe(true);
 }
});
