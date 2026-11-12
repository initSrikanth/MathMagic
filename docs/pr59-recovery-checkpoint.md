# PR59 durable recovery checkpoint — 12 November 2026

**Release BLOCKED. Do not merge or deploy.** Existing PR: <https://github.com/initSrikanth/MathMagic/pull/59>, branch `feature/measurement-production-pilot`, base recovered as `047666034299b6e6726e1e7a1d56eee8374aa74a`. Use [the recovery procedure](codex-github-recovery.md) to discover the current head/checks; this file cannot contain its own commit SHA.

## Lesson 1 repair — current execution, 12 November 2026

The latest PR59 branch head `2b5fa082260a68704273d5aab3867bb37169a88f` was read directly from GitHub and preserved. Only Lesson 1 media, its player/captions/transcript and focused evidence/tests are changed. [Current repair readiness](pr59-lesson1-repair-readiness.md) supersedes the Lesson 1 defect status below; the remaining recovery history is retained as historical evidence.

- The new unique Lesson 1 candidate is 406.733 seconds (6:46.733). Original source MP4/hash and historical captions/alignment/ASR are preserved for rollback. Every asset for Lessons 2–5 remains byte-for-byte unchanged.
- Reused the existing Kokoro recording and recovered acoustic word timing. Removed the branded welcome sentence at measured quiet boundaries, plus redundant demonstrations/closing material to meet the 5–7 minute target. No synthesis, pitch/speed effects, invented silence or paid services.
- Removed frame branding; repaired incorrect time equivalences, noon/midnight, hidden prediction answers, explicit duration jumps and crowded labels. Reused existing clock primitives/source models. Five native caption/transcript sets are now present on the PR candidate page, with top-band cues and a new Lesson 1 poster.
- Executed checks: final targeted desktop/mobile suite **22/22 PASS**, contract **31/31 PASS**, checkpoint safety **11/11 PASS**; all 12,202 frames decode, caption timing/coverage and independent duration checks pass. Final MP4 SHA-256: `3f6501d5fe8cfedff8cb266fe3b464c027bc19fece62c832aa75c0686610b0e1`. The canonical release guard lacks a Time/Angles inventory entry and remains a release blocker; no infrastructure is changed.
- Full listening/viewing, caption fidelity/readability, persistent-model review and physical Safari/iOS remain UNVERIFIED. This is an objectively checked repair candidate, not full perceptual or release approval. Live Firebase/rules and the historical assessment-design issues remain outside this repair.
- No merge, deployment, scheduling or subsequent production stage is authorised by this execution. Stop after committing the repair and finishing targeted checks.

## GitHub state recovered (historical, 11 November)


Recovered source head: `6520819d483214943d584daa132bc3e1796baece`. Its three existing commits were preserved: `1792e0e` (pilot and frozen legacy publication), `fb91cee` (dependency triggers/Year6 scope warning), `6520819` (ignored browser diagnostics). No PR discussion comments were present when fetched.

