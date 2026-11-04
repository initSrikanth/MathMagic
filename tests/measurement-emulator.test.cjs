// Actual isolated Firestore Emulator Suite test. Never points at the live project.
const fs=require('fs'),assert=require('node:assert/strict');
const {initializeTestEnvironment,assertSucceeds,assertFails}=require('@firebase/rules-unit-testing');
const {doc,getDoc,setDoc,updateDoc,runTransaction}=require('firebase/firestore');
(async()=>{
 assert(process.env.FIRESTORE_EMULATOR_HOST,'Emulator host required; production access prohibited');
 const env=await initializeTestEnvironment({projectId:'demo-mathmagic-year5',firestore:{rules:fs.readFileSync('tests/emulator/firestore.rules','utf8')}});
 const path='progress/student-a/topics/measurement',record={attempts:0,bestScore:0,lastScore:0,proficient:false,lastCompletedAt:null};
 try{
  await env.withSecurityRulesDisabled(async c=>{const db=c.firestore();for(const [uid,approved] of [['student-a',true],['student-b',true],['denied',false]])await setDoc(doc(db,'access',uid),{approved});await setDoc(doc(db,path),record);await setDoc(doc(db,'challengeSessions/private'),{owner:'student-a',answer:42})});
  const a=env.authenticatedContext('student-a').firestore(),b=env.authenticatedContext('student-b').firestore(),no=env.unauthenticatedContext().firestore(),denied=env.authenticatedContext('denied').firestore();
  await assertSucceeds(getDoc(doc(a,'access/student-a')));await assertFails(updateDoc(doc(a,'access/student-a'),{approved:true}));
  for(const db of [no,b,denied]){await assertFails(getDoc(doc(db,path)));await assertFails(setDoc(doc(db,path),record))}
  await assertFails(setDoc(doc(a,path),{...record,lastScore:31,bestScore:31}));
  for(const db of [a,b,no]){await assertFails(getDoc(doc(db,'challengeSessions/private')));await assertFails(setDoc(doc(db,'challengeSessions/private'),{answer:1}))}
  async function save(score){return runTransaction(a,async tx=>{const r=doc(a,path),s=await tx.get(r),p=s.data();tx.set(r,{attempts:p.attempts+1,bestScore:Math.max(p.bestScore,score),lastScore:score,proficient:p.proficient||score===30,lastCompletedAt:new Date().toISOString()})})}
  await Promise.all([save(18),save(30)]);let p=(await getDoc(doc(a,path))).data();assert.equal(p.attempts,2);assert.equal(p.bestScore,30);assert(p.proficient);
  const refreshed=env.authenticatedContext('student-a').firestore();assert.deepEqual((await getDoc(doc(refreshed,path))).data(),p);
  console.log('PASS: Firestore emulator approved-user persistence, concurrent transactions, fresh-context restore, owner isolation, denied/anonymous access, approval escalation rejection and private-session denial. Test policy only; deployed rules/live Firebase unverified.');
 }finally{await env.cleanup()}
})().catch(e=>{console.error(e);process.exit(1)});
