import { initializeApp } from "https://www.gstatic.com/firebasejs/12.3.0/firebase-app.js";
import { getAuth, onAuthStateChanged, signOut } from "https://www.gstatic.com/firebasejs/12.3.0/firebase-auth.js";
import { getFirestore, doc, getDoc, setDoc } from "https://www.gstatic.com/firebasejs/12.3.0/firebase-firestore.js";
import { firebaseConfig } from "./firebase-config.js";

const app=initializeApp(firebaseConfig),auth=getAuth(app),db=getFirestore(app);
const topicId="whole-numbers";
function localKey(uid){return "mathmagic:"+uid+":"+topicId+":progress"}
function cloudRef(uid){return doc(db,"progress",uid,"topics",topicId)}
function localRead(uid){try{return JSON.parse(localStorage.getItem(localKey(uid))||"{}")}catch{return{}}}
function localSave(uid,data){localStorage.setItem(localKey(uid),JSON.stringify(data))}
function clean(data={}){
 return {attempts:Number(data.attempts||0),bestScore:Number(data.bestScore||0),lastScore:Number(data.lastScore||0),proficient:data.proficient===true,lastCompletedAt:data.lastCompletedAt||null};
}
function paint(data={}){
 const p=clean(data),attempts=p.attempts;
 const dots=document.getElementById("attemptDots"),at=document.getElementById("attemptText"),bt=document.getElementById("bestText"),pr=document.getElementById("proficiencyText");
 if(dots)dots.textContent=Array.from({length:5},(_,i)=>i<Math.min(attempts,5)?"●":"○").join(" ");
 if(at)at.textContent=attempts<5?attempts+" of 5 completed":"5 of 5 minimum completed • "+attempts+" total attempts";
 if(bt)bt.textContent=attempts?"Best: "+p.bestScore+"/20":"Best: —";
 if(pr){pr.textContent=p.proficient?"✓ PROFICIENT":attempts>0?"Proficiency: In progress":"Proficiency: Start";pr.classList.toggle("proficient",p.proficient)}
}
async function loadProgress(uid){
 const ref=cloudRef(uid),snap=await getDoc(ref);
 if(snap.exists()){const data=clean(snap.data());localSave(uid,data);return data}
 const local=clean(localRead(uid));
 if(local.attempts>0){await setDoc(ref,local);return local}
 return local;
}
onAuthStateChanged(auth,async user=>{
 if(!user){location.replace("index.html");return}
 try{
  const access=await getDoc(doc(db,"access",user.uid));
  if(!(access.exists()&&access.data().approved===true)){location.replace("access-required.html");return}
  let current=await loadProgress(user.uid);paint(current);
  window.MathMagicProgress={async saveWholeNumbersAttempt(score){
   const latest=await loadProgress(user.uid),attempts=latest.attempts+1,best=Math.max(latest.bestScore,Number(score||0));
   const data={attempts,bestScore:best,lastScore:Number(score||0),proficient:latest.proficient||Number(score)===20,lastCompletedAt:new Date().toISOString()};
   await setDoc(cloudRef(user.uid),data);localSave(user.uid,data);current=data;paint(data);return data;
  }};
  document.body.classList.remove("auth-loading");
 }catch(e){console.error("MathMagic access/progress check failed:",e);location.replace("access-required.html?error=1")}
});
document.getElementById("logoutBtn")?.addEventListener("click",async()=>{await signOut(auth);location.replace("index.html")});