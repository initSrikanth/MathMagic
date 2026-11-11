# PR59 correction rule audit — 11 November 2026

Scope: four Time/Angles caption integrations, five-source recovery, Year5 core-assessment corrections and the existing Measurement verification pilot. **Overall FAIL/BLOCKED for full release.** PASS below means the specified scoped behaviour was observed, not blanket topic approval. Final-head GitHub CI remains authoritative for automated results.

| Applicable rule | Result | Evidence / limitation |
|---|---|---|
| Recover authoritative work and preserve existing branch | PASS | PR59 head6520819 and three prior commits recovered from GitHub; no history rewritten |
| Preserve approved assets, architecture and branding outside videos | PASS | No MP4 changes; existing Measurement hashes/evidence retained; page-only additions |
| No unrelated framework, dependencies or paid services | PASS | No application dependency changes; local free ASR/alignment only; zero paid calls |
| Existing new-topic production hold and frozen jobs | PASS | No new-topic work; legacy jobs remain frozen; no publish step |
| Curriculum authority verified | PASS | Scootle v9 M03/M04 plus Year6 M03/M04 checked; scope map links sources |
| Curriculum codes stay internal | PASS | No codes added to student HTML/JS output |
| Clear child language | PASS | Practical time displays, benchmark estimates, scale correction; no signed-difference instruction |
| Coverage before implementation | PASS | Current implementation reviewed and new correction map records families/teaching |
| Competitor research without copying | PASS | IXL coverage query; login-limited; no proprietary items copied |
| Teaching-assessment alignment | PASS | Core time conversions/angle measures taught in lessons1/3/4/5; later-year work labelled optional |
| Topic and Year-level boundaries | PASS | Kinds2/3/4/8/9 excluded; connection/timetable planning outside core |
| Representation diversity | PASS | Preserved symbolic/context/diagram tasks; corrected measure/estimate distinctions |
| Six bands and30 questions | PASS | Explicit30-position sequence; seeded generator and full-flow tests |
| Genuine progression | FAIL | New final bands combine conversion and duration/reasoning, but repeated families still limit cognitive differentiation; no claim of full module redesign |
| No artificial signed/awkward difficulty | PASS | Signed-angle differences removed; practical same-day times and named angle benchmarks |
| QCAA validity | PASS | Scope and ambiguous exact estimate corrected; practical construction is separate |
| QCAA accessibility | PASS | Controls labelled; benchmark options; local contrast correction and WCAG checks |
| QCAA reliability | PASS | Independent mathematical oracle;5° ticks; format validation and deterministic sample counts |
| Generator correctness | PASS |30,000 independent Time/Angles positions plus30,000 independent Measurement positions |
| Duplicate prompts/representations | PASS |1,000 attempts; uniqueness includes prompt plus diagram value; generation retains topic/answer key |
| Equivalent/format marking | PASS | Time/numeric/angle-name formats; A/B controls; malformed input does not consume an item |
| Fractions notation | PASS | No new student fraction expressions in this change; existing fraction regressions preserved |
| Mathematical diagrams | PASS | Correct5° protractor ticks; fixed benchmark marking; original angle rendering preserved |
| Input/browser hygiene | PASS | Existing autocomplete off, labels and mobile inputs retained; new response types tested |
| Worked feedback and colour states | PASS | Complete-flow correct answers; existing wrong-answer explanation test; shared green/red preserved |
| Dashboard and proficiency semantics | PASS | No adapter/dashboard changes;30-position completion and single-save/retry UI tests |
| Authentication fails closed | PASS | Production auth modules unchanged; test-only isolation explicitly documented |
| Progress security architecture | PASS | No change to Firebase/session/rules; protected-regression checks retained |
| Real access, save/restore and UID isolation | FAIL | No authorised live session/deployed-rule evidence; adapter/emulator tests are separate |
| Practical construction/learner mastery | FAIL | Lesson4 tool/paper task exists; no practical learner/teacher observation |
| Responsive layout and keyboard | PASS | Desktop/mobile tests; transcript disclosure keyboard access; overflow checks |
| WCAG contrast and focus | PASS | Measured3.04:1 failures corrected only within this page; no assertions disabled |
| Source/cache/version handling | PASS | Changed scripts usev2 URLs; unchanged media paths retained; native controls/playsinline |
| Existing external-resource pass | PASS | Focused correction uses existing owned videos; extra provider embed unnecessary; source selection recorded |
| Captions match actual speech | FAIL | Four aligned candidate tracks; full listening still unverified. Lesson1 actual branding differs from current script; faithful historical evidence kept unintegrated |
| Transcripts match actual speech | FAIL | Source-wording/ASR comparison and hashes retained, but exact listening not performed |
| Caption timing and coverage structure | PASS | Actual acoustic word times; ordered nonoverlapping cues, word preservation, two lines42characters maximum |
| Caption readability review | FAIL |61 speed/short-duration flags need review; structural/browser checks cannot resolve perceived reading load |
| Story/goal/criteria/teaching delivery | FAIL | Existing videos preserved; no full audiovisual pedagogy approval inferred from scripts |
| No branding in new active caption text | PASS | Four integrated sidecars brand-free; branded historical lesson1 files never referenced by player |
| No branding in every actual video | FAIL | Existing lesson1 sampled frames and independent ASR show branding throughout/opening/ending |
| No false script timing assumptions | PASS | Current lesson1 script rejected; actual audio and historical source wording recorded |
| Preserve voice/native timing | PASS | No video or audio bytes changed; no synthesis, speed/pitch effects or invented silence |
| Full technical/perceptual release gate | FAIL | Unchanged source hashes/probe/playback evidence; no new full-quality approval or fabricated decode/listening receipt |
| Actual frame inspection | PASS | Lesson1 defect contact sheet inspected; not misreported as complete visual review |
| Poster/fallback/controls | PASS | Four new poster images, native tracks and transcript/download fallbacks; existing lesson1 player preserved |
| Physical Safari/iOS | FAIL | Chromium playback tested; no physical Safari/iOS evidence |
| Quality-gate integrity | PASS | Report now refuses audited content blockers even with otherwise PASS receipts; negative regression test |
| Checkpoint integrity and bounded retries | PASS |11 pilot safety tests; hashes, source/run context and intact-log validation preserved |
| Exact-final-head required CI | FAIL | Pending at this committed checkpoint; consult latest PR runs before release. Historical/local PASS is not final-head evidence |
| Real deployment and public candidate bytes | FAIL | No deployment performed; PR candidate remains unpublished; baseline verification remains distinct |
| Reversible source and recovery documentation | PASS | Scripts, hashes, alignment, ASR, blocked historical record, manifest and GitHub recovery procedure committed |
| Credit safeguards | PASS | Zero paid calls; no repeated production; free model used only to investigate actual audio mismatch |
| Honest handoff | PASS | Four integrated / one blocked; full release explicitly blocked; concrete next actions and human-only requirements recorded |

The last three production-stage failures cannot be inferred away from green CI. Automated final-head outcomes and immutable run links belong in the PR body/readiness artifacts after execution; update this audit only against observed evidence. Lesson1 repair and full-quality review remain required work, not user approval inferred from historical technical checks.
