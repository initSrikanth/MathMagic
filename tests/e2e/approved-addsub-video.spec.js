const {test,expect}=require('@playwright/test');
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const filename='MathMagic_Adding_Subtracting_Fractions_CORRECTED_1080p.mp4';
test('approved Adding and Subtracting video preserves bytes, captions and responsive playback',async({page})=>{
 const url='/videos/'+filename,bytes=fs.readFileSync(path.join(__dirname,'../../videos',filename));
 expect(bytes.length).toBe(14169595);
 expect(crypto.createHash('sha256').update(bytes).digest('hex')).toBe('48ef9512c531cc6450ee22048152dad4e6d3ab757b74bf88eacc639df27358db');
 const first=await page.request.get(url,{headers:{Range:'bytes=0-1023'}});
 expect(first.status()).toBe(206);expect(first.headers()['content-type']).toBe('video/mp4');
 expect(first.headers()['content-range']).toBe('bytes 0-1023/14169595');
 expect(Buffer.compare(await first.body(),bytes.subarray(0,1024))).toBe(0);
 await page.route('**/js/fractions-auth.js*',route=>route.abort());
 await page.goto('/fractions.html');await page.evaluate(()=>document.body.classList.remove('auth-loading'));
 await page.locator('[data-screen="addsub"]').click();
 const video=page.getByLabel('MathMagic - Adding and Subtracting Fractions',{exact:true});
 await expect(video).toBeVisible();await expect(video).toHaveAttribute('controls','');
 await expect(video).toHaveAttribute('playsinline','');await expect(video).not.toHaveAttribute('autoplay',/.*/);
 await expect.poll(()=>video.evaluate(v=>v.readyState)).toBeGreaterThanOrEqual(2);
 const m=await video.evaluate(v=>({w:v.videoWidth,h:v.videoHeight,d:v.duration,error:v.error?.code}));
 expect(m).toEqual({w:1920,h:1080,d:91.72,error:undefined});
 const track=video.locator('track[kind="captions"]');await expect(track).toHaveAttribute('srclang','en-AU');
 const cc=await page.request.get(await track.getAttribute('src'));expect(cc.ok()).toBeTruthy();expect(await cc.text()).toMatch(/^WEBVTT/);
 await video.evaluate(v=>v.textTracks[0].mode='showing');
 await expect.poll(()=>video.evaluate(v=>v.textTracks[0].cues?.length||0)).toBe(50);
 await page.getByText('Read the video transcript',{exact:true}).click();
 await expect(page.locator('#addsub details')).toHaveAttribute('open','');
 for(const viewport of [{width:1440,height:1000},{width:768,height:1024},{width:390,height:844}]){
  await page.setViewportSize(viewport);await video.scrollIntoViewIfNeeded();
  await video.focus();await expect(video).toBeFocused();
  const box=await video.boundingBox();expect(box.x).toBeGreaterThanOrEqual(0);
  expect(box.x+box.width).toBeLessThanOrEqual(viewport.width+1);expect(Math.abs(box.width/box.height-16/9)).toBeLessThan(.01);
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=document.documentElement.clientWidth+1)).toBeTruthy();
  await video.evaluate(v=>{v.currentTime=0;return v.play()});await expect.poll(()=>video.evaluate(v=>v.currentTime)).toBeGreaterThan(.2);
  for(const t of [1,45,89]){await video.evaluate((v,t)=>{v.pause();v.currentTime=t},t);await expect.poll(()=>video.evaluate(v=>!v.seeking&&v.readyState>=2)).toBeTruthy();expect(await video.evaluate(v=>v.currentTime)).toBeCloseTo(t,1)}
 }
 await video.evaluate(v=>{v.currentTime=91.3;return v.play()});await expect.poll(()=>video.evaluate(v=>v.ended)).toBeTruthy();
 await expect(page.locator('#addsub .video-resource')).toHaveCount(1);
 await expect(page.getByText('Extension: Finding the Lowest Common Multiple (LCM)',{exact:true})).toHaveCount(0);
});
