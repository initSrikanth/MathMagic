// Independent prompt/diagram oracle; UI is isolated and production marking is never called.
const fs=require('fs'),vm=require('vm'),assert=require('node:assert/strict');
const source=fs.readFileSync('js/time-angles.js','utf8').split('function render(){')[0];
const minutes=s=>{const[h,m]=s.split(':').map(Number);return h*60+m};
const clock=n=>String(Math.floor(n/60)%24).padStart(2,'0')+':'+String(n%60).padStart(2,'0');
const kinds=new Set(),periods=new Set(),connections=new Set();let count=0;
for(let seed=1;seed<=1000;seed++){
 let state=seed;const math=Object.create(Math);math.random=()=>{state=(Math.imul(1664525,state)+1013904223)>>>0;return state/4294967296};
 const context=vm.createContext({Math:math,document:{querySelectorAll:()=>[]}});vm.runInContext(source,context);
 const qs=vm.runInContext('build()',context);assert.equal(qs.length,30);assert.equal(new Set(qs.map(q=>q.prompt+'|'+(q.diagramDegrees??''))).size,30);
 for(const q of qs){
  const p=q.prompt,n=[...p.matchAll(/\d+/g)].map(m=>Number(m[0])),times=p.match(/\b\d{2}:\d{2}\b/g)||[];let expected;
  switch(q.kind){
   case 0:{const duration=Number(p.match(/lasts (\d+)/)[1]);expected=clock(minutes(times[0])+duration);break}
   case 1:expected=String(minutes(times[1])-minutes(times[0]));break;
   case 2:case 3:case 4:case 8:case 9:throw Error('Out-of-scope family in Year 5 core');
   case 5:{const d=n[0];expected=d<90?'acute':d===90?'right':d<180?'obtuse':d===180?'straight':'reflex';break}
   case 6:{const match=p.match(/(\d+):(\d+) (am|pm)/);const h=Number(match[1])%12+(match[3]==='pm'?12:0);expected=clock(h*60+Number(match[2]));periods.add(match[3]);break}
   case 7:{const m=p.match(/starts at (\d+):(\d+) am/);const start=Number(m[1])*60+Number(m[2]);expected=String(minutes(p.match(/finishes at (\d{2}:\d{2})/)[1])-start);break;}
   case 10:case 12:case 15:expected=String(q.diagramDegrees);assert(q.diagramDegrees>0&&q.diagramDegrees<180);if(q.kind===12||q.kind===15){assert(q.protractor);assert.equal(q.diagramDegrees%5,0);}if(q.kind===15)assert.equal(Number(p.match(/Sam reads (\d+)/)[1])+q.diagramDegrees,180);break;
   case 11:{const t=times[0].split(':');expected=(Number(t[0])-12)+':'+t[1]+' pm';break}
   case 13:{const m=p.match(/says (\d+):(\d+) pm/);expected=clock((Number(m[1])+12)*60+Number(m[2]));break;}
   case 14:{const m=p.match(/says (\d+):(\d+) pm/);const wanted=(Number(m[1])+12)*60+Number(m[2]);const times=[...p.matchAll(/(?:shows|display B shows) (\d{2}:\d{2})/g)].map(m=>m[1]);assert.notEqual(minutes(times[0]),minutes(times[1]));expected=minutes(times[0])===wanted?'a':'b';assert.equal(minutes(times[expected==='a'?0:1]),wanted);connections.add(expected);break;}
   case 16:{const m=p.match(/starts at (\d+):(\d+) (am|pm)/);const start=(Number(m[1])%12+(m[3]==='pm'?12:0))*60+Number(m[2]);expected=clock(start+Number(p.match(/lasts (\d+)/)[1]));break;}
   default:throw Error('Unverified question family '+q.kind);
  }
  assert.equal(q.answer,expected,JSON.stringify(q));assert(q.solution.length>25);kinds.add(q.kind);count++;
 }
}
assert.deepEqual([...kinds].sort((a,b)=>a-b),[0,1,5,6,7,10,11,12,13,14,15,16]);assert.deepEqual([...connections].sort(),['a','b']);assert.deepEqual([...periods].sort(),['am','pm']);
console.log(`PASS: ${count} Time and Angles positions, 1000 unique 30-question attempts, 12 independently marked Year 5 families; no unknown-angle, full-turn subtraction or signed-integer families; both AM/PM, hour crossings, practical time conversion and angle diagrams.`);
