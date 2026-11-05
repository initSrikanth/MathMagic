# Scoped corrections for the existing 35-video library

The founder authorises independently verified branding-only and mathematical/visual corrections without waiting for unrelated accent review. This release contains **30 branding edits and two full 1080p mathematical-model corrections**. The other three Decimals videos have no confirmed branding/model defect requiring this release; their voice review remains open.

Every old MP4, caption file, transcript and poster is retained. [Rollback cards and original hashes](rollback.json) identify the previous players. [Release records](release.json) bind each new filename to its original, voice, correction scope and evidence. The [35-video audit](../../docs/video-quality-audit-35.md) distinguishes deployed corrections from unresolved quality dimensions.

- Twenty-nine branding edits retain exact original H.264/AAC packet prefixes. The internal Fractions edit preserves its subsequent optional LCM notice; 215.7 seconds of video are exact originals, only a 7.6-second tail and AAC are re-encoded without pitch or speed changes.
- The two mathematical videos replace only the affected 268 and 251 scene frames. All original AAC narration packets and every video packet outside those scenes are byte-identical. The midpoint, equal-whole widths and shaded cell counts are independently verified in the actual decoded final frames.
- Captions retain the existing line wrapping and safe on-screen placement. Removed branding is removed from the actual captions, transcript files and inline player transcripts.
- Website branding, written teaching content, quizzes, authentication and progress code are unchanged.

**These scoped corrections do not certify the complete videos. Accent, enthusiasm and full perceptual quality remain UNVERIFIED.** Full-quality and accent-dependent releases still require actual listening/viewing. New-topic production and all suspended production workflows remain off.

## Local voice feasibility

The installed Apache-2.0 Kokoro v1.0 `hf_alpha` profile was tested with Sherpa-ONNX 1.12.26: native English synthesis works locally without paid services or cloning. A new 16.327-second probe took 26.351 seconds on two CPU threads while other verification jobs were running. [Actual configuration, licence hashes and acoustic results](voice/feasibility.json) · [Audio](voice/hf-alpha-feasibility.wav) · [Transcript](voice/transcript.txt).

This is the same installed profile as the owner-praised Measurement baseline. The model label, successful synthesis and measured pitch variation **do not prove perceived Indian-English accent or expressiveness**. Listening remains necessary before an accent-dependent replacement receives full quality approval. No existing lesson narration has been replaced by this probe.

## Verified deployment

PR #54 merged as `63e855b14f5c37f9a2dfdae51c3e2eca37da04c9` after required CI on `7cce878df014f7af7eab2b0e9cf7de036d6ebdc8` passed all 179 browser cases and 21 contract tests. Pages run 41984615635 succeeded. **32 scoped corrections are live: 30 branding and 2 mathematical/visual.** All 35 active MP4 hashes, captions/transcripts and player references were checked against the published site; 35 published-byte Chromium playback checks passed. Browser media testing isolates Firebase and is not physical-device or live-authentication verification.

[Live file hashes and URLs](live-file-verification.json) · [Playback evidence and transport limitations](live-playback-verification.json). Accent/enthusiasm/full-quality status remains UNVERIFIED; no voice replacement was deployed.
