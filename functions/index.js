'use strict';
const {onCall,HttpsError}=require('firebase-functions/v2/https');
const {initializeApp}=require('firebase-admin/app');
const {getFirestore}=require('firebase-admin/firestore');
const crypto=require('crypto');
initializeApp();
const db=getFirestore(),TOTAL=30;
const rnd=(a,b)=>Math.floor(Math.random()*(b-a+1))+a,choice=a=>a[rnd(0,a.length-1)];
function gcd(a,b){while(b)[a,b]=[b,a%b];return Math.abs(a)||1} function simp(n,d){const g=gcd(n,d);return[n/g,d/g]}
function same(op='+'){const d=choice([4,5,6,8,10,12]);let a=rnd(1,d-2),b=rnd(1,d-2);if(op==='-'&&b>=a)[a,b]=[Math.max(a,b),Math.min(a,b)];return{topic:'Same Denominators',prompt:op==='+'?'Add and simplify.':'Subtract and simplify.',parts:[[a,d],op,[b,d]],answer:simp(op==='+'?a+b:a-b,d),type:'fraction',strict:true,solution:'Work with the numerators because the parts are the same size, then simplify.'}}
function equivalent(){const d=choice([3,4,5,6,8]),n=rnd(1,d-1),m=rnd(2,4);return{topic:'Equivalent Fractions',prompt:'Find the missing numerator.',parts:[[n,d],'=',['?',d*m]],answer:n*m,type:'single',solution:'Multiply the numerator and denominator by the same factor.'}}
function compare(){const d=choice([4,5,6,8,10]),a=rnd(1,d-1),b=rnd(1,d-1);return{topic:'Compare Fractions',prompt:'Choose the correct symbol.',parts:[[a,d],'___',[b,d]],answer:a>b?'>':a<b?'<':'=',type:'choice',options:['<','=','>'],solution:'With equal denominators, compare the numerators.'}}
function related(op='+'){const pair=choice([[2,4],[2,6],[3,6],[4,8],[5,10],[6,12]]),d1=pair[0],d2=pair[1];let a=rnd(1,d1-1),b=rnd(1,d2-1);if(op==='-'&&a/d1<=b/d2){a=d1-1;b=1}const n=op==='+'?a*(d2/d1)+b:a*(d2/d1)-b;return{topic:'Related Denominators',prompt:(op==='+'?'Add':'Subtract')+' and simplify.',parts:[[a,d1],op,[b,d2]],answer:simp(n,d2),type:'fraction',strict:true,solution:'Rename using the larger related denominator, calculate, then simplify.'}}
function visual(){const d=choice([6,8,10,12]),n=rnd(2,d-2);return{topic:'Visual Fractions',prompt:'The bar represents one whole. What fraction is shaded? Give your answer in simplest form.',visual:{kind:'bar',parts:d,filled:n},answer:simp(n,d),type:'fraction',strict:true,solution:'Count the shaded equal parts and simplify.'}}
function numberLine(){const d=choice([4,5,6,8]),n=rnd(1,d-1);return{topic:'Number Line',prompt:'What fraction is shown by the marker?',visual:{kind:'numberLine',parts:d,marker:n},answer:simp(n,d),type:'fraction',solution:'Count equal intervals from 0 to the marker.'}}
function improper(){const d=choice([3,4,5,6]),w=rnd(1,3),r=rnd(1,d-1);return{topic:'Mixed Numbers',prompt:'Change this improper fraction to a mixed number.',parts:[[w*d+r,d]],answer:[w,r,d],type:'mixed',solution:'Divide the numerator by the denominator.'}}
function word(){const set=choice([[[1,2],[1,4]],[[1,3],[1,6]],[[2,5],[1,5]]]),a=set[0],b=set[1],den=b[1],ans=simp(a[0]*(den/a[1])+b[0],den);return{topic:'Problem Solving',prompt:'A class uses '+a[0]+'/'+a[1]+' of a display for research and '+b[0]+'/'+b[1]+' for diagrams. What fraction is used altogether?',answer:ans,type:'fraction',strict:true,solution:'Rename the related fractions, add, then simplify.'}}
const bands=[['FOUNDATION',[visual,numberLine,compare,equivalent,visual]],['DEVELOPING',[()=>same('+'),()=>same('-'),equivalent,compare,()=>same('+')]],['DEVELOPING +',[improper,compare,equivalent,numberLine,improper]],['PROFICIENT',[()=>related('+'),()=>related('-'),()=>same('+'),()=>same('-'),()=>related('+')]],['APPLICATION',[word,()=>related('+'),word,()=>related('-'),word]],['CHALLENGE',[()=>related('+'),()=>related('-'),word,()=>same('+'),()=>same('-')]]];
function build(){return bands.flatMap(([level,fs])=>fs.map(f=>({...f(),level}))).slice(0,TOTAL)}
function publicQ(q,i){const {answer,solution,...safe}=q;return{...safe,index:i+1,total:TOTAL}}
async function approved(uid){const s=await db.doc('access/'+uid).get();return s.exists&&s.data().approved===true}
exports.startFractionsChallenge=onCall({enforceAppCheck:true},async req=>{if(!req.auth)throw new HttpsError('unauthenticated','Sign in required.');if(!(await approved(req.auth.uid)))throw new HttpsError('permission-denied','MathMagic approval required.');const qs=build(),id=crypto.randomUUID(),answers=qs.map(q=>({answer:q.answer,solution:q.solution,type:q.type,strict:!!q.strict}));await db.doc('challengeSessions/'+id).set({uid:req.auth.uid,topic:'fractions',answers,createdAt:Date.now(),nextIndex:0,score:0,complete:false});return{sessionId:id,question:publicQ(qs[0],0)};});
exports.submitFractionsAnswer=onCall({enforceAppCheck:true},async req=>{if(!req.auth)throw new HttpsError('unauthenticated','Sign in required.');const id=String(req.data?.sessionId||''),index=Number(req.data?.index),response=req.data?.response;if(!id)throw new HttpsError('invalid-argument','Missing session.');const ref=db.doc('challengeSessions/'+id);return db.runTransaction(async tx=>{const s=await tx.get(ref);if(!s.exists)throw new HttpsError('not-found','Session expired.');const d=s.data();if(d.uid!==req.auth.uid)throw new HttpsError('permission-denied','Wrong session owner.');if(d.complete||index!==d.nextIndex)throw new HttpsError('failed-precondition','Question is not current.');const key=d.answers[index],eq=(a,b)=>Array.isArray(a)&&Array.isArray(b)&&a.length===b.length&&a.every((v,i)=>Number(v)===Number(b[i]));let ok=false;if(key.type==='choice'||key.type==='single')ok=String(response)===String(key.answer);else if(Array.isArray(response)&&Array.isArray(key.answer)){if(key.type==='fraction'&&response.length===2){const n=response[0],den=response[1],an=key.answer[0],ad=key.answer[1];ok=Number(den)!==0&&Number(n)*Number(ad)===Number(an)*Number(den);if(key.strict)ok=ok&&Number(n)===Number(an)&&Number(den)===Number(ad)}else ok=eq(response,key.answer)}const score=d.score+(ok?1:0),next=index+1,complete=next>=TOTAL;tx.update(ref,{score,nextIndex:next,complete});return{correct:ok,solution:ok?null:key.solution,answer:ok?null:key.answer,score,complete,nextIndex:next};});});


