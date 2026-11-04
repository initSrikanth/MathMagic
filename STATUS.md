# Year 5 curriculum completion

- Preserved baseline: original six topics / 30 released videos; main 9420db7. Year 6 is excluded.
- Official v9 audit: 24 descriptors — 10 covered, 2 partial, 12 missing at baseline. Matrix: docs/year5/coverage.md.
- Current topic: **Measuring Our World**, AC9M5M01–M02; five pages and a 30-question challenge. Founder rejected PR #50 narration, then approved calibration `2ff0ffce` and authorised all five replacements.
- Current correction: five V3 graphics-only videos use the approved hf_alpha/Kokoro v1.0 profile, continuous native speech, spoken-word mathematical reveals, captions and transcripts. Old V2 bundles and original six topics/30 videos are preserved.
- Production checkpoint: video-agent/production-v2/measurement-quality-manifest.json; scripts/timing/source fingerprints and full media checks are retained. The manual produce_measurement.py entry delegates to the calibrated helper; do not rerender verified outputs or return to legacy bf_emma settings.
- Release gate: exact-final-head required CI, merge/Pages, five live bundle hashes and desktop/tablet/phone playback. Final observed evidence is recorded in the correction PR; this source checkpoint does not claim a future deployment.
- Dashboard correction: the Measurement card has its own Year 5 • Measurement strand heading; existing card/progress markup unchanged.
- Local-only limitations: emulator/WebKit binary downloads are blocked by cloud policy; their configured CI gates run outside this local environment. Live Firebase/rules and physical iOS remain distinct external checks.
- Legacy automation remains suspended. **Stop for founder review after this topic; do not start Time and Angles automatically.**
