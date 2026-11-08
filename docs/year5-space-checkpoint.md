# Year 5 Space implementation checkpoint — 2026-11-08

Branch: feature/year5-space-geometry, PR #57. This is development work, not a release.

## Implemented
- Ten preliminary lesson sections in space-lessons.html.
- Manipulatives: space-lab.html, space-coordinates.html, space-net-explorer.html, space-classification.html.
- js/space-question-bank.js: seeded 30-question six-band generator; each item has four unique options, correct answer, curriculum tag and explanation.
- Generator smoke-checked for seeds 1–100 using the fetched source evaluated in an isolated JavaScript function; 3,000 generated items had no structural/uniqueness-option exceptions.

- Added space-challenge.html, js/space-challenge.js and js/space-auth.js. Uses Firebase approved-user check and transaction-based, idempotent progress saving modelled on Fractions. Challenge UI implements 30-question flow and retryable save. **Not browser-tested, not independently mathematically validated, and not approved for release.**\n- Linked challenge from space-lessons.html.\n- Canonical video-production contract explicitly has an active new-topic production hold. **Do not start Space video renders while hold remains active**, even though the user has requested videos; reconcile authority before any render.\n\n## Critical remaining gates
1. Curriculum audit against exact authoritative AC9 descriptors, achievement standard and elaborations. Nets and branching algorithms need assessment coverage beyond the current prototype.
2. Replace prototype question families with rigorous diverse, genuinely nonrepeating mathematical tasks, including valid/invalid nets, rotations, algorithms, explanations, word problems and worked distractor feedback; add independent mathematical oracles and seed stress tests. Current generator is NOT a complete assessment and must not be presented as released.
3. Browser-test authenticated Space challenge, test reload/retry/fail-closed cases, preserve completed progress, and assess whether generated browser-side answers satisfy the project's transitional security model. The UI currently resets an unfinished attempt on reload.
4. Upgrade lessons with substantive scaffolding, multiple worked examples, differentiated practice and complete interactive coverage.
5. Produce videos under golden rules, independently verify actual narration, AV, duration, visual maths and no spoken/visible branding.
6. Add automated desktop/mobile/keyboard tests, resolve CI failures, merge only after gates pass; verify live deployed pages.

Next run: independently test the newly added challenge UI in desktop/mobile browsers, strengthen the generator with mathematical oracles and additional net/rotation problems, then integrate approved-user dashboard navigation. Do not revisit unrelated topics without a release-blocking reason.

## Mathematical oracle test addition — 2026-11-08
- Added `tests/space-question-bank.test.js` (commits `74e3038`, corrected regex `4bfc1f1`).
- Executed the fetched generator and independent test source in a JavaScript isolate: **PASS, 30,000 questions across 1,000 seeds**, validating six bands, distinct prompts/options, all four AC9M5SP descriptors, arithmetic of translations/reflections/routes/rotations, polygon properties, solid properties and fixed net/symmetry examples.
- This is a mathematical/structural generator test, **not** a browser test, Firestore integration test, full distractor pedagogy review, or proof that the bank meets the final diversity requirements. The bank currently uses five repeated coordinate-template variants per band; expand task families and worked distractor feedback before release.
- Next: browser-test Space challenge on desktop/mobile, inspect CI and repair failures, improve feedback and persistence, then release gates. Video-production hold remains unresolved.

## Hourly release session — 2026-11-08 06:45 Australia/Brisbane
- Verified PR #57 still open at `c884baa`, mergeable, but Browser QA run `42408133557` failed in `Run MathMagic browser QA` (job `128510196449`). The available GitHub REST connector exposes job/step conclusions but does not expose the Playwright log or artifact contents through its permitted text fetch endpoints; **root cause is not established**. Do not guess or alter unrelated Time and Angles code without failure evidence.
- Commit `f6204d0b` adds `node tests/space-question-bank.test.js` as a mandatory Browser QA workflow step, covering 30,000 generated questions and independent mathematical checks. The earlier isolated test pass is recorded above; this commit makes the same oracle a PR gate, but the new CI run has not yet been observed to pass.
- Next session: inspect fresh CI job and Playwright failure diagnostics through an available authorised interface, reproduce failing test, fix only verified cause; add desktop/mobile Space UI tests, complete lessons and verified videos. Do not merge until all release gates pass.

