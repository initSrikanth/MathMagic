# Agent instruction consolidation review

Reviewed on 16 October 2026 against main `e5a5124321b743090dc0ab25a3aa7f7a64030f37`. Its parent `65e3e898ffa935f30466f1f59a6ae9d51459e37e` has identical application/test files; main added only the original `AGENTS.md`. This review records decisions and evidence, not a parallel instruction authority or a production certification.

## Scope and sources

Only `AGENTS.md`, `MATHMAGIC_AGENT.md` and this review change. Application files, tests, workflows, assets and Firebase configuration remain untouched. The canonical instructions are in root `AGENTS.md`; `MATHMAGIC_AGENT.md` is a compatibility pointer.

Compared both original instruction documents with README/package manifests; HTML and `js/` authentication, progress and quiz implementations; `functions/index.js` and `functions/factors-multiples.js`; `firebase.json`; all ten root QA test scripts and the six Playwright topic suites; `.github/workflows/browser-qa.yml` and the video-publication workflow; topic specifications under `docs/`; explainer records; and `video-agent/VIDEO_PRODUCTION_RULES.md`.

## Conflict resolution ledger

| Previous inconsistency | Consolidated decision and evidence |
| --- | --- |
| Two general policy authorities | `AGENTS.md` owns all general policy. The detailed standards from `MATHMAGIC_AGENT.md` are incorporated there; its old path redirects readers. Topic/video specifications supplement the canonical rules. |
| `guard.js` reference | Corrected the operative path to `js/auth-guard.js`; login, denial and topic module paths are identified explicitly. |
| Generic 20 questions versus 30-question progression | Existing source and topic specs use 30 questions. Preserve all six current 30-question challenges and six five-question bands. Future count changes require an explicit topic specification and QA. |
| Five attempts versus proficiency | Current topic save handlers award proficiency for a full 30/30 score and preserve an earned flag. The five-attempt display is a practice target, not a new proficiency prerequisite. Preserve explicitly documented topic conditions. |
| Browser baseline versus protected-by-default | Preserve the five current browser topics as transitional and honestly describe their downloadable logic. New protected dependencies require a production-verified pipeline/pilot. Keep the protected target and rollout gate; do not downgrade the existing protected-only Multiplication & Division topic or its fail-closed tests. |
| Backend files versus live protection | Separate repository implementation from deployment evidence. Preserve Auth, approval, ownership, safe payloads, server marking and App Check requirements; record missing implementation/production evidence below. |
| Self-hosted MP4 versus Scrimba preference | Original explainers remain preferred. Scrimba is the default for new concept explainers; explicitly approved presenter footage/MP4 follows the retained production/replacement path. Keep working embeds until replacements are checked and playable. |
| Link-by-default versus required embeds | Research resources for substantial revisions. Prefer original explainers; otherwise link to the creator by default. Embed a suitable educational video where pedagogically useful and provider-supported, meeting privacy/copyright/accessibility rules. Record justified omissions. Never copy third-party media without rights. |
| Presenter preservation versus future expression requests | Reuse approved footage/voice unchanged. Modest expression/movement guidance applies only to newly authorised future generation. Retain all scene, notation, codec, frame/audio, source-retention and playback requirements. |
| Historical pending Mixed Numbers task | Retain the exact approved filename, destination and targeted replacement procedure as conditional historical requirements. Do not execute or infer new video approval during unrelated requests. |
| Mandatory PR workflow versus explicit main commit | Module work uses branch/PR, exact-head required checks and permitted squash merge. Explicit main commits may proceed where branch rules permit; no bypass or force push. A docs-only commit does not claim module release or deployment. |
| Universal release audit versus scoped documentation task | Keep all substantial-module release gates. Docs-only work receives a scoped consistency/path/scope audit, with unrelated baseline failures recorded separately and no application/test modifications. |
| README/older docs versus current implementation | Source establishes current behaviour; topic specs establish required scope. An implementation gap is recorded, not silently promoted into the standard. Production claims require separate observation. |

## Instruction preservation audit

PASS here means the instruction requirement was retained or explicitly reconciled in the canonical document. It does not mean the application satisfies it in production. The unchanged detailed standards cover each former quality-rule heading; the following groups identify the full migration coverage.

