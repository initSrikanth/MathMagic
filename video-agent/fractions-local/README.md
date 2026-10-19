# Local Fractions animation production

Five original MathMagic explainers, generated locally with Python, Manim Cairo,
Piper/VITS through sherpa-onnx, and FFmpeg. No avatars, hosted generation, paid
API calls or account credits. The user's October 2026 instruction explicitly
supersedes the previous presenter/Scrimba, immutable-old-video and PR workflows
for this five-video replacement.

## Reproduce

Install FFmpeg, Python 3.12, Cairo and Pango development libraries and the pinned
Python requirements. Download and extract this open-source voice package:

https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-piper-en_GB-cori-high.tar.bz2

```sh
python produce.py --voice-dir /path/to/vits-piper-en_GB-cori-high --work-dir /path/to/work
```

`produce.py` is the single production entry point. It saves all scripts and the
storyboard before synthesis; generates narration locally; derives cue timing
from actual PCM sample counts; renders every scene at 1920×1080 and 30 fps; and
muxes AAC narration into faststart H.264/yuv420p MP4 files in `videos/`. Text and
vector line objects render stacked fractions without requiring LaTeX. Content
hashes resume completed work. `--prepare-only` synthesises without rendering.

Narration uses the Cori high-quality British English female voice at synthesis
speed 1.02 with Australian mathematical terminology. Its supplied model card
lists public-domain LibriVox recordings. The model card is retained here. The
Piper model is executed with Apache-2.0 sherpa-onnx, not the GPL Piper executable.
Manim is MIT licensed; FFmpeg is run as a separate executable. Model files and
build dependencies are downloaded into the work directory, never into the site.

Each cue has a natural, complete spoken explanation. Narration cues are joined
without added silence, audio stretching, pitch changes or truncation. Scene
boundaries use measured sample counts, rounded to the nearest 30 fps frame.
These are cue-level timestamps, not forced-aligned individual word claims.
Captions and inline transcripts match the original narration script exactly.

## Scope and curriculum

The five films map in order to `#meaning`, `#equivalent`, `#mixed`, `#addsub` and
`#problems` in `fractions.html`. Equal parts, unit fractions and equivalence are
foundations; comparing/ordering and representing fractions and mixed numerals,
and adding/subtracting with same or related denominators support the Australian
Curriculum v9 Year 5 Number scope. Simplification develops equivalence. Contexts
use cups, metres, kilometres and litres. Formal LCM is clearly labelled extension
and is contained in the fourth film, replacing the separate old extension video.
No curriculum descriptor codes appear in student-facing content. This scoped
media task retains the repository's existing curriculum mapping; it does not
claim a fresh external curriculum certification.

`lessons.py` is the editable source. `storyboard.json`, five scripts, cue timing,
manifest hashes and QA reports preserve the release recipe. Original per-cue WAVs
and continuous narration are retained in the execution work directory; final
MP4s carry the complete narration. Re-running synthesis is not guaranteed to
produce identical neural audio bytes; the manifest identifies the actual finals.

## Integration and verification

Run `verify.py` with the production work directory and the free local NeMo CTC
ASR model directory for full decode, codec/dimension checks, audio energy and
three speech-recognition samples per film, plus every-cue frame review sheets.
Then run `integrate.py` once. It checks all five real MP4s exist and changes only
the existing video-resource wrappers. It proves all other lesson HTML, scripts,
quiz markup, CSS references and authentication/progress code remain unchanged.

Old assets remain available for rollback; the live Fractions page references
only the five new MP4s. The rollback tag is
`rollback/fractions-before-local-animation-20261019`.

The user's minimal verification scope supersedes broad generator/stress suites.
Existing tests pin the previous approved video filenames/bytes and six-player
layout; those historical media assertions do not describe this authorised
five-player replacement. Tests are not weakened or rewritten here. Production
Firebase integration and real Safari/iOS devices require separate access and
are not certified by isolated Chromium playback checks.
