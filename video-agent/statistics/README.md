# Statistics review-video production

The owner’s 20 November 2026 mission authorises exactly five Year 5 Statistics generation candidates through the canonical `statistics_generation_authorisation`. The unrelated-topic hold and all full listening/viewing, exact-byte approval and publication gates remain active. Generation is not release permission.

Stage A passed: `preflight.json` records the official archive, exact approved Kokoro model/voice hashes, ASR asset hash, installed native renderer dependencies and free storage. No paid service, voice substitution, avatar or project branding is used. `prepare_scripts.py` expanded the original five drafts with the required learning phrase, prior knowledge and meaningful explanations; it preserves already expanded scripts. The lesson pages and assessment are unchanged.

`produce.py` uses existing `production-v2/measurement_quality.py` and its synthesis, ASR, native rendering and verification functions, with `graphics.py` supplying only Statistics drawing/model adapters. Example command with the provisioned runtime:

```
/workspace/statistics-video-runtime/bin/python video-agent/statistics/produce.py 1
/workspace/statistics-video-runtime/bin/python video-agent/statistics/produce.py 2 3 4 5
```

Successful native utterances and rendered clips are cached outside the website tree at `/workspace/statistics-video-work`. Five minutes of meaningful narration is required **before** adding the two owner-requested five-second prediction opportunities. Exact pause intervals are recorded; no speech is stretched, pitch-shifted or padded to accommodate graphics.

Captions use actual native sentence PCM boundaries. Diagram focus and progressive reveals use recognised word emissions across each teaching step, with limitations recorded. ASR/reference comparison and sampled actual-frame OCR are retained. These checks cannot certify perfect pronunciation, accent, expression, pedagogy or full teaching quality.

The existing `checkpoint.json` records each checksum-bound candidate with **PENDING** approval, no reviewer/date invented. `audit_frames.py` adds decoded-picture static/rushed-interval flags for review. `package_review.py` freezes technically verified bundles with matching sidecars, timings, original lossless audio and QA in `review/`; it never calls production promotion, approved registration or page integration. The canonical release check continues to reject unapproved new MP4s. Review-only browser tests provide a native HTML5 playback harness without changing lessons/authentication.

Original preflight failure at 7bd0f23 is historical; model provisioning and scoped generation authorisation have now been resolved. See the live checkpoint and production QA report for current completion state.

Required human reviews remain exact-byte full listening/viewing for accent and expressiveness, pedagogy, all flagged intervals, and mobile legibility. Integrate lesson players only after the existing approval and release policy permits it. Do not treat a review bundle, source match, ASR/OCR, browser playback or technical PASS as publication approval.

The 21 November release preparation preserves all five media bundles unchanged. `approval.json` is an **unapproved template**, with no reviewer, date or positive review findings. It binds the exact MP4s, sidecars and proposed player assets; every flagged interval requires a real human resolution. The owner’s conditional release authority is recorded separately in the canonical contract. All unrelated holds remain active.

To reproduce the complete proposed integration without publishing players:

```
python3 tools/video-quality/statistics_release.py --prepare
python3 tests/serve.py
```

Open `http://127.0.0.1:4173/video-agent/statistics/review/integration-preview.html` with normal approved-user authentication. Review the exact MP4 files directly when an approved local sign-in is unavailable. The preview uses the real five lesson pages and adds native accessible players, below-picture caption controls and transcripts; it does not alter production authentication. At 390px the player reserves 72px for native controls, with captions in a separate readable panel. Native fullscreen uses native captions and still needs device/legibility review.

`python3 tools/video-quality/statistics_release.py --apply` is reserved for **after** a genuine, complete human approval record exists. It rechecks every bundle checksum and all five approvals before changing any production page, then registers the existing checkpoint and integrates all five complete players together. It is currently blocked and has not been executed successfully. CI independently checks the approval, registration and production embeds; merely allowlisting a pending candidate cannot pass the gate. No release workflow or test has been disabled.

See [the release QA report](../../docs/year5/statistics-release-qa.md), [fresh media verification](../../docs/year5/statistics-release-media-verification.json) and [all flagged-interval samples](review/flag-review/README.md). The older video QA report describes the previous checkpoint and its earlier native-caption overlap; the proposed player correction is review-only until approval.
