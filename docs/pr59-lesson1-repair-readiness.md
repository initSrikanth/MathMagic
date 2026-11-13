# PR59 Lesson 1 repair readiness — 13 November 2026

**Repair candidate; full release BLOCKED. No merge or deployment.** Existing branch: `feature/measurement-production-pilot`; parent `2b5fa082260a68704273d5aab3867bb37169a88f`. The final commit SHA is reported with the task result; this file cannot contain its own SHA.

## Current registry implementation — 13 November 2026

**The fixed35-video registration limitation is resolved. Release remains BLOCKED by explicit human approval and review requirements.** Parent: `62c595d50696e393959ed34a77794137f7139fa0`. The final implementation SHA is reported with task completion; this report cannot contain its own commit hash.

[Registry policy/process](../video-agent/media-registry/README.md) · [versioned index](../video-agent/media-registry/registry.json) · [schema](../video-agent/media-registry/schema.json) · [Time & Angles records](../video-agent/media-registry/topics/time-angles.json).

The registry declares nine topics and105 variants. All104 preserved variants retain exact asset checksums, original record bindings and ordered video/audio packet fingerprints. Declared topic inventories now control missing/unexpected-record validation. The historical35-record audit and existing approvals are unchanged. Space's existing special verifier/exception remains, with its old positive/negative tests and additional registry byte/packet protection. No files are mislabelled as Space or another topic.

Lesson1 is registered as `policy:replacement`, `status:pending`, with `human_approval.status:pending`. Its exact committed MP4, captions, transcript, poster, proposed actual-wording script, alignment and independent evidence are hash-bound. It is neither full-quality approved nor release-ready. The two earlier registration blockers (hardcoded global count and the old correction-format mismatch) are replaced by an honest extensible registration/replacement policy; strict historical packet-preservation gates are retained for unchanged media. Newly approved replacement/new media must also pass fresh actual decoding, faststart, loudness and clipping checks, plus complete independent script/caption/branding/voice/mathematics evidence and genuine full human review. A changed asset or an incomplete receipt cannot inherit approval.

Current automated evidence: [checksum-bound verification receipt](../video-agent/media-registry/verification-2026-11-13.json).

| Check | Result |
|---|---|
| Topic registration, schema, missing/unexpected IDs, complete asset/packet inventory | PASS —9 topics,105 variants;104 retained,1 pending; independent Draft2020-12 validation also PASS |
| New registry positive/negative tests | PASS —50; also run with Python site packages disabled |
| Existing contract and Space approval/protection tests | PASS —31; Space verifier/exception unchanged |
| Pilot/checkpoint safety | PASS —11 |
| Existing protected architecture/generator/progress/media regressions | PASS —`npm run test:protected` |
| Time & Angles curriculum/independent marking | PASS —30,000 positions,1,000 attempts,12 Year5 families; no assessment source change |
| Caption/hash/text/timing audit | PASS —all five registered player sets |
| Fresh independent Lesson1 media checks | PASS —12,202 decoded frames, RMS0.1526, clipping0, source-audio correlation0.99999279; new generic integrity gate also checks full decode/faststart/audio |
| Desktop/mobile browser media/captions/WCAG/student-flow regressions | PASS —22 tests, no retries; system Chromium |
| Canonical final release gate | EXPECTED BLOCK —registered active replacement requires genuine human approval; final committed-head result reported with task completion |

All earlier video policy/approval values are unchanged except the descriptive scope and new registry trust anchors. The original audit, Space manifest/verifier and Time & Angles media/evidence remain byte-for-byte unchanged. No current human approval was entered. The final implementation commit SHA is supplied in the task response; prior remote CI is not claimed as a pass for that SHA.

**Remaining release blockers:** genuine exact-byte human approval; the unchanged canonical full-release voice calibration approval (currently absent); full listening/viewing and proposed-script approval; caption fidelity/readability; the ten caption and twenty persistent-model flags; physical Safari/iOS and existing live-service/assessment-design requirements. Script alignment and caption fidelity remain UNVERIFIED in the registration evidence. No perceptual or physical-device test was marked PASS. CI should reject the active candidate with `time-angles-lesson1-repaired: PENDING_HUMAN_APPROVAL` even on a documentation-only diff; a registered path alone cannot clear the gate.

No video regeneration, paid services, unrelated lesson/assessment change, merge or deployment. No CI monitoring or scheduled continuation follows this task.

## Earlier registration verification — 13 November 2026 (superseded historical limitation)

