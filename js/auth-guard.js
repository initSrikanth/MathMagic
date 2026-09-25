import { initializeApp } from "https://www.gstatic.com/firebasejs/12.3.0/firebase-app.js";
import { getAuth, onAuthStateChanged, signOut } from "https://www.gstatic.com/firebasejs/12.3.0/firebase-auth.js";
import { getFirestore, doc, getDoc } from "https://www.gstatic.com/firebasejs/12.3.0/firebase-firestore.js";
import { firebaseConfig } from "./firebase-config.js";

const configured = !firebaseConfig.apiKey.includes("PASTE_");

if (!configured) {
  alert("Firebase is not configured. Add your Firebase web configuration first.");
  window.location.replace("index.html");
} else {
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

      const progressPanel = document.querySelector('[data-topic-progress="whole-numbers"]');
      if (progressPanel) {
        try {
          const key = "mathmagic:" + user.uid + ":whole-numbers:progress";
          const p = JSON.parse(localStorage.getItem(key) || "{}");
          const attempts = Number(p.attempts || 0);
          const best = Number(p.bestScore || 0);
          const proficient = p.proficient === true;
          progressPanel.querySelector(".practice-dots").textContent = Array.from({length:5}, (_,i) => i < Math.min(attempts,5) ? "●" : "○").join(" ");
          progressPanel.querySelector("[data-attempts]").textContent = Math.min(attempts,5) + "/5" + (attempts > 5 ? " • " + attempts + " total" : "");
          progressPanel.querySelector("[data-progress-bar]").style.width = (Math.min(attempts,5) * 20) + "%";
          progressPanel.querySelector("[data-best]").textContent = attempts ? "Best: " + best + "/20" : "Best: —";
          const badge = progressPanel.querySelector("[data-proficiency]");
          badge.textContent = proficient ? "✓ PROFICIENT" : "IN PROGRESS";
          badge.classList.toggle("achieved", proficient);
        } catch (progressError) {
          console.warn("Dashboard progress could not be loaded:", progressError);
        }
      }

      const fractionsPanel = document.querySelector('[data-topic-progress="fractions"]');
      if (fractionsPanel) {
        try {
          const key = "mathmagic:" + user.uid + ":fractions:progress";
          const p = JSON.parse(localStorage.getItem(key) || "{}");
          const attempts = Number(p.attempts || 0);
          const best = Number(p.bestScore || 0);
          const proficient = p.proficient === true;
          fractionsPanel.querySelector(".practice-dots").textContent = Array.from({length:5}, (_,i) => i < Math.min(attempts,5) ? "●" : "○").join(" ");
          fractionsPanel.querySelector("[data-attempts]").textContent = Math.min(attempts,5) + "/5" + (attempts > 5 ? " • " + attempts + " total" : "");
          fractionsPanel.querySelector("[data-progress-bar]").style.width = (Math.min(attempts,5) * 20) + "%";
          fractionsPanel.querySelector("[data-best]").textContent = attempts ? "Best: " + best + "/20" : "Best: —";
          const badge = fractionsPanel.querySelector("[data-proficiency]");
          badge.textContent = proficient ? "✓ PROFICIENT" : "IN PROGRESS";
          badge.classList.toggle("achieved", proficient);
        } catch (progressError) {
          console.warn("Fractions progress could not be loaded:", progressError);
        }
      }

      const decimalsPanel = document.querySelector('[data-topic-progress="decimals-percentages"]');
      if (decimalsPanel) {
        try {
          const key = "mathmagic:" + user.uid + ":decimals-percentages:progress";
          const p = JSON.parse(localStorage.getItem(key) || "{}");
          const attempts = Number(p.attempts || 0);
          const best = Number(p.bestScore || 0);
          const proficient = p.proficient === true;
          decimalsPanel.querySelector(".practice-dots").textContent = Array.from({length:5}, (_,i) => i < Math.min(attempts,5) ? "●" : "○").join(" ");
          decimalsPanel.querySelector("[data-attempts]").textContent = Math.min(attempts,5) + "/5" + (attempts > 5 ? " • " + attempts + " total" : "");
          decimalsPanel.querySelector("[data-progress-bar]").style.width = (Math.min(attempts,5) * 20) + "%";
          decimalsPanel.querySelector("[data-best]").textContent = attempts ? "Best: " + best + "/20" : "Best: —";
          const badge = decimalsPanel.querySelector("[data-proficiency]");
          badge.textContent = proficient ? "✓ PROFICIENT" : "IN PROGRESS";
          badge.classList.toggle("achieved", proficient);
        } catch (progressError) {
          console.warn("Decimals & Percentages progress could not be loaded:", progressError);
        }
      }

      const additionPanel = document.querySelector('[data-topic-progress="addition-subtraction"]');
      if (additionPanel) {
        try {
          const key = "mathmagic:" + user.uid + ":addition-subtraction:progress";
          const p = JSON.parse(localStorage.getItem(key) || "{}");
          const attempts = Number(p.attempts || 0);
          const best = Number(p.bestScore || 0);
          const proficient = p.proficient === true;
          additionPanel.querySelector(".practice-dots").textContent = Array.from({length:5}, (_,i) => i < Math.min(attempts,5) ? "●" : "○").join(" ");
          additionPanel.querySelector("[data-attempts]").textContent = Math.min(attempts,5) + "/5" + (attempts > 5 ? " • " + attempts + " total" : "");
          additionPanel.querySelector("[data-progress-bar]").style.width = (Math.min(attempts,5) * 20) + "%";
          additionPanel.querySelector("[data-best]").textContent = attempts ? "Best: " + best + "/20" : "Best: —";
          const badge = additionPanel.querySelector("[data-proficiency]");
          badge.textContent = proficient ? "✓ PROFICIENT" : "IN PROGRESS";
          badge.classList.toggle("achieved", proficient);
        } catch (progressError) {
          console.warn("Addition & Subtraction progress could not be loaded:", progressError);
        }
      }

      document.body.classList.add("authenticated");
      document.querySelectorAll("[data-user-name]").forEach(el => el.textContent = user.displayName || "MathMagic learner");
      document.querySelectorAll("[data-user-email]").forEach(el => el.textContent = user.email || "");
      document.querySelectorAll("[data-user-photo]").forEach(el => {
        if (user.photoURL) {
          el.src = user.photoURL;
          el.hidden = false;
        }
      });
    } catch (error) {
      console.error("MathMagic access check failed:", error);
      window.location.replace("access-required.html?error=1");
    }
  });

  document.addEventListener("click", async (event) => {
    const logout = event.target.closest("[data-logout]");
    if (!logout) return;
    logout.disabled = true;
    await signOut(auth);
    window.location.replace("index.html");
  });
}
