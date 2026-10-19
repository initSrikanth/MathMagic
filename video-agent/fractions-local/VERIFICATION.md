# Five-video release verification

All five final MP4s were rendered locally and checked before page integration. No paid API calls, avatars or commercial video services were used.

| Video | Seconds | Full decode | Audio | Scene review |
|---|---:|---|---|---|
| comparing | 84.97 | PASS | PASS: decoded levels and three speech-recognition samples | PASS: 14 cue frames |
| equivalent | 88.27 | PASS | PASS: decoded levels and three speech-recognition samples | PASS: 14 cue frames |
| mixed | 82.23 | PASS | PASS: decoded levels and three speech-recognition samples | PASS: 14 cue frames |
| addsub | 106.93 | PASS | PASS: decoded levels and three speech-recognition samples | PASS: 18 cue frames |
| problems | 93.27 | PASS | PASS: decoded levels and three speech-recognition samples | PASS: 16 cue frames |

Every file is native 1920×1080, 30 fps, H.264/yuv420p with AAC audio and faststart. Exact rational checks cover all narrated worked examples. Visual review covered equal-sized wholes, shading, stacked notation, conversions, comparisons, number lines, calculations and context units. Two Equivalent Fractions simplification cues were clarified; the unchanged animation segments and AAC stream were reused.

Desktop (1440×1000), tablet (820×1180) and mobile (390×844) system Chromium checks passed for all five players: metadata, advancing unmuted playback, middle/late seeking, ending, responsive 16:9 containment, caption-track/transcript presence, lesson navigation, practice feedback and initial challenge controls.

`integration.json` proves that all HTML outside the six original video-resource wrappers is unchanged byte for byte. The five new players use repository-relative sources, posters, captions, transcripts and direct fallback links. The LCM extension is a chapter link into the fourth film. CSS, JavaScript, Firebase authentication/progress code, quiz data and unrelated pages were untouched. The small protected-Fractions static architecture check also passed.

Firebase modules were deliberately isolated in browser QA; this is not a live Firebase or real Safari/iOS certification. No broad website audit, generator stress suite or unrelated tests were run, as requested. Historical tests pin the superseded six-player layout and old immutable filenames; they were not weakened or presented as passing.

The rollback tag is `rollback/fractions-before-local-animation-20261019`. GitHub Pages deployment and full published-byte verification are recorded after the production commit, separately from local media/code completion.
