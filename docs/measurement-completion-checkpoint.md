# Year 5 Measurement — resumable development checkpoint

Updated after commit `0851ff0be67a64917b04ec281488daa260443700`.

## Scope
Finish **only** Year 5 Australian Curriculum v9 Measurement. Preserve the completed `measurement.html` / Measuring Our World topic and its approved media. Five pages is a baseline, not a ceiling. No video rendering in this application-development task.

## Observed repository state
- Main dashboard has a Measurement section with a Measuring Our World card; the Time and Angles draft branch has additional work. Verify the current branch head before editing.
- Measuring Our World already has lesson tabs for length, mass/capacity, perimeter, area and design. Its HTML contains a dashboard link, but **functionality is unverified**.
- Draft PR #56 on branch `year5-time-angles-chatgpt` has a combined Time and Angles learning module, quiz and Firebase progress adapter. It is **not production-ready**.
- Quiz keyboard submission bug fixed in commit `0851ff0` by attaching Enter handling when each answer input is rendered.
- `AGENTS.md` is canonical. Review curriculum matrix before deciding whether to retain or split Time and Angles; avoid duplicating covered Measurement outcomes.

## Required next actions, in order
1. Inspect current GitHub branch and open PR #56, curriculum matrix, Measurement source and dashboard progress code; establish exact missing Measurement content descriptions.
2. Investigate why learners cannot return to dashboard from a topic, despite a link in `measurement.html`. Check auth guards, topic state, mobile layout and quiz screens; reproduce in a real browser and fix.
3. Finish substantive interactive teaching and mathematical coverage in the remaining Measurement topic(s); five pages is not a fixed cap.
4. Verify 30 unique valid questions per attempt, worked solutions, input validation, idempotent Firebase progress and dashboard state.
5. Run targeted and required release tests, then merge/deploy only when verified. Record tested SHA and observed outcomes.
6. Record missing video production separately; do not render without separate authorisation.

## Validation and blockers
- **No browser test or deployed Firebase check has been performed in this session.**
- Existing Time and Angles lessons are primarily static; interactive manipulatives and comprehensive QA remain outstanding.
- Dashboard navigation failure is user-reported and not yet reproduced.
- Production Firestore security rules and cross-device persistence remain unverified.

## Credit and session policy
Read this checkpoint and latest commit first. Work on one coherent task per run; do not redo completed audits or spawn duplicate agents. Commit actual changes, update this file, and resume at next authorised run. Do not imply unlimited schedule or credits.
