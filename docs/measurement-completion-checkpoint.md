# Year 5 Measurement — resumable development checkpoint

Updated after Measurement dashboard-return visibility fix commit `63059bef4d2b1d1df1f97eb153dd1522e2858ff9`.

## Scope
Finish **only** Year 5 Australian Curriculum v9 Measurement. Preserve the completed `measurement.html` / Measuring Our World topic and its approved media. Five pages is a baseline, not a ceiling. No video rendering in this application-development task.

## Observed repository state
- Branch dashboard already contains a Time and Angles card and a separate Measuring Our World card. The Time and Angles card was previously not wired to Firebase progress; commit `8a5b595` extends `js/measurement-dashboard.js` to read approved users' `progress/{uid}/topics/time-angles` and render attempts, best score and proficiency. The existing Measurement card remains supported. Dashboard now has one Measurement heading with both cards, each with a proficiency badge; dashboard script cache version bumped to v2. Browser/Firebase validation remains pending.
- Measuring Our World already has lesson tabs for length, mass/capacity, perimeter, area and design. Its HTML contains a dashboard link, but **functionality is unverified**.
- Draft PR #56 on branch `year5-time-angles-chatgpt` has a combined Time and Angles learning module, quiz and Firebase progress adapter. It is **not production-ready**.
- Quiz keyboard submission bug fixed in commit `0851ff0` by attaching Enter handling when each answer input is rendered.
- Added interactive self-checking activities to all five Time and Angles lessons (`js/time-angles-practice.js`, `time-angles.html`, `css/fractions.css`) with accessible inputs, timelines, timetable and SVG angle diagrams.
- Corrected quiz noon conversion and strict 24-hour input validation in `js/time-angles.js` (commit `c017429`).
- Quiz now shows six five-question difficulty labels and worked feedback for all answers (commit `a51072f`); validates angle type responses and sets appropriate mobile input modes (commit `bb329d1`).
- Added prominent dashboard-return links to the Time and Angles lesson and challenge views; root cause of reported navigation issue remains unverified.
- `AGENTS.md` is canonical. Review curriculum matrix before deciding whether to retain or split Time and Angles; avoid duplicating covered Measurement outcomes.

## Required next actions, in order
1. Review curriculum matrix and Measurement source to establish exact missing Year 5 content descriptions; preserve the five interactive activities. Dashboard progress wiring was committed, but needs browser/Firebase verification.
2. Investigate why learners cannot return to dashboard from a topic, despite a link in `measurement.html`. Check auth guards, topic state, mobile layout and quiz screens; reproduce in a real browser and fix.
3. Finish substantive interactive teaching and mathematical coverage in the remaining Measurement topic(s); five pages is not a fixed cap.
4. Verify 30 unique valid questions per attempt, worked solutions, input validation, idempotent Firebase progress and dashboard state.
5. Run targeted and required release tests, then merge/deploy only when verified. Record tested SHA and observed outcomes.
6. Record missing video production separately; do not render without separate authorisation.

## Current session — dashboard return visibility
- Added a clearly labelled `Back to Dashboard` anchor at the beginning of `measurement.html` learning content and within the challenge screen. Code commit `63059bef4d2b1d1df1f97eb153dd1522e2858ff9`.
- Static source inspection confirmed the previous two header links and the two new context-specific anchors, all pointing to `dashboard.html`. This improves discoverability but does **not** reproduce or establish the root cause of the user-reported navigation failure.
- Browser, mobile and authenticated Firebase navigation tests remain **not run**. Do not merge on the strength of static inspection.
- Next exact action: run authenticated browser navigation from Measuring Our World and Time and Angles lesson and challenge views; capture any redirect/console failure and fix it. Then validate 30-question generator and curriculum coverage.

## Validation and blockers
- Static inspection confirmed the Time and Angles dashboard card and its previously missing progress wiring; `js/measurement-dashboard.js` now handles both Measurement topic IDs. This was a source-level change, **not a passed Firebase/browser test**.\n- Source checks confirmed five lesson sections, five practice activities, a 30-question quiz structure, practice script inclusion, Enter handler, noon conversion and input validation. **No browser test or deployed Firebase check has been performed in this session.**
- Five lessons now have one self-checking interactive exercise each; further rich manipulatives, lesson depth, curriculum mapping and comprehensive QA remain outstanding.
- Dashboard navigation failure is user-reported and not yet reproduced.
- Production Firestore security rules and cross-device persistence remain unverified.

## Latest committed change and next action
- Code commit: `7c351c3b50eac9b4e53788cee4a3616e40fa573f` — consolidate two Year 5 Measurement dashboard sections into one, retain both cards and progress selectors, add Time and Angles proficiency badge, and bump Measurement dashboard script cache version.
- Checks actually performed: static HTML comparison confirmed one Measurement heading, one Time and Angles progress selector, one Measuring Our World selector. Inspected authentication redirect source; root cause of dashboard-return defect not yet reproduced. No browser or Firebase tests run.
- Next: reproduce navigation failure in authenticated browser, then fix and test; inspect curriculum matrix and validate the Time and Angles quiz before merge.

## Standing execution rule
Active interactive development must proceed immediately; the hourly automation is a checkpointed fallback, **never a wait gate**. Do not return to user simply to request continuation. Continue implementation in each available execution window and record exact unfinished actions.

## Credit and session policy
Read this checkpoint and latest commit first. Work on one coherent task per run; do not redo completed audits or spawn duplicate agents. Commit actual changes, update this file, and resume at next authorised run. Do not imply unlimited schedule or credits.
