# Recovered Time and Angles accessibility evidence

Recovered directly from the GitHub MP4s at PR59 head `6520819`. `manifest.json` binds all five original video hashes, sidecars, alignment and independent ASR evidence. No MP4 changed, no voice synthesis ran, and no paid credits were used.

`lesson2.json`–`lesson5.json` describe the four integrated tracks. `lesson1-historical.json`, historical VTT/transcript and `asr-lesson1.json` are **immutable historical source evidence of a BLOCKED asset**, not new approved captions or rendered text. They deliberately record the actual legacy branded wording instead of replacing it with the current script's different words. The player never references them. Actual frame review (`lesson1-existing-branding.jpg`) confirms branding throughout the video; the first spoken introduction and final sentence are also branded. No ending-only trim is retained or declared compliant.

Every source has measured decoded-audio pause boundaries. PocketSphinx5.0.4 acoustic forced alignment supplies word times at 10ms frame resolution; no word times are estimated from length. The four uncommon words use explicit CMU phoneme pronunciations in `../recover_captions.py`. Forced alignment follows the saved wording and does not prove fidelity independently. Offline `sherpa-onnx 1.12.26` / `sherpa-onnx-whisper-tiny.en` int8 recognition supplies a separate, imperfect transcript. ASR numeric formatting/recognition errors require listening; neither tool certifies accent or teaching quality.

The historical lesson1 wording was recovered from Git object `c4d27ce^:video-agent/time-angles/render_video1.py`, confirmed against ASR. Its current renderer script hash is retained to expose the mismatch, not to claim it produced those bytes.

Sixty-one cue flags (reading speed above17characters/second or duration under0.8seconds) remain for review. All cues preserve words, punctuation and natural pauses; native video/audio timing is unchanged. Browser tests check loaded cues during early, middle and late playback. Actual full listening/viewing, names/numbers, non-speech cue needs, speech fidelity, readable simultaneous diagrams and physical Safari/iOS remain UNVERIFIED. These are candidate accessibility repairs, not full-quality release approval.

To reproduce in an isolated local environment with FFmpeg and the free `pocketsphinx==5.0.4` package:

```sh
python video-agent/time-angles/recover_captions.py
python tests/time-angles-accessibility.py
```

Reproduction rewrites sidecars/evidence, never media. Stop on ambiguous/missing utterance boundaries or alignment failure. Review differences, regenerate the manifest hashes only after inspecting changed evidence, and rerun the quality gates. CI validates saved artifacts without downloading a speech model or rerunning production.

A real390×844 Chromium page screenshot exposed native captions covering an angle when controls were visible. Integrated cues now use the empty top band (`line:1% position:50% size:90%`) with a12px minimum page font; `caption-phone-layout.png` records the inspected correction. The browser checks every cue’s placement fields and active early/middle/late playback. Physical-device readability remains unverified.