// Decimals & Percentages protected-content pilot.
// Topic-exclusive Year 5 rules: decimal place value to thousandths; compare/order/locate
// decimals; percent as out of 100/relative size; common fraction-decimal-percentage
// equivalence. Percentage-of-quantity calculations are deliberately excluded.
const DP_CONNECTS=[[1,2,0.5,50],[1,4,0.25,25],[3,4,0.75,75],[1,10,0.1,10],[1,5,0.2,20]];
const dpShuffle=a=>{a=[...a];for(let i=a.length-1;i>0;i--){const j=rnd(0,i);[a[i],a[j]]=[a[j],a[i]]}return a};
const dpChoice=(topic,prompt,display,options,answer,solution)=>({topic,prompt,display,options:options.map(String),answer:String(answer),type:'choice',solution});
const dpNumber=(topic,prompt,display,answer,solution)=>({topic,prompt,display,answer:String(answer),type:'number',solution});
function dpPlace(){const whole=rnd(1,19),ds=[rnd(1,9),rnd(0,9),rnd(1,9)],i=rnd(0,2),names=['tenths','hundredths','thousandths'];return dpChoice('Decimal Place Value','Which place is the digit '+ds[i]+' in?',whole+'.'+ds.join(''),['tenths','hundredths','thousandths','ones'],names[i],'Read the decimal from left to right: tenths, hundredths, then thousandths.')}
function dpValue(){const whole=rnd(1,9),ds=[rnd(1,9),rnd(0,9),rnd(1,9)],i=rnd(0,2),vals=[ds[0]/10,ds[1]/100,ds[2]/1000],names=['tenths','hundredths','thousandths'];return dpNumber('Decimal Place Value','What is the value of the digit in the '+names[i]+' place?',whole+'.'+ds.join(''),vals[i],'Use the place of the digit to determine its value.')}
function dpCompare(){let a=rnd(1001,9999),b=rnd(1001,9999);while(a===b)b=rnd(1001,9999);return dpChoice('Compare Decimals','Which symbol makes the statement correct?',(a/1000).toFixed(3)+' ___ '+(b/1000).toFixed(3),['<','=','>'],a<b?'<':'>','Compare whole numbers, then tenths, hundredths and thousandths.')}
function dpOrder(){const s=new Set();while(s.size<3)s.add((rnd(101,999)/100).toFixed(2));const v=[...s],ans=Math.min(...v.map(Number)).toFixed(2);return dpChoice('Order Decimals','Which decimal is the smallest?',v.join(' • '),v,ans,'Compare corresponding place values from left to right.')}
function dpPercentMeaning(){const p=choice([10,20,25,40,50,60,75,80]);return dpChoice('Understanding Percent',p+'% means which amount out of 100?',p+'%',dpShuffle([p+' out of 100',p+' out of 10',(100-p)+' out of 100','100 out of '+p]),p+' out of 100','Percent means per hundred.')}
function dpF2P(){const [n,d,,p]=choice(DP_CONNECTS),pool=dpShuffle([10,20,25,50,75,80].filter(x=>x!==p)).slice(0,3);return dpChoice('Connect Representations','Which percentage is equivalent to '+n+'/'+d+'?',{kind:'fraction',numerator:n,denominator:d},dpShuffle([p,...pool]),p,'Rename the fraction as an equivalent amount out of 100.')}
function dpD2P(){const [,,dec,p]=choice(DP_CONNECTS),pool=dpShuffle([10,20,25,50,75,80].filter(x=>x!==p)).slice(0,3);return dpChoice('Connect Representations','Which percentage is equivalent to '+dec+'?',String(dec),dpShuffle([p,...pool]),p,'Use the known decimal and percentage equivalence.')}
function dpP2D(){const [,,dec,p]=choice(DP_CONNECTS),pool=DP_CONNECTS.filter(x=>x[2]!==dec).map(x=>x[2]);return dpChoice('Connect Representations','Which decimal is equivalent to '+p+'%?',p+'%',dpShuffle([dec,...dpShuffle(pool).slice(0,3)]),dec,'Percent describes hundredths; connect it to the equivalent decimal.')}
function dpP2F(){const [n,d,,p]=choice(DP_CONNECTS),others=DP_CONNECTS.filter(x=>x[3]!==p).slice(0,3).map(x=>x[0]+'/'+x[1]);return dpChoice('Connect Representations','Which fraction is equivalent to '+p+'%?',p+'%',dpShuffle([n+'/'+d,...others]),n+'/'+d,'Match the percentage to a familiar equivalent fraction.')}
function dpLocate(){const base=rnd(1,6),step=rnd(1,9),ans=(base+step/100).toFixed(2),pool=[(base+step/10).toFixed(2),(base+(step===5?4:10-step)/100).toFixed(2),(base+.1+step/100).toFixed(2)];return dpChoice('Decimals on a Number Line','Which decimal is '+step+' hundredths after '+base.toFixed(2)+'?',{kind:'numberLine',start:base.toFixed(2),end:(base+.1).toFixed(2)},dpShuffle([ans,...pool.filter(x=>x!==ans).slice(0,3)]),ans,'Move by hundredths, not tenths.')}
function dpRelative(){let a=choice([20,25,40,50,60,75,80]),b=choice([10,25,50,75,90]);while(a===b)b=choice([10,25,50,75,90]);return dpChoice('Compare Percentages','Which percentage is the greater relative amount?',a+'% or '+b+'%',[a+'%',b+'%','They are equal','Not enough information'],Math.max(a,b)+'%','Percentages use the same scale of 100, so compare their values directly.')}
function dpReason(){return choice([
 ()=>dpChoice('Reasoning','A battery is 0.75 full. Which percentage is equivalent?','0.75',['25%','50%','75%','100%'],'75%','0.75 is 75 hundredths, so it is 75%.'),
 ()=>dpChoice('Reasoning','Which decimal lies between 2.4 and 2.5?','2.4 < ? < 2.5',['2.35','2.405','2.45','2.505'],'2.45','Write 2.4 as 2.40 and compare hundredths.'),
 ()=>dpChoice('Reasoning','Which statement is true?','Equivalent decimal notation',['3.5 = 3.050','3.5 = 3.500','3.5 < 3.05','3.5 = 3.005'],'3.5 = 3.500','Zeros added after the final decimal digit do not change the value.'),
 ()=>dpChoice('Reasoning','A student says 0.62 < 0.599 because 62 < 599. What is correct?','Compare place values',['0.62 < 0.599','0.62 = 0.599','0.62 > 0.599','They cannot be compared'],'0.62 > 0.599','Write 0.62 as 0.620, then compare place values.')
 ])()}