| Requirement | Result and canonical location/evidence |
| --- | --- |
| Mission, scope, first inspection, preserve existing work, architecture and narrow changes | PASS — Authority, scope and first actions. No framework rewrite or unrelated changes authorised. |
| Build command contract and end-to-end work | PASS — Module build contract and detailed quality standards; scoped user requests take precedence. |
| Curriculum authority, verified internal descriptor codes, IB context, Year 5 scope | PASS — Curriculum invariants; Australian Curriculum is the authority; Curriculum codes stay internal. |
| Research, originality, coverage matrix, teaching sequence, teaching-assessment alignment | PASS — Mandatory workflow, Question-type coverage, Originality, Representation diversity and Teaching-assessment alignment retained. |
| Difficulty progression, no artificial difficulty, QCAA validity/accessibility/reliability | PASS — Genuine difficulty progression, No artificial difficulty and QCAA quality assessment rule retained. |
| Thirty questions and topic-exclusive boundaries | PASS — Curriculum invariants and linked topic specifications; generic twenty-question default explicitly resolved. |
| Generator reliability, stress QA, boundary/input/equivalence/distractor/duplicate checks | PASS — Curriculum invariants, Generator reliability and Checks sections retain the checks and actual-count reporting requirement. |
| Fraction notation, mixed-number separation, equivalence/simplification, visual integrity | PASS — Curriculum invariants, Notation rule and Visual integrity. Internal slash values must be rendered before display. |
| Branding, responsive layout, keyboard/labels/contrast/focus, child-friendly wording | PASS — Curriculum invariants, Student-language rule, Visual integrity and Input/browser hygiene. |
| Worked feedback, equivalent marking, green/red feedback classes and rendered colours | PASS — Feedback retained, including browser verification of state/class and computed colour for substantial changes. |
| Attempts, full-mark proficiency, best/last score, reset, save/restore and double-count prevention | PASS — Curriculum, assessment and progress invariants; current semantics distinguished from the five-attempt practice target. |
| Google Auth, approval gate, Firestore ownership, no bypasses/secrets, token handling | PASS — Current structure and security architecture; no client-side approval substitute for backend rules. |
| Transitional baseline and protected-content requirements | PASS — Operational baseline and protected-content target; protected-only topic preserved; staged production cutover checklist retained. |
| Rule-by-rule audit, exact-head checks, generator/browser separation, substantial-module release gate | PASS — Release QA, Rule-by-rule post-build compliance audit, Automated browser QA gate and Checks sections. |
| Visual/dimensional regression, desktop/mobile, traces/screenshots/reports, real-device checks | PASS — Visual regression and diagnostic evidence retained, plus Checks section. |
| New original explainers, Scrimba URL/access parameters, recording, supported embeds | PASS — Original MathMagic explainer rule retained with explicit approved-MP4 exception. |
| Resource research, copyright, no rehosting, child-directed settings, attribution/fallback, no autoplay | PASS — External learning resources and copyright rule and Embedded learning resource requirement retained. |
| Approved presenter appearance/voice, programmatic graphics, timing, codecs, media/source retention | PASS — Approved presenter videos and media replacement; all 18 numbered video-production rules remain applicable. |
| Exact approved Mixed Numbers bytes, scoped section/path, no substitution, playback verification | PASS — Historical Mixed Numbers replacement record. No media task executed. |
| Git/PR/main policy, no force push, truthful SHA/check/deployment reports | PASS — Checks, audit and release workflow; direct main does not imply browser CI or Pages deployment. |

## Checks and existing failures

Commands were run against the documentation candidate with application/test files unchanged from the reviewed baseline. Local Node was v24.19.0; the existing browser-QA workflow specifies Node 20. No claim of a Node-20 CI run is made.

| Check | Observed result |
| --- | --- |
| `npm run test:protected` | FAIL overall at `tests/external-video-pattern.test.js:29`. Prior scripts passed: Fractions, Decimals & Percentages, Whole Numbers, Addition & Subtraction, Multiplication & Division architecture/fail-closed checks; Factors & Multiples browser architecture; and both generator stress suites. |
| Multiplication & Division generator (within command above) | PASS — 500 challenges / 15,000 positions. |
| Factors & Multiples generator (within command above) | PASS — 1,000 challenges / 30,000 positions. No extra invalid/duplicate metrics are claimed beyond those suites' assertions. |
| Baseline `node tests/external-video-pattern.test.js` | Same FAIL at line 29 using a clean archive of `65e3e898ffa935f30466f1f59a6ae9d51459e37e`, whose app/tests equal reviewed main. This is pre-existing, not caused by instruction changes. |
| Video-coverage diagnosis | Test requires at least 14 provider iframes and at least five Scrimba embeds. Current source contains nine YouTube plus three Scrimba iframes (12 total), and two MP4 players that this test does not count. The second threshold is also unmet, although execution stops at the first. Preserve assertions; reconcile media coverage in separately authorised application/QA work. |
| `node tests/explainer-embed-pattern.test.js` (run separately after short-circuit) | PASS — three current Scrimba embeds. Does not establish network playback. |
| `npm run test:e2e` | BLOCKED before browser tests: configured Python web server cannot create its socket, `PermissionError: [Errno 1] Operation not permitted`. No student-flow, mobile visual or real-auth pass claimed. |
| Local Markdown target checks, whitespace and diff-scope audit | PASS — referenced local documents exist, canonical/stub links resolve, no trailing whitespace; only the three instruction/review documents are in the intended change. |
| Instruction coverage and backend syntax | PASS — all 24 prior detailed QA/architecture rule headings retained or explicitly reconciled; single canonical policy confirmed; `node --check functions/index.js` and `node --check functions/factors-multiples.js` passed. |
| Lint/build | No standalone lint/build scripts defined. No new scripts or tests added for documentation. |
| Production Firebase/Firestore/App Check, provider playback, Pages deployment | NOT VERIFIED — outside this documentation-only task; no suitable production sessions exercised. |

## Remaining implementation and production evidence gaps

No unresolved instruction-policy conflicts remain after the resolutions above. These existing implementation/configuration gaps remain open and are not fixed by documentation:

- No Firestore rules file is tracked; deployed approval/progress/session access rules cannot be established from this checkout.
- Callable handlers specify App Check enforcement, but the browser modules do not initialise App Check. Production registration, configuration, deployment and real success/rejection tests remain unverified.
- Submit-time approval rechecks, topic checks and session expiry are not uniform across backend pilots. The canonical target requires these protections; no application changes or claim of full compliance is made here.
- Browser QA cannot run in the current restricted environment; the existing video-coverage test remains failing. Tests and workflows were not weakened.
- The Mixed Numbers approved replacement is not published by this task. The current section's working Scrimba reference remains untouched; media playback has not been retested.

GitHub main was observed at the reviewed SHA with `protected: false` and required status checks off. The separate branch-protection-detail endpoint returned 403 (`Resource not accessible by integration`), so no detailed administration access is claimed. The expressly requested direct documentation commit uses the permitted non-force path; it does not bypass a module release gate or establish a deployed release.
