import { initializeApp } from "https://www.gstatic.com/firebasejs/12.3.0/firebase-app.js";
import { getAuth, onAuthStateChanged, signOut } from "https://www.gstatic.com/firebasejs/12.3.0/firebase-auth.js";
import { getFirestore, doc, getDoc } from "https://www.gstatic.com/firebasejs/12.3.0/firebase-firestore.js";
import { firebaseConfig } from "./firebase-config.js";

const app=initializeApp(firebaseConfig), auth=getAuth(app), db=getFirestore(app);
function key(uid){return "mathmagic:"+uid+":fractions:progress"}
function readProgress(uid){try{return JSON.parse(localStorage.getItem(key(uid))||"{}")}catch{return{}}}
function saveProgress(uid,data){localStorage.setItem(key(uid),JSON.stringify(data))}
function paint(data={}){
 const attempts=Number(data.attempts||0),best=Number(data.bestScore||0),proficient=data.proficient===true;
 const dots=document.getElementById("attemptDots"),attemptText=document.getElementById("attemptText"),bestText=document.getElementById("bestText"),prof=document.getElementById("proficiencyText");
 if(dots)dots.textContent=Array.from({length:5},(_,i)=>i<Math.min(attempts,5)?"●":"○").join(" ");
 if(attemptText)attemptText.textContent=attempts<5?attempts+" of 5 completed":"5 of 5 minimum completed • "+attempts+" total attempts";
 if(bestText)bestText.textContent=attempts?"Best: "+best+"/20":"Best: —";
 if(prof){prof.textContent=proficient?"✓ PROFICIENT":"Proficiency: In progress";prof.classList.toggle("proficient",proficient)}
}
onAuthStateChanged(auth,async user=>{
 if(!user){location.replace("index.html");return}
 try{
  const snap=await getDoc(doc(db,"access",user.uid));
  if(!(snap.exists()&&snap.data().approved===true)){location.replace("access-required.html");return}
  paint(readProgress(user.uid));
  window.MathMagicFractionsProgress={
   async saveAttempt(score){
    const old=readProgress(user.uid),attempts=Number(old.attempts||0)+1,best=Math.max(Number(old.bestScore||0),Number(score||0)),proficient=old.proficient===true||Number(score)===20;
    const data={attempts,bestScore:best,lastScore:Number(score||0),proficient,lastCompletedAt:new Date().toISOString()};
    saveProgress(user.uid,data);paint(data);return data;
   }
  };
  document.body.classList.remove("auth-loading");
 }catch(e){console.error("MathMagic access check failed:",e);location.replace("access-required.html?error=1")}
});
document.getElementById("logoutBtn")?.addEventListener("click",async()=>{await signOut(auth);location.replace("index.html")});