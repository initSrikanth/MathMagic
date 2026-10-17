# Whole Numbers and Place Value — five-video production

Resume from `manifest.json`; never repeat a dispatched paid request. Exact scripts and word-triggered boards are in `lessons.json` and `lesson1.txt` through `lesson5.txt`. Read `READINESS.md` for verified curriculum and budget evidence. `qa/voice-and-avatar-provenance.json` verifies the two original Avatar IV jobs and three saved-default ElevenLabs clone requests through HeyGen. No additional generation is permitted by this completed five-request project.

## Reproducible offline pipeline

1. Retain the downloaded original binaries in `sources/` and Git so recovery never depends on another generation. Source hashes and provider job/request IDs are recorded in the manifest; these identify the originals without committing signed media URLs. Provider word clocks are retained for graphics-only lessons, and acoustic word clocks plus original provider subtitles for the avatar lessons.
2. `python video-agent/whole-numbers/align.py` matches every script word and resolves every row reveal to actual audio. The aligner's analysis-only end context never enters an output audio file. The final missing word in lesson 3 is retained and cross-checked against the provider subtitle.
3. `python video-agent/whole-numbers/captions.py` creates matching WebVTT and transcripts. Put captions in the top margin (`line:1%`) so native playback controls and captions do not obscure the lower mathematical steps. This changes cue placement only, never the approved MP4.
4. `python video-agent/whole-numbers/render.py lessonN` renders a **local** composition, not a paid job. Native avatar frames/audio remain continuous; graphics-only audio is encoded to AAC without time filters. Output is written to a working file and atomically promoted only after FFmpeg succeeds. Never run two renders writing the same destination.
5. `python video-agent/whole-numbers/qa.py` checks exact arithmetic, full decode, format/faststart, audio correlation and copied-avatar PCM identity, word-clock events, reading windows, captions/transcripts and teacher-frame correspondence. It reuses a prior PASS only when final bytes retain the identical SHA-256. Graphic transition samples are in `qa/`.
6. `python video-agent/whole-numbers/integrate.py` requires five media PASS results and verified hashes, then adds the five native players without changing any baseline lesson bytes. Do not rerun after integration: it refuses duplicates.
7. Run the repository protected checks and full Playwright suite once for final integration, then exact-final-head CI before authorised merge. New media tests cover all five players and desktop/tablet/mobile containment, playback/seeking/end, captions/transcript and keyboard focus. Keep existing curated embeds and all other topic functionality.
8. Verify the Pages deployment, live file bytes/hash, captions/transcripts and actual browser playback for every player. Record post-merge evidence separately from pre-merge readiness.

Local Python dependencies: Pillow, NumPy, PocketSphinx 5.0.4 (alignment module available in `/workspace/work/audio-tools`); FFmpeg/FFprobe 7.1.5. Browser tests use Playwright 1.55.1 and Chrome/Chromium with H.264/AAC support. No additional service credentials, TTS calls or voice substitutions are required to resume finished media.

## Scope and limitations

The five actual pages include decimals on pages 4 and 5. They were not renamed into a presumed rounding/pattern sequence. Whole-number foundations support Year 5; the explicit decimal interpretation/comparison/number-line requirement is AC9M5N01. Rounding is a supporting estimation check, not a replacement topic. IB connections concern inquiry, representations and evidence for reasoning. No assessment scope, authentication, progress, Firebase or navigation code is changed.

The published teacher retains the complete original portrait at a uniform scale on the left. The provider's synthetic empty side padding is removed; the head, shoes and entire original portrait are retained, with source-to-final frame correspondence tested. No artificial narration pauses, pitch/speed edits or teacher freezes are added. Human perceived pronunciation/lip-sync and real device performance cannot be certified solely by frame/audio algorithms; report actual review scope and untested device/service limitations honestly.
