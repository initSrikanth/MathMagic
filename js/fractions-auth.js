import { initializeApp } from "https://www.gstatic.com/firebasejs/12.3.0/firebase-app.js";
import { getAuth, onAuthStateChanged, signOut } from "https://www.gstatic.com/firebasejs/12.3.0/firebase-auth.js";
import { getFirestore, doc, getDoc } from "https://www.gstatic.com/firebasejs/12.3.0/firebase-firestore.js";
import { firebaseConfig } from "./firebase-config.js";
const app=initializeApp(firebaseConfig),auth=getAuth(app),db=getFirestore(app);
onAuthStateChanged(auth,async user=>{if(!user){location.replace("index.html");return}try{const snap=await getDoc(doc(db,"access",user.uid));if(!(snap.exists()&&snap.data().approved===true)){location.replace("access-required.html");return}document.body.classList.remove("auth-loading")}catch(e){console.error("MathMagic access check failed:",e);location.replace("access-required.html?error=1")}});
document.getElementById("logoutBtn")?.addEventListener("click",async()=>{await signOut(auth);location.replace("index.html")});