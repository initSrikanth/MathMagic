// Safe, test-only SDK boundary. Executes the real access/progress adapters;
// never contacts production Firebase and never adds a production bypass.
async function mockFirebase(page,{uid='curriculum_student',approved=true,fail=false,seed={}}={}) {
 await page.addInitScript(({uid,approved,fail,seed})=>{
  const saved=JSON.parse(localStorage.getItem('TEST_ONLY_curriculum_firestore')||JSON.stringify(seed));
  if(uid)saved['access/'+uid]={approved};
  window.__curriculumMock={uid,fail,saved,reads:[],writes:[],queue:Promise.resolve(),commit(){localStorage.setItem('TEST_ONLY_curriculum_firestore',JSON.stringify(this.saved));}};
 },{uid,approved,fail,seed});
 await page.route('https://www.gstatic.com/firebasejs/**/firebase-app.js',r=>r.fulfill({contentType:'text/javascript',body:'const app={};export const initializeApp=()=>app;export const getApps=()=>[app];export const getApp=()=>app;'}));
 await page.route('https://www.gstatic.com/firebasejs/**/firebase-auth.js',r=>r.fulfill({contentType:'text/javascript',body:`const m=window.__curriculumMock;const a={currentUser:m.uid?{uid:m.uid,displayName:'Test learner'}:null};const listeners=[];export const getAuth=()=>a;export const onAuthStateChanged=(_,fn)=>{listeners.push(fn);queueMicrotask(()=>fn(a.currentUser));return()=>{}};export const signOut=async()=>{a.currentUser=null;for(const fn of listeners)await fn(null)};`}));
 await page.route('https://www.gstatic.com/firebasejs/**/firebase-firestore.js',r=>r.fulfill({contentType:'text/javascript',body:`const m=window.__curriculumMock;export const getFirestore=()=>({});export const doc=(_, ...p)=>p.join('/');export const getDoc=async p=>{m.reads.push(p);if(m.fail)throw Error('TEST unavailable');return{exists:()=>p in m.saved,data:()=>structuredClone(m.saved[p])}};export const setDoc=async(p,d)=>{m.writes.push(p);m.saved[p]=structuredClone(d);m.commit()};export const deleteDoc=async p=>{m.writes.push(p);delete m.saved[p];m.commit()};export const runTransaction=(_,fn)=>{const job=m.queue.then(async()=>{const edits=[];const result=await fn({get:getDoc,set:(p,d)=>edits.push([p,structuredClone(d)])});for(const[p,d]of edits)await setDoc(p,d);return result});m.queue=job.catch(()=>{});return job};`}));
 await page.route('https://www.gstatic.com/firebasejs/**/firebase-functions.js',r=>r.fulfill({contentType:'text/javascript',body:'export const getFunctions=()=>({});export const httpsCallable=()=>async()=>{throw Error("TEST callable unavailable")};'}));
}
module.exports={mockFirebase};
