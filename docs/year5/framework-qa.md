# Year 5 curriculum and strand navigation QA — 24 November 2026

Scope: all 24 descriptors audited; six independent strand pages and dashboard hierarchy; existing topic/progress/media preservation. No new topic/video, Firebase migration, merge or deployment in this task. Baseline main: `73b9b92a0dc307b1bb817154c8195968b86dcc20`.

## Preview

- [Desktop dashboard](previews/dashboard-desktop.png)
- [390px dashboard](previews/dashboard-390.png)
- [Measurement strand desktop](previews/measurement-strand-desktop.png)
- [Number strand at 390px](previews/number-strand-390.png)

[Sampled decoded media frames](previews/contact-1.jpg), [part 2](previews/contact-2.jpg), [part 3](previews/contact-3.jpg), [part 4](previews/contact-4.jpg) cover all 56 placements; these are not full audiovisual approval.

Screenshots use safe test-only Firebase SDK mocks and sample progress. They are not production sign-in evidence. Reproduce with `python3 tests/serve.py`, then open `http://127.0.0.1:4173/dashboard.html` using normal approved-user authentication. Six `year5-<strand>.html` landing pages lead to existing topic lessons, interactive activities and assessments. Existing direct topic links remain available under Your topic practice. No extra topic history is created for cross-strand reuse.

## Executed checks at implementation checkpoint

| Check | Actual result | Limit |
|---|---|---|
| Official scope / achievement standard | 24 exact descriptors, six strands; every achievement aspect mapped | Official QCAA reproduction plus directly readable ACARA achievement standard. ACARA workbook/DOCX download blocked by environment; older QCAA N010 typography is normalised to N10. |
| Public resource audit | **217/217** HTTP resources matched SHA-256: 10 lesson pages + 207 unique media/sidecars; 56 MP4 placements | Also **38/38** versioned script/style URLs match exact baseline blobs ([code audit](deployed-code-audit.json)). Actual served bytes, local metadata and transcript inspection; no new full audiovisual review/decode. This immutable inventory describes baseline main, before navigation tags. |
| Curriculum framework | **1 Node suite passed**, all 24 records, links, 207 media/sidecar hashes, six routes, sequential/year-level negative gates | Validates evidence structure/consistency; cannot replace teacher review of skill coverage. |
| Read-only Number generator audit | **120,000 positions**, 1,000 attempts per four existing engines; **1,340 / 1,013 / 1 / 10 duplicate positions**, plus **78 equal-plan comparisons** | Baseline defects recorded in assessment-audit.json and Number backlog; no generator changed. This does not replace exact mathematical validation. |
| New navigation Chromium | **18 passed, 0 failed, 0 skipped** on final scoped desktop + mobile check, **51.7 seconds**, after assessment-audit, accessibility and configurable-title updates | 390/768/1280px; real access/progress adapters with SDK mocks, not live Firebase or physical iOS. |
| Existing protected architecture / generators / progress | **19 scripts passed** | Includes 30,000 Fractions and 30,000 Statistics positions; actual sample counts per other generator recorded in command output. Transitional browser answers remain downloadable. |
| Space mathematics / geometry / progress | **3 scripts passed**, including 30,000 independently marked questions and all 35 free hexominoes (11 cube nets) | Mocked progress, not deployed database rules. |
| Media contract | **51 Python tests passed** | Exact Statistics/Space approvals retained; no new media approval is inferred. |
| Release contract | **PASS** against committed navigation diff | No video replacement/integration requested. |
| Complete Chromium regression | **302 passed, 0 failed, 0 skipped**, desktop + mobile system Chromium, **935.8 seconds** | Real existing-topic/assessment/media regressions plus new navigation. Firebase is isolated; no physical-device claim. |
| WebKit and isolated Firestore emulator | Existing GitHub Actions gates retained; current-PR outcome pending | Local pinned WebKit/emulator downloads are unavailable; CI is not physical iOS/live Firebase. |

## Applicable-rule audit

