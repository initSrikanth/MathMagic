# Measuring Our World — applicable release checks

Evidence is split deliberately: source/mathematics, mocked adapters, local Chromium, isolated CI emulators/WebKit, and live publication. A test fixture does not certify deployed Firestore rules or real Google sign-in. Existing general instructions remain in AGENTS.md; this is the topic evidence record.

| Applicable requirement | Evidence / result before release |
|---|---|
| Official Year 5 scope and six-strand audit | PASS — 24-code baseline matrix and QCAA v9 sources in coverage.md; M01/M02 only in this topic. |
| Research/originality/resources | PASS — IXL breadth review only; original lesson/quiz/graphics; Scootle original-provider links with safe external-link attributes. |
| Five meaningful learning pages | PASS — length/instruments, mass/capacity, perimeter, area, irregular design. |
| Goal and three criteria per page/video | PASS — HTML and 12-cue script assertions, local browser checks. |
| Prior knowledge/concrete/pictorial/abstract | PASS — physical ruler/string/tile/jug tasks, accessible SVG models, worked numerical strategies. |
| Guided examples, practical applications | PASS — two main examples per video/page plus recipe, regular sides, packs and design-cost examples. |
| Thinking/misconception/reflection | PASS — dedicated four-second challenge, positive correction and practical reflection in every script. |
| Topic-exclusive boundaries | PASS — no volume/triangle-area formula or area-unit conversion assessment; time/angles remain separate. |
| 30 questions / six bands | PASS — six bands of five, independently exported and checked. |
| Difficulty and teaching alignment | PASS — foundation concrete/unit tasks, developing scale/rectangle calculations, then inverses, planning and multistep design/remainder reasoning. All 27 families mapped in measurement.md. |
| Unique/equivalent prompts | PASS — 1,000 attempts, no within-attempt duplicates; rotated rectangle/L-shape and reversed design comparisons normalised independently. |
| Answers and distractors | PASS — 30,000 positions; Python exact arithmetic/SymPy geometry; four distinct options, one valid answer; reviewed unit, boundary/area, missing-corner and rounding distractors. |
| Worked feedback / valid equivalents | PASS — question-specific reasoning; numeric equivalents accepted; invalid/empty numeric input leaves Next disabled. |
| Mathematical notation/units | PASS — square units for area, length units for boundaries, appropriate attribute units; no numeric slash fractions in displayed content. |
| Audio/video format | PASS — five 1920×1080 H.264/AAC/yuv420p MP4s, full decode and faststart; original offline bf_emma configuration. |
| Synchronisation / persistence | PASS — actual sentence PCM clocks, continuous cue boundaries, persistent worked steps; no fabricated word timings claimed. |
| Blank frames / missing audio | PASS — all decoded frames checked for flat/blank contrast; every teaching cue must contain a model, equation or readable board; audio RMS, clipping, source correlation and every speech window checked. |
| Captions/transcripts/posters | PASS — measured-timing VTT, exact script transcript, decoded JPEGs, responsive native controls/fallback/transcript. |
| Accessibility and responsive layout | PASS locally — labelled SVGs/controls/inputs, keyboard-focusable players, red/green plus textual feedback, phone/tablet/desktop containment. |
| Authentication/progress pattern | PASS source/mocks — approved-user gate; transactional UID/topic state; score bounds, concurrent saves, blocked-cache tolerance, restore and failed writes. Browser assessment is not claimed secret. |
| Firestore security/progress emulator | Required CI gate — isolated demo project/test-only policy; production rules/config are untouched. Local binary download blocked by storage.googleapis.com HTTP 403. |
| WebKit / browser regression | Required CI gate — Chromium plus WebKit on the final head. Local WebKit download blocked by CDN policy; physical Safari/iOS is not equivalent to WebKit CI. |
| Preserve existing work/shared safety | PASS — original six topic pages, generators, authentication/config and dashboard content unchanged; only a new dashboard card/module; all 30 media hashes retained. Year 6 excluded. |
| Workflow/cost controls | PASS — one manual five-video batch; no paid services/HeyGen; no suspended production workflow changed. Active QA gains the explicitly requested emulator/WebKit tests. CI pins supported Ubuntu 24.04 (Playwright 1.55 rejects Ubuntu 26.04) and Node 22 for the emulator dependencies. |
| Final CI and publication | Required gate — exact-head CI, squash merge and Pages success, live byte hashes/MIME/ranges/sidecars and 15 published-byte playback cases. Final observed results are recorded in the release PR completion comment. |
| Human-review stop | Required — founder reviews this completed topic before any next topic starts. |

External checks remaining regardless of CI: real approved/unapproved Firebase sessions, deployed-rule inspection, actual cross-device Firestore persistence and physical iOS. Practical measurement/investigation activities also require pupils to perform and explain them; quiz results do not establish that observation.

Visual correction: five recap end clips gained persistent summaries; 55 original clips, original narration and all sidecars remain exact. A semantic scene-content assertion supplements pixel blank checks. WebKit media testing waits for completed seeking and uses native keyboard playback in Chromium and a trusted-click activation harness in WebKit, retaining metadata/caption/advancing-playback/seek/end assertions; a fail-fast smoke precedes full regression.

Headless WebKit CI receives an explicit PulseAudio null sink so unmuted AAC playback has an output device. This is a test runtime dependency; production audio, media files and playback assertions are unchanged. Failed playback records bounded media-state diagnostics, with small screenshot/context artifacts kept separately from large traces.

WebKit trace diagnosis: the fully buffered, error-free player stayed paused because focusing the video host and pressing Space scrolls the page. The WebKit test therefore invokes the same HTMLMediaElement play API within an actual trusted click handler, removes its temporary test button, and retains advancing playback, caption, seek/end and unmuted-media assertions. Production player controls and audio are unchanged.
