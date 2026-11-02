/* Native playback of actual TLS-verified published bytes. The route bridge uses
   that downloaded cache so managed-browser proxy trust does not get bypassed.
   Actual live HTTP200/206 + hashes are independently checked by verify_live.py. */
const {chromium}=require('playwright'),{expect}=require('@playwright/test');
const fs=require('fs'),path=require('path');
const batch=require('./decimals-release.json'),base='https://initsrikanth.github.io/MathMagic/';
const cache='/workspace/pr46-live-cache';
(async()=>{
 const verified=JSON.parse(fs.readFileSync(path.join(cache,'verification.json')));expect(verified.passed).toBe(true);
 const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true});const page=await browser.newPage();const results=[];
 await page.route('**/*',async route=>{
  const url=route.request().url();
  if(!url.startsWith(base)||url.includes('/js/decimals-percentages-auth.js'))return route.abort();
  const rel=new URL(url).pathname.slice('/MathMagic/'.length),file=path.resolve(cache,rel||'decimals-percentages.html');
  if(!file.startsWith(cache+'/')||!fs.existsSync(file))return route.abort();
  const data=fs.readFileSync(file),range=route.request().headers().range;let status=200,body=data;
  const type=file.endsWith('.mp4')?'video/mp4':file.endsWith('.vtt')?'text/vtt':file.endsWith('.css')?'text/css':file.endsWith('.js')?'application/javascript':file.endsWith('.jpg')?'image/jpeg':'text/html';
  const headers={'content-type':type,'accept-ranges':'bytes'};
  if(range){const m=range.match(/^bytes=(\d+)-(\d*)$/);if(m){const start=+m[1],end=Math.min(m[2]?+m[2]:data.length-1,data.length-1);body=data.subarray(start,end+1);status=206;headers['content-range']=`bytes ${start}-${end}/${data.length}`}}
  return route.fulfill({status,headers,body});
 });
 try{
  await page.goto(base+'decimals-percentages.html');await page.evaluate(()=>document.body.classList.remove('auth-loading'));
  for(const size of [{width:1440,height:1000},{width:768,height:1024},{width:390,height:844}]){
   await page.setViewportSize(size);
   for(const l of batch.lessons){
    await page.locator('[data-screen="'+l.section+'"]').click();const v=page.locator('[data-mathmagic-v2="'+l.id+'"] video');await v.scrollIntoViewIfNeeded();await v.focus();await expect(v).toBeFocused();
    await expect.poll(()=>v.evaluate(v=>v.readyState)).toBeGreaterThanOrEqual(2);expect(await v.evaluate(v=>[v.videoWidth,v.videoHeight])).toEqual([1920,1080]);
    expect(await v.evaluate(v=>v.duration)).toBeCloseTo(l.duration,1);await v.evaluate(v=>v.textTracks[0].mode='showing');await expect.poll(()=>v.evaluate(v=>v.textTracks[0].cues?.length||0)).toBe(l.caption_cues);
    const box=await v.boundingBox();expect(box.x).toBeGreaterThanOrEqual(0);expect(box.x+box.width).toBeLessThanOrEqual(size.width+1);expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1)).toBe(true);
    await v.evaluate(v=>{v.currentTime=0;return v.play()});await expect.poll(()=>v.evaluate(v=>v.currentTime)).toBeGreaterThan(.2);
    for(const t of [1,l.duration/2,l.duration-2]){await v.evaluate((v,t)=>{v.pause();v.currentTime=t},t);await expect.poll(()=>v.evaluate(v=>!v.seeking&&v.readyState>=2)).toBe(true);expect(await v.evaluate(v=>v.currentTime)).toBeCloseTo(t,1)}
    await v.evaluate(v=>{v.currentTime=v.duration-.3;return v.play()});await expect.poll(()=>v.evaluate(v=>v.ended)).toBe(true);
    if(size.width===390){const goal=require('./timings/'+l.id+'.json').cues.find(e=>e.role==='learning_goal');await v.evaluate((v,t)=>{v.currentTime=t;v.pause()},goal.start+1);await expect.poll(()=>v.evaluate(v=>!v.seeking)).toBe(true);await v.screenshot({path:path.join(cache,l.id+'-phone.png')})}
    results.push({lesson:l.id,viewport:size.width,metadata:true,captions:true,advancing_playback:true,seeks:true,ending:true,keyboard_focus:true,containment:true});
   }
  }
  fs.writeFileSync(path.join(cache,'native-playback.json'),JSON.stringify({passed:true,browser:await browser.version(),transport:'Actual published assets via TLS-verified byte cache/range bridge; Firebase isolated only for QA',real_iOS_Safari:false,results},null,2));console.log('PASS: 15 published-byte native playback cases, desktop/tablet/phone Chromium.');
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
