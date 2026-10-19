# MathMagic video production 2.0

This deterministic CPU pipeline covers the **30 existing lesson sections** in
Fractions, Whole Numbers, Addition & Subtraction, Multiplication & Division,
Decimals & Percentages, and Factors & Multiples. It needs no Codex API, paid
video service, teacher avatar, or recurring chat session. The current user
instruction authorises direct main publication and supersedes older presenter,
no-pause, paid-provider and broad-test defaults for this production task.

`content.py` retains the original exact fraction examples/diagram definitions
and whole-number teaching scripts, adds varied topic openings and think time,
and authors the other 20 lessons. Foundations and the existing fraction LCM
extension retain their labels. The curriculum scope follows the existing topic
specifications; this is not a new external curriculum certification. Existing
quizzes, authentication, progress, CSS and unrelated resources are untouched.

## Voice and timing

Kokoro v0.19 executes locally through Apache-2.0 sherpa-onnx. Voice **bf_emma**,
speaker 7 in the upstream v0.19 mapping, is British English, female. The model
package includes the Apache-2.0 licence retained in `VOICE_LICENSE.txt`, which
permits commercial use subject to its terms. Package/model/voice hashes are
pinned; no account credentials or paid calls are required. Australian English
is not supplied by this model. British English is used without an Australian
accent claim. No claim of superiority over an Australian voice is made.

Synthesis speed is 0.84 at generation time. Audio is never accelerated to meet a
video length, pitch-filtered, time-stretched or truncated. Sentence punctuation
provides phrasing, with recorded sentence/question pauses and four seconds of
unrevealed think time. Openings are written for about 15–25 seconds. Lessons
remain as long as their teaching requires; concise lessons are not padded to
three minutes. Sentence-level PCM sample counts drive captions and cue timing;
individual word alignment is not claimed. Graphics transitions take 0.8 seconds
at cue boundaries, with progressive shading and highlighting, then stable
reading time. All fractions use horizontal bars; equal wholes use equal scales.

**Limitation:** local neural speech is not a human-certified expressive teacher
performance. Technical audibility, pace and clipping checks cannot establish
perceived naturalness or perfect pronunciation. See the rendered sample and
recorded QA rather than assuming a voice-quality guarantee.

## Run locally

Python 3.12, FFmpeg/FFprobe, and DejaVu Sans at the system path in `graphics.py`
are required. No Manim/Cairo/Pango development packages are needed; the original
fraction scenes remain available in `../fractions-local/` for rollback.

```sh
python -m venv work/venv
work/venv/bin/pip install -r video-agent/production-v2/requirements.txt
mkdir -p work/models
curl -fL https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/kokoro-en-v0_19.tar.bz2 -o work/models/model.tar.bz2
echo '912804855a04745fa77a30be545b3f9a5d15c4d66db00b88cbcd4921df605ac7  work/models/model.tar.bz2' | sha256sum --check
tar -xjf work/models/model.tar.bz2 -C work/models
python video-agent/production-v2/pipeline.py init
python -m unittest discover -s video-agent/production-v2 -p 'test_*.py'
work/venv/bin/python video-agent/production-v2/pipeline.py run
```

`--resume-active` resumes only the current selected batch after a local
interruption; it cannot start the next batch early. Scheduled runs use the
normal due-time gate. Atomic WAV/MP4 writes and content-addressed sentence/cue
caches preserve progress. Completed verified outputs are hash-checked and are
not regenerated. Do not manually change completed hashes/status to force a
revision; diagnose the actual failure or explicitly author a new revision.

## Persistent schedule and recovery

`.github/workflows/mathmagic-production.yml` checks hourly at minute 17. A saved
UTC timestamp permits production only after five elapsed hours, including across
midnight. This is an earliest eligible start; GitHub may delay scheduled events.
A repository-wide concurrency group serialises this production workflow. Every
run uses current main, rebases without force-pushing, and stops on conflicts.

The active five lesson IDs are persisted before synthesis. An interruption
resumes those IDs, rather than selecting five more. All five must pass media QA
before the batch is integrated. The next production run gets the next five
unfinished lessons only after the current batch's live bytes are verified.
Normal render budget is 220 minutes inside a 270-minute job. Deadline checks
between sentences/cues and 10-minute subprocess timeouts reserve checkpoint and
upload time. Runner loss can still interrupt a command; previous caches and
committed state survive. Incomplete synthesis is reused by content hash; there
is no remote request to duplicate.

Git stores the manifest, scripts, sentence timings, media QA and completed
assets. Actions Cache stores the current model and newest compressed
intermediates; a seven-day workflow artifact also retains recovery material.
If the newest cache is lost, the workflow automatically downloads the newest
unexpired production recovery artifact and extracts only intermediate work.
It never overwrites the current main manifest or verified media with old artifact state. Previously committed finals are
never dependent on cache retention. Old artifacts expire automatically. No-op
hourly checks do not render or upload new artifacts. Production enforces a
90 MiB per-file and 800 MiB total MP4 budget; exceeding it is a recorded blocker
requiring a storage decision, rather than silently bloating the repository.

At completion the scheduler selects no work and makes no further production
commits. The hourly gate remains installed so the status can be inspected or
future explicitly catalogued work can be handled.

## Publication and rollback

The rollback tag is `rollback/animated-v2-before-20261019`. Original MP4s and
sources are retained. Each batch also records its baseline commit SHA. New V2
filenames leave old media available. Only the matching section's existing media
wrapper is replaced after five verified finals exist. Sections without a video
receive one new native player. The integrator proves that all bytes outside the
one resource wrapper/insertion survive; repeated integration is idempotent.
Players provide native controls, playsinline, metadata preload, a poster,
accessible title, English captions, fallback link and matching transcript.

The workflow explicitly requests a legacy GitHub Pages build: bot-token commits
alone do not trigger another workflow/Pages build reliably. This requires the
workflow's `pages: write` permission and the existing Pages configuration. A
request failure is a deployment blocker, never counted as publication. Public
verification independently checks the correct HTML association, full MP4 size
and SHA-256, and accessible captions, transcript and poster. A status-only
commit then records that observed evidence. It cannot contain its own commit
SHA; per-video commit SHAs refer to the actual media commits.

`manifest.json` and `status.json` distinguish pending/incomplete, verified local
renders, integrated HTML, media commit SHA, and verified-live deployment. A
render or passing test is never counted as published. See `STATUS.md` for the
current counters, next eligible run and errors. Browser playback checks and
technical audio checks are distinct from human narration review and real-device
Safari/Firebase testing, which are not claimed here.
