const fs=require('fs'),vm=require('vm');
const out={method:'1000 deterministic attempts per existing engine; exact normalised prompt/display duplicates only (not a proof of all semantic equivalences or mathematical correctness). Read-only audit; no generator was changed.',topics:[]};
for(const name of ['whole-numbers','decimals-percentages','addition-subtraction','multiplication-division']){
 let source=fs.readFileSync(name==='multiplication-division'?'functions/index.js':'js/'+name+'.js','utf8');
 if(name==='multiplication-division'){source='const TOTAL=30,rnd=(a,b)=>Math.floor(Math.random()*(b-a+1))+a,choice=a=>a[rnd(0,a.length-1)];'+source.slice(source.indexOf('function mdN('),source.indexOf('exports.startMultiplicationDivisionChallenge'))+';globalThis.build=buildMultiplicationDivision;';}
 else {source=source.slice(0,source.indexOf('let quiz='))+';globalThis.build=buildQuiz;';}
 let state=0;const math=Object.create(Math);math.random=()=>{state=(Math.imul(1664525,state)+1013904223)>>>0;return state/4294967296};
 const box={Math:math,document:{querySelectorAll:()=>[]},window:{}};vm.createContext(box);vm.runInContext(source,box);
 const result={topic:name,attempts:1000,positions:0,attempts_with_exact_duplicate:0,duplicate_positions:0,examples:[],equal_plan_comparisons:0};
 for(let seed=1;seed<=1000;seed++){
  state=seed;const qs=box.build();result.positions+=qs.length;const seen=new Map();let dup=false;
  qs.forEach((q,i)=>{
   const key=JSON.stringify([q.prompt,q.display,q.html,q.line]).replace(/\s+/g,' ').trim();
   if(seen.has(key)){dup=true;result.duplicate_positions++;if(result.examples.length<2)result.examples.push({seed,positions:[seen.get(key)+1,i+1],prompt:q.prompt,display:q.display,html:q.html});}else seen.set(key,i);
   if(name==='multiplication-division'&&q.topic==='Reasoning'){
    const m=q.prompt.match(/Plan A packs (\d+).*Plan B packs (\d+)/);if(m&&m[1]===m[2])result.equal_plan_comparisons++;
   }
  });
  if(dup)result.attempts_with_exact_duplicate++;
 }
 out.topics.push(result);
}
fs.writeFileSync('docs/year5/assessment-audit.json',JSON.stringify(out,null,2)+'\n');
console.log(out.topics.map(({examples,...r})=>r));
