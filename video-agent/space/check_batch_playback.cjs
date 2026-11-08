// Actual local review-media playback. No production Firebase or site changes.
const {chromium}=require('playwright'),fs=require('fs'),path=require('path'),assert=require('node:assert/strict');
const out='/workspace/output/space-review',manifest=path.join(__dirname,'batch-manifest.json');
(async()=>{
 const state=JSON.parse(fs.readFileSync(manifest)),resultsFile=path.join(out,'playback-qa.json');
 const results=fs.existsSync(resultsFile)?JSON.parse(fs.readFileSync(resultsFile)):[];
 const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--allow-file-access-from-files']});
 try{
  for(const [id,e]of Object.entries(state.lessons)){
   if(e.status!=='TECHNICALLY_VERIFIED')continue;
   for(const viewport of [{width:1280,height:800},{width:390,height:844}]){
    if(results.some(r=>r.sha256===e.sha256&&r.passed&&r.viewport.width===viewport.width))continue;
    const page=await browser.newPage({viewport});
    const prefix=e.output.slice(0,-4);const html=path.join(out,`review-${id}.html`);
    fs.writeFileSync(html,`<!doctype html><meta name="viewport" content="width=device-width,initial-scale=1"><title>${id} review</title><style>body{margin:0;background:#fff9ef;font:18px sans-serif}video{display:block;width:100%;object-fit:contain}h1{font-size:22px}a{padding:10px;display:inline-block}</style><h1>${id}: review candidate; full quality unverified</h1><video controls playsinline preload="metadata" aria-label="${id}" poster="file://${prefix}_poster.jpg"><source type="video/mp4" src="file://${e.output}"><track default kind="captions" srclang="en" label="English" src="file://${prefix}.vtt"><a href="file://${e.output}">Open video</a></video><a href="file://${prefix}_transcript.txt">Read transcript</a>`);
    await page.goto('file://'+html);
    await page.waitForFunction(()=>{const v=document.querySelector('video');return v.readyState>=2&&v.duration>300});
    const meta=await page.locator('video').evaluate(v=>({duration:v.duration,width:v.videoWidth,height:v.videoHeight,rectWidth:v.getBoundingClientRect().width,tracks:v.textTracks.length}));
    assert.equal(meta.width,1920);assert.equal(meta.height,1080);assert(meta.rectWidth<=viewport.width);assert.equal(meta.tracks,1);
    await page.locator('video').evaluate(async v=>{v.muted=true;await v.play()});
    await page.waitForFunction(()=>document.querySelector('video').currentTime>1);
    await page.locator('video').evaluate(v=>v.pause());
    const seeks=[];
    for(const fraction of [.05,.5,.9]){
     const target=meta.duration*fraction;
     await page.locator('video').evaluate((v,t)=>new Promise(resolve=>{v.addEventListener('seeked',resolve,{once:true});v.currentTime=t}),target);
     const actual=await page.locator('video').evaluate(v=>v.currentTime);assert(Math.abs(actual-target)<.15);seeks.push(actual);
    }
    await page.locator('video').evaluate(v=>{v.currentTime=v.duration-.7;return v.play()});
    await page.waitForFunction(()=>document.querySelector('video').ended,{},{timeout:10000});
    const r={lesson:id,sha256:e.sha256,viewport,metadata:meta,advancingPlayback:true,seeks,ended:true,passed:true,scope:'Local Chromium, muted playback; not actual listening, real Safari/iOS or deployed playback'};
    results.push(r);fs.writeFileSync(resultsFile,JSON.stringify(results,null,2)+'\n');await page.close();
    console.log('PASS local playback',id,viewport.width);
   }
  }
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
