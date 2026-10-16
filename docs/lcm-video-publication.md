# Approved LCM video integration audit

Scope: publish the explicitly approved LCM extension, without regeneration or changes to its mathematical animations, narration or the existing lesson. Source final: review commit `9ec0be51671a738ae964130a9c56adbc384433d9`.

| Applicable rule | Result and evidence |
| --- | --- |
| Explicit publication authorisation | PASS — user approved the completed final and requested PR, checks, merge and Pages verification. |
| Exact approved media | PASS — 3,111,284 bytes; SHA-256 `374bae53a7d727587b7940e2e302dcf30c528e17a964db914d2c8eb7107a3c00`; copied, never transcoded. |
| No synthesis, credits or voice changes | PASS — no generation API invoked; the approved MP4 contains the original cloned narration and graphics. |
| Preserve curriculum and assessment | PASS — LCM explicitly labelled extension; no question, generator or curriculum scope changes. |
| Mathematical accuracy | PASS — exact rational arithmetic verifies the two equivalent fractions, sum and simplification; lowest positive shared multiple of four and six is twelve. |
| Fraction notation and animation integrity | PASS — approved graphics unchanged; no new rendered equations; transcript uses spoken fraction names. |
| Continuous audio and synchronisation | PASS — exact approved bytes preserve validated word-clock alignment, natural narration and persistent graphics. No production filters applied. |
| Technical media format | PASS — complete FFmpeg decode; 1920×1080, H.264/yuv420p, 30 fps, AAC 44.1 kHz, 87.666667 seconds. |
| Additive placement | PASS — one extension card immediately follows the existing Adding & Subtracting player; removing that card restores baseline `fractions.html` byte-for-byte. |
| Preserve existing content and security | PASS — no edits to authentication, navigation, scripts, styles, progress, Firebase, quizzes or existing assets. |
| Responsive native player | Checked by `approved-lcm-video.spec.js` — controls, inline playback, metadata preload, no autoplay, typed source and direct fallback; desktop/tablet/mobile 16:9 containment. |
| Accessibility | Checked by `approved-lcm-video.spec.js` — descriptive heading/name, keyboard focus, 27 native caption cues and matching complete expandable transcript. |
| Playback and ranges | Checked by `approved-lcm-video.spec.js` — HTTP 200/206/416, bytes/hash, metadata, advancing playback, early/middle/late seeks and ending. |
| Existing video coverage | Protected pattern and browser checks retain every core lesson video; extension cannot satisfy the established core resource minimum. |
| Regression gate | Run `npm run test:protected` and complete Playwright suite; merge only after exact-final-head GitHub CI passes. |
| Production checks | Verify Pages deployment and actual served HTML, MP4 checksum, captions and byte ranges after merge. Report direct live browser access separately if environment TLS prevents it. |
| Production-only services / real devices | NOT CLAIMED — isolated CI does not certify live Firebase auth/progress, App Check, Firestore rules, external-provider playback or real Safari/iOS. These systems are unchanged. |
| Workflow documentation | Existing canonical `AGENTS.md` continuous-narration and publication rules already apply; no additional rule needed. |

Reproduction: `npm run test:protected`; `npm run test:e2e` using Chrome with H.264/AAC support; `ffmpeg -v error -i videos/MathMagic_Finding_LCM_FINAL_1080p.mp4 -f null -`. See PR CI for exact final commit and observed full-suite results. Retain the approved rendering sources and original narration on the review branch.
