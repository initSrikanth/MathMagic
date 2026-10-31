// Isolated adapter tests: Firebase/Firestore and DOM are mocks, not live-service proof.
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const source=fs.readFileSync('js/fractions-auth.js','utf8').replace(/^import .*;\n/gm,'');
function harness({cacheFails=false,readFails=false,approved=true,stored={}}={}){
 const data=new Map(Object.entries(stored)),cache=new Map(),redirects=[],writes=[];let listener,queue=Promise.resolve(),uncertain=false;
 const auth={currentUser:{uid:'student-a'}},elements=new Map();
 const element=id=>{if(!elements.has(id))elements.set(id,{textContent:'',classList:{toggle(){}},addEventListener(){}});return elements.get(id)};
 const snapshot=path=>({exists:()=>data.has(path),data:()=>structuredClone(data.get(path))});
 data.set('access/student-a',{approved});
 const context={console:{error(){},warn(){}},window:{},location:{replace:x=>redirects.push(x)},localStorage:{getItem:k=>{if(cacheFails)throw Error('cache blocked');return cache.get(k)||null},setItem:(k,v)=>{if(cacheFails)throw Error('cache blocked');cache.set(k,v)}},document:{getElementById:element,body:{classList:{add(){},remove(){}}}},initializeApp:()=>({}),firebaseConfig:{},getAuth:()=>auth,getFirestore:()=>({}),doc:(_, ...parts)=>parts.join('/'),getDoc:async path=>{if(readFails)throw Error('offline');return snapshot(path)},onAuthStateChanged:(_,fn)=>listener=fn,signOut:async()=>{},runTransaction:(_,callback)=>{
  const task=queue.then(async()=>{
   const changes=[];const result=await callback({get:async path=>snapshot(path),set:(path,value)=>changes.push([path,structuredClone(value)])});
   for(const [path,value] of changes){data.set(path,value);writes.push(path)}
   if(uncertain){uncertain=false;throw Error('acknowledgement lost after commit')}
   return result;
  });queue=task.catch(()=>{});return task;
 }};
 vm.runInNewContext(source,context);
 return {context,auth,data,cache,writes,redirects,login:()=>listener(auth.currentUser),logout:()=>{auth.currentUser=null;return listener(null)},loseAcknowledgement:()=>uncertain=true,service:()=>context.window.MathMagicFractionsProgress};
}
(async()=>{
 const path='progress/student-a/topics/fractions';
 let h=harness();await h.login();assert(h.service());
 const [one,two]=await Promise.all([h.service().saveAttempt(18,'attempt-a-0001'),h.service().saveAttempt(30,'attempt-a-0002')]);
 assert.equal(h.data.get(path).attempts,2);assert.equal(h.data.get(path).bestScore,30);assert.equal(h.data.get(path).lastScore,30);assert.equal(h.data.get(path).proficient,true);
 await h.service().saveAttempt(30,'attempt-a-0002');assert.equal(h.data.get(path).attempts,2,'duplicate event must not increment');
 for(const score of [-1,31,NaN,Infinity,1.5,'30'])await assert.rejects(()=>h.service().saveAttempt(score,'invalid-score-0001'));
 await assert.rejects(()=>h.service().saveAttempt(30,'bad'));assert.equal(h.data.get(path).attempts,2);
 h.loseAcknowledgement();await assert.rejects(()=>h.service().saveAttempt(22,'attempt-a-uncertain'));
 assert.equal(h.data.get(path).attempts,3);await h.service().saveAttempt(22,'attempt-a-uncertain');assert.equal(h.data.get(path).attempts,3,'retry after ambiguous commit must reconcile');
 h.data.set('access/student-a',{approved:false});await assert.rejects(()=>h.service().saveAttempt(30,'attempt-a-revoked'));assert.equal(h.data.get(path).attempts,3);
 h.auth.currentUser={uid:'student-b'};await assert.rejects(()=>h.service().saveAttempt(30,'attempt-a-stale'));assert(!h.data.has('progress/student-b/topics/fractions'));
 await h.logout();assert.equal(h.service(),undefined);assert.equal(h.redirects.at(-1),'index.html');
 h=harness({cacheFails:true,stored:{[path]:{attempts:4,bestScore:21,lastScore:18,proficient:false}}});await h.login();const saved=await h.service().saveAttempt(25,'attempt-cache-blocked');assert.equal(saved.attempts,5);assert.equal(h.data.get(path).attempts,5,'blocked cache cannot turn successful remote save into failure');
 h=harness({readFails:true});await h.login();assert.equal(h.service(),undefined);assert.equal(h.redirects.at(-1),'access-required.html?error=1');assert.equal(h.writes.length,0);
 h=harness({approved:false});await h.login();assert.equal(h.service(),undefined);assert.equal(h.redirects.at(-1),'access-required.html');assert.equal(h.writes.length,0);
 // Existing Firestore progress wins over a stale local cache; unrelated topics stay untouched.
 h=harness({stored:{[path]:{attempts:7,bestScore:28,lastScore:20,proficient:false},'progress/student-a/topics/whole-numbers':{attempts:9}}});h.cache.set('mathmagic:student-a:fractions:progress',JSON.stringify({attempts:99,bestScore:30}));await h.login();await h.service().saveAttempt(29,'attempt-reload-0001');assert.equal(h.data.get(path).attempts,8);assert.equal(h.data.get('progress/student-a/topics/whole-numbers').attempts,9);
 console.log('Fractions progress mocked-adapter checks passed: concurrent transactions, duplicate/ambiguous retries, validation, approval, auth changes, unavailable storage and UID/topic isolation. Live Firebase was not tested.');
})().catch(error=>{console.error(error);process.exitCode=1});
