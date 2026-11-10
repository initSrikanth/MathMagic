// Independent prompt-based oracle. UI/bootstrap is isolated; no production generator code changes.
const fs=require('fs'),vm=require('vm'),assert=require('node:assert/strict');
const source=fs.readFileSync('js/time-angles.js','utf8').split('function render(){')[0];
const minutes=s=>{const[h,m]=s.split(':').map(Number);return h*60+m};
const clock=n=>String(Math.floor(n/60)%24).padStart(2,'0')+':'+String(n%60).padStart(2,'0');
const kinds=new Set(),periods=new Set();let count=0;
for(let seed=1;seed<=1000;seed++){
 let state=seed;const math=Object.create(Math);math.random=()=>{state=(Math.imul(1664525,state)+1013904223)>>>0;return state/4294967296};
 const context=vm.createContext({Math:math,document:{querySelectorAll:()=>[]}});vm.runInContext(source,context);
 const qs=vm.runInContext('build()',context);assert.equal(qs.length,30);assert.equal(new Set(qs.map(q=>q.prompt+'|'+(q.diagramDegrees??''))).size,30);
 for(const q of qs){
  const p=q.prompt,n=[...p.matchAll(/\d+/g)].map(m=>Number(m[0])),times=p.match(/\b\d{2}:\d{2}\b/g)||[];let expected;
  switch(q.kind){
   case 0:{const duration=Number(p.match(/lasts (\d+)/)[1]);expected=clock(minutes(times[0])+duration);break}
   case 1:expected=String(minutes(times[1])-minutes(times[0]));break;
   case 2:expected=String(180-n[0]);break;
   case 3:case 8:expected=String(360-n[0]-n[1]);break;
   case 4:expected=String(n[0]*360/12);break;
   case 5:{const d=n[0];expected=d<90?'acute':d===90?'right':d<180?'obtuse':d===180?'straight':'reflex';break}
   case 6:{const match=p.match(/(\d+):(\d+) (am|pm)/);const h=Number(match[1])%12+(match[3]==='pm'?12:0);expected=clock(h*60+Number(match[2]));periods.add(match[3]);break}
   case 7:{const t=times.map(minutes);assert(t.every((v,i)=>!i||v>t[i-1]));expected=String(t[3]-t[0]);assert(q.solution.includes('Wait: '+(t[2]-t[1])));break}
   case 9:expected=String(n[1]-90);break;
   case 10:case 12:expected=String(q.diagramDegrees);assert(q.diagramDegrees>0&&q.diagramDegrees<180);if(q.kind===12)assert(q.protractor);break;
   case 11:{const t=times[0].split(':');expected=(Number(t[0])-12)+':'+t[1]+' pm';break}
   default:throw Error('Unverified question family '+q.kind);
  }
  assert.equal(q.answer,expected,JSON.stringify(q));assert(q.solution.length>25);kinds.add(q.kind);count++;
 }
}
assert.equal(kinds.size,13);assert.deepEqual([...periods].sort(),['am','pm']);
console.log(`PASS: ${count} Time and Angles positions, 1000 unique 30-question attempts, 13 independently marked families; both AM/PM, hour crossings, waiting periods and angle diagrams.`);
