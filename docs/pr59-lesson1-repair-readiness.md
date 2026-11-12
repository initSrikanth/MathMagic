# PR59 Lesson 1 repair readiness — 12 November 2026

**Repair candidate; full release BLOCKED. No merge or deployment.** Existing branch: `feature/measurement-production-pilot`; parent `2b5fa082260a68704273d5aab3867bb37169a88f`. The final commit SHA is reported with the task result; this file cannot contain its own SHA.

The repaired Lesson 1 is 406.733 seconds, with 107 acoustic-timed caption cues, matching transcript, poster and native player integration. The source Kokoro recording is reused at its original speed and pitch. Branded speech, frame branding, inconsistent time comparisons, prediction answer leaks and missing duration working are corrected. Removed passages are redundant examples/repeated explanations and the branded final repeated challenge. The story-first opening, learning declaration, goal, three criteria, worked examples, thinking pauses, misconception, independent train problem and reflection remain.

The original Lesson 1 MP4 and historical evidence are preserved. Lessons 2–5 and every associated caption/transcript/evidence asset remain unchanged. No other lessons, assessments, auth/progress code, dependencies or infrastructure are modified.

Evidence: [edit/sample map](../video-agent/time-angles/lesson1-repair/edit.json), [alignment](../video-agent/time-angles/lesson1-repair/alignment.json), [media QA](../video-agent/time-angles/lesson1-repair/qa.json), [actual-frame contact sheet](../video-agent/time-angles/lesson1-repair/contact.jpg), [accessibility manifest](../video-agent/time-angles/accessibility/manifest.json).

## Targeted verification

Final results are recorded below after the final candidate checks. Historical PR59 CI receipts are not passes for this repair.

Candidate SHA-256: `3f6501d5fe8cfedff8cb266fe3b464c027bc19fece62c832aa75c0686610b0e1`.

| Check | Result |
|---|---|
| Final MP4 H.264/AAC, 1920×1080, 30fps, yuv420p, faststart, duration | PASS — 406.733s |
| Full decode and blank-frame checks | PASS — all 12,202 frames; minimum frame contrast 8.146 |
| Recorded-voice preservation / splice / levels | PASS — source PCM reconstruction; correlation 0.99999279, SNR 48.73dB, RMS 0.1526, clipping 0; internal splice near zero |
| Branding and actual model checks | PASS — empty branding band in every frame; OCR and sampled actual viewing for all 31 retained scenes; prediction and proportional timeline pixel checks |
| Caption timing/coverage and transcript | PASS — five integrated sets; exact retained source-word mapping, ordered/nonoverlapping cues, complete text, two lines ≤42 characters, top-band positioning |
| Independent lesson calculations | PASS — bus 45+5=50, movie 40+10=50, swimming 35+10=45, train 25+20=45; 12/24-hour equivalences |
| Lessons 2–5 preservation | PASS — all recorded asset hashes and lesson player sections unchanged |
| Contract unit tests | PASS — 31 tests |
| Pilot checkpoint/release-safety tests | PASS — 11 tests |
| Existing Golden Rules script preflight | PASS — source-only check; not proof of rendered quality |
| Desktop/mobile UI, WCAG, transcript keyboard access | PASS — 22/22 on final unchanged bytes |
| Canonical final-diff release guard | BLOCKED — Time/Angles absent from its approved-media inventory; final command result reported with task completion |

Final browser receipt: [browser.json](../video-agent/time-angles/lesson1-repair/browser.json). Final full suite: **22 passed**, retries disabled, desktop/mobile system Chromium. An earlier run during render work had one five-second load timeout; the final isolated playback check passed both projects (2/2), then the complete final suite passed 22/22 without assertion changes. All checks ran on the source/media state committed by this repair. Unchanged assessment stress suites and remote CI were not rerun or monitored.

## Remaining blockers and limits

- Exact full listening/viewing, speech/caption fidelity, warmth/accent/expressiveness, simultaneous phone readability and persistent-model pacing are UNVERIFIED. Twenty model intervals over eight seconds are flagged for review in `qa.json`. Ten Lesson 1 cue speed/duration flags remain in the alignment. Automated checks and sampled viewing cannot certify those attributes.
- Physical Safari/iOS playback/controls/captions remain unverified. Local Chromium runs isolate Firebase and do not certify live authentication, deployed rules, persistence or UID isolation. Historical PR59 assessment-design and real-service blockers remain unchanged and outside this task.
- Time and Angles is outside the canonical release guard's 35-record inventory (the separate ten-video Space exception does not apply). The new MP4 is therefore expected to be rejected as unaudited media by the unchanged guard. This task does not modify that infrastructure or bypass its gate. Final observed guard result is recorded with the tests.
- No full remote CI result, public-byte check, deployment or merge is claimed. A candidate committed to this branch is not publication to students.

This bounded repair task ends after the commit and targeted checks; no monitoring, scheduled work or subsequent stage follows.
