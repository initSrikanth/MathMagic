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