- [Pilot42892836322](https://github.com/initSrikanth/MathMagic/actions/runs/42892836322): all8 gates passed on source6520819 / merge-test4f256cc4b024c3e6ab7579587f1696113ebe0add. Readiness job130102407233 logs explicitly reported **BLOCKED**: exact-video listening/viewing, live Firebase approval/denial, real Firestore persistence/UID isolation, deployed rules, physical Safari/iOS, five missing Time/Angles caption sets and Year6 angle scope. Candidate Measurement HTML/CSS were unpublished.
- [Regression42892836320](https://github.com/initSrikanth/MathMagic/actions/runs/42892836320): success at that historical head (238 browser tests, 31 contract tests, independent mathematics and emulator gates). This is historical evidence, not approval of new changes.
- Retained artifacts: readiness13799127824 (SHA256 `2168032d77e2c98be0046fa7746b5a7187678b81b2d5ce9b8f6f4acd41191aa5`); source13798638111; student-flow13798534246; live13799313115; browser13800560499. Receipts/readiness expire24November; browser diagnostics17November. Artifact availability was queried directly. This runtime's direct download redirect to Azure blob storage was denied; the complete rendered readiness report was recovered from GitHub job logs through the connector. No historical receipts were rewritten as current local passes.

## Work completed in the earlier recovery (historical)

- Preserved every MP4 and approved Measurement media/evidence. Five Time/Angles source hashes are in `video-agent/time-angles/accessibility/manifest.json`; no paid credits, synthesis, new-topic production or retained candidate MP4.
- Recovered actual audio pause boundaries and forced word alignment for all five lessons, plus independent offline ASR. Four brand-free tracks/transcripts and posters are integrated. Browser tests verify native track loading and advancing early/middle/late playback.
- **Lesson1 remains FAIL/BLOCKED**. The exact published video has a branded opening, branded ending and branding throughout actual frames. It disagrees with the current saved renderer script. Historical wording from `c4d27ce^` agrees with independent ASR. Faithful historical transcript/VTT/word evidence is retained under `video-agent/time-angles/accessibility/`, never referenced by the player. Frame evidence shows the defect. A tentative ending-only trim was discarded as insufficient; all source MP4s remain unchanged. Do not replace the actual speech with guessed script captions. A proper existing-video branding correction with exact-source quality evidence is still needed before its captions can be integrated under the video contract.
- Removed Year6 unknown-angle/full-turn and signed-angle families from the core. Multi-service timetable planning is optional Year6 extension, not core marking. Added taught practical12/24-hour comparison/conversion and protractor error-analysis tasks. Preserved30 positions, six bands, useful feedback, unique attempts and the progress adapter.
- A phone screenshot exposed native captions covering the angle model while controls were visible. The four integrated tracks now use the empty top band with a12px minimum font; placement fields and active cues are browser-tested. See `video-agent/time-angles/accessibility/caption-phone-layout.png`.
- Corrected unreliable exact marking of an ungraduated angle estimate by offering benchmarks; added5° protractor marks. Corrected measured page contrast failures within Time/Angles only.
- Strengthened readiness so audited content defects themselves prevent release, even if all automated receipts and manual fields otherwise pass. Added a regression test for that boundary.

## Executed checks and current-head verification

Local source gates: inventory, curriculum, mathematics and unchanged Measurement media PASS. Independent marking covers30,000 Measurement plus30,000 Time/Angles positions.11 checkpoint/release-safety tests PASS. Existing protected architecture/generator/progress regression PASS. Initial targeted Time/Angles tests passed16 cases; adding real caption/WCAG/format tests exposed contrast failures (fixed) and a new test's incorrect assumption about the existing feedback green (corrected to the actual shared colour). Final combined browser/CI outcomes must be read from the latest PR head's runs and readiness artifacts; do not reuse these initial local results as exact-final-head evidence.

## Earlier remaining actions (historical; current repair status above)

1. Remediate the exact lesson1 source's visible and spoken branding under the existing-video correction gate, preserving the original voice/file and rollback. Re-align captions to actual corrected speech; validate and integrate only after evidence passes. Existing historical sidecars are not approved output.
2. Perform full listening/viewing and caption-fidelity review of exact video/caption hashes, including names/numbers, introductions/endings/transitions and61 reading-speed/short-duration flags. ASR/forced alignment cannot approve these. Practical angle construction/measurement needs learner/teacher evidence; a numeric quiz is insufficient.
3. Obtain authorised real Google/Firebase approved/denied access, Firestore save/restore/UID isolation, deployed-rule isolation and cross-device persistence evidence. Emulator/test-adapter results do not certify production. Physical Safari/iOS controls, captions and playback remain unverified.
4. Run applicable quality gates and required Browser QA on the final remediation head, inspect readiness and preserve receipts/logs. CI may be green while this checkpoint is BLOCKED. Do not regenerate verified Measurement videos or restart suspended topics.
5. Only after explicit release authority and all mandatory gates pass, perform the controlled publication workflow and verify actual public bytes/playback. This resume does not merge or deploy.

M03/M04 remain Partial. The source profiles, tests, alignment, hashes, missing-review state and this checkpoint are recoverable through GitHub without conversation history.
