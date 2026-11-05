# Year 5 Measurement — resumable development checkpoint

Updated after commit `bb329d181585998374a660efa91569d24796efac`.

## Scope
Finish **only** Year 5 Australian Curriculum v9 Measurement. Preserve the completed `measurement.html` / Measuring Our World topic and its approved media. Five pages is a baseline, not a ceiling. No video rendering in this application-development task.

## Observed repository state
- Main dashboard has a Measurement section with a Measuring Our World card; the Time and Angles draft branch has additional work. Verify the current branch head before editing.
- Measuring Our World already has lesson tabs for length, mass/capacity, perimeter, area and design. Its HTML contains a dashboard link, but **functionality is unverified**.
- Draft PR #56 on branch `year5-time-angles-chatgpt` has a combined Time and Angles learning module, quiz and Firebase progress adapter. It is **not production-ready**.
- Quiz keyboard submission bug fixed in commit `0851ff0` by attaching Enter handling when each answer input is rendered.
- Added interactive self-checking activities to all five Time and Angles lessons (`js/time-angles-practice.js`, `time-angles.html`, `css/fractions.css`) with accessible inputs, timelines, timetable and SVG angle diagrams.
- Corrected quiz noon conversion and strict 24-hour input validation in `js/time-angles.js` (commit `c017429`).
- Quiz now shows six five-question difficulty labels and worked feedback for all answers (commit `a51072f`); validates angle type responses and sets appropriate mobile input modes (commit `bb329d1`).
- Added prominent dashboard-return links to the Time and Angles lesson and challenge views; root cause of reported navigation issue remains unverified.
- `AGENTS.md` is canonical. Review curriculum matrix before deciding whether to retain or split Time and Angles; avoid duplicating covered Measurement outcomes.

## Required next actions, in order
1. Inspect current GitHub branch and open PR #56, curriculum matrix, Measurement source and dashboard progress code; establish exact missing Measurement content descriptions. Preserve the five interactive activities just implemented.
2. Investigate why learners cannot return to dashboard from a topic, despite a link in `measurement.html`. Check auth guards, topic state, mobile layout and quiz screens; reproduce in a real browser and fix.
3. Finish substantive interactive teaching and mathematical coverage in the remaining Measurement topic(s); five pages is not a fixed cap.
4. Verify 30 unique valid questions per attempt, worked solutions, input validation, idempotent Firebase progress and dashboard state.
5. Run targeted and required release tests, then merge/deploy only when verified. Record tested SHA and observed outcomes.
6. Record missing video production separately; do not render without separate authorisation.

## Validation and blockers
- Source checks confirmed five lesson sections, five practice activities, a 30-question quiz structure, practice script inclusion, Enter handler, noon conversion and input validation. **No browser test or deployed Firebase check has been performed in this session.**
- Five lessons now have one self-checking interactive exercise each; further rich manipulatives, lesson depth, curriculum mapping and comprehensive QA remain outstanding.
- Dashboard navigation failure is user-reported and not yet reproduced.
- Production Firestore security rules and cross-device persistence remain unverified.

## Standing execution rule
Active interactive development must proceed immediately; the hourly automation is a checkpointed fallback, **never a wait gate**. Do not return to user simply to request continuation. Continue implementation in each available execution window and record exact unfinished actions.

## Credit and session policy
Read this checkpoint and latest commit first. Work on one coherent task per run; do not redo completed audits or spawn duplicate agents. Commit actual changes, update this file, and resume at next authorised run. Do not imply unlimited schedule or credits.
