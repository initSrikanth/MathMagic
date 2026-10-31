import { initializeApp } from "https://www.gstatic.com/firebasejs/12.3.0/firebase-app.js";
import { getAuth,onAuthStateChanged,signOut } from "https://www.gstatic.com/firebasejs/12.3.0/firebase-auth.js";
import { getFirestore,doc,getDoc,runTransaction } from "https://www.gstatic.com/firebasejs/12.3.0/firebase-firestore.js";
import { firebaseConfig } from "./firebase-config.js";
const app=initializeApp(firebaseConfig),auth=getAuth(app),db=getFirestore(app),topicId="fractions";
const key=uid=>"mathmagic:"+uid+":"+topicId+":progress",ref=uid=>doc(db,"progress",uid,"topics",topicId);
const count=value=>Number.isSafeInteger(Number(value))&&Number(value)>=0?Number(value):0;
const mark=value=>Math.min(30,count(value));
function clean(d={}){return{attempts:count(d.attempts),bestScore:mark(d.bestScore),lastScore:mark(d.lastScore),proficient:d.proficient===true,lastCompletedAt:d.lastCompletedAt||null,completedAttemptIds:Array.isArray(d.completedAttemptIds)?d.completedAttemptIds.filter(id=>typeof id==='string').slice(-100):[]}}
function localRead(uid){try{return clean(JSON.parse(localStorage.getItem(key(uid))||"{}"))}catch{return clean()}}
// The cache must never turn a successful remote write into a failed attempt.
function localSave(uid,d){try{localStorage.setItem(key(uid),JSON.stringify(d))}catch(e){console.warn("MathMagic progress cache unavailable:",e)}}
function paint(d={}){const p=clean(d),a=p.attempts;const dots=document.getElementById("attemptDots"),at=document.getElementById("attemptText"),best=document.getElementById("bestText"),prof=document.getElementById("proficiencyText");if(dots)dots.textContent=Array.from({length:5},(_,i)=>i<Math.min(a,5)?"●":"○").join(" ");if(at)at.textContent=a<5?a+" of 5 completed":"5 of 5 minimum completed • "+a+" total attempts";if(best)best.textContent=a?"Best: "+p.bestScore+"/30":"Best: —";if(prof){prof.textContent=p.proficient?"✓ PROFICIENT":a>0?"Proficiency: In progress":"Proficiency: Start";prof.classList.toggle("proficient",p.proficient)}}
async function load(uid){
 const s=await getDoc(ref(uid));
 if(s.exists()){const p=clean(s.data());localSave(uid,p);return p}
 const cached=localRead(uid);
 // Preserve legacy cache recovery, but never overwrite a concurrently saved attempt.
 const p=cached.attempts>0?await runTransaction(db,async transaction=>{
  const current=await transaction.get(ref(uid));
  if(current.exists())return clean(current.data());
  transaction.set(ref(uid),cached);return cached;
 }):cached;
 localSave(uid,p);return p;
}
onAuthStateChanged(auth,async user=>{
 delete window.MathMagicFractionsProgress;
 document.body.classList.add("auth-loading");
 if(!user){location.replace("index.html");return}
 try{
  const access=await getDoc(doc(db,"access",user.uid));
  if(!(access.exists()&&access.data().approved===true)){location.replace("access-required.html");return}
  const progress=await load(user.uid);
  if(auth.currentUser?.uid!==user.uid)return;
  paint(progress);
  window.MathMagicFractionsProgress={async saveAttempt(score,attemptId){
   if(!Number.isInteger(score)||score<0||score>30)throw new RangeError("Score must be a whole number from 0 to 30.");
   if(typeof attemptId!=="string"||!/^[A-Za-z0-9_-]{8,100}$/.test(attemptId))throw new TypeError("A stable challenge attempt ID is required.");
   if(auth.currentUser?.uid!==user.uid)throw new Error("Please sign in again before saving progress.");
   const approved=await getDoc(doc(db,"access",user.uid));
   if(!(approved.exists()&&approved.data().approved===true))throw new Error("Your access could not be verified.");
   const data=await runTransaction(db,async transaction=>{
    if(auth.currentUser?.uid!==user.uid)throw new Error("Your sign-in changed before the attempt could be saved.");
    const snapshot=await transaction.get(ref(user.uid)),old=snapshot.exists()?clean(snapshot.data()):clean();
    if(old.completedAttemptIds.includes(attemptId))return old;
    const next={attempts:old.attempts+1,bestScore:Math.max(old.bestScore,score),lastScore:score,proficient:old.proficient||score===30,lastCompletedAt:new Date().toISOString(),completedAttemptIds:[...old.completedAttemptIds,attemptId].slice(-100)};
    transaction.set(ref(user.uid),next);return next;
   });
   localSave(user.uid,data);
   if(auth.currentUser?.uid===user.uid)paint(data);
   return data;
  }};
  document.body.classList.remove("auth-loading");
 }catch(e){console.error("MathMagic access/progress check failed:",e);location.replace("access-required.html?error=1")}
});
document.getElementById("logoutBtn")?.addEventListener("click",async()=>{await signOut(auth);location.replace("index.html")});