const DP_BANDS=[
 ['FOUNDATION',[dpPlace,dpValue,dpPercentMeaning,dpF2P,dpD2P]],
 ['DEVELOPING',[dpCompare,dpOrder,dpP2D,dpP2F,dpLocate]],
 ['DEVELOPING +',[dpLocate,dpCompare,dpRelative,dpD2P,dpF2P]],
 ['PROFICIENT',[dpOrder,dpRelative,dpP2D,dpReason,dpReason]],
 ['APPLICATION',[dpRelative,dpReason,dpReason,dpP2F,dpD2P]],
 ['CHALLENGE',[dpReason,dpLocate,dpRelative,dpReason,dpCompare]]
];
function buildDecimalsPercentages(){return DP_BANDS.flatMap(([level,makers])=>dpShuffle(makers.map(make=>({...make(),level})))).slice(0,TOTAL)}
function publicDecimalQ(q,i){const {answer,solution,...safe}=q;return{...safe,index:i+1,total:TOTAL}}
exports.startDecimalsPercentagesChallenge=onCall({enforceAppCheck:true},async req=>{
 if(!req.auth)throw new HttpsError('unauthenticated','Sign in required.');
 if(!(await approved(req.auth.uid)))throw new HttpsError('permission-denied','MathMagic approval required.');
 const qs=buildDecimalsPercentages(),id=crypto.randomUUID();
 const answers=qs.map(q=>({answer:q.answer,solution:q.solution,type:q.type}));
 const questions=qs.map((q,i)=>publicDecimalQ(q,i));
 await db.doc('challengeSessions/'+id).set({uid:req.auth.uid,topic:'decimals-percentages',answers,questions,createdAt:Date.now(),nextIndex:0,score:0,complete:false});
 return{sessionId:id,question:questions[0]};
});
exports.submitDecimalsPercentagesAnswer=onCall({enforceAppCheck:true},async req=>{
 if(!req.auth)throw new HttpsError('unauthenticated','Sign in required.');
 const id=String(req.data?.sessionId||''),index=Number(req.data?.index),response=req.data?.response;
 if(!id)throw new HttpsError('invalid-argument','Missing session.');
 const ref=db.doc('challengeSessions/'+id);
 return db.runTransaction(async tx=>{
  const s=await tx.get(ref);if(!s.exists)throw new HttpsError('not-found','Session expired.');
  const d=s.data();if(d.uid!==req.auth.uid)throw new HttpsError('permission-denied','Wrong session owner.');
  if(d.topic!=='decimals-percentages'||d.complete||index!==d.nextIndex)throw new HttpsError('failed-precondition','Question is not current.');
  const key=d.answers[index],ok=key.type==='number'?Number.isFinite(Number(response))&&Math.abs(Number(response)-Number(key.answer))<1e-9:String(response)===String(key.answer);
  const score=d.score+(ok?1:0),next=index+1,complete=next>=TOTAL;
  tx.update(ref,{score,nextIndex:next,complete});
  return{correct:ok,solution:ok?null:key.solution,answer:ok?null:key.answer,score,complete,nextIndex:next,question:complete?null:d.questions[next]};
 });
});


