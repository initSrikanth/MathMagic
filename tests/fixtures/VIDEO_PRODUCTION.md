# Non-production video readiness fixture

`video-production-smoke.mp4` is a four-second transport/encoding fixture derived
from the opening of MathMagic's approved Mixed Numbers composite. It is not a
lesson replacement and is not referenced by any lesson page. It contains the
existing teacher, audio and graphics; no HeyGen generation was submitted.

- Source: `videos/MathMagic_Mixed_Numbers_FINAL.mp4`.
- Source SHA-256: `92c831fce1d463b7a369511098a1a5eff47a8756d840e5fe52f510dc3f7cdc56`.
- Fixture SHA-256: `d91185f8a6e50891f533cc6e76fc1e308271d99715c0043391c76f701da61643`.
- Fixture: 314,344 bytes, 4.000 seconds, 1920×1080, H.264/yuv420p, AAC, faststart.
- The 720p source was scaled uniformly for this explicitly authorised readiness
  test. This does not add native 1080p teacher detail, alter the approved source,
  establish a new narration-to-graphics alignment, or validate the old independent
  avatar compositor. It deliberately retains the approved full-frame composition.

From the repository root, with Python, Pillow, FFmpeg and FFprobe available:

```sh
python -m pip install -r tests/requirements-video-readiness.txt
python tests/video-production-readiness.py \
  --fixture tests/fixtures/video-production-smoke.mp4 \
  --evidence /workspace/work/video-phase2
```

Add `--build` only to regenerate the non-production fixture. Encoder-version
differences can change its bytes; review new output and update provenance before
committing any regenerated fixture. The script validates source identity, five
exact worked examples, a Pillow fraction graphic, complete decoding, streams,
dimensions, duration, MP4 atom ordering, four teacher/board image comparisons and
ten reference geometry samples. Generated graphics/evidence stay under `work/`.

```sh
npx playwright test video-production-readiness.spec.js
```

The standalone browser harness tests actual bytes, HTTP 206/416, playback,
early/middle/late seeking, ending and desktop/mobile containment through the
existing range-capable local server. It does not navigate through authentication
or change lesson content. CI uses its normal pinned browser. This environment's
system Chromium fallback was configured only in an uncommitted scratch config.
Chromium device emulation does not certify Safari/iOS or real student progress.
