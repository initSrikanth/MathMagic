const screens = [...document.querySelectorAll(".screen")];
const tabs = [...document.querySelectorAll(".tab")];
const rnd = (a,b) => Math.floor(Math.random() * (b-a+1)) + a;
const fmt = n => Number(n).toLocaleString("en-AU");
const PLACE_NAMES = {1:"ones",10:"tens",100:"hundreds",1000:"thousands",10000:"ten thousands",100000:"hundred thousands"};
const PLACES = [10,100,1000,10000,100000];

function showScreen(id){
  screens.forEach(s => s.classList.toggle("active", s.id === id));
  tabs.forEach(t => t.classList.toggle("active", t.dataset.screen === id));
  window.scrollTo({top:0,behavior:"smooth"});
  if(id === "challenge" && !quiz.length) startQuiz();
}
tabs.forEach(t => t.addEventListener("click", () => showScreen(t.dataset.screen)));
document.querySelectorAll("[data-next]").forEach(b => b.addEventListener("click", () => showScreen(b.dataset.next)));

document.querySelectorAll(".practice button[data-answer]").forEach(btn => btn.addEventListener("click", () => {
  const box = btn.closest(".practice");
  const input = box.querySelector("input");
  const fb = box.querySelector(".practice-feedback");
  const ok = input.value.trim().replace(/,/g,"") === btn.dataset.answer;
  fb.textContent = ok ? "Correct — well done." : "Not quite. Look back at the example and try again.";
  fb.className = "practice-feedback " + (ok ? "correct" : "incorrect");
}));