// Whole Numbers & Place Value protected-content pilot.
// Topic-exclusive Year 5 rules: whole-number place value/representation/comparison;
// decimal place value to thousandths; compare/order/locate decimals; powers-of-ten
// place relationships; whole-number rounding/estimation for reasonableness.
const wnShuffle=a=>{a=[...a];for(let i=a.length-1;i>0;i--){const j=rnd(0,i);[a[i],a[j]]=[a[j],a[i]]}return a};
const WN_PLACES={10:'tens',100:'hundreds',1000:'thousands',10000:'ten thousands',100000:'hundred thousands'};
function wnPlace(){const place=choice([10,100,1000,10000,100000]),digit=rnd(1,9),n=Math.floor(rnd(100000,999999)/(place*10))*(place*10)+digit*place+rnd(0,place-1);return{topic:'Whole-number place value',prompt:'What is the value of the specified digit?',display:String(n),detail:{digit,place:WN_PLACES[place]},answer:String(digit*place),type:'number',solution:'Use the digit position to find its place value.'}}
function wnExpanded(){const n=rnd(100000,999999),parts=[];[100000,10000,1000,100,10,1].forEach(p=>{const d=Math.floor(n/p)%10;if(d)parts.push(d*p)});return{topic:'Representing numbers',prompt:'What whole number is shown by this expanded form?',display:parts.join(' + '),answer:String(n),type:'number',solution:'Combine the place-value parts to rebuild the number.'}}
function wnCompare(){let a=rnd(10000,999999),b=rnd(10000,999999);while(a===b)b=rnd(10000,999999);return{topic:'Compare whole numbers',prompt:'Choose the correct symbol.',display:a+' ___ '+b,options:['<','=','>'],answer:a>b?'>':'<',type:'choice',solution:'Compare from the greatest place value.'}}
function wnDecimalValue(){const w=rnd(0,9),t=rnd(0,9),h=rnd(0,9),th=rnd(1,9),place=choice(['tenths','hundredths','thousandths']),digit=place==='tenths'?t:place==='hundredths'?h:th,value=place==='tenths'?digit/10:place==='hundredths'?digit/100:digit/1000;return{topic:'Decimal place value',prompt:'What is the value of the digit in the '+place+' place?',display:w+'.'+t+h+th,answer:String(value),type:'number',solution:'Read the digit using its decimal place.'}}
function wnDecimalCompare(){const base=rnd(0,4),a=(base+rnd(1,999)/1000).toFixed(3),b=(base+rnd(1,999)/1000).toFixed(3);if(a===b)return wnDecimalCompare();return{topic:'Compare decimals',prompt:'Choose the correct symbol.',display:a+' ___ '+b,options:['<','=','>'],answer:Number(a)>Number(b)?'>':'<',type:'choice',solution:'Compare ones, tenths, hundredths and thousandths in order.'}}
function wnDecimalLine(){const start=rnd(0,3),k=rnd(1,9),ans=(start+k/100).toFixed(2);return{topic:'Decimal number line',prompt:'The interval is split into 10 equal hundredth steps. What decimal is at mark '+k+'?',display:{kind:'numberLine',start:start.toFixed(2),end:(start+.1).toFixed(2),mark:k},answer:ans,type:'number',solution:'Each step is one hundredth.'}}
function wnRelation10(){const digit=rnd(1,9),a=digit/10,b=digit/100;return{topic:'Place-value relationships',prompt:'How many times greater is '+a+' than '+b+'?',display:a+' compared with '+b,answer:'10',type:'number',solution:'Moving one place left makes a digit value 10 times greater.'}}
function wnRound(){const n=rnd(10000,999999),place=choice([100,1000,10000]);return{topic:'Whole-number estimation',prompt:'Round '+n+' to the nearest '+WN_PLACES[place].replace(/s$/,'')+'.',display:String(n),answer:String(Math.round(n/place)*place),type:'number',solution:'Use the digit immediately to the right of the rounding place.'}}
function wnReason(){return choice([
 ()=>({topic:'Reasoning',prompt:'Which statement is true?',display:'4.7 and 4.700',options:['4.7 < 4.700','4.7 = 4.700','4.7 > 4.700'],answer:'4.7 = 4.700',type:'choice',solution:'Trailing zeros do not change a decimal value.'}),
 ()=>({topic:'Reasoning',prompt:'A student compares 2.407 and 2.47 as whole-number digit strings. Which correction is true?',display:'2.407 ___ 2.470',options:['2.407 < 2.470','2.407 > 2.470','They cannot be compared'],answer:'2.407 < 2.470',type:'choice',solution:'Align equal place values before comparing.'})
 ])()}
