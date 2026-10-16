const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {chromium,devices}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const root=path.resolve(__dirname,'../..'),file='final/MathMagic_Finding_LCM_REVIEW_1080p.mp4',origin=process.env.REVIEW_ORIGIN||'http://127.0.0.1:4189';
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium',headless:true,args:['--no-sandbox']});const results=[];
 try{for(const [device,settings]of[['desktop',{viewport:{width:1440,height:1000}}],['tablet',{viewport:{width:768,height:1024},isMobile:true,hasTouch:true}],['mobile',devices['Pixel 7']]]){
  const context=await browser.newContext(settings),page=await context.newPage();await page.goto(origin+'/reviews/lcm/');const v=page.getByLabel('MathMagic Finding the Lowest Common Multiple review');
  assert.ok(await page.getByText('Completed 1080p review candidate', {exact:false}).isVisible());
  const response=await context.request.get(origin+'/reviews/lcm/'+file);assert.equal(response.status(),200);assert.equal(response.headers()['content-type'],'video/mp4');
  const local=fs.readFileSync(path.join(root,'reviews/lcm',file));assert.equal(crypto.createHash('sha256').update(await response.body()).digest('hex'),crypto.createHash('sha256').update(local).digest('hex'));
  const range=await context.request.get(origin+'/reviews/lcm/'+file,{headers:{Range:'bytes=0-1023'}});assert.equal(range.status(),206);assert.equal((await range.body()).length,1024);
  const invalid=await context.request.get(origin+'/reviews/lcm/'+file,{headers:{Range:`bytes=${local.length}-`}});assert.equal(invalid.status(),416);
  await page.waitForFunction(()=>document.querySelector('video').readyState>=2);assert.deepEqual(await v.evaluate(x=>[x.videoWidth,x.videoHeight,x.duration]),[1920,1080,87.666667]);
  await v.evaluate(x=>x.textTracks[0].mode='showing');await page.waitForFunction(()=>document.querySelector('video').textTracks[0].cues?.length===27);
  await v.focus();assert.ok(await v.evaluate(x=>x===document.activeElement&&x.controls&&x.playsInline&&x.preload==='metadata'&&!x.autoplay));
  await v.evaluate(x=>x.play());await page.waitForTimeout(400);assert.ok(await v.evaluate(x=>x.currentTime>.1));
  for(const t of[1,43,85])await v.evaluate((x,t)=>new Promise(resolve=>{x.pause();x.addEventListener('seeked',resolve,{once:true});x.currentTime=t}),t);
  await v.evaluate(x=>{x.currentTime=87.2;return x.play()});await page.waitForFunction(()=>document.querySelector('video').ended);
  const box=await v.boundingBox();assert.ok(box.x>=0&&box.x+box.width<=page.viewportSize().width+1);assert.ok(Math.abs(box.width/box.height-16/9)<.01);
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=document.documentElement.clientWidth+1));
  results.push({device,metadata:'PASS',playback:'PASS',seeking:'PASS',end:'PASS',ranges:'PASS',keyboard:'PASS',containment:'PASS',captions:'PASS',audio:'AAC narration present; technical identity checked separately'});await context.close();
 }}finally{await browser.close()}
 fs.writeFileSync(path.join(root,'reviews/lcm/final/final-playback-qa.json'),JSON.stringify(results,null,2)+'\n');console.log(JSON.stringify(results,null,2));
})().catch(e=>{console.error(e);process.exit(1)});
