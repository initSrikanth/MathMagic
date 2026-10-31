# Fractions — current media inventory and review status

Audited against main `bebf1528e2f5c816e070ba897a6a5872b3c52583` for [CEO mission #39](https://github.com/initSrikanth/MathMagic/issues/39). The previous Scrimba inventory and standalone-player publication descriptions were historical; they did not describe the current five V2 players. Do not treat this inventory as fresh approval of narration quality.

## Current published baseline

All five core lessons currently use owned, self-hosted native HTML5 players. Each has controls, `playsinline`, metadata preload, a typed MP4 source, accessible name, responsive 16:9 containment, a matching English (`en-GB`) VTT, poster, direct fallback and expandable transcript.

| Lesson section | MP4 basename under `videos/` | Bytes | Duration (seconds) | VTT cues |
| --- | --- | ---: | ---: | ---: |
| `meaning` | `MathMagic_V2_fractions_comparing.mp4` | 2,531,705 | 128.733333 | 33 |
| `equivalent` | `MathMagic_V2_fractions_equivalent.mp4` | 2,731,610 | 136.066667 | 36 |
| `mixed` | `MathMagic_V2_fractions_mixed.mp4` | 2,399,070 | 124.333333 | 33 |
| `addsub` | `MathMagic_V2_fractions_addsub.mp4` | 3,152,773 | 161.581 | 42 |
| `problems` | `MathMagic_V2_fractions_problems.mp4` | 2,802,528 | 144.933333 | 39 |

For each basename, captions are `.vtt`, poster is `_poster.jpg`, and standalone transcript is `_transcript.txt`. Fresh source checks confirm every caption's words match both the standalone and inline transcript after whitespace normalisation. Cue times are positive, ordered, nonoverlapping and within the media duration. Caption text uses spoken fraction names, not slash notation. These are Kokoro v0.19 `bf_emma` graphics-only videos, not the approved original teacher/clone. The founder subsequently rejected the narration/presentation quality; technical playback alone does not resolve that objection.

The baseline LCM card is only a link to `MathMagic_Adding_Subtracting_Fractions_Animated_1080p.mp4#t=72.12`, a different, earlier file than the V2 player above it. Its sentence saying the extension is in the video "above" is misleading because its link opens another video. The approved standalone LCM still exists but is not embedded in this baseline.

## Preserved approved assets

| Asset | Bytes | Freshly verified SHA-256 |
| --- | ---: | --- |
| `MathMagic_Adding_Subtracting_Fractions_CORRECTED_1080p.mp4` | 14,169,595 | `48ef9512c531cc6450ee22048152dad4e6d3ab757b74bf88eacc639df27358db` |
| `MathMagic_Finding_LCM_FINAL_1080p.mp4` | 3,111,284 | `374bae53a7d727587b7940e2e302dcf30c528e17a964db914d2c8eb7107a3c00` |
| `MathMagic_Mixed_Numbers_FINAL.mp4` | 4,870,811 | `92c831fce1d463b7a369511098a1a5eff47a8756d840e5fe52f510dc3f7cdc56` |

The first two also match the Git blob IDs of the original approved review files (`41cc150…` and `9ec0be5…`). Original captions/transcripts remain available. No approved MP4 bytes were modified or re-encoded. The Mixed Numbers final is an older 1280×720 approved presenter asset; this audit does not authorise replacing the current mixed player.

## Review-only proposed restoration — founder approval required

Branch `ceo/fractions-39-media-approval` proposes restoring the already approved corrected Adding & Subtracting player and the standalone approved LCM player immediately below it. It reuses their existing `en-AU` captions and matching transcripts without generation. All five V2 MP4 assets remain untouched; four stay in their current players. Current teaching, assessment, authentication, progress and unrelated content are preserved. The LCM lesson remains explicitly an extension, not a new assessed Year 5 LCM requirement.

This is a review candidate, **not a statement that the proposal is deployed or newly approved**. The founder must approve the player restoration before merge/publication. Existing immutable-byte and approved-player tests remain meaningful release gates; source drift must not be hidden by deleting their approved-media assertions.

Comparing Fractions review prototypes also remain outside main: two voice-comparison candidates at `78f7f595…`, and the 5:55 scaffolded candidate at `69d1d19…`. The latter's underlying Kokoro `af_heart` voice has no explicit emotion controls; natural, expressive teaching performance remains unverified. None is authorised for live replacement by this audit.

## Observed verification and limits

Fresh hashes, FFprobe metadata, complete decode and volume analysis for all five baseline V2 files plus approved Add/Subtract and LCM are recorded in `docs/qa/fractions-39-media.json`. Read-only live HTTP, MIME, byte-range and checksum results are in `docs/qa/fractions-39-media-live.json`. The reusable local browser gate and its baseline/proposal reports distinguish desktop/tablet/phone **Chromium viewports** from untested real Safari/iOS.

Observed browser results: all 15 baseline cases (five players × 1440/768/390 viewports) and all 18 proposal cases (six players × the same viewports) passed in Chromium 154. The two existing approved-player Playwright tests also passed, retaining exact hashes, captions, metadata, range handling, seeks, ending, keyboard focus and layout checks. The approved Add/Subtract transcript locator is scoped to its own card because other core lessons now also have transcripts; no approved-media assertion was removed. These local reports describe the tested worktree, not production deployment or a green CI run.

The local browser gate deliberately isolates Firebase auth modules. It does not establish real Google login, entitlement, live Firestore rules, cross-device progress, native Safari/iPhone playback, perceptual pronunciation or student learning outcomes. Historical production records in `video-agent/production-v2/` are evidence from their recorded dates, not fresh tests. No paid services, video generation, pipeline restart or publication was performed by the video audit.

Historical Scrimba references are retained in Git history; they are not the current player inventory. The original ownership/copyright, privacy, fallback and external-resource policies in `AGENTS.md` continue to apply.
