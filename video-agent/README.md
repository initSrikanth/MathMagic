# MathMagic video production agent — phase 1

## Current status

**Implemented:** five Fractions lesson specifications, rational-number validation, scalable 1920×1080 SVG teaching scenes, narration files, silent board-preview rendering, unit tests, GitHub Actions workflow, and a guarded replacement mechanism for the five existing Scrimba embeds.

**Phase 2 implemented and locally tested:** a gated HeyGen transparent-WebM request client, completed-video status lookup, automatic HTTPS download, VP9 alpha-boundary detection, bounded-memory FFmpeg overlay and H.264/AAC MP4 technical QA. A 3-second proof using the existing user-provided transparent HeyGen WebM passed locally. Seven provider tests passed locally. GitHub CI results and live authenticated API integration remain unverified.\n\n**Not implemented or approved yet:** corrected HeyGen avatar, unattended paid HeyGen video creation, narration-to-scene alignment, remote video hosting, automatic production video upload, full visual QA of teeth/feet/alpha edges, or live replacement of Scrimba. Do not describe phase 1 as a complete unattended publishing agent.

The existing `fractions.html` and Firebase code are **not modified** by the preparation workflow.

## One-command dry run

After merging the PR, open **Actions → MathMagic Video Agent (safe preparation) → Run workflow** and select `fractions`. Optionally enable `preview`. The run checks the arithmetic, writes narration, exports seven? No: it writes one SVG per scene and a QA report for all five lessons. With `preview`, it also creates silent board-only MP4s. All output is downloadable from the run's `mathmagic-fractions-prepared` artifact. No HeyGen credit is used.

Local equivalents:

```bash
python -m pip install -r video-agent/requirements.txt
python -m unittest discover -s video-agent/tests -v
python video-agent/agent.py prepare
python video-agent/agent.py preview  # requires ffmpeg
```

## Planned production orchestration (phase 2)

1. **Curriculum/script:** a reviewed lesson JSON file is the single source of truth. The renderer verifies every fraction comparison, arithmetic operation and mixed-number conversion using Python's exact `fractions.Fraction` (never floating-point guessing). A teacher reviews narration and wording before the first production batch.
2. **Maths visuals:** produce SVG diagrams, shaded equal-part fraction bars and number lines at 1920×1080. In phase 2, render SVG to frames and animate highlights and equation steps, aligning scene timings with narration.
3. **Avatar:** first correct the facial source/look in HeyGen. Generate a 5–10-second mouth/teeth test and **require explicit approval**. Save approved avatar/look/voice IDs as secrets/config, not in public HTML. Do not automatically use the current teeth-distorted avatar.
4. **HeyGen provider:** GitHub Actions obtains `HEYGEN_API_KEY` from Actions Secrets; sends the reviewed script to the documented HeyGen avatar-video endpoint; stores the returned job ID; polls status with bounded retries or receives a verified webhook; downloads the finished transparent WebM directly to the runner (not iPhone Photos). The endpoint/payload/transparent-background options must be verified against the account's live API before enabling paid runs. **No paid generation API call is implemented in phase 1.**
5. **FFmpeg composition:** inspect WebM with `ffprobe`, decode alpha correctly (libvpx-vp9 when necessary), crop using a calibrated alpha bounding box (not a guessed fixed crop), scale proportionally to the teacher lane (<=22% frame width), and place feet on the floor line. Composite against the central board without covering equations. Export H.264/yuv420p MP4, AAC, +faststart. Preserve high-resolution source edges, never use destructive black chroma keying on genuine alpha.
6. **QA gates:** validate exact maths, correct scene order, all symbols in board safe area, full head/body/shoes inside frame, clean alpha edges, synchronised speech/scene changes, audible AAC, H.264 compatibility, duration, size and a real mobile playback test. Automatic image checks can detect clipping, but **cannot certify that HeyGen generated natural teeth**; that needs human approval.
7. **Hosting:** upload MP4s to a video/CDN service (e.g. Cloudflare R2 with a custom public HTTPS domain). Do not store API keys in browser JavaScript. Configure a stable `https://.../fractions/<lesson>.mp4` URL. GitHub Pages repository is not ideal for hundreds of MP4s.
8. **Embedding:** only after all five hosted URLs pass QA, write a JSON manifest mapping `comparing`, `equivalent`, `mixed`, `addsub`, `problems` to their HTTPS MP4s. Set `settings.avatar_approved=true` **only after approval**. Run `python video-agent/agent.py publish --manifest published.json --page fractions.html` on a publication PR, not automatically against main. The tool replaces one iframe per matching section with a native mobile-friendly HTML5 `video`; retain Scrimba fallback until the production video is verified. Human review/merge remains required.
9. **Scaling:** a workflow-dispatch batch accepts a topic list, schedules jobs with concurrency and spend caps, caches approved voice/avatar assets, uploads files and opens a PR containing changed embeds. Each video is idempotent via a content hash. Budget and failed jobs stop the batch.

