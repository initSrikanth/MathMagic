const {test,expect}=require('@playwright/test');
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const batch=require('../../video-agent/production-v2/measurement-release.json');
const root=path.join(__dirname,'../..'),normal=s=>s.replace(/\s+/g,' ').trim();
for(const l of batch.lessons)test('graphics-only '+l.title+' exact media, captions and responsive playback',async({page},testInfo)=>{
 const bytes=fs.readFileSync(path.join(root,l.src));expect(bytes.length).toBe(l.bytes);expect(crypto.createHash('sha256').update(bytes).digest('hex')).toBe(l.sha256);
 const first=await page.request.get('/'+l.src,{headers:{Range:'bytes=0-1023'}});
 expect(first.status()).toBe(206);expect(first.headers()['content-type']).toBe('video/mp4');expect(first.headers()['content-range']).toBe('bytes 0-1023/'+l.bytes);expect(Buffer.compare(await first.body(),bytes.subarray(0,1024))).toBe(0);
 expect((await page.request.get('/'+l.src,{headers:{Range:'bytes='+l.bytes+'-'}})).status()).toBe(416);
 // UI/media isolation; this does not test production Firebase or physical iOS.
 await page.route('**/js/measurement-auth.js*',r=>r.abort());await page.goto('/measurement.html');await page.evaluate(()=>document.body.classList.remove('auth-loading'));
 await page.locator('[data-screen="'+l.section+'"]').click();
 const card=page.locator('[data-mathmagic-v2="'+l.id+'"]'),video=card.locator('video');
 await expect(video).toBeVisible();for(const a of ['controls','playsinline'])await expect(video).toHaveAttribute(a,'');
 await expect(video).toHaveAttribute('preload','metadata');await expect(video).not.toHaveAttribute('autoplay',/.*/);
 await expect.poll(()=>video.evaluate(v=>v.readyState)).toBeGreaterThanOrEqual(2);
 expect(await video.evaluate(v=>[v.videoWidth,v.videoHeight])).toEqual([1920,1080]);expect(await video.evaluate(v=>v.duration)).toBeCloseTo(l.duration,1);
 const track=video.locator('track[kind="captions"]');await expect(track).toHaveAttribute('srclang','en-GB');
 await video.evaluate(v=>v.textTracks[0].mode='showing');await expect.poll(()=>video.evaluate(v=>v.textTracks[0].cues?.length||0)).toBe(l.caption_cues);
 expect(await video.evaluate(v=>Array.from(v.textTracks[0].cues).every(c=>c.startTime>=0&&c.endTime>c.startTime&&c.endTime<=v.duration+.1))).toBeTruthy();

 expect(await video.evaluate(v=>Array.from(v.textTracks[0].cues).every(c=>c.line===0&&c.snapToLines===false&&c.text.split('\n').length<=3))).toBeTruthy();
 const transcript=fs.readFileSync(path.join(root,l.transcript),'utf8');expect(normal(await video.evaluate(v=>Array.from(v.textTracks[0].cues,c=>c.text).join(' ')))).toBe(normal(transcript));
 await card.locator('summary').click();expect(normal((await card.locator('details p').allTextContents()).join(' '))).toBe(normal(transcript));
 for(const viewport of [{width:1440,height:1000},{width:768,height:1024},{width:390,height:844}]){
  await page.setViewportSize(viewport);await video.scrollIntoViewIfNeeded();await video.focus();await expect(video).toBeFocused();const box=await video.boundingBox();expect(box.x).toBeGreaterThanOrEqual(0);expect(box.x+box.width).toBeLessThanOrEqual(viewport.width+1);expect(Math.abs(box.width/box.height-16/9)).toBeLessThan(.01);
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1)).toBeTruthy();
  const timing=require('../../video-agent/production-v2/timings/'+l.id+'.json');const goal=timing.cues.find(e=>e.role==='learning_goal');
  await video.evaluate((v,t)=>{v.pause();v.currentTime=t},goal.start+1);await expect.poll(()=>video.evaluate(v=>!v.seeking&&v.readyState>=2)).toBeTruthy();
  if(viewport.width!==768)await video.screenshot({path:testInfo.outputPath(l.id+'-goal-'+viewport.width+'.png')});
  if(viewport.width===390){const concept=timing.cues.find(c=>c.chapter==='Build the idea');await video.evaluate((v,t)=>{v.currentTime=t;v.pause()},concept.start+1);await expect.poll(()=>video.evaluate(v=>!v.seeking&&v.readyState>=2)).toBeTruthy();await video.screenshot({path:testInfo.outputPath(l.id+'-concept-390.png')})}
  await video.evaluate(v=>{v.currentTime=0;return v.play()});await expect.poll(()=>video.evaluate(v=>v.currentTime)).toBeGreaterThan(.2);
  for(const t of [1,l.duration/2,l.duration-2]){await video.evaluate((v,t)=>{v.pause();v.currentTime=t},t);await expect.poll(()=>video.evaluate(v=>!v.seeking&&v.readyState>=2)).toBeTruthy();expect(await video.evaluate(v=>v.currentTime)).toBeCloseTo(t,1)}
 }
 await video.evaluate(v=>{v.currentTime=v.duration-.4;return v.play()});await expect.poll(()=>video.evaluate(v=>v.ended)).toBeTruthy();
 expect(l.presenter).toBe(false);
});
