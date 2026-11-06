'use strict';
/* Original accessible SVG diagrams for MathMagic Year 5 Time and Angles. */
(()=> {
 const NS='http://www.w3.org/2000/svg';
 const E=(name,attrs={},text)=>{const e=document.createElementNS(NS,name);Object.entries(attrs).forEach(([k,v])=>e.setAttribute(k,String(v)));if(text!==undefined)e.textContent=text;return e;};
 function diagram(deg,{size=180,protractor=false}={}){
  const svg=E('svg',{viewBox:'0 0 240 210',role:'img','aria-label':deg+' degree angle diagram',style:'width:100%;max-width:'+size+'px;height:auto'});
  const cx=110,cy=153,r=76,theta=deg*Math.PI/180;
  const pt=(a,rad=r)=>[cx+rad*Math.cos(-a*Math.PI/180),cy+rad*Math.sin(-a*Math.PI/180)];
  if(protractor){svg.append(E('path',{d:'M 18 153 A 92 92 0 0 1 202 153',fill:'none',stroke:'#94a3b8','stroke-width':2}));for(let i=0;i<=180;i+=10){const p=pt(i,92),q=pt(i,i%30===0?79:85);svg.append(E('line',{x1:p[0],y1:p[1],x2:q[0],y2:q[1],stroke:'#64748b','stroke-width':i%30===0?2:1}));if(i%30===0){const t=pt(i,67);svg.append(E('text',{x:t[0],y:t[1],fill:'currentColor','text-anchor':'middle','font-size':11},String(i)));}}}
  const p=pt(deg);svg.append(E('line',{x1:cx,y1:cy,x2:cx+r,y2:cy,stroke:'currentColor','stroke-width':4,'stroke-linecap':'round'}),E('line',{x1:cx,y1:cy,x2:p[0],y2:p[1],stroke:'currentColor','stroke-width':4,'stroke-linecap':'round'}));
  const arcR=34,arcEnd=pt(deg,arcR);
  if(deg===360){svg.append(E('circle',{cx,cy,r:arcR,stroke:'#0891b2','stroke-width':4,fill:'none'}));}
  else if(deg>0){svg.append(E('path',{d:'M '+(cx+arcR)+' '+cy+' A '+arcR+' '+arcR+' 0 '+(deg>180?1:0)+' 0 '+arcEnd[0]+' '+arcEnd[1],stroke:'#7c3aed','stroke-width':4,fill:'none','stroke-linecap':'round'}));}
  svg.append(E('circle',{cx,cy,r:3,fill:'currentColor'}));return svg;
 }
 const groups=[['Acute',45,'Greater than 0° and less than 90°'],['Right',90,'Exactly 90°'],['Obtuse',125,'Greater than 90° and less than 180°'],['Straight',180,'Exactly 180°'],['Reflex',250,'Greater than 180° and less than 360°'],['Full turn',360,'Exactly 360°']];
 const gallery=document.getElementById('angle-gallery');
 if(gallery){gallery.className='angle-gallery';groups.forEach(([name,deg,range])=>{const card=document.createElement('figure');card.className='angle-tile';card.append(diagram(deg));const label=document.createElement('figcaption');const strong=document.createElement('strong');strong.textContent=name;const span=document.createElement('span');span.textContent=range;label.append(strong,span);card.append(label);gallery.append(card);});}
 const examples=document.getElementById('protractor-examples');
 if(examples){[65,125].forEach(deg=>{const fig=document.createElement('figure');fig.className='angle-tile';fig.append(diagram(deg,{size:260,protractor:true}));const cap=document.createElement('figcaption');cap.textContent=deg+'°: start at 0° on the baseline and follow the correct scale.';fig.append(cap);examples.append(fig);});}
 const slider=document.getElementById('angle-slider'),visual=document.getElementById('angle-slider-visual'),value=document.getElementById('angle-slider-value');
 if(slider&&visual&&value){const update=()=>{const n=Number(slider.value);visual.replaceChildren(diagram(n,{size:260}));value.textContent=n+'° — '+(n===0?'zero angle':n<90?'acute':n===90?'right':n<180?'obtuse':n===180?'straight':n<360?'reflex':'full turn');};slider.addEventListener('input',update);update();}
 window.MathMagicAngleDiagram=diagram;
})();