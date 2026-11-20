# Statistics instructional videos — technical review delivery

Five real 1920×1080 review MP4s, captions, transcripts, posters, native lossless audio, measured timings and QA are packaged in the existing Statistics checkpoint. **All five remain unapproved and unintegrated.** No merge, deployment or approved-player registration occurred.

Generation was explicitly authorised for these five Year 5 Statistics candidates only. The canonical unrelated-topic hold, exact voice checks and full perceptual/approval gates remain active. Preflight obtained the official Kokoro and ASR archives once each; both required Kokoro hashes match the contract.

## Files and actual media checks

| Video | MP4 / sidecars / evidence | Total / meaningful narration | Caption cues | Exact MP4 SHA-256 |
| --- | --- | --- | --- | --- |
| 1. Become a Data Detective | [MP4](../../video-agent/statistics/review/lesson1/Statistics_Lesson01_REVIEW_1080p.mp4) • [captions](../../video-agent/statistics/review/lesson1/captions.vtt) • [transcript](../../video-agent/statistics/review/lesson1/transcript.txt) • [poster](../../video-agent/statistics/review/lesson1/poster.jpg) • [QA](../../video-agent/statistics/review/lesson1/qa.json) | 325.965s / 315.965s | 83 | `30a62799547a453dcc9abc0423402e9f0d07c91050b5ff76688c42c74ce6b96b` |
| 2. Collect and Organise Data | [MP4](../../video-agent/statistics/review/lesson2/Statistics_Lesson02_REVIEW_1080p.mp4) • [captions](../../video-agent/statistics/review/lesson2/captions.vtt) • [transcript](../../video-agent/statistics/review/lesson2/transcript.txt) • [poster](../../video-agent/statistics/review/lesson2/poster.jpg) • [QA](../../video-agent/statistics/review/lesson2/qa.json) | 334.861s / 324.861s | 77 | `24af87f512d83491c380b8d2b8ba74f0d6533f231af36cece3c36b3e4f3e42b4` |
| 3. Discover the Mode | [MP4](../../video-agent/statistics/review/lesson3/Statistics_Lesson03_REVIEW_1080p.mp4) • [captions](../../video-agent/statistics/review/lesson3/captions.vtt) • [transcript](../../video-agent/statistics/review/lesson3/transcript.txt) • [poster](../../video-agent/statistics/review/lesson3/poster.jpg) • [QA](../../video-agent/statistics/review/lesson3/qa.json) | 331.165s / 321.165s | 81 | `3b5cf6f02baf350f82449f88ec9f02684e6e994a5b68c387c8701f68f85fb708` |
| 4. Read Line Graphs | [MP4](../../video-agent/statistics/review/lesson4/Statistics_Lesson04_REVIEW_1080p.mp4) • [captions](../../video-agent/statistics/review/lesson4/captions.vtt) • [transcript](../../video-agent/statistics/review/lesson4/transcript.txt) • [poster](../../video-agent/statistics/review/lesson4/poster.jpg) • [QA](../../video-agent/statistics/review/lesson4/qa.json) | 347.022s / 337.022s | 83 | `106b5ef43e5443ea6bdbbd5126e06321a3f50c7aa2abc15b19539ff019e6034c` |
| 5. Investigate and Communicate | [MP4](../../video-agent/statistics/review/lesson5/Statistics_Lesson05_REVIEW_1080p.mp4) • [captions](../../video-agent/statistics/review/lesson5/captions.vtt) • [transcript](../../video-agent/statistics/review/lesson5/transcript.txt) • [poster](../../video-agent/statistics/review/lesson5/poster.jpg) • [QA](../../video-agent/statistics/review/lesson5/qa.json) | 348.174s / 338.174s | 79 | `d95d6e121b3cbce7b038af9009a265ff52ba8bb17a246338c719808061224326` |

Every MP4 passed H.264/yuv420p, 1920×1080, 30fps, AAC, faststart, full decode, decoded-frame contrast, audio RMS, zero clipping and source/encoded audio correlation checks. Exactly two planned five-second thinking opportunities are recorded per file; **every file exceeds five minutes excluding them**. No unplanned silence over 1.5 seconds was found.

Caption times come from actual native sentence PCM boundaries. Caption text and transcript match the delivered synthesis reference; complete ASR recognition/reference records are retained for discrepancy review. Visual emphasis uses actual ASR word emissions across teaching steps; these are approximate and not certified forced alignment. Human full listening remains necessary for pronunciation/transcript perception, accent, expressiveness and pedagogical timing.

Automated branding checks passed on rendered source text, captions/transcripts, full-narration ASR and 13 sampled exact-video frames per film (65 total). ASR/OCR and sampled frames can miss content; they do not replace full viewing/listening. No spoken/rendered project name was deliberately introduced.

