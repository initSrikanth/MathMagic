// Isolated demo-project Firestore tests, not deployed production-rule evidence.
const fs=require('fs'),assert=require('node:assert/strict'),{initializeTestEnvironment,assertSucceeds,assertFails}=require('@firebase/rules-unit-testing'),{doc,getDoc,setDoc,runTransaction}=require('firebase/firestore');
(async()=>{assert(process.env.FIRESTORE_EMULATOR_HOST,'No live Firebase calls allowed');const env=await initializeTestEnvironment({projectId:'demo-mathmagic-year5',firestore:{rules:fs.readFileSync('tests/emulator/firestore.rules','utf8')}});try{await env.withSecurityRulesDisabled(async c=>{for(const [u,approved]of[['a',true],['b',true],['denied',false]])await setDoc(doc(c.firestore(),'access',u),{approved})});const path='progress/a/topics/space',a=env.authenticatedContext('a').firestore(),record={attempts:0,bestScore:0,lastScore:0,proficient:false,lastCompletedAt:null,completedAttemptIds:[]};await assertSucceeds(setDoc(doc(a,path),record));for(const db of [env.unauthenticatedContext().firestore(),env.authenticatedContext('b').firestore(),env.authenticatedContext('denied').firestore()]){await assertFails(getDoc(doc(db,path)));await assertFails(setDoc(doc(db,path),record))}await assertFails(setDoc(doc(a,'access/a'),{approved:true}));await assertFails(getDoc(doc(a,'challengeSessions/secret')));await assertFails(setDoc(doc(a,path),{...record,bestScore:31}));async function save(score,id){return runTransaction(a,async tx=>{const ref=doc(a,path),old=(await tx.get(ref)).data();if(old.completedAttemptIds.includes(id))return old;const next={attempts:old.attempts+1,bestScore:Math.max(old.bestScore,score),lastScore:score,proficient:old.proficient||score===30,lastCompletedAt:new Date().toISOString(),completedAttemptIds:[...old.completedAttemptIds,id]};tx.set(ref,next);return next})}await Promise.all([save(18,'attempt_1'),save(30,'attempt_2')]);await save(30,'attempt_2');let actual=(await getDoc(doc(a,path))).data();assert.equal(actual.attempts,2);assert.equal(actual.bestScore,30);assert(actual.proficient);assert.deepEqual((await getDoc(doc(env.authenticatedContext('a').firestore(),path))).data(),actual);await productionAdapterRecovery(env);console.log('PASS: Space Firestore emulator owner/approval isolation, escalation/private-session rejection, concurrent idempotent progress and fresh-context restoration. Production access/rules remain unverified.')}finally{await env.cleanup()}})().catch(e=>{console.error(e);process.exit(1)});
// Exercise the actual browser adapter against real emulator transactions.
// Auth-state callbacks and a lost acknowledgement are injected; Google login is not tested.
async function productionAdapterRecovery(env){
 const vm=require('node:vm'),cache=new Map(),uid='space_adapter_student';
 await env.withSecurityRulesDisabled(async context=>{await setDoc(doc(context.firestore(),'access',uid),{approved:true})});
 const database=env.authenticatedContext(uid).firestore();
 const source=fs.readFileSync('js/space-auth.js','utf8').replace(/^import .*;\n/gm,'');
 function create(){
  let listener,loseAck=false;const auth={currentUser:{uid}},redirect=[];
  const context={console:{warn(){},error(){}},window:{},firebaseConfig:{},initializeApp:()=>({}),getAuth:()=>auth,getFirestore:()=>database,doc,getDoc,
   runTransaction:async(db,callback)=>{
    const result=await runTransaction(db,transaction=>callback({get:ref=>transaction.get(ref),set:(ref,data)=>transaction.set(ref,JSON.parse(JSON.stringify(data)))}));
    if(loseAck){loseAck=false;throw Error('Injected lost acknowledgement AFTER emulator commit')}
    return result;
   },onAuthStateChanged:(_,callback)=>{listener=callback},signOut:async()=>{},
   localStorage:{getItem:key=>cache.get(key)||null,setItem:(key,value)=>cache.set(key,value),removeItem:key=>cache.delete(key)},
   document:{getElementById:()=>null,body:{classList:{add(){},remove(){}}}},location:{replace:path=>redirect.push(path)}};
  vm.runInNewContext(source,context);
  return{auth,redirect,context,login:()=>listener(auth.currentUser),api:()=>context.window.MathMagicSpaceProgress,loseNextAck:()=>{loseAck=true},logout:async()=>{auth.currentUser=null;await listener(null)}};
 }
 const first=create();await first.login();assert(first.api());first.loseNextAck();
 await assert.rejects(()=>first.api().saveAttempt(22,'adapter_attempt_0001'),/lost acknowledgement/);
 assert.equal((await getDoc(doc(database,'progress',uid,'topics','space'))).data().attempts,1);
 const fresh=create();await fresh.login();assert.equal(fresh.api().getPendingAttempt().id,'adapter_attempt_0001');
 await fresh.api().saveAttempt(22,'adapter_attempt_0001');assert.equal(fresh.api().getPendingAttempt(),null);
 await fresh.api().saveAttempt(30,'adapter_attempt_0002');
 const restored=(await getDoc(doc(env.authenticatedContext(uid).firestore(),'progress',uid,'topics','space'))).data();
 assert.equal(restored.attempts,2);assert.equal(restored.bestScore,30);assert(restored.proficient);
 await env.withSecurityRulesDisabled(async context=>{await setDoc(doc(context.firestore(),'access',uid),{approved:false})});
 await assert.rejects(()=>fresh.api().saveAttempt(18,'adapter_attempt_0003'),/access could not be verified/);
 const denied=create();await denied.login();assert(!denied.api());assert.equal(denied.redirect.at(-1),'access-required.html');
 await assertFails(getDoc(doc(database,'progress',uid,'topics','space')));
 await assertFails(setDoc(doc(env.authenticatedContext('denied').firestore(),'progress','denied','topics','space'),{attempts:0,bestScore:0,lastScore:0,proficient:false,lastCompletedAt:null,completedAttemptIds:[]}));
 const old=fresh.api();await fresh.logout();assert(!fresh.api());assert.equal(fresh.redirect.at(-1),'index.html');
 await assert.rejects(()=>old.saveAttempt(10,'adapter_attempt_0004'),/sign in again/);
 console.log('PASS: production Space adapter with emulator transactions; injected lost-ack recovery after refresh; duplicate suppression; proficiency; revoked approval; denied owner writes; stale-service rejection after sign-out. Google login/live Firebase NOT tested.');
}
