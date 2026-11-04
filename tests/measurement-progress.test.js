// Mocked Firebase/Firestore adapter checks; these do not establish live security or persistence.
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const source=fs.readFileSync('js/measurement-auth.js','utf8').replace(/^import .*;\n/gm,'');
function harness({data=new Map(),approved=true,readFails=false,writeFails=false,cacheFails=false}={}){
 const cache=new Map(),redirects=[],writes=[],elements=new Map();let listener,queue=Promise.resolve();
 const element=id=>{if(!elements.has(id))elements.set(id,{textContent:'',classList:{toggle(){}},addEventListener(){}});return elements.get(id)};
 data.set('access/student-a',{approved});
 const ctx={console:{error(){},warn(){}},window:{},location:{replace:p=>redirects.push(p)},localStorage:{getItem:k=>{if(cacheFails)throw Error("cache blocked");return cache.get(k)||null},setItem:(k,v)=>{if(cacheFails)throw Error("cache blocked");cache.set(k,v)}},document:{getElementById:element,body:{classList:{remove(){}}}},initializeApp:()=>({}),firebaseConfig:{},getAuth:()=>({}),getFirestore:()=>({}),doc:(_, ...s)=>s.join('/'),getDoc:async path=>{if(readFails)throw Error('offline');return{exists:()=>data.has(path),data:()=>structuredClone(data.get(path))}},setDoc:async(path,value)=>{if(writeFails)throw Error('offline');data.set(path,structuredClone(value));writes.push(path)},runTransaction:(_,callback)=>{const task=queue.then(async()=>{const changes=[];const result=await callback({get:async path=>({exists:()=>data.has(path),data:()=>structuredClone(data.get(path))}),set:(path,value)=>changes.push([path,structuredClone(value)])});if(writeFails)throw Error('offline');for(const [path,value] of changes){data.set(path,value);writes.push(path)}return result});queue=task.catch(()=>{});return task},onAuthStateChanged:(_,fn)=>listener=fn,signOut:async()=>{}};
 vm.runInNewContext(source,ctx);return{ctx,data,cache,redirects,writes,elements,login:uid=>listener(uid?{uid}:null),service:()=>ctx.window.MathMagicMeasurementProgress};
}
(async()=>{
 const path='progress/student-a/topics/measurement',other='progress/student-b/topics/measurement';let h=harness();await h.login('student-a');assert(h.service());
 await h.service().saveAttempt(18);await h.service().saveAttempt(30);await h.service().saveAttempt(22);
 assert.deepEqual({...h.data.get(path),lastCompletedAt:null},{attempts:3,bestScore:30,lastScore:22,proficient:true,lastCompletedAt:null});assert(!h.data.has(other));
 const saved=h.data.get(path),fresh=harness({data:h.data});await fresh.login('student-a');assert.equal(fresh.elements.get('bestText').textContent,'Best: 30/30');assert.equal(fresh.elements.get('attemptText').textContent,'3 of 5 completed');
 await fresh.login(null);assert.equal(fresh.redirects.at(-1),'index.html');await fresh.login('student-a');assert.deepEqual(fresh.data.get(path),saved);
 fresh.data.set('access/student-b',{approved:true});await fresh.login('student-b');await fresh.service().saveAttempt(12);assert.equal(fresh.data.get(other).attempts,1);assert.deepEqual(fresh.data.get(path),saved);
 for(const config of [{approved:false},{readFails:true}]){const denied=harness(config);await denied.login('student-a');assert(!denied.service());assert(denied.redirects.at(-1).startsWith('access-required.html'));assert.equal(denied.writes.length,0)}
 const fail=harness({writeFails:true});await fail.login('student-a');await assert.rejects(()=>fail.service().saveAttempt(20),/offline/);assert(!fail.data.has(path));
 const parallel=harness();await parallel.login('student-a');await Promise.all([parallel.service().saveAttempt(18),parallel.service().saveAttempt(30)]);assert.equal(parallel.data.get(path).attempts,2);assert.equal(parallel.data.get(path).bestScore,30);
 const blocked=harness({cacheFails:true,data:new Map([[path,{attempts:2,bestScore:20,lastScore:20,proficient:false}]])});await blocked.login('student-a');assert(blocked.service());await blocked.service().saveAttempt(25);assert.equal(blocked.data.get(path).attempts,3);assert.equal(blocked.data.get(path).bestScore,25);
 for(const score of [-1,31,NaN,Infinity,1.5,'30'])await assert.rejects(()=>parallel.service().saveAttempt(score),/Invalid/);
 console.log('PASS: mocked approved/denied access, atomic concurrent and sequential score/best/proficiency, blocked-cache tolerance, invalid-score rejection, refresh/sign-in restoration, UID-scoped paths and failed network requests. Live Firebase/rules and cross-device access remain unverified.');
})().catch(e=>{console.error(e);process.exit(1)});