const WN_BANDS=[
 ['FOUNDATION',[wnPlace,wnExpanded,wnCompare,wnDecimalValue,wnRelation10]],
 ['DEVELOPING',[wnDecimalValue,wnDecimalCompare,wnDecimalLine,wnRelation10,wnRound]],
 ['DEVELOPING +',[wnDecimalCompare,wnDecimalLine,wnDecimalValue,wnRound,wnReason]],
 ['PROFICIENT',[wnDecimalLine,wnDecimalCompare,wnRound,wnReason,wnRelation10]],
 ['APPLICATION',[wnRound,wnDecimalLine,wnReason,wnCompare,wnDecimalCompare]],
 ['CHALLENGE',[wnReason,wnDecimalLine,wnRound,wnDecimalCompare,wnPlace]]
];
function buildWholeNumbers(){return WN_BANDS.flatMap(([level,makers])=>wnShuffle(makers.map(make=>({...make(),level})))).slice(0,TOTAL)}
function publicWholeQ(q,i){const {answer,solution,...safe}=q;return{...safe,index:i+1,total:TOTAL}}
exports.startWholeNumbersChallenge=onCall({enforceAppCheck:true},async req=>{
 if(!req.auth)throw new HttpsError('unauthenticated','Sign in required.');
 if(!(await approved(req.auth.uid)))throw new HttpsError('permission-denied','MathMagic approval required.');
 const qs=buildWholeNumbers(),id=crypto.randomUUID(),answers=qs.map(q=>({answer:q.answer,solution:q.solution,type:q.type})),questions=qs.map((q,i)=>publicWholeQ(q,i));
 await db.doc('challengeSessions/'+id).set({uid:req.auth.uid,topic:'whole-numbers',answers,questions,createdAt:Date.now(),nextIndex:0,score:0,complete:false});
 return{sessionId:id,question:questions[0]};
});
exports.submitWholeNumbersAnswer=onCall({enforceAppCheck:true},async req=>{
 if(!req.auth)throw new HttpsError('unauthenticated','Sign in required.');
 const id=String(req.data?.sessionId||''),index=Number(req.data?.index),response=req.data?.response;if(!id)throw new HttpsError('invalid-argument','Missing session.');
 const ref=db.doc('challengeSessions/'+id);
 return db.runTransaction(async tx=>{
  const s=await tx.get(ref);if(!s.exists)throw new HttpsError('not-found','Session expired.');
  const d=s.data();if(d.uid!==req.auth.uid)throw new HttpsError('permission-denied','Wrong session owner.');
  if(d.topic!=='whole-numbers'||d.complete||index!==d.nextIndex)throw new HttpsError('failed-precondition','Question is not current.');
  const key=d.answers[index],ok=key.type==='number'?String(response).replace(/,/g,'').trim()===String(key.answer).replace(/,/g,'').trim():String(response)===String(key.answer);
  const score=d.score+(ok?1:0),next=index+1,complete=next>=TOTAL;tx.update(ref,{score,nextIndex:next,complete});
  return{correct:ok,solution:ok?null:key.solution,answer:ok?null:key.answer,score,complete,nextIndex:next,question:complete?null:d.questions[next]};
 });
});

