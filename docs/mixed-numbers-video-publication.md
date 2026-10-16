# Approved Mixed Numbers video publication audit

## Scope and identity

The user authorised publishing the supplied `MathMagic_Mixed_Numbers_CAREFULLY_TIMED.mp4` unchanged. It is copied to `videos/MathMagic_Mixed_Numbers_FINAL.mp4`. The only application change is the Mixed Numbers `#mixed` video-resource block in `fractions.html`: its Scrimba iframe becomes a responsive native HTML5 player, with an MP4 fallback link and matching resource label. All explanatory text, practice, quiz, other lesson sections, Firebase modules and progress code remain byte-identical to the starting main commit `6b0ff415d039c9bb35cc5e8d558ecc71d5ffb8a8`.

- SHA-256: `92c831fce1d463b7a369511098a1a5eff47a8756d840e5fe52f510dc3f7cdc56`.
- Size: 4,870,811 bytes; duration: 75.889 seconds.
- Video: 1280×720, H.264, yuv420p. Audio: AAC, 48 kHz, stereo.
- `cmp`/binary comparison confirms the destination matches the approved attachment. FFmpeg decoded the complete copied media without reported errors. No transcoding, teacher/narration/graphics/timing changes, regeneration or paid service use occurred.

## Coverage and test infrastructure

The static video audit retains the existing minimum of 14 resources across six modules and five original Fractions explainers. It recognises only the three established/approved MathMagic MP4 replacements in addition to supported provider embeds, rejects duplicate MP4s, checks required player attributes, typed sources, real local MP4 files and fallback links, and pins the approved Mixed Numbers hash. Each Fractions lesson must have exactly one explainer; Mixed Numbers must reference its exact approved local path. Current coverage is nine YouTube, two Scrimba and three approved MP4 players, with one original explainer in each of five Fractions lessons. The previous iframe-only coverage failure is resolved without reducing either coverage minimum or altering unrelated lesson content.

Browser coverage now verifies the correct MP4 or exact Scrimba URL for each of those same five lessons. The new Mixed Numbers check validates HTTP byte ranges/content type/size, metadata, actual time advancement, seeking across the clip, end-of-video handling and desktop/mobile containment. Existing quiz, notation, resource, layout and generator checks remain in place.

The old `python3 -m http.server` test server returned HTTP 200 to Range requests, and Chromium reported a zero-length seekable range despite valid media. `tests/serve.py` adds bounded single-byte-range responses for the local Playwright server, including HTTP 206/416 and Content-Range. `playwright.config.js` changes only its server command. This is test infrastructure, not a production auth bypass or an alteration to the video. The server binds only to loopback. The initial seek failure was corrected at the server rather than deleting the assertion.

## Applicable canonical instruction audit

PASS below concerns this scoped media replacement, not a certification of the whole site. Curriculum/question redesign and competitor/resource research are not applicable: approved teaching media is being published, and no assessed content or coverage is changed.

