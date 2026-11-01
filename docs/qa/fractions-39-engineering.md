# Issue 39 — Engineering evidence and remaining limits

## Changes

- Added a labelled 0–3 number line with twelve equal quarter steps, placing two and one half at ten quarters and two and three quarters at eleven quarters. SVG accessible title/description and adjacent stacked-fraction reasoning distinguish the positions without colour alone.
- Added the actual eight-part model for three quarters minus one eighth: rename six eighths, remove one eighth, leave five eighths. Clarified equal-sized wholes and non-zero multiplication/common-factor division.
- Aligned generated number-line ticks with the axis and removed a superseded pseudo-element that drew a second axis. Navigation pauses hidden video players, updates current-page accessibility, and focuses the new heading. Practice answer reveals use the shared green feedback state.
- Restored visible **New Challenge** after completion, plus **Retry saving this attempt** on save failure. Each retry retains the same attempt ID. Saves in flight disable conflicting actions; discarding an unsaved result requires an explicit confirmation.
- Progress updates use Firestore transactions in the existing UID/topic document, avoiding read-modify-write lost updates. Scores are validated, approval/sign-in checked again, blocked local storage cannot turn a successful remote save into a false failure, and stale auth callbacks cannot redirect a newly approved account.
- Added isolated progress adapter tests and focused browser tests. Both the adapter tests and the assessment specialist's seeded generator test are included in `npm run test:protected`, with all earlier checks preserved.

## Observed tests

- `node tests/fractions-progress.test.js`: PASS. Mocked Firebase/DOM tests cover concurrent attempts, duplicate events, retry after a committed write whose acknowledgement fails, invalid scores/IDs, revoked approval, sign-in changes, stale denied/error callbacks after account switch, blocked cache, remote read failure, and UID/topic isolation.
- `node tests/generator-fractions.test.js`: PASS on the combined engineering/assessment source; 1,000 attempts / 30,000 positions, seeded exact arithmetic/marking checks. This is not browser or real Firebase integration.
- `tests/e2e/fractions-engineering.spec.js`: six Playwright cases across desktop Chromium and Pixel 7 Chromium emulation. Worked-model containment additionally checks 390/768/1280-pixel viewports; tests cover labelled models, equal number-line endpoints, current-page/focus behaviour, hidden-player pause calls, rendered green/red feedback, and a complete 30-position UI flow through failed save → same-ID retry → new challenge. Firebase auth is deliberately aborted and the progress service stubbed in these UI tests.
- Browser environment: existing `/usr/bin/chromium` via temporary configuration, private localhost server on port 42739, no retries. An initial setup attempt lacked socket permission; the next used an already occupied port and served the video specialist's older JS. Both causes were diagnosed before the valid isolated run. No product assertions were weakened to obtain a pass.

## Not certified / remaining gaps

Real Firebase authentication, deployed Firestore rules/transaction permissions, production save/restore across devices, and real Safari/iOS have not been exercised. The existing legacy cache-recovery baseline remains; a local cache is not authoritative proof of achievement or entitlement. Static browser-delivered assessment still exposes its answers as recorded in AGENTS.md; this work does not claim server-protected assessment.

The existing progress document retains the most recent **100 completed attempt IDs**. Idempotent retry reconciliation is bounded to that history, not an unlimited exactly-once guarantee. Dashboard resets clear that document's metadata; an already open page with an old pending save can race a dashboard reset. That race is recorded rather than silently expanding this task into a cross-page reset protocol.

No approved video bytes or player selection were changed by engineering. Media restoration, any required founder approval, exact integrated-head CI, and post-deployment validation remain CEO/independent-QA gates. Local Chromium checks are not physical-device or production-service proof.
