# Year 5 graphics-only lessons

Reuse the founder-approved Fractions local Kokoro `hf_alpha` voice, colour/type primitives, measured sentence clocks, captions, FFmpeg composition and media QA. No avatars, paid APIs, production schedules or assessment/auth changes. Scripts and original FLAC narration are retained per topic; model weights and resumable clip caches stay outside git.

Run with `PYTHONPATH=/workspace/fractions-local-tools MATHMAGIC_TOPIC=whole-numbers python3 video-agent/year5-graphics-2026/produce.py`, then `qa.py`, `integrate.py` and `register_media.py`. The default model directory is `/workspace/fractions-five-work/kokoro-multi-lang-v1_0`; `FRACTIONS_TTS_MODEL` and `FRACTIONS_RENDER_WORK` override local paths. Dependencies/voice licence are the same as `../fractions-graphics-2026/README.md` and `VOICE_LICENSE.txt`.

Each topic retains scripts, original narration, exact sample timing, caption/transcript sidecars, checksums, old integration/media backups and media/mathematical QA evidence. Generated sentence timing is measured; word-level alignment and human listening are not claimed. Real Safari/iOS and live Firebase require separate external verification; isolated Chromium UI tests do not establish them. Do not activate suspended production workflows.