| Requirement | Result and evidence |
| --- | --- |
| Scope, existing architecture and unrelated work preservation | PASS — isolated checkout; source comparison limits the HTML change to the Mixed Numbers video-resource block. |
| Curriculum, assessment count/bands, notation, marking and feedback | PASS for preservation — teaching/practice/quiz files and logic unchanged; representative approved video frames use correct stacked notation and equivalent values. Existing automated suites remain required. |
| Auth, approval, progress, secrets and protected-only behaviour | PASS for preservation — no auth, Firebase configuration, backend, progress, rules or production test-bypass changes. Real Firebase integration remains separately unverified. |
| Five Fractions explainers and total resource coverage | PASS — original five-lesson and 14-resource requirements retained and strengthened with per-lesson/approved-byte checks. |
| Responsive/accessibility/player/fallback requirements | PASS — native controls, playsinline, metadata preload, accessible name, typed source, 16:9 container, full-width containment and direct fallback; no autoplay. Browser results are recorded below. |
| Video rule 1: mathematics focus and full-body teacher on left | PASS — representative source frames and local browser preview inspected; approved composition preserved. |
| Video rule 2: reuse approved footage/voice | PASS — exact binary copy; no regeneration or credit spend. |
| Video rule 3: programmatic mathematical graphics | PASS for preservation — supplied approved graphics retained without redrawing or generation. |
| Video rule 4: visuals track explanation | PASS for preservation — approved timing unchanged; sampled frames show distinct mathematical scenes. No new word-level synchronisation claim. |
| Video rule 5: correct lesson scene definitions | PASS — Mixed Numbers/improper-fraction conversion and comparison scenes, not a substituted lesson. |
| Video rule 6: correct mathematics, equal wholes and fraction bars | PASS for sampled review — seven quarters, eleven quarters, three and two fifths, mixed-number comparison and nine quarters are mathematically consistent with stacked fraction bars. This is not an exhaustive new narration audit. |
| Video rule 7: start, scene boundaries and ending | PASS for preservation — full decode, representative frames, ending frame and browser seeking/end checks; approved timing unchanged. Independent word-by-word audio alignment was not re-established. |
| Video rule 8: no unnecessary intros or damaging trims | PASS — approved narration unchanged; no trims. |
| Video rule 9: no framed/clipped teacher or distracting alterations | PASS — full-body teacher and legible graphics in reviewed frames; unchanged bytes. |
| Video rule 10: future presenter prompts | Not applicable — no presenter generation requested. |
| Video rule 11: H.264 yuv420p/AAC mobile-compatible MP4 | PASS — FFprobe confirms required streams/pixel format; no re-encode. |
| Video rule 12: preserve other videos until replacements checked | PASS for local replacement — only the approved target embed changes; other players remain untouched. Production playback limitation is explicit below. |
| Video rule 13: actual MP4 on target branch and player reference | Local checks PASS; remote branch verification occurs after committing and is reported separately. No workflow-only publication claim. |
| Video rule 14: mathematical, representative-frame, duration/audio and playback checks | Local frame, decode, metadata and browser checks performed; live-production playback is blocked as recorded below. |
| Video rule 15: auth, progress and unrelated lessons | PASS — byte-identical outside the targeted resource block and authorised QA/docs. |
| Video rule 16: reversible source retention | PASS — uploaded source preserved separately and unchanged bytes tracked; no existing footage or generation code removed. |
| Video rule 17: one lesson at a time, commit and URL report | PASS for scope — only Mixed Numbers published. Commit SHA and deployment/URL observations are reported separately. |
| Video rule 18: success requires more than workflow/HTML commit | PASS — video-byte identity, complete decode, static architecture and actual local Chromium playback evidence; production verification explicitly limited. |
| Captions/transcripts | No captions/transcript supplied; none fabricated. |
| External provider copyright/access parameters | PASS for preservation — no third-party content copied; remaining provider embeds and share parameters unchanged. |
| Git scope, no test weakening, truthful results | PASS — explicit paths only; no force push or reduced coverage thresholds. Final SHA and test outcomes are reported separately. |

## Verification results and limitations

Static checks: `npm run test:protected` passes all architecture checks, 500 Multiplication & Division challenges / 15,000 positions, 1,000 Factors & Multiples challenges / 30,000 positions, the updated 14-resource video audit, and the remaining two Scrimba embed audits. Whitespace, scoped HTML comparison, exact approved-byte comparison and complete FFmpeg decode pass.

Local browser serving returned HTTP 200, `Content-Type: video/mp4` and all 4,870,811 bytes. System Chromium loaded metadata and advanced playback; desktop/mobile player screenshots were inspected. Browser tests deliberately isolate Firebase auth/progress through their existing test-only adapters, so they do not prove real Google sign-in, access approval, Firestore rules, real student persistence or App Check.

The pinned Playwright Chromium executable was absent and its download hosts were denied by network policy. Available `/usr/bin/chromium` was used through a temporary external configuration, retaining the repository's desktop Chromium and Pixel 7 projects. That temporary config is not committed; standard CI continues to install its pinned browser normally. Initial harness/configuration failures were corrected before final QA.

The focused Mixed Numbers playback test passed on both desktop and Pixel 7 mobile Chromium (2/2), including HTTP 206, seeking and end-of-clip handling. The complete 70-test regression suite is required before the main-branch push; its observed result and final tested SHA are reported in the task completion report rather than inferred from this audit.

Production: access to `https://initsrikanth.github.io/MathMagic/fractions.html` returned a proxy CONNECT 403. The Pages origin is unavailable under the current network policy. Production video serving/playback, real signed-in UI and cross-device progress are not verified. The intended video URL after Pages publication is `https://initsrikanth.github.io/MathMagic/videos/MathMagic_Mixed_Numbers_FINAL.mp4`; this URL is not evidence of a successful playback check.
