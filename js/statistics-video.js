'use strict';
// Native controls and track remain available when JavaScript is unavailable.
document.querySelectorAll('.statistics-player').forEach(card=>{
 const video=card.querySelector('video'),button=card.querySelector('[data-caption-toggle]'),panel=card.querySelector('.statistics-caption-panel'),text=card.querySelector('[data-caption-text]');
 const track=video.textTracks[0];if(!track)return;
 let enabled=false,changing=false;
 const fullscreen=()=>document.fullscreenElement===video||video.webkitDisplayingFullscreen===true;
 function paint(){text.textContent=Array.from(track.activeCues||[],c=>c.text.replace(/<[^>]*>/g,'')).join(' ')||'Captions appear here during speech.'}
 function setCaptions(on){enabled=on;changing=true;track.mode=enabled?(fullscreen()?'showing':'hidden'):'disabled';button.setAttribute('aria-pressed',String(enabled));button.textContent=enabled?'Hide captions':'Show captions';panel.hidden=!enabled||fullscreen();paint();queueMicrotask(()=>changing=false)}
 button.addEventListener('click',()=>setCaptions(!enabled));track.addEventListener('cuechange',paint);
 video.textTracks.addEventListener('change',()=>{if(!changing)setCaptions(track.mode!=='disabled')});
 for(const event of ['fullscreenchange','webkitfullscreenchange'])document.addEventListener(event,()=>setCaptions(enabled));
 video.addEventListener('webkitbeginfullscreen',()=>setCaptions(enabled));video.addEventListener('webkitendfullscreen',()=>setCaptions(enabled));
 const size=()=>{if(!fullscreen()){const width=card.querySelector('.statistics-video-stage').clientWidth;if(width)video.style.height=Math.round(width*9/16+72)+'px'}};
 new ResizeObserver(size).observe(card.querySelector('.statistics-video-stage'));size();
 // Hidden lesson panels must not leave narration playing in the background.
 new MutationObserver(()=>{const screen=card.closest('.screen');if(screen&&!screen.classList.contains('active'))video.pause()}).observe(card.closest('.screen')||card,{attributes:true,attributeFilter:['class']});
});
