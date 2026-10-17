const {test,expect}=require('@playwright/test');
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const lessons=require('../../video-agent/whole-numbers/lessons.json');
const root=path.join(__dirname,'../..'),norm=s=>s.replace(/\s+/g,' ').trim();
for(const lesson of lessons)test('Whole Numbers '+lesson.id+' media, captions, transcript and responsive playback',async({page})=>{
 const qa=JSON.parse(fs.readFileSync(path.join(root,'video-agent/whole-numbers/qa',lesson.id+'-qa.json')));
 const url='/videos/'+qa.filename,bytes=fs.readFileSync(path.join(root,'videos',qa.filename));
 expect(crypto.createHash('sha256').update(bytes).digest('hex')).toBe(qa.sha256);expect(bytes.length).toBe(qa.bytes);
 const response=await page.request.get(url,{headers:{Range:'bytes=0-1023'}});
 expect(response.status()).toBe(206);expect(response.headers()['content-type']).toBe('video/mp4');
 expect(response.headers()['content-range']).toBe('bytes 0-1023/'+qa.bytes);expect(Buffer.compare(await response.body(),bytes.subarray(0,1024))).toBe(0);
 expect((await page.request.get(url,{headers:{Range:'bytes='+qa.bytes+'-'}})).status()).toBe(416);
 // Deterministic UI isolation only; production Firebase is unchanged.
 await page.route('**/js/whole-numbers-auth.js*',r=>r.abort());
 await page.goto('/whole-numbers.html');await page.evaluate(()=>document.body.classList.remove('auth-loading'));
 await page.locator('[data-screen="'+lesson.id+'"]').click();
 const card=page.locator('#'+lesson.id+' #mathmagic-wn-'+lesson.id),video=card.locator('video');
 await expect(card).toHaveCount(1);await expect(video).toBeVisible();await expect(card.locator('h3')).toHaveText('MathMagic explainer: '+lesson.title);
 await expect(video).toHaveAttribute('aria-label','MathMagic - '+lesson.title);
 for(const attr of ['controls','playsinline'])await expect(video).toHaveAttribute(attr,'');
 await expect(video).toHaveAttribute('preload','metadata');await expect(video).not.toHaveAttribute('autoplay',/.*/);
 await expect(video.locator('source')).toHaveAttribute('type','video/mp4');await expect(card.locator('.video-frame + a')).toHaveAttribute('href',url.slice(1));
 await expect.poll(()=>video.evaluate(v=>v.readyState)).toBeGreaterThanOrEqual(2);
 expect(await video.evaluate(v=>[v.videoWidth,v.videoHeight])).toEqual([1920,1080]);expect(await video.evaluate(v=>v.duration)).toBeCloseTo(qa.duration,2);
 await expect(video.locator('track')).toHaveAttribute('srclang','en-AU');
 await video.evaluate(v=>v.textTracks[0].mode='showing');await expect.poll(()=>video.evaluate(v=>v.textTracks[0].cues?.length||0)).toBe(qa.caption_cues);
 expect(await video.evaluate(v=>Array.from(v.textTracks[0].cues).every(c=>c.line===1&&c.snapToLines===false))).toBeTruthy();
 const transcript=fs.readFileSync(path.join(root,'video-agent/whole-numbers',lesson.id+'.txt'),'utf8');
 await card.locator('summary').focus();await expect(card.locator('summary')).toBeFocused();await page.keyboard.press('Enter');
 await expect(card.locator('details')).toHaveAttribute('open','');expect(norm((await card.locator('details p').allTextContents()).join(' '))).toBe(norm(transcript));
 expect(norm(await video.evaluate(v=>Array.from(v.textTracks[0].cues,c=>c.text).join(' ')))).toBe(norm(transcript));
 for(const viewport of [{width:1440,height:1000},{width:768,height:1024},{width:390,height:844}]){
  await page.setViewportSize(viewport);await video.scrollIntoViewIfNeeded();await video.focus();await expect(video).toBeFocused();
  const b=await video.boundingBox();expect(b.x).toBeGreaterThanOrEqual(0);expect(b.x+b.width).toBeLessThanOrEqual(viewport.width+1);expect(Math.abs(b.width/b.height-16/9)).toBeLessThan(.01);
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=document.documentElement.clientWidth+1)).toBeTruthy();
  await video.evaluate(v=>{v.currentTime=0;return v.play()});await expect.poll(()=>video.evaluate(v=>v.currentTime)).toBeGreaterThan(.2);
  for(const time of [1,qa.duration/2,qa.duration-2]){await video.evaluate((v,t)=>{v.pause();v.currentTime=t},time);await expect.poll(()=>video.evaluate(v=>!v.seeking&&v.readyState>=2)).toBeTruthy();expect(await video.evaluate(v=>v.currentTime)).toBeCloseTo(time,1)}
 }
 await video.evaluate(v=>{v.currentTime=v.duration-.4;return v.play()});await expect.poll(()=>video.evaluate(v=>v.ended)).toBeTruthy();
});