## Credentials and spend controls

- `HEYGEN_API_KEY` (GitHub Actions secret; phase 2 only).
- Video host credentials, e.g. `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET`, `R2_PUBLIC_BASE_URL` (phase 2).
- An **explicit** `avatar_approved` flag and an `allow_paid_generation` workflow input; both must be true before an API call can consume credits.
- A max videos/job and spend cap, and no unattended rerendering on transient failures.

## Embedding manifest format (future)

```json
{
  "comparing": {"url":"https://media.example.org/fractions/comparing.mp4","qa_passed":true},
  "equivalent": {"url":"https://media.example.org/fractions/equivalent.mp4","qa_passed":true},
  "mixed": {"url":"https://media.example.org/fractions/mixed.mp4","qa_passed":true},
  "addsub": {"url":"https://media.example.org/fractions/addsub.mp4","qa_passed":true},
  "problems": {"url":"https://media.example.org/fractions/problems.mp4","qa_passed":true}
}
```

## Production quality rules

- Mathematics occupies the central board; teacher stands entirely within the left lane.
- No decorative plant or MathMagic logo in the video scene.
- No equations outside the 5% safe margins of the board.
- All shaded fraction bars use equal-sized cells and represent the same whole.
- Fraction values and comparisons are checked using exact rational arithmetic.
- Do not claim full automation or publish new videos before avatar approval and a successful end-to-end pilot.

## Phase 2 — safe integration commands

The HeyGen provider client uses the documented legacy transparent-WebM endpoint `POST /v1/video.webm` (avatar **pose** ID and voice ID) and `GET /v1/video_status.get`. These endpoints may have account-specific access or changes; validate against the actual HeyGen account before paid production. Newer v3 APIs also exist; this first connector deliberately isolates the endpoint for replacement.

```bash
# Completed video: fetch without paying or using the HeyGen browser.
python video-agent/production.py fetch \
  --url 'https://resource2.heygen.ai/path/to/completed.webm' \
  --output video-agent/output/existing.webm

# Existing completed video ID: requires HEYGEN_API_KEY for status.
python video-agent/production.py fetch --video-id EXISTING_ID \
  --output video-agent/output/existing.webm

# Composite a previously prepared board-only MP4 with transparent presenter.
python video-agent/production.py render \
  --board video-agent/output/equivalent/BOARD_ONLY_PREVIEW.mp4 \
  --avatar-webm video-agent/output/existing.webm \
  --output video-agent/output/equivalent/proof.mp4

python video-agent/production.py qa \
  --output video-agent/output/equivalent/proof.mp4
```

**Paid generation is blocked unless all three are present:** `--approved-avatar`, `--allow-paid`, and `HEYGEN_API_KEY`. The GitHub Actions workflow exposes **no paid generation option**. It accepts an optional already-completed video URL or ID, automatically downloads it and composites a **3-second proof**. Do not enter a private API key as a workflow input; use Actions Secrets.

The compositor requires a true VP9 alpha stream (`ALPHA_MODE=1`), uses `libvpx-vp9` decoding, measures the visible alpha bounding box, and places the entire presenter within the left lane. A single alpha-frame crop is a starting point, not yet a guarantee for changing poses throughout a video. For hundreds of videos, future QA must sample all scenes and detect clipping and sync drift.

**Local evidence:** 3-second output was `1280×720`, `H.264`, `yuv420p`, `AAC`, duration `3.0s`, QA passed. It used the already-generated WebM and a plant-free board; **no new paid video was generated**. This does not prove live GitHub Actions or API access yet.
