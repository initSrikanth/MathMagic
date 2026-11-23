# Year 5 Statistics release preparation — 21 November 2026

Historical checkpoint below. On23 November2026 the owner supplied explicit exact-file audiovisual approval, recorded in [owner-approval-2026-11-23.json](../../video-agent/statistics/owner-approval-2026-11-23.json). The existing gated registration/integration has now been applied with all five MP4 hashes unchanged. Current release/CI/deployment results are recorded on PR #60; the pending-approval findings below describe21 November, not the current approval state.

**Release blocked by missing full human audiovisual approval.** Five complete videos and all sidecars are technically verified. The production Statistics page still has zero video players. No merge, production registration or deployment has occurred. The owner’s conditional release authority is recorded in the canonical contract without changing the unrelated-topic hold, Space exception or approved voice.

## CI cause and release safeguard

[Actions run 44780550839](https://github.com/initSrikanth/MathMagic/actions/runs/44780550839), on `699858b72617c7eaa0c258bf35472659c5ef4ac1`, failed at **Enforce teaching-video production contract**. Its 39 contract unit tests passed. The subsequent release check rejected the five unaudited new MP4 paths; browser and emulator steps never ran. This was an approval prerequisite failure, not a failing browser assertion.

The release check now recognises Statistics through an explicit, conditional, checksum-bound path. It still rejects all five pending files. A real complete approval record, unchanged player assets, all 92 human flag resolutions, approved checkpoint registration and all five production embeds are required together. No workflow, test, assertion or hold is disabled to manufacture a green run. CI cannot legitimately pass this release gate before the required approval exists.

## Prepared integration and human review

`python3 tools/video-quality/statistics_release.py --prepare` builds the complete proposed five-lesson integration at `video-agent/statistics/review/integration-preview.html`. It includes the existing lessons/tools/challenge, named keyboard-focusable native players, playsinline, caption controls and full transcript disclosures. Normal authentication remains enabled. With `python3 tests/serve.py`, the review URL is `http://127.0.0.1:4173/video-agent/statistics/review/integration-preview.html`.

Inline captions appear in a separate 18px-or-larger panel beneath the video. The player reserves 72px for native controls beneath the 16:9 picture. Saved [390px preview samples](../../video-agent/statistics/review/player-evidence/) cover all five lessons. Native fullscreen continues to use native captions: physical-device and full human legibility review remain pending.

`video-agent/statistics/approval.json` is an **unapproved template**. Reviewer, date, evidence record and all perceptual findings remain empty/false. Human reviewers must listen to and view each entire exact file, check accent/expressiveness, teaching, mobile legibility and each flagged interval. Technical samples do not populate approval fields. After that real record exists, `statistics_release.py --apply` will reverify all bytes before registering the existing checkpoint and integrating all five complete players together. A failed gate writes neither page nor checkpoint.

## Exact review files

These immutable links identify the final media commit. Corresponding lesson directories also contain the caption file, transcript, poster, timings, ASR/OCR and source audio. See [fresh media evidence](statistics-release-media-verification.json) for measured results and [the checkpoint](../../video-agent/statistics/checkpoint.json) for every sidecar checksum.

| Video | Exact MP4 SHA-256 |
| --- | --- |
| [1 — Become a Data Detective](https://github.com/initSrikanth/MathMagic/blob/699858b72617c7eaa0c258bf35472659c5ef4ac1/video-agent/statistics/review/lesson1/Statistics_Lesson01_REVIEW_1080p.mp4) | `30a62799547a453dcc9abc0423402e9f0d07c91050b5ff76688c42c74ce6b96b` |
| [2 — Collect and Organise Data](https://github.com/initSrikanth/MathMagic/blob/699858b72617c7eaa0c258bf35472659c5ef4ac1/video-agent/statistics/review/lesson2/Statistics_Lesson02_REVIEW_1080p.mp4) | `24af87f512d83491c380b8d2b8ba74f0d6533f231af36cece3c36b3e4f3e42b4` |
| [3 — Discover the Mode](https://github.com/initSrikanth/MathMagic/blob/699858b72617c7eaa0c258bf35472659c5ef4ac1/video-agent/statistics/review/lesson3/Statistics_Lesson03_REVIEW_1080p.mp4) | `3b5cf6f02baf350f82449f88ec9f02684e6e994a5b68c387c8701f68f85fb708` |
| [4 — Read Line Graphs](https://github.com/initSrikanth/MathMagic/blob/699858b72617c7eaa0c258bf35472659c5ef4ac1/video-agent/statistics/review/lesson4/Statistics_Lesson04_REVIEW_1080p.mp4) | `106b5ef43e5443ea6bdbbd5126e06321a3f50c7aa2abc15b19539ff019e6034c` |
| [5 — Investigate and Communicate](https://github.com/initSrikanth/MathMagic/blob/699858b72617c7eaa0c258bf35472659c5ef4ac1/video-agent/statistics/review/lesson5/Statistics_Lesson05_REVIEW_1080p.mp4) | `d95d6e121b3cbce7b038af9009a265ff52ba8bb17a246338c719808061224326` |

All five freshly passed full FFmpeg decode, 1920×1080 H.264/yuv420p/30fps, AAC, faststart, source-audio correlation above 0.99998, non-silent speech-window checks and zero measured clipping. Existing unexpected-silence checks passed; the two planned thinking pauses remain unchanged. All recorded bundle checksums match, including captions, transcript, poster, original narration and technical evidence. No videos or narration were rerendered.

The existing scripts/checkpoints retain the hook, exact learning phrase, goal, three success criteria, prior knowledge, examples, predictions, thinking pauses, misconception correction and reflection. Golden Rules structural checks pass; natural delivery, educational pacing and full audiovisual quality remain human-review gates. Captions follow native sentence audio boundaries. ASR word emissions and sampled OCR remain approximate checks, not perceptual certification.

All **71 static intervals and 21 brief transitions** have three decoded-frame samples, overlapping sentence text and individual technical notes in [the flagged-interval record](../../video-agent/statistics/review/flag-review/README.md). Samples show persistent teaching models and brief focus/context changes; no objective mathematical/reveal correction was established from those samples. All human resolutions remain pending. Samples cannot exclude defects between sampled times.

## Observed checks

- Final broad Chromium run: **142 passed, 0 failed, 10 skipped**, no retries. Desktop and Pixel 7 profiles use system `/usr/bin/chromium`; responsive checks include 390px, 768px and desktop. This includes the dashboard, all five lessons/tools, complete 30-question assessment and feedback, actual review-file playback/captions/transcripts/posters, proposed accessible integration, and the actual auth/progress adapter with safe mock Firebase SDK modules. Existing Fractions, Whole Numbers, Decimals, Addition/Subtraction, Multiplication/Division, Factors/Multiples, Measurement and Space navigation regressions passed.
- The ten skips are approval-dependent **production** Statistics video-player checks. All ten real review-media cases and all ten proposed integration-player cases ran successfully. Production integration is deliberately withheld.
- Additional targeted Chromium run: **4 passed, 0 failed**: two lesson 1 fullscreen/player rechecks and two existing native Measurement Choose Units video regressions.
- Protected checks: **19 scripts passed**. Statistics assessment validation covers **30,000 positions / 1,000 seeded attempts**, all 30 families, six bands, three curriculum descriptions, correct feedback and zero detected within-attempt duplicate prompts/keys/options.
- Python: **51 contract tests passed** (including 12 new release-gate tests), **8 independent video-model tests passed**, **7 timing/model regressions passed**. Three additional Space assessment/geometry/progress regression scripts passed. Updated Statistics checkpoint verification passed separately.
- WebKit: **1 launch failure; 0 test bodies executed**. The pinned `webkit-2203` executable is absent; one official CDN provisioning attempt returned 403. Browser assertions were not disabled. This is neither WebKit nor physical Safari/iOS verification.
- Firestore emulator: **0 test bodies executed**. After correcting its cache/config location to a writable workspace, the official v1.19.8 emulator JAR download returned **403 Domain forbidden**. No further download retries. Mock tests verify actual adapter behaviour, not deployed Firestore rules or live persistence.

Machine-readable results and limitations are in [statistics-release-qa.json](statistics-release-qa.json). Browser media-request cancellations produced local-server connection-reset diagnostics; they did not cause test failures.

## Live baseline and remaining gate

Read-only live checks observed the [dashboard](https://initsrikanth.github.io/MathMagic/dashboard.html) returning **HTTP 200**, without a Statistics link. The intended Statistics URL, `https://initsrikanth.github.io/MathMagic/statistics.html`, returned **HTTP 404**. The latest successful existing Pages run is [42704173497](https://github.com/initSrikanth/MathMagic/actions/runs/42704173497), on **047666034299b6e6726e1e7a1d56eee8374aa74a**. There is no deployed Statistics commit and no post-deployment success claim. Existing Pages and suspended video-production workflows are unchanged.

Before release: obtain and record genuine full approval for all five exact files and all flags; run WebKit where its pinned executable is available; run emulator checks where its JAR is available; apply the gated registration/integration; pass required checks on that final head; then perform the authorised merge through existing Pages deployment and verify the live topic. No authorised live Firebase test account was available; Google sign-in, production rules, cross-device persistence and physical iOS remain unverified. No student data or production Firebase settings were modified.

Elapsed release preparation: approximately **22 minutes to the QA checkpoint**, starting 19:30:06 UTC; commit/upload follows. Five existing videos were preserved; no rendering time was incurred in this release task.
