// Actual local review-media playback. No production Firebase or site changes.
const {chromium}=require('playwright'),fs=require('fs'),path=require('path'),assert=require('node:assert/strict'),http=require('http');
const out='/workspace/output/space-review',manifest=path.join(__dirname,'batch-manifest.json');
(async()=>{
 const state=JSON.parse(fs.readFileSync(manifest)),resultsFile=path.join(out,'playback-qa.json');
 const results=fs.existsSync(resultsFile)?JSON.parse(fs.readFileSync(resultsFile)):[];
 const server=http.createServer((req,res)=>{
  const name=decodeURIComponent(new URL(req.url,'http://localhost').pathname).slice(1);
  if(path.basename(name)!==name){res.writeHead(403);return res.end()}
  const file=path.join(out,name);if(!fs.existsSync(file)){res.writeHead(404);return res.end()}
  const size=fs.statSync(file).size;const mime={'.mp4':'video/mp4','.vtt':'text/vtt','.html':'text/html','.txt':'text/plain','.jpg':'image/jpeg'}[path.extname(file)]||'application/octet-stream';
  let start=0,end=size-1,status=200;
  if(req.headers.range){const match=/^bytes=(\d+)-(\d*)$/.exec(req.headers.range);if(!match||+match[1]>=size){res.writeHead(416,{'Content-Range':`bytes */${size}`});return res.end()}start=+match[1];end=match[2]?Math.min(+match[2],size-1):size-1;if(end<start){res.writeHead(416);return res.end()}status=206}
  res.writeHead(status,{'Content-Type':mime,'Accept-Ranges':'bytes','Content-Length':end-start+1,...(status===206?{'Content-Range':`bytes ${start}-${end}/${size}`}:{})});
  if(req.method==='HEAD')return res.end();fs.createReadStream(file,{start,end}).pipe(res);
 });
 await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));const base=`http://127.0.0.1:${server.address().port}/`;
 const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--allow-file-access-from-files']});
 try{
  for(const [id,e]of Object.entries(state.lessons)){
   if(e.status!=='TECHNICALLY_VERIFIED')continue;
   for(const viewport of [{width:1280,height:800},{width:390,height:844}]){
    if(results.some(r=>r.sha256===e.sha256&&r.passed&&r.viewport.width===viewport.width&&r.captionCueCount>0))continue;
    const page=await browser.newPage({viewport});
    const prefix=path.basename(e.output).slice(0,-4);const html=path.join(out,`review-${id}.html`);
    fs.writeFileSync(html,`<!doctype html><meta name="viewport" content="width=device-width,initial-scale=1"><title>${id} review</title><style>body{margin:0;background:#fff9ef;font:18px sans-serif}video{display:block;width:100%;object-fit:contain}h1{font-size:22px}a{padding:10px;display:inline-block}</style><h1>${id}: review candidate; full quality unverified</h1><video controls playsinline preload="metadata" aria-label="${id}" poster="${prefix}_poster.jpg"><source type="video/mp4" src="${path.basename(e.output)}"><track default kind="captions" srclang="en" label="English" src="${prefix}.vtt"><a href="${path.basename(e.output)}">Open video</a></video><a href="${prefix}_transcript.txt">Read transcript</a>`);
    const url=base+path.basename(e.output);
    const head=await fetch(url,{method:'HEAD'});assert.equal(head.status,200);assert.equal(head.headers.get('content-type'),'video/mp4');
    const range=await fetch(url,{headers:{Range:'bytes=0-31'}});assert.equal(range.status,206);assert.equal((await range.arrayBuffer()).byteLength,32);
    const invalid=await fetch(url,{headers:{Range:`bytes=${e.bytes+10}-`}});assert.equal(invalid.status,416);
    await page.goto(base+path.basename(html));
    await page.waitForFunction(()=>{const v=document.querySelector('video');return v.readyState>=2&&v.duration>300});
    await page.waitForFunction(()=>document.querySelector('video').textTracks[0]?.cues?.length>0);
    const captionCueCount=await page.locator('video').evaluate(v=>v.textTracks[0].cues.length);assert.equal(captionCueCount,e.qa.caption_cues);
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
    const r={lesson:id,sha256:e.sha256,viewport,metadata:meta,captionCueCount,advancingPlayback:true,seeks,ended:true,httpStatusChecks:[200,206,416],mime:'video/mp4',passed:true,scope:'Local Chromium, muted playback; not actual listening, real Safari/iOS or deployed playback'};
    results.push(r);fs.writeFileSync(resultsFile,JSON.stringify(results,null,2)+'\n');await page.close();
    console.log('PASS local playback',id,viewport.width);
   }
  }
 }finally{await browser.close();await new Promise(resolve=>server.close(resolve))}
})().catch(e=>{console.error(e);process.exit(1)});