/* Addition & Subtraction protected Year 5 pilot. Whole-number efficient strategies,
   estimation/reasonableness and practical modelling only; decimal arithmetic excluded. */
function asN(topic,prompt,display,answer){return{topic,prompt,display,answer:String(answer),type:'number',solution:'Choose an efficient addition or subtraction strategy and check reasonableness.'}}
function asAdd(){const a=rnd(1000,89999),b=rnd(1000,89999);return asN('Addition','Calculate exactly.',a+' + '+b,a+b)}
function asSub(){let a=rnd(12000,99999),b=rnd(1000,89999);if(b>a)[a,b]=[b,a];return asN('Subtraction','Calculate exactly.',a+' − '+b,a-b)}
function asEst(){const a=rnd(25,95)*1000+rnd(0,999),b=rnd(10,45)*1000+rnd(0,999);return asN('Estimation','Estimate by rounding to the nearest ten thousand.',a+' + '+b,Math.round(a/10000)*10000+Math.round(b/10000)*10000)}
function asUnknown(){const x=rnd(1500,15000),b=rnd(1200,9000);return asN('Missing Value','Find the missing number.','□ + '+b+' = '+(x+b),x)}
function asProblem(){const t=rnd(18000,45000),h=rnd(7000,t-3000);return asN('Problem Solving','A project needs $'+t+' and has $'+h+'. How much more is needed?','Choose the operation.',t-h)}
function asTwo(){const s=rnd(12000,30000),a=rnd(1500,5000),r=rnd(500,1400);return asN('Two-step Problem','Start with '+s+', add '+a+', then remove '+r+'.','Model both changes.',s+a-r)}
const AS_BANDS=[['FOUNDATION',[asAdd,asSub,asAdd,asSub,asEst]],['DEVELOPING',[asAdd,asSub,asEst,asUnknown,asAdd]],['DEVELOPING +',[asSub,asUnknown,asAdd,asEst,asProblem]],['PROFICIENT',[asProblem,asTwo,asEst,asUnknown,asSub]],['APPLICATION',[asTwo,asProblem,asUnknown,asEst,asProblem]],['CHALLENGE',[asTwo,asProblem,asEst,asUnknown,asTwo]]];
function buildAdditionSubtraction(){return AS_BANDS.flatMap(([level,fs])=>fs.map(f=>({...f(),level}))).slice(0,TOTAL)}
function publicAS(q,i){const{answer,solution,...safe}=q;return{...safe,index:i+1,total:TOTAL}}
exports.startAdditionSubtractionChallenge=onCall({enforceAppCheck:true},async req=>{if(!req.auth)throw new HttpsError('unauthenticated','Sign in required.');if(!(await approved(req.auth.uid)))throw new HttpsError('permission-denied','MathMagic approval required.');const qs=buildAdditionSubtraction(),id=crypto.randomUUID(),answers=qs.map(q=>({answer:q.answer,solution:q.solution,type:q.type})),questions=qs.map((q,i)=>publicAS(q,i));await db.doc('challengeSessions/'+id).set({uid:req.auth.uid,topic:'addition-subtraction',answers,questions,createdAt:Date.now(),nextIndex:0,score:0,complete:false});return{sessionId:id,question:questions[0]};});
exports.submitAdditionSubtractionAnswer=onCall({enforceAppCheck:true},async req=>{if(!req.auth)throw new HttpsError('unauthenticated','Sign in required.');const id=String(req.data?.sessionId||''),index=Number(req.data?.index),response=req.data?.response;if(!id)throw new HttpsError('invalid-argument','Missing session.');const ref=db.doc('challengeSessions/'+id);return db.runTransaction(async tx=>{const s=await tx.get(ref);if(!s.exists)throw new HttpsError('not-found','Session expired.');const d=s.data();if(d.uid!==req.auth.uid)throw new HttpsError('permission-denied','Wrong session owner.');if(d.topic!=='addition-subtraction'||d.complete||index!==d.nextIndex)throw new HttpsError('failed-precondition','Question is not current.');const key=d.answers[index],ok=String(response).replace(/[$, ]/g,'').trim()===String(key.answer).replace(/[$, ]/g,'').trim(),score=d.score+(ok?1:0),next=index+1,complete=next>=TOTAL;tx.update(ref,{score,nextIndex:next,complete});return{correct:ok,solution:ok?null:key.solution,answer:ok?null:key.answer,score,complete,nextIndex:next,question:complete?null:d.questions[next]};});});

