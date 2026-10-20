# Comparing Fractions — two review prototypes

These candidates reuse production-v2's fraction drawing primitives and FFmpeg scene composition, without calling its integration or batch functions. Existing videos and website files are unchanged. No paid services, avatars or external generation APIs were used. Automation remains suspended.

- Voice A: local Kokoro v1.0 **af_heart**, American English female, speaker 3.
- Voice B: local Kokoro v1.0 **bm_george**, British English male, speaker 26.
- Native synthesis speed 0.94 for both; no post-generation time stretching, pitch adjustment or voice imitation.
- Both use the identical script in `script.json`, thirteen shared visual cues, brighter background, teal/orange equal-whole models, proper stacked fraction notation, and short graphic dissolves. Reveal timings follow each speaker's measured waveform duration. Five seconds of thinking time precede the challenge answer.

## Voice choice and limits

The existing local pipeline used Kokoro v0.19 bf_emma at 0.84. This comparison uses the newer v1.0 model with two separate speaker embeddings rather than minor variants of that voice. Piper was considered as a lightweight local alternative, but was not installed or auditioned; no perceptual engine comparison is claimed. The newer Kokoro model works with the existing lightweight runtime, so installing a large additional neural framework was not justified for this two-candidate experiment. Selection is practical, not a claim of a subjective listening benchmark. Direct perceptual listening is unavailable here: **only your listening review can establish whether either candidate meets the requested natural, warm classroom delivery.** They are English US/UK voices, not Australian-specific voices.

`Voice_*.timeline.json` records actual sample-clock scene boundaries and thinking time. VTT files contain matching narration-segment transcripts; they are optional sidecars, not word-aligned captions. Mathematical models introduce the equivalent amount visually before the common-denominator explanation. Equal numerators are taught with positive unit fractions; the comparison rule assumes equal-sized wholes.

Run `produce.py` with Pillow, NumPy, soundfile and sherpa-onnx 1.12.26, FFmpeg/FFprobe, and the local `kokoro-multi-lang-v1_0` model directory at the path in the script. Work files are outside the repository. No model weights are committed. Upstream model archive includes the Apache-2.0 licence.

Model and speaker mapping: https://k2-fsa.github.io/sherpa/onnx/tts/pretrained_models/kokoro.html and https://github.com/k2-fsa/sherpa-onnx/blob/master/scripts/kokoro/v1.0/generate_voices_bin.py

Focused QA: `qa.py` checks exact rational comparisons, complete decode, media specification, audible speech per segment, peak clipping, continuous timeline, actual challenge pause and distinct speaker embeddings. This does not prove human-sounding speech. `qa-results.json` records measured durations and SHA-256 values. Visual contact sheets record the models reviewed. No website audit or production publishing is involved.
