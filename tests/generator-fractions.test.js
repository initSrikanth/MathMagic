'use strict';
// Isolated generator/marking tests. No Firebase, browser or production claims.
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const nodes=new Map();
function node(id){if(!nodes.has(id))nodes.set(id,{value:'',textContent:'',innerHTML:'',className:'',style:{},handlers:{},classList:{toggle(){}},addEventListener(event,fn){this.handlers[event]=fn},querySelectorAll(){return[]}});return nodes.get(id)}
let seed=0x39f5a;
const math=Object.create(Math);math.random=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296};
const context={Math:math,Date,console,document:{querySelectorAll(){return[]},querySelector(){return node('query')},getElementById:node},window:{scrollTo(){}}};
vm.createContext(context);
vm.runInContext(fs.readFileSync('js/fractions.js','utf8')+`\nglobalThis.subject={buildQuiz,fingerprint,stripSubtract,classProjectProblem,estimateReasonable,rich,
setQuestion(q){quiz=[q];index=0;score=0;answered=false;qf.textContent='';qf.className=''},
state(){return {index,score,answered,feedback:qf.textContent,feedbackClass:qf.className}},
check(){check.handlers.click()},next(){next.handlers.click()}};`,context);
const api=context.subject;
const gcd=(a,b)=>b?gcd(b,a%b):Math.abs(a)||1;
const q=(n,d=1)=>{assert(d!==0);const g=gcd(n,d);return[n/g,d/g]};
const add=(a,b)=>q(a[0]*b[1]+b[0]*a[1],a[1]*b[1]);
const sub=(a,b)=>q(a[0]*b[1]-b[0]*a[1],a[1]*b[1]);
const same=(a,b)=>a[0]*b[1]===b[0]*a[1];
const cmp=(a,b)=>a[0]*b[1]===b[0]*a[1]?'=':a[0]*b[1]>b[0]*a[1]?'>':'<';
const fromText=s=>[...s.matchAll(/(\d+)\/(\d+)/g)].map(m=>[Number(m[1]),Number(m[2])]);
const fromHtml=s=>[...s.matchAll(/<span class="frac"><span>(\d+)<\/span><i><\/i><span>(\d+)<\/span><\/span>/g)].map(m=>[Number(m[1]),Number(m[2])]);
const levels=['FOUNDATION','DEVELOPING','DEVELOPING +','PROFICIENT','APPLICATION','CHALLENGE'];
let positions=0,duplicateRemainders=0;const covered=new Map();
for(let attempt=0;attempt<1000;attempt++){
 const quiz=api.buildQuiz();assert.strictEqual(quiz.length,30);const keys=new Set();
 for(let i=0;i<quiz.length;i++){
  const x=quiz[i];positions++;covered.set(x.topic,(covered.get(x.topic)||0)+1);assert.strictEqual(x.level,levels[Math.floor(i/5)]);assert(x.solution,'Missing worked feedback');
  const key=api.fingerprint(x);assert(!keys.has(key),'Duplicate mathematical question');keys.add(key);
  assert(!/\d+\/\d+/.test(api.rich(x.prompt)),'Rendered prompt slash leak');assert(!/\d+\/\d+/.test(api.rich(x.solution)),'Rendered feedback slash leak');
  if(x.options){assert.strictEqual(new Set(x.options).size,x.options.length);assert.strictEqual(x.options.filter(o=>o===x.answer).length,1)}
  if(Array.isArray(x.answer)){assert(x.answer.every(Number.isSafeInteger));assert(x.answer[x.answer.length-1]>0);assert(x.answer.every(n=>n>=0));if(x.type==='mixed')assert(x.answer[1]<x.answer[2]);if(x.strict)assert.strictEqual(gcd(x.answer[0],x.answer[1]),1)}
  const f=fromText(x.prompt);let expected;
  switch(x.topic){
   case 'Same Denominators':case 'Related Denominators':expected=x.parts[1]==='+'?add(x.parts[0],x.parts[2]):sub(x.parts[0],x.parts[2]);break;
   case 'Multi-step Fractions':expected=sub(add(x.parts[0],x.parts[2]),x.parts[4]);break;
   case 'Simplifying':expected=x.parts[0];break;
   case 'Equivalent Fractions':assert.strictEqual(x.answer,x.parts[0][0]*x.parts[2][1]/x.parts[0][1]);break;
   case 'Compare Fractions':case 'Compare Related Fractions':assert.strictEqual(x.answer,cmp(x.parts[0],x.parts[2]));break;
   case 'Compare Mixed Numbers':{const a=fromHtml(x.html);assert.strictEqual(x.answer,cmp(a[0],a[1]));break}
   case 'Mixed Numbers':if(x.type==='mixed'){const a=x.parts[0];assert(same(a,add([x.answer[0],1],x.answer.slice(1))))}else{const a=fromHtml(x.html)[0],w=Number(x.html.match(/<strong>(\d+)<\/strong>/)[1]);expected=add([w,1],a)}break;
   case 'Partition Fractions':{const a=fromHtml(x.html)[0],b=fromText(x.answer);assert(same(a,add(b[0],b[1])));const optionValues=x.options.map(o=>{const p=fromText(o);return add(p[0],p[1]).join('/')});assert.strictEqual(new Set(optionValues).size,4);for(const distractor of x.options.filter(v=>v!==x.answer)){const d=fromText(distractor);assert(!same(a,add(d[0],d[1])))}break}
   case 'Area Model':{const d=Number(x.html.match(/(\d+) of (\d+) equal parts/)[2]);const n=Number(x.html.match(/(\d+) of (\d+) equal parts/)[1]);expected=[n,d];break}
   case 'Strip Model':assert(/of the whole selected/.test(x.prompt));assert(!/of that amount/.test(x.prompt));expected=sub(f[0],f[1]);break;
   case 'Visual Fractions':{const m=x.html.match(/aria-label="(\d+) of (\d+)/);expected=[Number(m[1]),Number(m[2])];break}
   case 'Number Line':{const m=x.html.match(/split into (\d+) equal intervals; blue marker at interval (\d+)/);expected=[Number(m[2]),Number(m[1])];break}
   case 'Number Line Strategy':expected=add(f[0],f[1]);break;
   case 'Problem Solving':case 'Project Planning':{assert(f[0][1]%f[1][1]===0||f[1][1]%f[0][1]===0,'Unrelated denominators in assessed context');if(x.prompt.startsWith('A water tank')){assert.strictEqual(f.length,3);assert(f.every(v=>Math.max(...f.map(t=>t[1]))%v[1]===0));expected=add(sub(f[0],f[1]),f[2]);assert(expected[0]<=expected[1])}else expected=sub([1,1],add(f[0],f[1]));break}
   case 'Measurement Problem':expected=sub(f[0],f[1]);break;
   case 'Reading Challenge':expected=add(f[0],f[1]);break;
   case 'Reasoning in Context':assert.strictEqual(x.answer,cmp(f[0],f[1]));break;
   case 'Estimate First':{const a=fromHtml(x.html),sum=add(a[0],a[1]);assert.deepStrictEqual(Array.from(x.options),['less than 1','equal to 1','greater than 1']);assert.strictEqual(x.answer,sum[0]<sum[1]?'less than 1':sum[0]===sum[1]?'equal to 1':'greater than 1');break}
   case 'Multi-step Problem':expected=sub(sub(f[0],f[1]),f[2]);break;
   case 'Missing Fraction':{const a=fromHtml(x.html);assert(same([x.answer,a[1][1]],sub(a[1],a[0])));break}
   case 'Mixed Number Line':{const m=x.html.match(/from (\d+) to (\d+) split into (\d+) equal intervals; marked point (\d+) intervals/);assert.strictEqual(Number(m[2]),Number(m[1])+1);assert.strictEqual(x.answer[0],Number(m[1]));assert(same(x.answer.slice(1),[Number(m[4]),Number(m[3])]));break}
   case 'Mixed Numerals':{const a=fromHtml(x.html),w=Number(x.html.match(/<strong>(\d+)<\/strong>/)[1]);assert(same(add([w,1],add(a[0],a[1])),add([x.answer[0],1],x.answer.slice(1))));assert.strictEqual(gcd(x.answer[1],x.answer[2]),1);break}
   case 'Order Fractions':{const a=fromText(x.answer);assert(a.every((v,j)=>!j||cmp(a[j-1],v)==='<'));assert.strictEqual(new Set(a.map(v=>q(...v).join('/'))).size,3);break}
   case 'Reasoning':assert.strictEqual(x.answer,'Rename the fractions with a common denominator before adding.');break;
   default:throw new Error('Unverified topic '+x.topic);
  }
  if(expected)assert(same(expected,x.answer),JSON.stringify({x,expected}));
 }
 const remainders=quiz.filter(x=>x.topic==='Project Planning'||x.topic==='Problem Solving').map(x=>api.fingerprint(x));if(new Set(remainders).size<remainders.length)duplicateRemainders++;
}
assert.strictEqual(duplicateRemainders,0);
// Actual marking callbacks with isolated input nodes, including malformed large input.
function checkQuestion(question,values){api.setQuestion(question);for(const[id,v]of Object.entries(values))node(id).value=String(v);api.check();return api.state()}
for(const bad of [{num:'-1',den:'-2'},{num:'1',den:'0'},{num:'9'.repeat(400),den:'9'.repeat(400)}]){const s=checkQuestion({type:'fraction',answer:[1,2]},bad);assert.strictEqual(s.answered,false);assert.strictEqual(s.score,0)}
assert.strictEqual(checkQuestion({type:'fraction',answer:[1,2]},{num:2,den:4}).score,1);
// Both inputs are safe integers, but Number cross-products round these unequal ratios equal.
assert.strictEqual(checkQuestion({type:'fraction',answer:[2,3]},{num:6004799503160659,den:9007199254740988}).score,0);
assert.strictEqual(checkQuestion({type:'fraction',answer:[1,2]},{num:4503599627370495,den:9007199254740990}).score,1);
assert.strictEqual(checkQuestion({type:'fraction',strict:true,answer:[1,2]},{num:2,den:4}).answered,false);
assert.strictEqual(checkQuestion({type:'fraction',strict:true,answer:[1,2]},{num:1,den:2}).score,1);
assert.strictEqual(checkQuestion({type:'mixed',answer:[1,1,2]},{whole:1,num:-1,den:-2}).answered,false);
assert.strictEqual(checkQuestion({type:'mixed',answer:[1,1,2]},{whole:1,num:3,den:2}).answered,false);
assert.strictEqual(checkQuestion({type:'mixed',answer:[1,1,2]},{whole:1,num:2,den:4}).score,1);
api.setQuestion({type:'single',answer:2});api.next();assert.strictEqual(api.state().index,0,'Cannot advance unanswered question');assert.notStrictEqual(node('query').hidden,true,'Cannot finish an unanswered question');
console.log(JSON.stringify({status:'passed',seed:'0x39f5a',attempts:1000,positions,questionFamilies:covered.size,duplicateRemainders,scope:'Isolated seeded generator, exact-answer and marking callbacks; not browser/Firebase integration.'}));
