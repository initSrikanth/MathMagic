import { initializeApp } from "https://www.gstatic.com/firebasejs/12.3.0/firebase-app.js";
import { getAuth, onAuthStateChanged, signOut } from "https://www.gstatic.com/firebasejs/12.3.0/firebase-auth.js";
import { getFirestore, doc, getDoc } from "https://www.gstatic.com/firebasejs/12.3.0/firebase-firestore.js";
import { firebaseConfig } from "./firebase-config.js";

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);

onAuthStateChanged(auth, async (user) => {
  if (!user) {
    window.location.replace("index.html");
    return;
  }

  try {
    const accessSnap = await getDoc(doc(db, "access", user.uid));
    const approved = accessSnap.exists() && accessSnap.data().approved === true;

    if (!approved) {
      window.location.replace("access-required.html");
      return;
    }

    document.body.classList.remove("auth-loading");
  } catch (error) {
    console.error("MathMagic access check failed:", error);
    window.location.replace("access-required.html?error=1");
  }
});

document.getElementById("logoutBtn")?.addEventListener("click", async () => {
  await signOut(auth);
  window.location.replace("index.html");
});