function makeNumberWithDigitAtPlace(place,digit){
  const n = rnd(100000,999999);
  return Math.floor(n/(place*10))*(place*10) + digit*place + (n%place);
}
function placeValueQuestion(){
  const place = PLACES[rnd(0,PLACES.length-1)];
  const digit = rnd(1,9);
  const n = makeNumberWithDigitAtPlace(place,digit);
  return {
    topic:"Place Value",
    prompt:`In ${fmt(n)}, what is the value of the digit in the ${PLACE_NAMES[place]} place?`,
    display:fmt(n),
    highlightPlace:place,
    answer:String(digit*place),
    type:"number"
  };
}
function identifyPlaceQuestion(){
  const place = PLACES[rnd(0,PLACES.length-1)];
  const digit = rnd(1,9);
  const n = makeNumberWithDigitAtPlace(place,digit);
  return {
    topic:"Place Value",
    prompt:`In ${fmt(n)}, which place is the highlighted digit in?`,
    display:fmt(n),
    highlightPlace:place,
    answer:PLACE_NAMES[place],
    type:"select",
    options:["tens","hundreds","thousands","ten thousands","hundred thousands"]
  };
}
function expandedQuestion(){
  const n = rnd(100000,999999);
  const parts = [];
  [100000,10000,1000,100,10,1].forEach(p => {
    const d = Math.floor(n/p)%10;
    if(d) parts.push(fmt(d*p));
  });
  return {topic:"Representing Numbers",prompt:"What number is shown by this expanded form?",display:parts.join(" + "),answer:String(n),type:"number"};
}
function digitContributionQuestion(){
  const place = [100,1000,10000][rnd(0,2)];
  const digit = rnd(1,9);
  const n = makeNumberWithDigitAtPlace(place,digit);
  return {
    topic:"Representing Numbers",
    prompt:`In ${fmt(n)}, what is the value of the digit in the ${PLACE_NAMES[place]} place?`,
    display:fmt(n),
    highlightPlace:place,
    answer:String(digit*place),
    type:"number"
  };
}
function compareQuestion(){
  let a=rnd(10000,999999), b=rnd(10000,999999);
  if(a===b) b++;
  return {topic:"Compare & Order",prompt:"Which symbol makes this statement correct?",display:`${fmt(a)}  ___  ${fmt(b)}`,answer:a>b?">":"<",type:"select",options:["<",">","="]};
}
function orderQuestion(){
  let nums;
  do { nums=[rnd(10000,999999),rnd(10000,999999),rnd(10000,999999)]; } while(new Set(nums).size<3);
  return {topic:"Compare & Order",prompt:"Which of these numbers is the smallest?",display:nums.map(fmt).join("   •   "),answer:String(Math.min(...nums)),type:"number"};
}
function roundingQuestion(){
  const place=[10,100,1000,10000][rnd(0,3)];
  const n=rnd(10000,999999);
  return {topic:"Rounding & Estimation",prompt:`Round ${fmt(n)} to the nearest ${PLACE_NAMES[place].replace(/s$/,"")}.`,display:"",answer:String(Math.round(n/place)*place),type:"number"};
}
function estimateQuestion(){
  const a=rnd(12000,89000), b=rnd(12000,89000);
  const answer=Math.round(a/10000)*10000 + Math.round(b/10000)*10000;
  return {topic:"Rounding & Estimation",prompt:"Estimate the sum. Round each number to the nearest ten thousand first.",display:`${fmt(a)} + ${fmt(b)}`,answer:String(answer),type:"number"};
}
function reasoningQuestion(i){
  const set=[
    {topic:"Reasoning",prompt:"A six-digit number has 6 in the hundred-thousands place, 3 in the thousands place, 8 in the tens place and 2 in the ones place. All other digits are zero. What is the number?",display:"",answer:"603082",type:"number"},
    {topic:"Reasoning",prompt:"Which number rounds to 450,000 when rounded to the nearest ten thousand?",display:"Choose one",answer:"447200",type:"select",options:["443,900","447,200","455,100","461,000"]},
    {topic:"Reasoning",prompt:"Compare 398,950 and 400,012. Which number is greater?",display:"",answer:"400012",type:"number"},
    {topic:"Reasoning",prompt:"A stadium attendance was 248,761. Round this attendance to the nearest ten thousand.",display:"",answer:"250000",type:"number"},
    {topic:"Reasoning",prompt:"What is 42,506 multiplied by 10?",display:"",answer:"425060",type:"number"}
  ];
  return set[i%set.length];
}
function buildQuiz(){
  return [
    placeValueQuestion(), identifyPlaceQuestion(), expandedQuestion(), compareQuestion(), roundingQuestion(),
    placeValueQuestion(), expandedQuestion(), orderQuestion(), roundingQuestion(), compareQuestion(),
    digitContributionQuestion(), orderQuestion(), roundingQuestion(), estimateQuestion(), compareQuestion(),
    reasoningQuestion(0), reasoningQuestion(1), reasoningQuestion(2), reasoningQuestion(3), reasoningQuestion(4)
  ];
}

let quiz=[], index=0, score=0, answered=false, attemptSaved=false;
const qn=document.getElementById("qNumber"), ql=document.getElementById("qLevel"), qs=document.getElementById("qScore");
const qp=document.getElementById("quizProgress"), qt=document.getElementById("qTopic"), qprompt=document.getElementById("qPrompt");
const qd=document.getElementById("qDisplay"), qa=document.getElementById("qAnswer"), qf=document.getElementById("qFeedback");
const check=document.getElementById("checkAnswer"), next=document.getElementById("nextQuestion"), result=document.getElementById("resultCard");

