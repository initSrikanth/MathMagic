/* Read-only media gate. Use the repository range server at BASE_URL. Firebase is
   isolated in this local test only; this is not a real-auth or Safari/iOS test. */
const {chromium}=require('playwright');
const {expect}=require('@playwright/test');
const fs=require('fs'),cp=require('child_process');
const base=process.env.BASE_URL||'http://127.0.0.1:4175';
const mode=process.argv[2]||'baseline';
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CHROME_EXECUTABLE_PATH||'/usr/bin/chromium',headless:true,args:['--no-sandbox','--autoplay-policy=no-user-gesture-required']});
 const page=await browser.newPage();await page.route('**/js/fractions-auth.js*',r=>r.abort());
 const results=[];const report={source_commit:cp.execFileSync('git',['rev-parse','HEAD'],{encoding:'utf8'}).trim(),mode,browser:await browser.version(),auth_isolated:true,real_iOS_Safari:false,results};
 try{
  await page.goto(base+'/fractions.html');await page.evaluate(()=>document.body.classList.remove('auth-loading'));
  for(const viewport of [{width:1440,height:1000},{width:768,height:1024},{width:390,height:844}]){
   await page.setViewportSize(viewport);
   for(const section of ['meaning','equivalent','mixed','addsub','problems']){
    await page.locator(`[data-screen="${section}"]`).click();
    const videos=page.locator(`#${section} video`);const count=await videos.count();expect(count).toBe(section==='addsub'&&mode==='proposal'?2:1);
    for(let i=0;i<count;i++){
     const video=videos.nth(i);await video.scrollIntoViewIfNeeded();await video.focus();await expect(video).toBeFocused();
     await expect.poll(()=>video.evaluate(v=>v.readyState),{timeout:20000}).toBeGreaterThanOrEqual(2);
     const meta=await video.evaluate(v=>({src:v.querySelector('source').getAttribute('src'),width:v.videoWidth,height:v.videoHeight,duration:v.duration,controls:v.controls,inline:v.playsInline,preload:v.preload,autoplay:v.autoplay,error:v.error?.code||null}));
     expect(meta.error).toBe(null);expect(meta.controls&&meta.inline&&!meta.autoplay).toBe(true);expect(meta.preload).toBe('metadata');expect(meta.width).toBe(1920);expect(meta.height).toBe(1080);
     const box=await video.boundingBox();expect(box.x).toBeGreaterThanOrEqual(0);expect(box.x+box.width).toBeLessThanOrEqual(viewport.width+1);expect(Math.abs(box.width/box.height-16/9)).toBeLessThan(.01);
     expect(await page.evaluate(()=>document.documentElement.scrollWidth<=document.documentElement.clientWidth+1)).toBe(true);
     await video.evaluate(v=>{v.textTracks[0].mode='showing'});await expect.poll(()=>video.evaluate(v=>v.textTracks[0].cues?.length||0)).toBeGreaterThan(0);
     const caption=await video.evaluate(v=>Array.from(v.textTracks[0].cues,c=>c.text).join(' '));const transcript=await video.evaluate(v=>Array.from(v.closest('.video-resource').querySelectorAll('details p'),p=>p.textContent).join(' '));
     const norm=x=>x.replace(/\s+/g,' ').trim();expect(norm(caption)).toBe(norm(transcript));
     await video.evaluate(v=>{v.currentTime=0;return v.play()});await expect.poll(()=>video.evaluate(v=>v.currentTime)).toBeGreaterThan(.2);
     for(const time of [1,meta.duration/2,meta.duration-2]){await video.evaluate((v,t)=>{v.pause();v.currentTime=t},time);await expect.poll(()=>video.evaluate(v=>!v.seeking&&v.readyState>=2)).toBe(true);expect(await video.evaluate(v=>v.currentTime)).toBeCloseTo(time,1)}
     await video.evaluate(v=>{v.currentTime=v.duration-.3;return v.play()});await expect.poll(()=>video.evaluate(v=>v.ended)).toBe(true);
     results.push({section,viewport:viewport.width,...meta,caption_cues:await video.evaluate(v=>v.textTracks[0].cues.length),caption_transcript_match:true,advancing:true,seeks:true,ended:true,keyboard_focus:true,responsive_containment:true});
    }
   }
  }
  report.passed=true;
 }catch(e){report.passed=false;report.error=e.message;await page.screenshot({path:'/tmp/fractions-39-media-browser-failure.png',fullPage:true});throw e}
 finally{fs.writeFileSync(`docs/qa/fractions-39-media-browser-${mode}.json`,JSON.stringify(report,null,2)+'\n');await browser.close()}
 console.log(JSON.stringify(report,null,2));
})().catch(e=>{console.error(e);process.exit(1)});
