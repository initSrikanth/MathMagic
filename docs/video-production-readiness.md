# Video production integration readiness — Phase 2

Audit: 16 October 2026 (Australia/Brisbane). Baseline: [report at 1271e3a](https://github.com/initSrikanth/MathMagic/blob/1271e3ae8010e662d1a37635b9a9fad1ab7db961/docs/video-production-readiness.md). Follow [AGENTS.md](../AGENTS.md) and the [specialised workflow](../agents/VIDEO_PRODUCTION.md).

## Decision

**Existing-asset retrieval from GitHub, free local processing, composition-preserving encoding, GitHub MP4 upload and local desktop/mobile Chromium playback work. New HeyGen production is not fully verified.** The approved look is available and supports the required engine. Current voice eligibility, HeyGen media downloads, independent-avatar compositing, native 1080p teacher detail and live Pages playback remain blocked or unverified. No paid generation, replacement look/voice, lesson edit or application change occurred.

The checkout was fetched and switched to latest main `1271e3ae8010e662d1a37635b9a9fad1ab7db961` **before tests**. Untracked dependency directories were preserved. Non-production test code/MP4 was committed and uploaded on main at `bc1192c35383c84823e8ac0c894b667ae33e3845`.

## Networking: diagnosis and exact settings

Two restrictions were distinguished:

1. Default shell execution could not reach the managed proxy: `proxy` resolved, but ports 8080 and 8088 returned `Operation not permitted`. Supported additional **shell network permission** allowed Git/HTTPS through the inherited proxy. This did not disable or broaden its destination policy. No proxy, routes, CA trust or TLS checks were altered. No unrestricted internet setting or proxy repair was needed.
2. With shell permission enabled, `github.com`, `raw.githubusercontent.com` and `pypi.org` returned HTTP 200. Missing destinations returned proxy CONNECT 403. Fresh environment status reports revision 3, policy **restricted/enforced**, with no custom allowed hosts, secret bindings or outbound identities. This supersedes Phase 1's unknown policy state.

Keep restricted networking and the existing package-manager preset. Add these exact custom hosts in Codex environment settings:

| Host | Purpose |
| --- | --- |
| `files2.heygen.ai` | Actual existing narration MP4 and approved look preview host returned by HeyGen; shell access denied. |
| `resource2.heygen.ai` | Existing transparent WebM URLs used by the prior implementation; needed for those assets. An approved independent Mixed Numbers transparent source is not yet established. |
| `api.heygen.com` | Direct API look/voice/status reads if using a secret-managed HeyGen API key; connector reads work separately. |
| `initsrikanth.github.io` | Actual MathMagic Pages origin for live media/range/playback verification. |
| `api.github.com` | Direct CLI/API metadata/deployment diagnostics; connector metadata is a working alternative. Ordinary Git upload/raw download already work. |

All five currently return CONNECT 403 from the shell. `github.com` and `raw.githubusercontent.com` already work and need no additional grant. No wildcard, general cloud/CDN grant, VPN, TCP exception or unrestricted internet is needed for this route. Inspect any actual asset redirect before adding its exact host.

The user agreed to update these hosts during the audit. **Last observed running configuration still reports `allowed_hosts: []`.** Agreement is not proof settings were saved/applied. Save/apply to this environment, then require current observations, policy state enforced and successful actual requests. Restart/re-attach only if the settings interface requires it. Editing the on-disk policy snapshot cannot grant access.

Optional only: installed Playwright's download dry-run names `cdn.playwright.dev` and fallback `playwright.download.prss.microsoft.com`. Neither is needed for the system-Chromium test route used here; allow them only if installing the pinned browser is desired.

The cloud runtime skill requires environment configuration changes through its supported configuration workflow and user review. The task therefore documents settings rather than bypassing the proxy.

## HeyGen look, voice and existing media

Connected read authentication succeeds for video/scene/look/group/account and voice catalogue reads. An account subscription with remaining credits is observable; it does not prove specific API/transparent-output entitlement.

Existing narration `c2126e788e37f727e608df2b87d1d386` is completed, 70.5567 seconds. Scene metadata identifies look `2e895abe1f515732737973186daa2e51`, engine `avatar_iv`, voice `2ec5ec7926eb471d9f33e1b7ba4bb77d`, pitch 0, speed 1, volume 1. The look is completed and supports avatar_iv/avatar_v/avatar_iii. Its group exists with one look; consent status is unspecified, not a verified consent failure.

**Voice eligibility remains unconfirmed.** Private voice/model lists are empty. Public model voices and 180 English/male catalogue entries did not identify the ID; the latter listing remains incomplete. This is not evidence that the voice is deleted/unusable. Available tools expose no exact-voice eligibility/dry-run lookup. Do not substitute another voice or invoke synthesis/generation to test it.

Use an approved read-only account/API lookup covering the original voice. If Python API access is needed, bind `HEYGEN_API_KEY` as a **Codex secret**, never in chat/source/logs/docs or workflow inputs. No such binding is currently reported ready. Connected credentials are not automatically available to Python/Actions. If read metadata cannot establish eligibility, retain the limitation rather than spending credits.

HeyGen returns the existing MP4 URL on `files2.heygen.ai`; signed URLs are omitted here. Shell downloads remain blocked by host policy. No HeyGen asset-byte download is claimed from metadata alone. No avatar/look/voice/speech/generation/lipsync/translation creation request was made.

## Approved asset retrieval and composition

The approved `videos/MathMagic_Mixed_Numbers_FINAL.mp4` was retrieved by refreshed Git and separately by raw GitHub HTTPS at the baseline revision. Both match **4,870,811 bytes**, SHA-256 `92c831fce1d463b7a369511098a1a5eff47a8756d840e5fe52f510dc3f7cdc56`. FFprobe confirms 75.889 seconds, 1280×720 H.264/yuv420p and 48 kHz AAC. Complete FFmpeg decode passed. Audio analysis reports mean −20.7 dB and peak −3.7 dB; this is technical evidence, not a new subjective intelligibility/lip-sync certification. Approved bytes remain unchanged.

Ten extracted frames (0, 5, 12, 20, 30, 40, 50, 60, 70, 75 seconds) were visually reviewed. They retain the left full-body teacher, navy suit, white shirt, burgundy tie, proportions and visible head/shoes. Right-side diagrams show distinct conversion/comparison/recap scenes with stacked fractions. Five worked examples passed independent exact rational checks. This is sampled review, not a full word-by-word narration audit.

Measured 1280×720 reference geometry:

- Teacher panel approximately x=0–404, y=56–664: 31.56% of frame width, with original grey background.
- Rounded pale blue/white board approximately x=429–1258, y=25–697.
- Ten dark clothing/hair/shoe diagnostics span x=105–301, y=73–656, within the panel. These are colour-threshold bounds, not semantic identification or proof about every moving frame.

**Correction to Phase 1:** the feature branch's beige wall/brown floor and ≤22% teacher lane are not the approved final composition. Do not force the teacher into that old layout. The final was supplied separately; its exact authoring/compositor/cue sheet is not tracked on main.

A board-only frame-difference scan finds visual changes around 5.375, 10.750, 15.049, 20.424, 30.121, 36.571, 46.245, 55.405, 62.907 and 73.657 seconds. These are visual transition candidates, not speech timestamps. The approved final has more steps than the older seven weighted scenes. Independent new composition still needs approved source layers, cue recovery and actual narration alignment.

## Free production, GitHub upload and playback

Added [offline media check](../tests/video-production-readiness.py), [browser check](../tests/e2e/video-production-readiness.spec.js), [fixture provenance](../tests/fixtures/VIDEO_PRODUCTION.md) and optional Pillow requirements. There is no production generator/publisher in these tests.

The offline check generated a programmatic horizontal-bar fraction PNG in scratch space and encoded a **four-second non-production MP4** from the existing approved composite. Uniform scaling preserves framing/proportions and existing audio/graphic timing. It uses 720p detail in a 1920×1080 encoding test; it is not native 1080p teacher footage, new teaching content or a replacement lesson.

Fixture `tests/fixtures/video-production-smoke.mp4`: **314,344 bytes**, 4.000 seconds, 1920×1080 H.264/yuv420p, AAC, faststart. SHA-256 `d91185f8a6e50891f533cc6e76fc1e308271d99715c0043391c76f701da61643`. Complete decoding and moov-before-mdat checks pass. Source-size comparisons at 0/1/2/3 seconds have mean absolute channel errors 0.5744–0.6976 for the teacher panel and 0.4384–0.4390 for the board (0–255 scale). Visual review confirms the fixture preserves composition; this does not validate the old independent-avatar compositor.

The real binary was uploaded by normal authenticated Git push on main at `bc1192c35383c84823e8ac0c894b667ae33e3845`, then [downloaded at that exact revision](https://raw.githubusercontent.com/initSrikanth/MathMagic/bc1192c35383c84823e8ac0c894b667ae33e3845/tests/fixtures/video-production-smoke.mp4). HTTP 200 returned the identical byte count/hash; the downloaded copy fully decoded. Raw GitHub returns `application/octet-stream`: this proves byte delivery, not Pages MIME/playback. No LFS pointer was used. No lesson references the fixture.

The local range server returns `video/mp4`, HTTP 200 for complete bytes, 206 for valid ranges and 416 for an invalid range. Desktop and Pixel 7 Chromium both load 1080p metadata, advance playback, seek early/middle/late, reach the ending and contain the player. Those tested bytes match the GitHub download. Safari/iOS and live Pages playback remain unverified.

## Executed QA and failure classification

| Check | Actual outcome |
| --- | --- |
| `npm run test:protected` on refreshed main | PASS: six architecture checks; Multiplication & Division 500 challenges/15,000 positions; Factors & Multiples 1,000 challenges/30,000 positions; 14 video resources across six modules (9 YouTube, 2 Scrimba, 3 approved MP4), five original Fractions lesson explainers preserved. |
| Existing full Playwright suite on refreshed baseline | 70/70 PASS. |
| New fixture suite | 2/2 PASS. Initial mobile containment failure came from the new harness's missing viewport meta; fixed and rerun without changing a lesson or weakening assertions. |
| Full suite including fixture on `bc1192c` | 72/72 PASS, including both new playback cases; all existing assertions retained. |
| Offline media validation | PASS: approved hash, five exact examples, Pillow graphic, source/fixture full decode, dimensions/codecs/duration/faststart, four image comparisons, ten geometry samples. |
| Actual GitHub upload/download/decode | PASS at `bc1192c`; identical fixture bytes verified. |
| Shell default network failure | Environment execution restriction; resolved for task commands using supported shell network permission and the managed proxy. |
| HeyGen/Pages/API host denials | Environment destination-policy failures (CONNECT 403), not application failures. |
| Pinned Playwright browser absent | Environment setup limitation. An uncommitted scratch config selects `/usr/bin/chromium`, retaining both repository projects and assertions. No repository browser requirement changed. |

Used Python 3.12.14, Pillow 12.3.0, FFmpeg/FFprobe 7.1.5. CairoSVG remains absent; the successful Pillow test does not need it. The older SVG renderer still requires its dependencies and documented correctness/720p/timing fixes.

Browser tests retain existing Firebase isolation and do not certify real sign-in, Firestore rules, App Check or cross-device progress. Those integrations were unchanged. Scope/whitespace checks cover docs and non-production tests only: no lesson HTML/CSS, application JavaScript, Firebase, workflows or approved-video changes.

## Remaining actions

1. Save/apply the five specific custom hosts in Codex environment settings, then verify fresh enforced policy and actual requests. Keep restricted networking, proxy and TLS checks. No unrestricted internet is needed.
2. Retrieve existing HeyGen narration/look bytes after grants apply; confirm the exact original voice through read-only account/API metadata. Add a secret-managed API key only if that route requires it. Do not create replacements.
3. Recover approved independent layers and precise timing settings. Old scripts are not a verified native-1080p compositor for this layout. Any new production implementation must preserve it and pass full maths/timing/visual QA.
4. Verify the exact Pages deployment, media type/ranges and live playback once reachable. GitHub upload and local playback are proven separately. Paid generation and lesson publication remain outside Phase 2.
