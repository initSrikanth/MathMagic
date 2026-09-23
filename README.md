# MathMagic — lean authentication prototype

This test build intentionally contains only the files needed to test Google sign-in, protected pages, logout, and the Fraction Challenge.

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
- `fractions.html` — protected 25-question Fraction Challenge
- `css/style.css` — all site/game styling
- `js/firebase-config.js` — Firebase values go here
- `js/login.js` — Google sign-in
- `js/auth-guard.js` — protects pages and handles logout

No payment/subscription code is included yet. That should be added only after authentication is working reliably.
