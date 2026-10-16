const {test,expect}=require('@playwright/test');
const fs=require('fs'),path=require('path'),crypto=require('crypto');
test('approved LCM extension retains exact bytes, accessible text and responsive playback',async({page})=>{
 const src='videos/MathMagic_Finding_LCM_FINAL_1080p.mp4';
 const bytes=fs.readFileSync(path.join(__dirname,'../../',src));
 expect(bytes.length).toBe(3111284);
 expect(crypto.createHash('sha256').update(bytes).digest('hex')).toBe('374bae53a7d727587b7940e2e302dcf30c528e17a964db914d2c8eb7107a3c00');
 const response=await page.request.get('/'+src);expect(response.status()).toBe(200);
 expect(crypto.createHash('sha256').update(await response.body()).digest('hex')).toBe(crypto.createHash('sha256').update(bytes).digest('hex'));
 const range=await page.request.get('/'+src,{headers:{Range:'bytes=0-1023'}});
 expect(range.status()).toBe(206);expect(range.headers()['content-type']).toBe('video/mp4');
 expect(range.headers()['content-range']).toBe('bytes 0-1023/3111284');expect(Buffer.compare(await range.body(),bytes.subarray(0,1024))).toBe(0);
 expect((await page.request.get('/'+src,{headers:{Range:'bytes=3111284-'}})).status()).toBe(416);
 // Isolate Firebase only in QA; production authentication remains untouched.
 await page.route('**/js/fractions-auth.js*',r=>r.abort());
 await page.goto('/fractions.html');await page.evaluate(()=>document.body.classList.remove('auth-loading'));
 await page.locator('[data-screen="addsub"]').click();
 const card=page.locator('#addsub #mathmagic-lcm-extension');
 await expect(card.locator('h3')).toHaveText('Extension: Finding the Lowest Common Multiple (LCM)');
 expect(await card.evaluate(c=>c.previousElementSibling.querySelector('video')?.id)).toBe('mathmagic-addsub-video');
 const video=card.getByLabel('MathMagic - Finding the Lowest Common Multiple (LCM)',{exact:true});
 await expect(video).toBeVisible();for(const a of ['controls','playsinline'])await expect(video).toHaveAttribute(a,'');
 await expect(video).toHaveAttribute('preload','metadata');await expect(video).not.toHaveAttribute('autoplay',/.*/);
 await expect(card.locator('.video-frame + a')).toHaveAttribute('href',src);
 await expect.poll(()=>video.evaluate(v=>v.readyState)).toBeGreaterThanOrEqual(2);
 expect(await video.evaluate(v=>({w:v.videoWidth,h:v.videoHeight}))).toEqual({w:1920,h:1080});
 expect(await video.evaluate(v=>v.duration)).toBeCloseTo(87.666667,2);
 await expect(video.locator('track')).toHaveAttribute('srclang','en-AU');
 await video.evaluate(v=>v.textTracks[0].mode='showing');
 await expect.poll(()=>video.evaluate(v=>v.textTracks[0].cues?.length||0)).toBe(27);
 const normalize=s=>s.replace(/\s+/g,' ').trim();
 const transcript=fs.readFileSync(path.join(__dirname,'../../videos/MathMagic_Finding_LCM_Transcript.txt'),'utf8');
 await card.locator('summary').focus();await expect(card.locator('summary')).toBeFocused();await page.keyboard.press('Enter');
 await expect(card.locator('details')).toHaveAttribute('open','');
 expect(normalize((await card.locator('details p').allTextContents()).join(' '))).toBe(normalize(transcript));
 expect(normalize(await video.evaluate(v=>Array.from(v.textTracks[0].cues,c=>c.text).join(' ')))).toBe(normalize(transcript));
 for(const viewport of [{width:1440,height:1000},{width:768,height:1024},{width:390,height:844}]){
  await page.setViewportSize(viewport);await video.scrollIntoViewIfNeeded();await video.focus();await expect(video).toBeFocused();
  const b=await video.boundingBox();expect(b.x).toBeGreaterThanOrEqual(0);expect(b.x+b.width).toBeLessThanOrEqual(viewport.width+1);expect(Math.abs(b.width/b.height-16/9)).toBeLessThan(.01);
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=document.documentElement.clientWidth+1)).toBeTruthy();
  await video.evaluate(v=>{v.currentTime=0;return v.play()});await expect.poll(()=>video.evaluate(v=>v.currentTime)).toBeGreaterThan(.2);
  for(const t of [1,43,85]){await video.evaluate((v,t)=>{v.pause();v.currentTime=t},t);await expect.poll(()=>video.evaluate(v=>!v.seeking&&v.readyState>=2)).toBeTruthy();expect(await video.evaluate(v=>v.currentTime)).toBeCloseTo(t,1)}
 }
 await video.evaluate(v=>{v.currentTime=87.3;return v.play()});await expect.poll(()=>video.evaluate(v=>v.ended)).toBeTruthy();
});