## Hourly release session — 2026-11-08 07:40 Australia/Brisbane
- Inspected latest PR #57 head `7974214a` and GitHub Actions run `42412401797`. The independent Space assessment mathematical gate **passed** (job step 13), as did the preliminary native WebKit video playback gate; full `Run MathMagic browser QA` **failed** (step 16). Detailed failing Playwright assertions remain unavailable via the permitted GitHub text-fetch interface; no unrelated Time and Angles code was changed speculatively.
- Found a concrete Space assessment data-loss issue by code inspection: the `Try a new challenge` button remained active during a failed/in-flight Firestore save, allowing the student to discard the retryable unsaved result. Fixed in `js/space-challenge.js` commit `35f59690`: hide/disable the new-attempt action until the current attempt has been saved successfully; preserve the stable attempt ID and retry path on failure; block accidental restart while saving. This is a code-reviewed fix, **not yet browser-verified**.
- Next: write authenticated desktop/mobile Playwright coverage for save success/failure/retry and reload, investigate the failing browser QA assertions using available trace/log access, and continue full lesson/video production and independent QA. Do not merge until all gates pass.

## Hourly release session — 2026-11-08 08:46 Australia/Brisbane
- Latest inspected PR head `c9e90860`; GitHub Actions run `42417051308` passed mathematical oracle, Firestore emulator, protected-architecture and native WebKit preflight, but full Playwright browser QA failed. Available job metadata shows only failing step, not the underlying assertion.
- Added `tests/e2e/space-challenge.spec.js` at commit `996f440f`, running on existing desktop Chromium and Pixel 7 mobile projects. It exercises all 30 questions and six bands, rendered choices, worked feedback, successful save, simulated failed Firestore save and idempotent retry using the same attempt ID. Firebase is stubbed only within test network routing; production authentication remains unchanged.
- **Tests newly committed, not yet observed passing in CI.** Next inspect fresh Actions result, fix reproducible failures, add true Firebase-approved-user/fail-closed integration and video QA. No merge/deploy claim.

## Hourly release session — 2026-11-08 09:48 Australia/Brisbane
- Inspected PR #57 at `aed28304`; latest run `42422204597` passed Space mathematical oracle, Firestore emulator, protected architecture and WebKit playback preflight, but full Playwright suite failed. GitHub jobs metadata still lacks individual failing assertion text; no unverified root cause claimed.
- Commit `981441ef` integrates Year 5 Space into the existing dashboard as a dedicated navigation card, without falsely displaying progress that the dashboard loader does not yet support.
- Commit `0500abe0` adds desktop/mobile Playwright coverage for dashboard navigation and fail-closed challenge start when the approved-user service is absent. These tests have been committed but have not yet been observed passing in CI.
- Next: inspect fresh workflow result; resolve concrete Playwright assertions, add authenticated progress/dashboard support, and complete pedagogical and perceptual video QA. PR remains unmerged and undeployed.

## Hourly release session — 2026-11-08 11:48 Australia/Brisbane
- Retrieved actual decoded GitHub Actions job log for run `42431121492`, job `128580013155` (previous assertion that logs were inaccessible is superseded). Browser QA: 195 passed, 8 failed; four Space navigation assertions (desktop/mobile) and four Time and Angles completion/retry assertions (desktop/mobile). Failures are not evidence that all Space assessment tests failed.
- Space dashboard link exists with href `space-lessons.html`; Playwright `getByRole` could not see it because dashboard remains protected without approved authentication in test. Challenge Start button also exists disabled but is inside `body.auth-loading main` (visibility hidden), so `getByRole` cannot find it. Commit `a18cc7a` updates tests to inspect protected DOM by stable locators without claiming an unauthenticated dashboard click is valid; lesson destination is visited directly. The new test run has NOT been verified.
- Next: inspect new exact-head CI; repair remaining Time and Angles shared regression only with log evidence; verify authenticated Space UI and video pipeline. No merge or deployment.

## Hourly release session — 2026-11-08 12:41 Australia/Brisbane
- Inspected exact-head run `42435850085`: 199 browser tests passed, 4 failed, all in existing Time and Angles 30-question completion/retry tests (desktop/mobile). Space browser navigation failures from previous run were resolved.
- Decoded job `128594399622` and identified concrete defect: Time and Angles kind 11 correctly requires `h:mm pm`, but the subsequent generic integer-only validator mistakenly also applied to kind 11, rejecting even the canonical correct answer with `Use h:mm pm format.` This also caused the retry test to stall waiting for the next button.
- Commit `a3f43ed` excludes kind 11 from integer validation while preserving its dedicated strict 12-hour format validator. Commit `0b5c2a2` adds explicit Playwright regression coverage for canonical pm answers.
- New commits are NOT yet observed passing in CI. Next inspect exact-head run; if green, continue Space interactive tool audit, approved-user integration and perceptual video creation. Do not merge until all video and QA gates pass.