/* Multiplication & Division protected Year 5 pilot. Whole-number multiplication by one/two-digit numbers and division by a single-digit number. */
function mdN(topic,prompt,display,answer,solution='Use multiplication facts, place value, inverse operations and estimation to check reasonableness.',type='number',options){return{topic,prompt,display,answer:String(answer),type,solution,...(options?{options}:{})}}
function mdMult1(){const a=rnd(120,9999),b=rnd(2,9);return mdN('Multiplication','Calculate exactly.',a+' × '+b,a*b)}
function mdMult2(){const a=rnd(120,9999),b=rnd(10,99);return mdN('Multiplication','Calculate exactly.',a+' × '+b,a*b)}
function mdDiv(){const d=rnd(2,9),q=rnd(25,1200);return mdN('Division','Calculate exactly.',(d*q)+' ÷ '+d,q)}
function mdUnknown(){const a=rnd(12,180),b=rnd(2,9);return mdN('Unknown Value','Find □.','□ × '+b+' = '+(a*b),a)}
function mdEstimate(){const a=rnd(180,950),b=rnd(11,49),A=Math.round(a/100)*100,B=Math.round(b/10)*10;return mdN('Estimation','Estimate using friendly rounded numbers.',a+' × '+b,A*B,'Round to useful numbers, then multiply to check the size of the exact answer.')}
function mdRemainder(){const d=rnd(2,9),q=rnd(10,80),r=rnd(1,d-1);return mdN('Remainders','What is the remainder?',(d*q+r)+' ÷ '+d,r)}
function mdDecimalQuotient(){const d=choice([2,4,5,8]),q=rnd(3,30),r=choice(Array.from({length:d-1},(_,i)=>i+1)),a=d*q+r,ans=String(Number((a/d).toFixed(3)));return mdN('Division result','Express the result as a decimal.',a+' ÷ '+d,ans,'The remainder is part of the divisor: '+r+' ÷ '+d+'. Combine it with the whole-number quotient.')}
function mdFractionQuotient(){const d=choice([2,3,4,5,6,8]),q=rnd(2,20),r=rnd(1,d-1),g=(a,b)=>b?g(b,a%b):a,k=g(r,d),nr=r/k,nd=d/k,a=d*q+r,ans=q+' '+nr+'⁄'+nd,candidates=[ans,(q+1)+' '+nr+'⁄'+nd,String(q),(q-1)+' '+nr+'⁄'+nd],opts=[...new Set(candidates)];return mdN('Division result','Which mixed number represents the result?',a+' ÷ '+d,ans,'Write the remainder as a fraction of the divisor, then simplify the fractional part.','choice',opts)}
function mdGroups(){const size=rnd(4,9),q=rnd(20,90),r=rnd(1,size-1),total=size*q+r;return mdN('Remainders','How many groups are needed so everyone is included?',total+' people, '+size+' per group',q+1,'The remainder means another group is needed, so round the quotient up.')}
function mdModel(){const n=rnd(12,80),each=rnd(12,45);return mdN('Modelling','A supplier packs '+each+' items in each box. How many items are in '+n+' boxes?','Choose the operation.',n*each,'Equal groups require multiplication.')}
function mdDivideModel(){const d=rnd(2,9),q=rnd(30,300),a=d*q;return mdN('Modelling',a+' items are shared equally among '+d+' groups. How many per group?','Choose the operation.',q,'Equal sharing requires division.')}
function mdTwoStep(){const teams=rnd(4,9),per=rnd(12,35),extra=rnd(2,9);return mdN('Two-step Reasoning','A club has '+teams+' teams with '+per+' students in each team. Then '+extra+' more students join each team. How many students are there now?','Choose and sequence the operations.',teams*(per+extra),'First find the new number in each team, then multiply by the number of teams.')}
function mdCompare(){const a=rnd(12,35),b=rnd(12,35),n=rnd(8,24);return mdN('Reasoning','Plan A packs '+a+' items in each of '+n+' boxes. Plan B packs '+b+' items in each of '+n+' boxes. How many more items does the larger plan pack?','Compare the two totals.',Math.abs(a-b)*n,'Compare the products efficiently: difference per box × number of boxes.')}
function mdError(){const a=rnd(120,450),b=rnd(12,25),wrong=a*(b-10);return mdN('Error Analysis','A student says '+a+' × '+b+' = '+wrong+' because they multiplied only by '+(b-10)+'. What should the answer be?','Correct the reasoning.',a*b,'The tens in the two-digit multiplier must also be included.')}
const MD_BANDS=[['FOUNDATION',[mdMult1,mdMult1,mdDiv,mdUnknown,mdEstimate]],['DEVELOPING',[mdMult1,mdMult2,mdDiv,mdUnknown,mdRemainder]],['DEVELOPING +',[mdMult2,mdDiv,mdEstimate,mdFractionQuotient,mdModel]],['PROFICIENT',[mdMult2,mdDecimalQuotient,mdGroups,mdModel,mdDivideModel]],['APPLICATION',[mdMult2,mdGroups,mdFractionQuotient,mdDecimalQuotient,mdTwoStep]],['CHALLENGE',[mdTwoStep,mdCompare,mdError,mdTwoStep,mdCompare]]];
function buildMultiplicationDivision(){return MD_BANDS.flatMap(([level,fs])=>fs.map(f=>({...f(),level}))).slice(0,TOTAL)}
function publicMD(q,i){const{answer,solution,...safe}=q;return{...safe,index:i+1,total:TOTAL}}
exports.startMultiplicationDivisionChallenge=onCall({enforceAppCheck:true},async req=>{if(!req.auth)throw new HttpsError('unauthenticated','Sign in required.');if(!(await approved(req.auth.uid)))throw new HttpsError('permission-denied','MathMagic approval required.');const qs=buildMultiplicationDivision(),id=crypto.randomUUID(),answers=qs.map(q=>({answer:q.answer,solution:q.solution,type:q.type})),questions=qs.map((q,i)=>publicMD(q,i));await db.doc('challengeSessions/'+id).set({uid:req.auth.uid,topic:'multiplication-division',answers,questions,createdAt:Date.now(),nextIndex:0,score:0,complete:false});return{sessionId:id,question:questions[0]};});
exports.submitMultiplicationDivisionAnswer=onCall({enforceAppCheck:true},async req=>{if(!req.auth)throw new HttpsError('unauthenticated','Sign in required.');if(!(await approved(req.auth.uid)))throw new HttpsError('permission-denied','MathMagic approval required.');const id=String(req.data?.sessionId||''),index=Number(req.data?.index),response=req.data?.response,ref=db.doc('challengeSessions/'+id);return db.runTransaction(async tx=>{const s=await tx.get(ref);if(!s.exists)throw new HttpsError('not-found','Session expired.');const d=s.data();if(d.uid!==req.auth.uid)throw new HttpsError('permission-denied','Wrong owner.');if(d.topic!=='multiplication-division'||d.complete||index!==d.nextIndex)throw new HttpsError('failed-precondition','Question is not current.');const k=d.answers[index],ok=String(response).replace(/[, ]/g,'')===String(k.answer).replace(/[, ]/g,''),score=d.score+(ok?1:0),next=index+1,complete=next>=TOTAL;tx.update(ref,{score,nextIndex:next,complete});return{correct:ok,solution:ok?null:k.solution,score,complete,nextIndex:next,question:complete?null:d.questions[next]};});});
