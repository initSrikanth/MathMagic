# Fractions — Original MathMagic Explainers

This topic now uses original MathMagic explainers in place of generic third-party YouTube embeds.

| Lesson | Explainer | Scrimba guide | Teaching purpose |
| --- | --- | --- | --- |
| Fraction Sense | Comparing Fractions | https://scrimba.com/explain/guide0do8gaihl?claim=qp18gt2ns5crtvtb&fullscreen=1 | Compare and order fractions using equal parts and equivalence |
| Equivalent Fractions | Equivalent Fractions | https://scrimba.com/explain/guide0sg51dt0a?claim=880ibeuj7t4u685p&fullscreen=1 | Explain equivalent values, scaling and simplification |
| Mixed Numbers | Mixed Numbers and Improper Fractions | `videos/MathMagic_Mixed_Numbers_FINAL.mp4` (approved local MP4) | Convert and compare amounts greater than one whole |
| Add & Subtract | Adding and Subtracting Fractions | https://scrimba.com/explain/guide0pl10dlm6?claim=12ondtimn8vnq0il&fullscreen=1 | Use common/related denominators and reliable calculation steps |
| Problems | Fraction Word Problems | https://scrimba.com/explain/guide0qcibakhr?claim=klaes8bm913i2o8c&fullscreen=1 | Identify the whole, choose an operation and check reasonableness |

## Style reference

The user-created MP4 “Adding and subtracting fractions” was reviewed before this set was produced. Its short-slide structure, clean worked examples, visual fraction models, real-world example and summary/checklist approach informed the MathMagic explainer style.

The uploaded MP4 itself is not embedded because the deployed MathMagic site needs a stable hosted source URL. The lesson instead embeds the corresponding original MathMagic Scrimba explainer, which can be maintained and regenerated through the connected explainer workflow.

## Embed QA

All five embeds use:
- `https://scrimba.com/explain/...`
- lazy loading
- accessible titles
- fullscreen support
- responsive 16:9 containment through the existing `.video-frame`
- a visible direct fallback link to the original explainer


## Access note

Embed and fallback links must preserve the complete share URL returned by the Explain generator, including its access query parameters. Stripping those parameters can make an unclaimed/unlisted explainer appear private or require account access.


## Approved Mixed Numbers MP4 publication — 16 October 2026

The Mixed Numbers section now uses the supplied `MathMagic_Mixed_Numbers_CAREFULLY_TIMED.mp4`, copied without transcoding or edits to `videos/MathMagic_Mixed_Numbers_FINAL.mp4`. Its SHA-256 is `92c831fce1d463b7a369511098a1a5eff47a8756d840e5fe52f510dc3f7cdc56`; size 4,870,811 bytes; duration 75.889 seconds; 1280×720 H.264 yuv420p video and stereo AAC audio. The teacher, narration, graphics and timing are unchanged. No captions/transcript were supplied.

This approved replacement supersedes the historical Scrimba player/QA description above for Mixed Numbers only. Its HTML5 player has native controls, inline playback, metadata-only preload, responsive 16:9 containment, an accessible name and a direct MP4 fallback link. Other lesson content and players are unchanged by this publication. Do not regenerate this approved video.

Coverage retains at least 14 resources across the six modules and an original explainer in every one of the five Fractions lessons, counting approved MP4 replacements alongside supported embeds. The static audit pins the Mixed Numbers bytes; browser QA checks metadata, actual playback, seeking/end and desktop/mobile containment. See [the scoped publication audit](../mixed-numbers-video-publication.md) for observed checks and production limitations.


## Approved LCM extension publication

The approved graphics-only “Finding the Lowest Common Multiple (LCM)” explainer is an additional player immediately after the approved Adding & Subtracting Fractions player, under “Extension: Finding the Lowest Common Multiple (LCM)”. The five original lesson explainers remain in place. Formal LCM is useful extension material; the Year 5 assessed related-denominator scope is unchanged.

- Asset: `videos/MathMagic_Finding_LCM_FINAL_1080p.mp4`, copied byte-for-byte from review commit `9ec0be51671a738ae964130a9c56adbc384433d9`.
- Size: 3,111,284 bytes; SHA-256: `374bae53a7d727587b7940e2e302dcf30c528e17a964db914d2c8eb7107a3c00`.
- Format: 1920×1080, 30 fps, 87.666667 seconds, H.264/yuv420p, AAC, faststart.
- Accessibility: 27 final word-timed English caption cues and the matching complete narration transcript, available inline and in `videos/MathMagic_Finding_LCM_Transcript.txt`.
- Provenance: user-approved final mathematical animation and original HeyGen cloned narration. No synthesis, re-encoding, pitch/speed change, added silence, avatar generation or credit expenditure during publication.
- Release gates: immutable-byte checks, complete decode, exact fraction arithmetic, native playback/seeking/end, captions/transcript, keyboard focus and desktop/tablet/mobile containment; full architecture/generator and browser regressions. CI isolates Firebase and cannot certify live Firebase services or real Safari/iOS.

The canonical continuous-narration production and integration workflow already covers this publication; no new `AGENTS.md` rule is needed.
