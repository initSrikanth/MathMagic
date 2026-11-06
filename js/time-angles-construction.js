'use strict';
/* Year 5 interactive angle construction. No external dependencies or authentication bypass. */
(()=>{
 const $=id=>document.getElementById(id),host=$('construction-canvas'),slider=$('construction-slider'),choice=$('construction-target'),task=$('construction-task'),feedback=$('construction-feedback');
 if(!host||!slider||!choice||!task||!feedback)return;
 const ns='http://www.w3.org/2000/svg',make=(tag,attrs={})=>{const n=document.createElementNS(ns,tag);for(const [k,v] of Object.entries(attrs))n.setAttribute(k,String(v));return n;};
 const svg=make('svg',{viewBox:'0 0 440 310',role:'img','aria-label':'Interactive angle construction with draggable endpoint',style:'display:block;width:100%;height:auto;touch-action:none'});
 const cx=220,cy=178,r=105;
 const baseline=make('line',{x1:cx,y1:cy,x2:cx+r,y2:cy,stroke:'currentColor','stroke-width':4,'stroke-linecap':'round'});
 const ray=make('line',{x1:cx,y1:cy,x2:cx+r,y2:cy,stroke:'#2563eb','stroke-width':5,'stroke-linecap':'round'});
 const arc=make('path',{fill:'none',stroke:'#9333ea','stroke-width':4});
 const center=make('circle',{cx,cy,r:5,fill:'currentColor'});
 const handle=make('circle',{cx:cx+r,cy,r:14,fill:'#2563eb',stroke:'white','stroke-width':3,style:'cursor:grab'});
 const degrees=make('text',{x:cx,y:285,'text-anchor':'middle','font-size':19,fill:'currentColor'});
 const guide=make('path',{d:'M 110 178 A 110 110 0 0 1 330 178',stroke:'#94a3b8','stroke-width':1.5,fill:'none'});
 svg.append(guide,baseline,arc,ray,center,handle,degrees);host.append(svg);
 let target=35,current=0,dragging=false;
 const point=(a,radius)=>({x:cx+radius*Math.cos(-a*Math.PI/180),y:cy+radius*Math.sin(-a*Math.PI/180)});
 function draw(){const p=point(current,r);ray.setAttribute('x2',p.x);ray.setAttribute('y2',p.y);handle.setAttribute('cx',p.x);handle.setAttribute('cy',p.y);const q=point(current,37);arc.setAttribute('d',current===0?'':current===360?'M '+(cx+37)+' '+cy+' A 37 37 0 1 0 '+(cx-37)+' '+cy+' A 37 37 0 1 0 '+(cx+37)+' '+cy:'M '+(cx+37)+' '+cy+' A 37 37 0 '+(current>180?1:0)+' 0 '+q.x+' '+q.y);degrees.textContent='Your angle: '+current+'°';slider.value=String(current);}
 function set(a){current=Math.max(0,Math.min(360,Math.round(a)));feedback.textContent='';draw();}
 function choose(){target=choice.value==='random'?Math.floor(Math.random()*35)*5+5:Number(choice.value);task.textContent='Construct an angle of '+target+'°.';set(0);}
 function pointer(e){const rect=svg.getBoundingClientRect();const x=(e.clientX-rect.left)*440/rect.width-cx,y=(e.clientY-rect.top)*310/rect.height-cy;let angle=(Math.atan2(-y,x)*180/Math.PI+360)%360;if(current>=270&&angle<90&&x>0&&Math.abs(y)<12)angle=360;set(angle);}
 svg.addEventListener('pointerdown',e=>{if(e.button!==undefined&&e.button!==0)return;dragging=true;svg.setPointerCapture(e.pointerId);pointer(e);});
 svg.addEventListener('pointermove',e=>{if(dragging)pointer(e);});
 svg.addEventListener('pointerup',()=>{dragging=false;});
 svg.addEventListener('pointercancel',()=>{dragging=false;});
 slider.addEventListener('input',()=>set(Number(slider.value)));
 choice.addEventListener('change',choose);
 $('construction-reset').addEventListener('click',()=>set(0));
 $('construction-check').addEventListener('click',()=>{const difference=Math.abs(current-target);const success=difference<=2;feedback.textContent=success?'Well constructed! '+current+'° is within 2° of '+target+'°. Explain how you estimated and checked it.':'Your angle is '+current+'°. The target is '+target+'°. You are '+difference+'° away. Compare with 90° or 180°, then adjust the ray and try again.';feedback.className='practice-feedback '+(success?'correct':'incorrect');});
 choose();
})();