function level(){ return index<5?"FOUNDATION":index<10?"DEVELOPING":index<15?"PROFICIENT":"CHALLENGE"; }
function renderNumberDisplay(q){
  if(!q.highlightPlace){ qd.textContent=q.display; return; }
  const raw=String(q.display).replace(/,/g,"");
  const highlightIndex=raw.length-1-Math.log10(q.highlightPlace);
  qd.innerHTML="";
  [...raw].forEach((ch,i)=>{
    if(i>0 && (raw.length-i)%3===0) qd.append(document.createTextNode(","));
    const span=document.createElement("span");
    span.textContent=ch;
    if(i===highlightIndex){ span.className="highlight-digit"; span.setAttribute("aria-label",ch+" highlighted"); }
    qd.append(span);
  });
}
function render(){
  const q=quiz[index];
  answered=false;
  qn.textContent=`${index+1} / 20`;
  ql.textContent=level();
  qs.textContent=`${score} / 20`;
  qp.style.width=`${((index+1)/20)*100}%`;
  qt.textContent=q.topic;
  qprompt.textContent=q.prompt;
  renderNumberDisplay(q);
  qf.textContent="";
  qf.className="q-feedback";
  check.disabled=false;
  next.disabled=true;
  qa.innerHTML="";
  if(q.type==="select"){
    const s=document.createElement("select");
    s.innerHTML='<option value="">Choose an answer</option>'+q.options.map(o=>`<option value="${o.replace(/,/g,"")}">${o}</option>`).join("");
    qa.appendChild(s);
  }else{
    const input=document.createElement("input");
    input.inputMode="numeric";
    input.placeholder="Your answer";
    qa.appendChild(input);
    input.focus();
  }
}
function normal(v){ return String(v).trim().toLowerCase().replace(/,/g,"").replace(/-/g," "); }

check.addEventListener("click",()=>{
  if(answered) return;
  const field=qa.querySelector("input,select");
  if(!field || !field.value.trim()){ qf.textContent="Enter or choose an answer first."; return; }
  answered=true;
  const q=quiz[index];
  const ok=normal(field.value)===normal(q.answer);
  if(ok){
    score++;
    qf.textContent="Correct!";
    qf.className="q-feedback correct";
  }else{
    const shown=q.type==="number"&&!isNaN(Number(q.answer))?fmt(Number(q.answer)):q.answer;
    qf.textContent=`Not quite. The correct answer is ${shown}. Review ${q.topic} before your next attempt.`;
    qf.className="q-feedback incorrect";
  }
  qs.textContent=`${score} / 20`;
  check.disabled=true;
  next.disabled=false;
});

next.addEventListener("click",()=>{ if(index<19){ index++; render(); } else { finish(); } });

async function finish(){
  document.querySelector(".quiz-card").hidden=true;
  result.hidden=false;
  const pct=score*5;
  const msg=score===20?"Perfect score — proficiency achieved!":pct>=85?"Excellent understanding.":pct>=70?"Strong work. Review any concepts you missed.":pct>=50?"Good progress. Revisit the learning pages before another attempt.":"Revisit Pages 1–4, then try the challenge again.";
  result.innerHTML=`<p class="page-tag">CHALLENGE COMPLETE</p><h2>${pct}%</h2><strong>${score} out of 20 correct</strong><p>${msg}</p><p id="saveStatus">Recording completed attempt…</p>`;
  if(attemptSaved) return;
  attemptSaved=true;
  const status=document.getElementById("saveStatus");
  try{
    let tries=0;
    while(!window.MathMagicProgress?.saveWholeNumbersAttempt && tries<20){
      await new Promise(resolve=>setTimeout(resolve,100));
      tries++;
    }
    if(!window.MathMagicProgress?.saveWholeNumbersAttempt) throw new Error("Progress service unavailable");
    const p=await window.MathMagicProgress.saveWholeNumbersAttempt(score);
    if(status) status.textContent=`✓ Attempt recorded • ${Math.min(p.attempts,5)}/5 completed • Best ${p.bestScore}/20${p.proficient?" • PROFICIENT":""}`;
  }catch(e){
    console.error("Progress save failed:",e);
    attemptSaved=false;
    if(status){ status.textContent="This attempt could not be recorded. Please keep this page open and try Finish again."; status.className="incorrect"; }
  }
}
function startQuiz(){
  quiz=buildQuiz(); index=0; score=0; attemptSaved=false;
  document.querySelector(".quiz-card").hidden=false;
  result.hidden=true;
  render();
}
document.getElementById("restartQuiz").addEventListener("click",startQuiz);
qa?.addEventListener("keydown",e=>{ if(e.key==="Enter"&&!check.disabled) check.click(); });