Initial native utterance caches and successful clips were preserved. One bounded objective correction pass fixed sentence-local summary flashes, delayed extra-example results, and removed an overlapping comparison heading. Only affected graphics clips were rerendered; native narration hashes remained unchanged. Previous candidates remain outside the website tree for rollback.

## Golden Rules evidence

| Requirement | Automated/source evidence | Remaining judgement |
| --- | --- | --- |
| Curiosity hook | All five open with an original school-context question | Engagement/age fit: full human review pending |
| “Today we are learning…” | Required phrase in all five narration references | Listening confirmation pending |
| Clear goal and three measurable criteria | Goal scene and three numbered criteria in every source/template; actual frames sampled | Full mobile legibility review pending |
| Prior knowledge | Each script explicitly recalls sorting/counting, table reading or earlier skills before developed examples | Teaching judgement pending |
| Concrete → pictorial → abstract | Anonymous cards/counters, tables/graphs and contextual number statements; model checks passed | Full pedagogical viewing pending |
| Two worked examples | Two guided prediction/explanation pairs in each existing lesson script | Full teaching quality pending |
| Prediction and reasoning | Unrevealed input models, question prompts and two actual five-second opportunities before worked explanations | Timing/naturalness review pending |
| Meaningful duration | 315.965–338.174 seconds of narration per film, pauses excluded | No padding claim based solely on duration; human review pending |
| Misconception correction | One explicit positive correction per script, plus exact model/timing regression tests | Listener/teacher review pending |
| Reflection and natural ending | Reflective final questions and brand-free conclusions in all five scripts | Perceived ending quality pending |

**No full Golden Rules/perceptual approval is claimed.** The decoded-picture audit flagged 71 static intervals over eight seconds and 21 visual-state changes under 0.9 seconds. Every flag is timestamped in its file’s QA and remains PENDING HUMAN REVIEW. Persistent graphs and word-focus transitions may be appropriate; a metric cannot decide that.

## Executed tests

- Chromium main suite: **50 passed, 0 failed, 10 skipped**. This includes all ten real-media desktop/mobile review cases, Statistics learning/assessment flows and existing Measurement UI regressions. Layout checks cover 390px, 768px and desktop widths.
- Existing approved native Measurement video regression: **2 passed, 0 failed**.
- The ten skips are the original approved-lesson-player checks; players are deliberately absent until human approval. Actual review-file tests were not skipped.
- WebKit: **5 runner launch failures**, all caused by the absent WebKit executable before test bodies ran. No physical Safari/iOS claim.
- **19 protected/unit check scripts passed**, including existing architecture/generator/progress/media patterns and all five real review-bundle checks.
- Python: **39 contract tests, 8 independent data-model tests and 7 timing/model regression tests passed**.

The local browser harness uses installed system Chromium and test-only Firebase isolation. It does not grant production access or verify live Firebase, deployed rules or physical devices. Review playback exercised exact bytes/range requests, metadata, advancing playback, early/middle/late seeks, ending, controls, playsinline, caption loading/text/times, transcripts, posters, keyboard focus and responsive containment.

Actual decoded source frames were sampled from all five films. The corrected comparison title is readable and no longer overlaps. Additional 390px Chromium samples are saved in each review directory: native paused controls/top captions may cover parts of the canvas, so paused/fullscreen mobile legibility remains an explicit human/device review item. Samples are not full video viewing.

## Release status and human-only checks

The existing checkpoint binds all pending bundles and sidecar hashes. It does not add them to the approved media map. The unchanged release CI must reject these unapproved new MP4s; this is expected release blocking, not permission to bypass the integrity/approval controls. PR #60 remains a draft.

- [ ] Full listening and viewing of each exact SHA above, with real reviewer identity/date.
- [ ] Accent, warmth, expressiveness, pronunciation and transcript wording confirmed through listening.
- [ ] Teacher checks all Golden Rules and every static/fast-change flag.
- [ ] Paused/fullscreen mobile legibility, captions/controls and physical Safari/iOS reviewed.
- [ ] WebKit tests run where its pinned executable is installed.
- [ ] Only after approval: use the existing approved registration/integration procedure, verify exact hashes, then test the real lesson players. No automatic merge/deployment.

## Reproduce and timing

Use `preflight.json` for approved asset hashes and actual tool versions. `produce.py` calls the existing production-v2 native functions; `repair_review.py` preserves native audio and unaffected clips. `package_review.py` stages review bundles without promotion.

```sh
npm run test:protected
python3 tools/video-quality/test_contract.py
python3 tests/statistics-video-models.py
/workspace/statistics-video-runtime/bin/python tests/statistics-video-timing.py
npx playwright test statistics-video-review.spec.js
```

Task started **16:05:28 UTC, 20 November 2026**. Measured elapsed to this delivery QA checkpoint: **3656 seconds (60.9 minutes)**, including provisioning, script expansion, rendering, the objective correction pass and QA. Git commit/upload follow this checkpoint. No background production or future automation is scheduled.
