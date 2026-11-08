# Space lessons 2–10: review production

The owner's 8 November 2026 resume directive authorises rendering all nine remaining videos without waiting for an audio-capable evaluator. It does not authorise publication, merging, deployment or passing an unexamined quality attribute. PR #57 and its application implementation at `7ac9fe747171c7e92d13582c5e235b73bef0bc64` are preserved.

Production uses the existing `measurement_quality` pipeline: Kokoro v1.0 `hf_alpha`, speaker31, `lang=en`, two inference threads, native role-specific synthesis speeds .94/.98/1.0, peak headroom gain only, 24kHz source PCM; 25 mathematical animation frames/s encoded at30fps, 1080p H.264/yuv420p, veryfast CRF23, AAC128k, faststart. The representative's three explicit five-second prediction pauses are reused; no speech stretching, pitch effects or graphics-fit padding is used. No paid API calls. A sequential voice worker in a separate local process overlaps synthesis with encoding; completed utterances and scene clips are reused.

- `batch_content.py`: original scripts and explicit scene models for existing lessons2–10. Lesson9 remains labelled enrichment; codes stay internal.
- `batch_graphics.py`: exact cube edge-hinge geometry, dimension-matched prism/pyramid/box nets, intersection grids, coordinate paths, translations, equal-distance mirror constructions, fixed-centre turns, symmetry and property decisions.
- `validate_batch.py`: pre-render source, mathematical, storyboard and sample-frame checks. Start/end frames for every scene are preserved for review. A cube face-depth order error and a non-square rhombus dimension error were corrected before any completed render.
- `produce_batch.py`: guarded, cached synthesis and rendering. Updates `batch-manifest.json` after every completed video and verifies the exact bytes before copying to the output directory.
- `audit_batch_outputs.py`: independent final-hash, native-voice ID, caption timing, caption/transcript, ASR-brand and mathematical-scene sample checks. It records static/short-caption flags without approving them.
- `check_batch_playback.cjs`: actual local Chromium playback at1280px and390px, caption track, advancing playback, three seeks and ending. Muted browser playback is not listening or real-device/Safari evidence.

Commands from the repository root after restoring the approved models and dependencies:

```sh
PYTHONPATH=/workspace/video-python OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=2 python -u video-agent/space/produce_batch.py
PYTHONPATH=/workspace/video-python python video-agent/space/audit_batch_outputs.py
node video-agent/space/check_batch_playback.cjs
```

The original representative's source, FLAC, timing, VTT, transcript, QA and `manifest.json` are unchanged. Its recorded SHA-256 remains `32f712baa2e9baa0b56d2569b53152289079d4d5caac5fb42ec9b0264d3547c1`. The old `/workspace/output/Space_Lesson1_3D_Objects_Review_1080p.mp4` was outside Git and is absent from this fresh environment. It has not been regenerated, replaced, deleted or certified anew; recover those exact original bytes from the previous storage for the ten-video release.

## Quality and release gates

Technical verification is separate from perceptual approval. For each exact final SHA-256, an audio-capable evaluator must listen to the whole video and view the full temporal sequence, including beginning/middle/ending, all transitions, worked examples, reveals and pauses. Record reviewer identity/date/hash. Check natural Indian-English accent, warmth/expressiveness, pronunciation, pacing, teaching quality, audio/visual/caption correspondence and every flagged static, silence, rapid-reveal or short-caption interval. Approximate offline ASR emissions are not certified forced alignment or listening. Any needed enthusiasm calibration remains subject to genuine listening approval; no substitute voice or pitch/speed effects are authorised.

Real Safari/iOS, mobile legibility and native controls/caption checks remain separate from Chromium emulation. Release must also recover and recheck the representative, integrate only approved media, run appropriate browser/media gates and CI on the final changed integration SHA, and verify deployed bytes/playback after an authorised release. No merge or deployment while mandatory gates remain unresolved. Existing videos, site pages, authentication, tools, assessment and legacy workflow suspension remain unchanged.

## Firebase evidence

Existing Measurement and Space suites passed in one demo-project emulator process. Additional `tests/space-emulator-boundaries.test.cjs` passed own-path signed-out/unapproved denial, cross-user approval isolation, nine malformed payloads, private-session read/write isolation, retained IDs beyond100, concurrent duplicate/lost-ack retries, sticky proficiency, fresh-context restore, revocation and reset. Mocked Space progress checks also passed. Logs are preserved with the output bundle.

These tests use `tests/emulator/firestore.rules`, a fixture, not deployed rules. Live Firebase remains **PENDING** until authorised live network scope and an approved test identity are available. Required live checks: deployed rule inspection; approved/denied/signed-out access; own versus cross-UID reads/writes and approval-escalation rejection; real complete-attempt save/restore across refresh, sign-in and a second session/device; retry/concurrency and revocation; direct-client isolation of private challenge sessions. Existing callable/App Check production claims must be checked with valid and invalid tokens where applicable. No live calls were attempted here.
