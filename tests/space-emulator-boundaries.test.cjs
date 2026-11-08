// Additional local policy boundaries; never deployed rules or live Firebase evidence.
const fs=require('fs'),assert=require('node:assert/strict');
const {initializeTestEnvironment,assertSucceeds,assertFails}=require('@firebase/rules-unit-testing');
const {doc,getDoc,setDoc,runTransaction}=require('firebase/firestore');
(async()=>{
 assert(process.env.FIRESTORE_EMULATOR_HOST,'Emulator host required; no live calls');
 const env=await initializeTestEnvironment({projectId:'demo-mathmagic-year5',firestore:{rules:fs.readFileSync('tests/emulator/firestore.rules','utf8')}});
 const initial={attempts:0,bestScore:0,lastScore:0,proficient:false,lastCompletedAt:null,completedAttemptIds:[]};
 try{
  await env.withSecurityRulesDisabled(async c=>{for(const [uid,approved]of[['owner',true],['other',true],['unapproved',false]]){await setDoc(doc(c.firestore(),'access',uid),{approved});await setDoc(doc(c.firestore(),`progress/${uid}/topics/space`),initial)}});
  const db=env.authenticatedContext('owner').firestore(),path='progress/owner/topics/space',ref=doc(db,path);
  const signedOut=env.unauthenticatedContext().firestore(),unapproved=env.authenticatedContext('unapproved').firestore();
  for(const [context,ownPath]of[[signedOut,path],[unapproved,'progress/unapproved/topics/space']]){
   await assertFails(getDoc(doc(context,ownPath)));await assertFails(setDoc(doc(context,ownPath),initial));
  }
  await assertFails(getDoc(doc(db,'access/other')));
  await assertFails(setDoc(doc(db,'access/owner'),{approved:true}));
  await assertFails(setDoc(doc(db,'progress/other/topics/space'),initial));
  for(const invalid of [
   {...initial,attempts:-1},{...initial,attempts:0.5},{...initial,bestScore:-1},
   {...initial,bestScore:31},{...initial,bestScore:10,lastScore:11},
   {...initial,proficient:'yes'},{...initial,completedAttemptIds:['duplicate','duplicate']},
   {...initial,completedAttemptIds:'not-a-list'},{...initial,admin:true}
  ])await assertFails(setDoc(ref,invalid));
  for(const context of [db,env.authenticatedContext('other').firestore(),unapproved,signedOut]){
   await assertFails(getDoc(doc(context,'challengeSessions/private-space')));
   await assertFails(setDoc(doc(context,'challengeSessions/private-space'),{answer:42}));
  }
  const ids=Array.from({length:105},(_,i)=>`completed_${i}`);
  await assertSucceeds(setDoc(ref,{...initial,attempts:105,bestScore:30,lastScore:18,proficient:true,completedAttemptIds:ids}));
  async function persist(id,score){return runTransaction(db,async tx=>{const prior=(await tx.get(ref)).data();if(prior.completedAttemptIds.includes(id))return prior;const next={...prior,attempts:prior.attempts+1,bestScore:Math.max(prior.bestScore,score),lastScore:score,proficient:prior.proficient||score===30,completedAttemptIds:[...prior.completedAttemptIds,id]};tx.set(ref,next);return next})}
  await persist(ids[0],30);assert.equal((await getDoc(ref)).data().attempts,105);
  await Promise.all([persist('lost_ack',22),persist('lost_ack',22)]);
  let saved=(await getDoc(ref)).data();assert.equal(saved.attempts,106);assert.equal(saved.completedAttemptIds.length,106);assert.equal(saved.bestScore,30);assert(saved.proficient);
  assert.deepEqual((await getDoc(doc(env.authenticatedContext('owner').firestore(),path))).data(),saved);
  await env.withSecurityRulesDisabled(c=>setDoc(doc(c.firestore(),'access/owner'),{approved:false}));
  await assertFails(getDoc(ref));await assertFails(setDoc(ref,initial));
  await env.withSecurityRulesDisabled(c=>setDoc(doc(c.firestore(),'access/owner'),{approved:true}));
  await assertSucceeds(setDoc(ref,initial));assert.deepEqual((await getDoc(ref)).data(),initial);
  console.log('PASS: Space emulator own-path unapproved/signed-out denial, cross-user approval isolation, 9 invalid payloads, private-session read/write isolation, >100 retained IDs, concurrent lost-ack idempotence, sticky proficiency, fresh-context restoration, approval revocation and intentional reset. Fixture policy only.');
 }finally{await env.cleanup()}
})().catch(e=>{console.error(e);process.exit(1)});
