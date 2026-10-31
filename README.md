# MathMagic — mathematics lessons and practice

MathMagic is a static GitHub Pages site with six mathematics topics, Google sign-in, approval-gated access and student progress. Fractions has five learning pages and a 30-question challenge in six bands of five. Browser assessment is the current transitional baseline; passing local tests does not establish production Firebase security or cross-device persistence.

## 1. Upload to GitHub
Upload the contents of this folder to the root of the `MathMagic` repository and commit them.

## 2. Enable GitHub Pages
Repository **Settings → Pages → Deploy from a branch → main → /(root) → Save**.

## 3. Create/configure Firebase
1. Create a Firebase project.
2. Add a **Web app** to the project.
3. Copy the Firebase configuration values into `js/firebase-config.js`.
4. In Firebase Authentication, enable **Google** as a sign-in provider.
5. In Authentication settings, add your GitHub Pages hostname to **Authorized domains** (for example `initsrikanth.github.io`).

## 4. Test
1. Open the GitHub Pages site.
2. Sign in with Google.
3. Confirm you reach `dashboard.html`.
4. Open the Fraction Challenge.
5. Log out.
6. Try opening `dashboard.html` or `fractions.html` directly; you should be returned to the login page.

## Files
- `index.html` — login page
- `dashboard.html` — protected dashboard
- `fractions.html` — five Fractions learning pages and the 30-question Fraction Challenge
- `css/style.css` — all site/game styling
- `js/firebase-config.js` — Firebase values go here
- `js/login.js` — Google sign-in
- `js/auth-guard.js` — protects pages and handles logout

No payment/subscription code is included yet. That should be added only after authentication is working reliably.


## Fractions verification

[GitHub Issue #39](https://github.com/initSrikanth/MathMagic/issues/39) is the central completion record. Curriculum, assessment, media, engineering and independent QA evidence is retained under `docs/qa/` and the Fractions coverage document. Keep video production workflows suspended; existing approved video bytes must be preserved and replacement publication needs founder approval.

Use `npm run test:protected` and `npm run test:e2e` for the repository release checks. Browser tests isolate authentication for UI checks; real Google sign-in, approval, deployed Firestore rules, cross-device saves and real Safari/iOS require separate observed verification.