**Registration is impossible with the canonical guard unchanged. No registration or approval is claimed.** GitHub PR59 was OPEN at exact head `902b47f0cb7bf5115b2e0c0a189ccd84e50e565e`; fetched branch and local HEAD matched. This verification records the blocker and ends the task; it does not start a rendering, policy-change or publication stage.

### Exact asset recovered

`videos/Time_Angles_01_Reading_Time_and_Duration_REPAIRED.mp4` is committed in that head: **10,236,194 bytes**, SHA-256 **`3f6501d5fe8cfedff8cb266fe3b464c027bc19fece62c832aa75c0686610b0e1`**. Git-object bytes, working bytes, accessibility manifest, alignment, edit map and retained technical QA all agree. No expired artifact or reconstruction is needed. Source/renderer/caption/transcript hashes also match their committed evidence. Existing full-decode/frame/PCM/browser evidence below is retained evidence from 12 November, revalidated by exact hashes; those expensive checks were not repeated in this blocked registration attempt.

The retained speech matches every non-omitted current script beat except the introduction's harmless wording variant: the saved script says “By the end of this lesson”; the retained original recording and faithful captions say “By the end”. The required bus-story opening and learning declaration remain. No prohibited brand is present in the active transcript/caption words. The retained mathematics evidence covers 45+5=50, 40+10=50, 35+10=45 and 25+20=45 minutes. These checks do not certify full speech fidelity or perception.

### Why metadata alone cannot register it

- [Canonical guard](../tools/video-quality/ci_check.py), line7, asserts **exactly35** distinct original media records in `docs/video-quality-audit-35.json`. [Inventory production](../tools/video-quality/inventory.py) enumerates exactly seven other topics; Time & Angles is absent. Adding a legitimate36th record fails the existing assertion.
- The guard's known-media set, lines23–29, accepts only those records/their associated corrections or candidates, plus the separately approved ten Space videos. It never reads the Time & Angles accessibility manifest as release registration. That manifest already records the checksum with `ALIGNED_REVIEW_REQUIRED`, not approval. A checksum added to an ignored field/file would not fix this.
- Assigning Lesson1 to an unrelated35-video record, replacing an original record, or relabelling it as Space would falsely associate the evidence and violate preservation. The Space path is bound to its exact topic, manifest hash, ten approved IDs and media checksums. No such workaround was attempted.
- [Scoped correction contract](../tools/video-quality/contract.py), lines112–134, accepts `branding_only` or `mathematical_visual_only`. The current combined branding/visual/duration edit re-encodes AAC: it has PCM reconstruction/correlation evidence, not a truthful packet-copy proof. The branding branch requires packet-copy proof or the specific LCM-preservation quiet-boundary evidence; the mathematical branch requires every original audio packet and outside-scene video packet unchanged. Source and candidate AAC frame counts reported by ffprobe are23,679 and19,067 respectively. The existing evidence cannot be declared to satisfy those formats. Full approval is also unavailable because mandatory perceptual evidence remains absent.

Fresh checks on `902b47f`:

| Check | Result |
|---|---|
| Committed/working/source/sidecar/evidence hashes and ffprobe | PASS — MP4 present, 406.733s, H.264/AAC1080p; source preserved |
| `python tests/time-angles-accessibility.py` | PASS —107 Lesson1 cues; all five hash-bound sets, ordered timing/text, other assets unchanged; release remains false |
| `python tools/video-quality/test_contract.py` | PASS —31 tests |
| `python tools/video-quality/ci_check.py 2b5fa082260a68704273d5aab3867bb37169a88f` | FAIL/EXPECTED BLOCK — line32: `Unaudited new/replacement media under production hold: ['videos/Time_Angles_01_Reading_Time_and_Duration_REPAIRED.mp4']` |

The GitHub head already showed required `fractions-browser-qa` FAILURE and pilot source/student-flow/live-verification/readiness job SUCCESS when read once; a successful readiness job is not release approval. No runs were retried, scheduled or monitored. No human perceptual or physical iOS approval was added. Only this report and the durable checkpoint change in this attempt; the canonical guard, approval policy, manifests, all media and unrelated assets remain unchanged.

An authorised change to the registration/verification process would be needed to admit this topic and evidence type honestly. Such a change is expressly outside this task's no-guard-change constraint, so no registration commit is possible. The task stops with these findings.

## Retained repair evidence — 12 November 2026

