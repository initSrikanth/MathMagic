# Year 5 Statistics — QA and recoverable delivery

> Video-production update: the separate owner-authorised five-video task has completed the review bundles. See [current video QA](statistics-video-qa.md) and `video-agent/statistics/checkpoint.json`. The results below preserve the earlier topic-delivery checkpoint at 7bd0f23 and its historical blockers.

Implementation commit: `ce25e618a749f8c590fdc81a0e53b0a60acba9bb` (following initial checkpoint `83e9930`). Base: `047666034299b6e6726e1e7a1d56eee8374aa74a`. Draft PR: https://github.com/initSrikanth/MathMagic/pull/60. No merge, deployment, PR59 changes or production Firebase writes.

Delivery: five written constructivist lessons, five interactive experiences, 30-question assessment with six bands, worked correct/incorrect feedback, approved-user Firebase-compatible progress and dashboard. Title is configurable in `js/statistics-config.js`. Data tools accept nominal choices, ordered ratings and discrete counts; reject invalid/missing responses; retain real repeated choices; export a checked spreadsheet CSV. The investigation report checklist explicitly requires partner/teacher reasoning review.

## Observed results

| Check | Actual result |
| --- | --- |
| Final targeted Statistics Chromium | **24 passed, 0 failed, 10 skipped** (76.4 seconds); desktop and Pixel mobile projects, 390/768/1280 widths |
| Statistics assessment | **1,000 seeded attempts / 30,000 positions passed**; independent answer checks for all 30 families; 0 invalid answers and 0 within-attempt duplicate prompts/keys/options |
| Question variation | 13 families vary; 17 reasoning families intentionally fixed. This is not a claim of 30,000 different questions |
| Protected/unit command | **19 check scripts passed**, including assessment, actual progress adapter with mocks, dashboard and blocked-video checkpoint |
| Progress mocks | Approved/denied and stale access; UID isolation; concurrent/idempotent writes; lost-ack refresh recovery; 105-attempt history; valid score/ID bounds; lesson completion preserved across attempts |
| Dashboard mocks | 3 states passed: Start, In Progress, Proficient; best score and minimum-five cap |
| Existing Space checks | 3 scripts passed: 30,000 questions, exact geometry/net enumeration and progress mocks |
| Existing Measurement independent validation | 1,000 attempts / 30,000 positions passed, 0 duplicate/invalid answers; 5 lessons / 60 scenes / 40 models / 27 board equations checked with Python/SymPy |
| Canonical video contract | **31 tests passed**; release guard check against base passed without claiming Statistics media complete |
| Visual review | Actual 390px line-graph and desktop distribution screenshots inspected; enlarged mobile labels, readable table alternatives, no page overflow in automated layouts |
| Statistics WebKit | **16 runner failures caused by missing browser executable**, before any test body. Install attempts failed with network-policy 403 at cdn.playwright.dev / playwright.download.prss.microsoft.com. Final suite config has 17 cases (CSV case added later); none verified in WebKit |
| Firestore emulator | Locally **0 tests executed** (JAR download 403). On implementation commit ce25e61, existing Actions job 136225631782 step 11 **completed successfully**, running Measurement, Space and Statistics emulator scripts, including actual adapter transactions and isolated rules. This is demo-emulator evidence, never deployed production rules |
| New Statistics media | **0 of 5 videos**, 0 actual-audio transcripts, 0 caption files. Ten Chromium media checks explicitly skipped; no fabricated media/timing |
| Broad Chromium regression | **244 passed, 0 failed, 10 skipped** in 694.3 seconds; desktop 122 passed/5 skipped and mobile 122 passed/5 skipped. All **222 pre-existing Chromium cases passed**. Broad enumeration preceded the CSV test addition; the separate final targeted run includes it |
| GitHub Actions | Existing Browser QA run started on ce25e61: https://github.com/initSrikanth/MathMagic/actions/runs/44717834564 . Not a claimed pass; final documentation commit triggers its own run |

Local browser execution used the installed `/usr/bin/chromium` through an uncommitted scratch config because pinned browsers could not be downloaded. It retained the repository tests/assertions and both desktop/mobile projects; retries were 0. Browser modules were deliberately isolated with test-only adapters/routes. This does not test Google sign-in, deployed Firestore rules, App Check, cross-device persistence or physical iOS. No production bypass was added.

## Precise media checkpoint

`video-agent/statistics/checkpoint.json` records five script/proposed-narration hashes and word-trigger storyboards. The unchanged `assert_generation_allowed('production', …)` rejects Statistics with **VIDEO PRODUCTION SUSPENDED**. The approved Kokoro/ASR model directories are also absent. The current task authorises this product but explicitly forbids changing Golden Rules/bypassing controls; no workaround or hold exception was added. No synthesis or rendering jobs were dispatched, no credits used, no media registered, no blank players published. Proposed narration texts are not described as transcripts of nonexistent audio.

Resume using the existing production-v2 native Kokoro renderer/configuration after its gate permits Statistics and exact models are available, then actual alignment, chart drawing adapter, render/decode/media checks and full listening/viewing. See `video-agent/statistics/README.md`. No infrastructure redesign is proposed.

## Reproduce

No build step or new dependency is required; this is the platform's existing static HTML/JS architecture.

```sh
npm ci
npx playwright install chromium webkit
npm run test:protected
npx playwright test statistics.spec.js
npx firebase emulators:exec --project demo-mathmagic-year5 --only firestore --config tests/emulator/firebase.json "node tests/statistics-emulator.test.cjs"
python3 tests/serve.py
```

Open `http://127.0.0.1:4173/statistics.html` using an approved account. Local serving preserves the production authentication/approval guard. For an isolated UI preview use the automated Playwright flow, which supplies only safe test adapters. Storyboard HTML under `video-agent/statistics/storyboards/` can be opened directly as **silent, untimed design references**, not video previews.

## Human-only release checklist

- [ ] Teacher reviews language, genuine cognitive progression and open investigation reports; test with Year 5 learners.
- [ ] Five final videos rendered with actual matching captions/transcripts; full listening/viewing, accent/enthusiasm, model accuracy and mobile legibility reviewed and approved against exact SHA-256 bytes.
- [ ] Physical Safari/iOS and touch/assistive-technology checks; complete WebKit suite where installation is allowed.
- [ ] Approved-user live Firebase save/restore across devices, rejected signed-out/unapproved/cross-UID access, deployed rules and App Check verified by an authorised operator.
- [ ] Exact-final-head Actions results reviewed; unresolved applicable FAILs in statistics-rule-audit.md prevent release.

Production elapsed time and broad-suite outcome are recorded in the final delivery entry below. Work ends at this recoverable checkpoint; no future waiting task is created.

## Final delivery entry

Broad Chromium, final targeted Statistics, all 19 protected scripts, 3 Space scripts, independent Measurement mathematics, and 31 contract tests passed. No assertion failures in the executed Chromium runs. All 10 Chromium skips are Statistics video checks. Local WebKit produced 16 missing-executable launch failures; CI full browser/WebKit results were still pending at handoff. CI emulator step passed on ce25e61, without a live Firebase claim. Final documentation-only commit leaves runtime/test code unchanged from ce25e61 and starts the existing workflow for its own head; no green final-head result is inferred.

Production time to final QA checkpoint: 1480 seconds (24.7 minutes), 09:59:06–10:23:45 UTC on 20 November 2026, including startup and test execution. This measures elapsed task time, not the duration of unrendered videos.
