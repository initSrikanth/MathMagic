import { initializeApp } from "https://www.gstatic.com/firebasejs/12.3.0/firebase-app.js";
import { getAuth, onAuthStateChanged, signOut } from "https://www.gstatic.com/firebasejs/12.3.0/firebase-auth.js";
import { firebaseConfig } from "./firebase-config.js";

const configured = !firebaseConfig.apiKey.includes("PASTE_");
if (!configured) {
  alert("Firebase is not configured. Add your Firebase web configuration first.");
  window.location.replace("index.html");
} else {
  const app = initializeApp(firebaseConfig);
  const auth = getAuth(app);

  onAuthStateChanged(auth, (user) => {
    if (!user) {
      window.location.replace("index.html");
      return;
    }
    document.body.classList.add("authenticated");
    document.querySelectorAll("[data-user-name]").forEach(el => el.textContent = user.displayName || "MathMagic learner");
    document.querySelectorAll("[data-user-email]").forEach(el => el.textContent = user.email || "");
    document.querySelectorAll("[data-user-photo]").forEach(el => {
      if (user.photoURL) { el.src = user.photoURL; el.hidden = false; }
    });
  });

  document.addEventListener("click", async (event) => {
    const logout = event.target.closest("[data-logout]");
    if (!logout) return;
    logout.disabled = true;
    await signOut(auth);
    window.location.replace("index.html");
  });
}