| Rule | Finding / evidence |
|---|---|
| Read canonical, domain, security, testing and video documentation | PASS — current AGENTS/contract/workflow and topic specs inspected; stale planning claims distinguished from actual source. |
| Official scope, exact codes and achievement alignment | PASS — [matrix](curriculum-coverage.md), sources, attribution and N10 extraction caveat; no invented SP04. |
| Inspect actual teaching/tools/generators/media/deployment | PASS — HTML section/controls, actual generator functions, matching transcripts, ffprobe and served-byte inventory. Practical pupil work and new audiovisual judgement remain separate. |
| No unsupported completion claim | PASS — 12 COMPLETE, 10 PARTIAL, 2 MISSING; ten descriptor gaps and concrete corrective actions and separate media/deployment/service states. No strand declared fully released. |
| Architecture and resource reuse | PASS — vanilla static pages, shared CSS/guards/adapters, original URLs, topic IDs and challenges; no dependencies/framework/service/registry. |
| Child-facing wording and internal curriculum codes | PASS — source tests prohibit descriptor codes on new pages; coverage and personal practice are labelled separately. |
| Navigation/accessibility/responsiveness | PASS in targeted Chromium — six cards/pages, named links, keyboard focus/Enter, no overflow at 390/768/1280px. Reset buttons moved outside links while preserving selectors and handlers. |
| Assessment/progress invariants | PASS source/mocks — no generator/answer/progress implementation edits; existing 30-question histories, five-attempt display, best scores, reset and UID/topic scopes retained. |
| Authentication/security | PASS repository/mocks and scoped diff secret-pattern scan — original approved-user guard on all new pages; signed-out, unapproved and approval-read failures redirect on all seven routes; protected MD callable still fails closed. No Firebase config/backend/rules changes. |
| Existing approved media and canonical holds | PASS — every recorded media/sidecar hash unchanged, no generation, approval alteration or production-workflow change. |
| Originality/resources | PASS within navigation/audit scope — no new teaching/question/video content; exact official curriculum text reproduced under CC BY 4.0 with attribution. |
| New-topic five lessons, 30 questions and videos | NOT APPLICABLE to this task — permanent development requirements recorded; no new topic is represented as complete. |
| Regression, exact-head CI and permitted GitHub delivery | PASS locally; CI gate required — local regression passed; exact-head Actions receipt belongs to the dedicated PR; no merge/deploy authorised in this task. |

## Genuine limitations and follow-up

- Live approved/unapproved Firebase sessions, deployed rules/App Check, protected callable success, cross-device persistence and physical iOS/assistive-technology testing are not verified by these tests. No security setting was weakened to obtain a pass.
- The 35-video quality register still lacks full perceptual acceptance for its scoped corrections; Time and Angles lacks caption tracks/transcripts and exact-file approval evidence, with four stale availability notices. Video 1 visibly contains project branding at its sampled midpoint (252.6s). Space and Statistics retain their recorded exact-file owner approvals. No videos are changed or re-approved here.
- Repeated Number questions and equal-plan comparison wording are baseline defects independently reproduced by the read-only audit. N01/N04 are downgraded to PARTIAL; see assessment-audit.json.
- An angle-estimation question currently requires an exact answer from an unmarked diagram. Number modelling/algorithm creation and Algebra fact-family/unknown-division reasoning need the corrective work listed in the matrix. These are content-backlog findings, not new defects introduced by navigation.
- Teacher/pupil observation is required for practical net/grid building, measurement, spreadsheet transfer and open modelling/investigation reports.

## Final delivery receipt

Local full Chromium: **302 passed, 0 failed, 0 skipped** in 935.8 seconds. Final targeted navigation: **18 passed, 0 failed, 0 skipped** in 51.7 seconds; this is a scoped rerun after the final navigation refinements, not 18 additional unique regression cases. Exact-head Actions results are recorded on the dedicated pull request. The existing Actions job has a finite 25-minute budget because the measured Chromium run alone takes 15.6 minutes; all assertions and mandatory gates remain enabled. Actions retains Chromium, WebKit, isolated Firestore, mathematical, security and media-contract gates; a green local run does not imply their result. No merge/deployment is requested or claimed.

Approved media/sidecars remain byte-identical. Removing only the added stylesheet/script tags reconstructs all 16 existing lesson/tool/challenge pages exactly. No existing authentication, progress, generator, Functions, Firebase configuration or deployment workflow source is changed.

Actual elapsed task time and final CI status are reported in the PR completion receipt; the task began at 18:32:50 UTC on 24 November 2026.