The repaired Lesson 1 is 406.733 seconds, with 107 acoustic-timed caption cues, matching transcript, poster and native player integration. The source Kokoro recording is reused at its original speed and pitch. Branded speech, frame branding, inconsistent time comparisons, prediction answer leaks and missing duration working are corrected. Removed passages are redundant examples/repeated explanations and the branded final repeated challenge. The story-first opening, learning declaration, goal, three criteria, worked examples, thinking pauses, misconception, independent train problem and reflection remain.

The original Lesson 1 MP4 and historical evidence are preserved. Lessons 2–5 and every associated caption/transcript/evidence asset remain unchanged. No other lessons, assessments, auth/progress code, dependencies or infrastructure are modified.

Evidence: [edit/sample map](../video-agent/time-angles/lesson1-repair/edit.json), [alignment](../video-agent/time-angles/lesson1-repair/alignment.json), [media QA](../video-agent/time-angles/lesson1-repair/qa.json), [actual-frame contact sheet](../video-agent/time-angles/lesson1-repair/contact.jpg), [accessibility manifest](../video-agent/time-angles/accessibility/manifest.json).

## Targeted verification

The following are retained results from the 12 November repair. The fresh 13 November registration checks are listed above. Historical PR59 CI receipts are not new passes.

Candidate SHA-256: `3f6501d5fe8cfedff8cb266fe3b464c027bc19fece62c832aa75c0686610b0e1`.

| Check | Result |
|---|---|
| Final MP4 H.264/AAC, 1920×1080, 30fps, yuv420p, faststart, duration | PASS — 406.733s |
| Full decode and blank-frame checks | PASS — all 12,202 frames; minimum frame contrast 8.146 |
| Recorded-voice preservation / splice / levels | PASS — source PCM reconstruction; correlation 0.99999279, SNR 48.73dB, RMS 0.1526, clipping 0; internal splice near zero |
| Branding and actual model checks | PASS — empty branding band in every frame; OCR and sampled actual viewing for all 31 retained scenes; prediction and proportional timeline pixel checks |
| Caption timing/coverage and transcript | PASS — five integrated sets; exact retained source-word mapping, ordered/nonoverlapping cues, complete text, two lines ≤42 characters, top-band positioning |
| Independent lesson calculations | PASS — bus 45+5=50, movie 40+10=50, swimming 35+10=45, train 25+20=45; 12/24-hour equivalences |
| Lessons 2–5 preservation | PASS — all recorded asset hashes and lesson player sections unchanged |
| Contract unit tests | PASS — 31 tests |
| Pilot checkpoint/release-safety tests | PASS — 11 tests |
| Existing Golden Rules script preflight | PASS — source-only check; not proof of rendered quality |
| Desktop/mobile UI, WCAG, transcript keyboard access | PASS — 22/22 on final unchanged bytes |
| Canonical final-diff release guard | BLOCKED — Time/Angles absent from its approved-media inventory; final command result reported with task completion |

Final browser receipt: [browser.json](../video-agent/time-angles/lesson1-repair/browser.json). Final full suite: **22 passed**, retries disabled, desktop/mobile system Chromium. An earlier run during render work had one five-second load timeout; the final isolated playback check passed both projects (2/2), then the complete final suite passed 22/22 without assertion changes. All checks ran on the source/media state committed by this repair. Unchanged assessment stress suites and remote CI were not rerun or monitored.

## Remaining blockers and limits

- Exact full listening/viewing, speech/caption fidelity, warmth/accent/expressiveness, simultaneous phone readability and persistent-model pacing are UNVERIFIED. Twenty model intervals over eight seconds are flagged for review in `qa.json`. Ten Lesson 1 cue speed/duration flags remain in the alignment. Automated checks and sampled viewing cannot certify those attributes.
- Physical Safari/iOS playback/controls/captions remain unverified. Local Chromium runs isolate Firebase and do not certify live authentication, deployed rules, persistence or UID isolation. Historical PR59 assessment-design and real-service blockers remain unchanged and outside this task.
- Time and Angles is outside the canonical release guard's 35-record inventory (the separate ten-video Space exception does not apply). The new MP4 was rejected as unaudited media by the unchanged guard, reproduced on13November. This task does not modify that infrastructure or bypass its gate. Final observed guard result is recorded with the tests.
- No full remote CI result, public-byte check, deployment or merge is claimed. A candidate committed to this branch is not publication to students.

This bounded repair task ends after the commit and targeted checks; no monitoring, scheduled work or subsequent stage follows.
