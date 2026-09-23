import { initializeApp } from "https://www.gstatic.com/firebasejs/12.3.0/firebase-app.js";
import { getAuth, GoogleAuthProvider, signInWithPopup, onAuthStateChanged } from "https://www.gstatic.com/firebasejs/12.3.0/firebase-auth.js";
import { firebaseConfig } from "./firebase-config.js";

const status = document.getElementById("loginStatus");
const button = document.getElementById("googleLoginBtn");
const configured = !firebaseConfig.apiKey.includes("PASTE_");

if (!configured) {
  status.textContent = "Firebase is not configured yet. Add your Firebase web configuration to js/firebase-config.js.";
  button.disabled = true;
} else {
  const app = initializeApp(firebaseConfig);
  const auth = getAuth(app);
  const provider = new GoogleAuthProvider();
  provider.setCustomParameters({ prompt: "select_account" });

  onAuthStateChanged(auth, (user) => {
    if (user) window.location.replace("dashboard.html");
  });

  button.addEventListener("click", async () => {
    button.disabled = true;
    status.textContent = "Opening Google sign-in…";
    try {
      await signInWithPopup(auth, provider);
    } catch (error) {
      console.error(error);
      status.textContent = error.code === "auth/unauthorized-domain"
        ? "This GitHub Pages domain is not authorised in Firebase yet."
        : `Sign-in failed: ${error.message}`;
      button.disabled = false;
    }
  });
}
