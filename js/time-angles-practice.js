'use strict';
/* Interactive, self-checking Year 5 Measurement explorations. No external services. */
(()=>{
 const activities=[
 {title:'Build an elapsed-time timeline',prompt:'A trip starts at 09:35 and finishes at 10:20. How many minutes pass?',answer:45,unit:'minutes',explain:'09:35 to 10:00 is 25 minutes; 10:00 to 10:20 is 20 minutes. 25 + 20 = 45 minutes.',draw:'timeline'},
 {title:'Read the connection timetable',prompt:'Bus: 10:28–11:03. Train: 11:18–11:54. How many minutes is the entire journey, including the wait?',answer:86,unit:'minutes',explain:'10:28 to 11:03 = 35 minutes; wait = 15 minutes; train = 36 minutes. Total = 86 minutes.',draw:'timetable'},
 {title:'Estimate an angle',prompt:'The blue ray has rotated 135° anticlockwise from the horizontal. Is the angle acute, right, obtuse, straight or reflex?',answer:'obtuse',unit:'',explain:'135° is greater than a right angle (90°) and less than a straight angle (180°), so it is obtuse.',draw:'angle',degrees:135},
 {title:'Check a protractor reading',prompt:'A ray begins at the 0° baseline and passes through the 65° mark. What is the angle in degrees?',answer:65,unit:'degrees',explain:'Start at 0° on the baseline and read the scale in the direction of the turn. The angle is 65°, not 115°.',draw:'angle',degrees:65},
 {title:'Complete the full turn',prompt:'A robot turns 120° and then another 85° in the same direction. How many degrees remain to complete a full turn?',answer:155,unit:'degrees',explain:'A full turn is 360°. The robot has turned 120° + 85° = 205°, so 360° − 205° = 155°.',draw:'angle',degrees:205}
 ];
 function svgAngle(deg){
  const rad=deg*Math.PI/180, x=110+76*Math.cos(-rad),y=100+76*Math.sin(-rad);
  const arcEndX=110+42*Math.cos(-rad),arcEndY=100+42*Math.sin(-rad);
  const large=deg>180?1:0;
  return '<svg viewBox="0 0 260 190" role="img" aria-label="Angle of '+deg+' degrees from a horizontal baseline" style="width:min(100%,340px);height:auto"><path d="M110 100 L206 100" stroke="#06445a" stroke-width="4" fill="none"/><path d="M110 100 L'+x.toFixed(1)+' '+y.toFixed(1)+'" stroke="#17a2b8" stroke-width="4" fill="none"/><path d="M152 100 A42 42 0 '+large+' 0 '+arcEndX.toFixed(1)+' '+arcEndY.toFixed(1)+'" stroke="#b45309" stroke-width="3" fill="none"/><circle cx="110" cy="100" r="5" fill="#06445a"/><text x="119" y="120" font-size="15" fill="#06445a">'+deg+'°</text></svg>';
 }
 function visual(a){
  if(a.draw==='angle')return svgAngle(a.degrees);
  if(a.draw==='timeline')return '<div class="measurement-visual" role="img" aria-label="Timeline from 09:35 to 10:00 to 10:20"><span>09:35</span><span>+25 min →</span><span>10:00</span><span>+20 min →</span><span>10:20</span></div>';
  return '<table class="measurement-table"><caption>Journey timetable</caption><thead><tr><th scope="col">Service</th><th scope="col">Departs</th><th scope="col">Arrives</th></tr></thead><tbody><tr><th scope="row">Bus</th><td>10:28</td><td>11:03</td></tr><tr><th scope="row">Train</th><td>11:18</td><td>11:54</td></tr></tbody></table>';
 }
 activities.forEach((a,i)=>{
  const section=document.getElementById('lesson'+(i+1));if(!section)return;
  const card=document.createElement('div');card.className='learn measurement-interactive';
  const heading=document.createElement('h3');heading.textContent='Explore and check: '+a.title;card.append(heading);
  const art=document.createElement('div');art.innerHTML=visual(a);card.append(art);
  const p=document.createElement('p');p.textContent=a.prompt;card.append(p);
  const label=document.createElement('label');const id='measurement-answer-'+(i+1);label.htmlFor=id;label.textContent='Your answer'+(a.unit?' ('+a.unit+')':'')+': ';card.append(label);
  const input=document.createElement('input');input.id=id;input.type='text';input.autocomplete='off';input.setAttribute('aria-describedby','measurement-feedback-'+(i+1));label.append(input);
  const button=document.createElement('button');button.type='button';button.textContent='Check my reasoning';card.append(button);
  const feedback=document.createElement('p');feedback.id='measurement-feedback-'+(i+1);feedback.setAttribute('role','status');feedback.setAttribute('aria-live','polite');card.append(feedback);
  const check=()=>{
   const raw=input.value.trim().toLowerCase();if(!raw){feedback.textContent='Enter your answer before checking.';return}
   const normalized=raw.replace(/°/g,'').trim();
   const ok=typeof a.answer==='number'? /^[-+]?\d+$/.test(normalized)&&Number(normalized)===a.answer:normalized===a.answer;
   feedback.className='practice-feedback '+(ok?'correct':'incorrect');
   feedback.textContent=(ok?'Correct. ':'Not yet. ')+a.explain;
  };
  button.addEventListener('click',check);input.addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();check()}});
  section.insertBefore(card,section.querySelector('.next-page'));
 });
})();
