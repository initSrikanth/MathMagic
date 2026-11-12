# Lesson 1 correction candidate — PR59

Only the existing Lesson 1 is repaired. No synthesis, paid service, new topic, merge or deployment. `edit.json` preserves the exact source hash, omitted utterances and retained sample ranges. The original MP4 and historical evidence remain unchanged. `alignment.json` binds the corrected MP4, transcript, captions, exact shifted acoustic word times and unresolved reading flags. `qa.json` binds the checks to the final candidate hash; `contact.jpg` contains actual final-media samples from every retained scene.

The source Kokoro hf_alpha/speaker31 recording is preserved at native speed and pitch. An internal welcome sentence is cut at near-zero PCM boundaries; whole redundant passages are removed in natural quiet gaps. The duration is 6:46.733. No silence is added. Kept question pauses are the original five-second thinking gaps. Audio is encoded once to AAC; sample reconstruction/correlation measures encoding differences rather than claiming packet identity.

Reused clock primitives and source models retain the cream/dark-blue/teal/orange style. Corrected boards distinguish morning/afternoon equivalents and noon/midnight, hide prediction answers, show proportional split timelines and reveal numerical working at acoustic cues. A short last timeline jump uses staggered labels to avoid overlap. Blank branding space at the top is reserved for native captions. Static retained models and ten caption speed/duration flags still need actual perceptual review; no full-quality or accent approval is asserted.

Reproduce only when needed, from the repository root, using installed FFmpeg, numpy, Pillow and Tesseract:

```sh
python video-agent/time-angles/lesson1-repair/repair.py
python video-agent/time-angles/lesson1-repair/verify.py
python tests/time-angles-accessibility.py
```

The repair script uses ignored `work/time-angles-lesson1-repair-cache` to reuse this recipe's images/clips. A recipe/source change rejects that cache; remove it before rendering changed source. The manifest must be updated to the actual final sidecar hashes after an intentional new render. Never rerun the historical five-lesson caption recovery command over these repaired assets.

For browser checks use the existing `tests/e2e/time-angles.spec.js` suite. This execution uses system Chromium through a temporary config outside the repository because the environment's browser is `/usr/bin/chromium`. Firebase is isolated only in tests, never in production. The canonical release guard remains unchanged; this candidate does not authorise deployment. See [readiness](../../../docs/pr59-lesson1-repair-readiness.md).
