// Same trusted-activation approach used by measurement-videos.spec.js.
// Only the review harness needs this; integrated players have a real Play button.
async function activateReviewPlayback(video){
 await video.focus();
 if(video.page().context().browser().browserType().name()!=='webkit')return video.press('Space');
 await video.evaluate(v=>{
  const b=document.createElement('button');b.id='qa-statistics-playback';b.type='button';b.textContent='Start review playback';
  b.style.cssText='position:fixed;left:0;bottom:0;z-index:2147483647';
  b.onclick=()=>v.play().catch(e=>{v.dataset.qaPlayError=e.name+': '+e.message});document.body.appendChild(b);
 });
 await video.page().locator('#qa-statistics-playback').click();
 await video.page().locator('#qa-statistics-playback').evaluate(b=>b.remove());
}
module.exports={activateReviewPlayback};
