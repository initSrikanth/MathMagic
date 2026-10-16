# Finding the Lowest Common Multiple (LCM) — completed narrated review candidate

The existing animation/script from `a4ad2da` now has narration from the user's **existing HeyGen voice**. No avatar, replacement clone, audition, second speech request or lesson publication was created. The original 80-second draft remains as a historical visual reference; the finished narration lasts 87.640813 seconds and the 30 fps review MP4 lasts 87.666667 seconds. Graphics follow the actual narration; the audio is never fitted to the old 80-second draft.

## Review deliverables

- `../../reviews/lcm/final/MathMagic_Finding_LCM_REVIEW_1080p.mp4`: completed 1920×1080 H.264/yuv420p, AAC, faststart review candidate.
- `../../reviews/lcm/final/LCM_Original_HeyGen_Narration.mp3`: original downloaded narration, unchanged, 44.1 kHz mono, 256 kbps MP3. The service's URL/widget called it WAV; FFprobe identified MP3, so the original bytes were preserved with the correct extension.
- `../../reviews/lcm/final/MathMagic_Finding_LCM_REVIEW_1080p.vtt`: source-clock captions, 27 cues; transcript remains `narration.txt`.
- `../../reviews/lcm/final/voice-provenance.json`: exact voice identity, returned engine/settings, request ID, input hash and one-request ledger.
- `../../reviews/lcm/final/heygen-speech-response.json`: actual returned word timestamps; no signed download URLs or credentials.
- `../../reviews/lcm/final/MathMagic_Finding_LCM_REVIEW_1080p.json`: actual scene ranges and word mapping.
- `../../reviews/lcm/final/final-technical-qa.json`, `alignment-crosscheck.json`, `final-playback-qa.json`: measured QA, with subjective review kept separate.
- `../../reviews/lcm/index.html`: local review page only. No LCM player has been inserted into `fractions.html`.

## Verified narration generation

The user explicitly authorised **one** connected HeyGen `create_speech` request with voice ID `2ec5ec7926eb471d9f33e1b7ba4bb77d`, accepting the applicable charge without a pre-generation quote or US$1 cap. Request `5wHM1c4XHiNJkTuKRq9D` succeeded and identified **Srikanth sogathur**, engine `elevenlabs`, speed `1`. Engine/model/speed overrides were omitted to preserve the voice's saved defaults. No pitch adjustment, break markup, added silence, sentence holds, voice replacement or avatar generation was requested. The account's previously observed balance was 428 and its post-request balance was 424; this is an observed four-credit difference, not a per-request invoice or a verified USD conversion.

Earlier empty private-catalogue results did not establish that the voice was unusable. The authorised generation endpoint has now verified actual access. Direct ElevenLabs account configuration is not needed for this successful route. Do not call synthesis again to download, align, test, or rerender this existing audio. A new generation or retry requires new user authorisation.

## Reuse and timing

All existing mathematical drawing and animation functions are AST-identical to `a4ad2da`; no graphics were redesigned. Only the alignment loader was extended to accept the returned HeyGen word intervals and verified voice provenance. Contraction/hyphen tokens are normalised solely for script matching while retaining their original provider word interval. The entire script matches. Key number/result reveals use those actual word starts, quantised to the next 30 fps frame.

Render again locally, with **no generation or credit expenditure**, from the repository root:

```sh
python video-agent/lcm/render.py --audio reviews/lcm/final/LCM_Original_HeyGen_Narration.mp3 --alignment reviews/lcm/final/heygen-speech-response.json --provenance reviews/lcm/final/voice-provenance.json --output /tmp/MathMagic_LCM_review.mp4
python -m unittest discover -s video-agent/lcm -p 'test_*.py'
python video-agent/lcm/qa_final.py
```

Python needs Pillow and NumPy for graphics/QA, plus FFmpeg/FFprobe and DejaVu Sans. The renderer has no networking or synthesis calls. Original narration samples are used at their original rate; the only audio processing is AAC encoding for MP4 playback. Codec-frame tail padding is measured separately from artificial pauses.

## QA and remaining approval

Exact arithmetic verifies LCM(4,6)=12, equal-value renaming, the addition result and simplest form. Fractions use stacked numerators, horizontal bars and denominators; slash text is rejected by the drawing helpers. Earlier conversions persist while later calculations need them, and the answer persists through the recap. Full decode, faststart, actual board-frame comparisons and audio-continuity checks pass. Independent offline acoustic alignment agrees with all eleven key mathematical reveal anchors within 0.061 seconds; it is diagnostic, not a subjective listening certification.

The final technical report measures audio correlation/SNR, gain, clipping, original/final sample counts, source-clock scene mapping and existing-graphics integrity. `playback_final.cjs` tests the finished review on desktop, tablet and mobile Chromium, including captions, controls, keyboard focus, advancing playback, early/middle/late seeks, ending, ranges and containment. It requires a local byte-range server (default `http://127.0.0.1:4189`) and Playwright; point `PLAYWRIGHT_MODULE` at the installed package if needed. This does not certify real Safari/iOS or production Firebase integration.

**Ready for user review; publication remains prohibited until approved.** Human review must assess the natural voice, pronunciation, perceived synchronisation and teaching experience. `integration-after-approval.html` is still only a proposed snippet, not a published lesson.

## Curriculum scope

This is optional Year 5 extension material. Year 5 AC9M5N05 covers same/related-denominator calculations, and AC9M5N02 includes multiples; a formal LCM procedure is not prescribed. Broader fraction calculations progress in Year 6 AC9M6N05. Sources checked during preparation:

- https://www.australiancurriculum.edu.au/resources/work-samples/mathematics/year-5/ws03-representing-and-adding-fractions
- https://www.mathematicshub.edu.au/search/factors-multiples-primes-year-5-planning-tool/
- https://www.mathematicshub.edu.au/search/fractions-year-6-planning-tool/
