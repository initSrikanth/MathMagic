// Mocked Firebase/Firestore adapter checks; these do not establish live security or persistence.
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const source=fs.readFileSync('js/factors-multiples-auth.js','utf8').replace(/^import .*;\n/gm,'');
function harness({data=new Map(),approved=true,readFails=false,writeFails=false}={}){
 const cache=new Map(),redirects=[],writes=[],elements=new Map();let listener;
 const element=id=>{if(!elements.has(id))elements.set(id,{textContent:'',classList:{toggle(){}},addEventListener(){}});return elements.get(id)};
 data.set('access/student-a',{approved});
 const ctx={console:{error(){}},window:{},location:{replace:p=>redirects.push(p)},localStorage:{getItem:k=>cache.get(k)||null,setItem:(k,v)=>cache.set(k,v)},document:{getElementById:element,body:{classList:{remove(){}}}},initializeApp:()=>({}),firebaseConfig:{},getAuth:()=>({}),getFirestore:()=>({}),doc:(_, ...s)=>s.join('/'),getDoc:async path=>{if(readFails)throw Error('offline');return{exists:()=>data.has(path),data:()=>structuredClone(data.get(path))}},setDoc:async(path,value)=>{if(writeFails)throw Error('offline');data.set(path,structuredClone(value));writes.push(path)},onAuthStateChanged:(_,fn)=>listener=fn,signOut:async()=>{}};
 vm.runInNewContext(source,ctx);return{ctx,data,cache,redirects,writes,elements,login:uid=>listener(uid?{uid}:null),service:()=>ctx.window.MathMagicFactorsMultiplesProgress};
}
(async()=>{
 const path='progress/student-a/topics/factors-multiples',other='progress/student-b/topics/factors-multiples';let h=harness();await h.login('student-a');assert(h.service());
 await h.service().saveAttempt(18);await h.service().saveAttempt(30);await h.service().saveAttempt(22);
 assert.deepEqual({...h.data.get(path),lastCompletedAt:null},{attempts:3,bestScore:30,lastScore:22,proficient:true,lastCompletedAt:null});assert(!h.data.has(other));
 const saved=h.data.get(path),fresh=harness({data:h.data});await fresh.login('student-a');assert.equal(fresh.elements.get('bestText').textContent,'Best: 30/30');assert.equal(fresh.elements.get('attemptText').textContent,'3 of 5 completed');
 await fresh.login(null);assert.equal(fresh.redirects.at(-1),'index.html');await fresh.login('student-a');assert.deepEqual(fresh.data.get(path),saved);
 fresh.data.set('access/student-b',{approved:true});await fresh.login('student-b');await fresh.service().saveAttempt(12);assert.equal(fresh.data.get(other).attempts,1);assert.deepEqual(fresh.data.get(path),saved);
 for(const config of [{approved:false},{readFails:true}]){const denied=harness(config);await denied.login('student-a');assert(!denied.service());assert(denied.redirects.at(-1).startsWith('access-required.html'));assert.equal(denied.writes.length,0)}
 const fail=harness({writeFails:true});await fail.login('student-a');await assert.rejects(()=>fail.service().saveAttempt(20),/offline/);assert(!fail.data.has(path));
 console.log('PASS: mocked approved/denied access, sequential score/best/proficiency, refresh/sign-in restoration, UID-scoped paths and failed network requests. Live Firebase/rules and cross-device access remain unverified.');
})().catch(e=>{console.error(e);process.exit(1)});
