# Space lessons 2–10: nine review videos

**Nine rendered and technically verified; zero perceptually approved; zero published.** All use the approved Kokoro hf_alpha speaker31 profile. The current files total54m46s and98,568 decoded nonblank frames. No paid generation calls.

[Exact MP4 checksums](SHA256SUMS) · [Completion summary](completion-summary.json) · [Final-byte audit and timing flags](final-audit.json) · [18 current local playback checks](playback-current-qa.json) · [Full-listening/viewing evidence template](perceptual-review-template.json)

| Lesson | Title | Duration | Review files |
| --- | --- | --- | --- |
| 2 | Explore Nets | 5:59 | [MP4](Space_Lesson02_Explore_Nets_Review_1080p.mp4) · [Captions](Space_Lesson02_Explore_Nets_Review_1080p.vtt) · [Transcript](Space_Lesson02_Explore_Nets_Review_1080p_transcript.txt) · [QA](Space_Lesson02_Explore_Nets_Review_1080p_qa.json) |
| 3 | Design and Test Nets | 6:03 | [MP4](Space_Lesson03_Design_and_Test_Nets_Review_1080p.mp4) · [Captions](Space_Lesson03_Design_and_Test_Nets_Review_1080p.vtt) · [Transcript](Space_Lesson03_Design_and_Test_Nets_Review_1080p_transcript.txt) · [QA](Space_Lesson03_Design_and_Test_Nets_Review_1080p_qa.json) |
| 4 | Coordinates and Position | 5:56 | [MP4](Space_Lesson04_Coordinates_and_Position_Review_1080p.mp4) · [Captions](Space_Lesson04_Coordinates_and_Position_Review_1080p.vtt) · [Transcript](Space_Lesson04_Coordinates_and_Position_Review_1080p_transcript.txt) · [QA](Space_Lesson04_Coordinates_and_Position_Review_1080p_qa.json) |
| 5 | Map Routes and Directions | 6:05 | [MP4](Space_Lesson05_Map_Routes_and_Directions_Review_1080p.mp4) · [Captions](Space_Lesson05_Map_Routes_and_Directions_Review_1080p.vtt) · [Transcript](Space_Lesson05_Map_Routes_and_Directions_Review_1080p_transcript.txt) · [QA](Space_Lesson05_Map_Routes_and_Directions_Review_1080p_qa.json) |
| 6 | Translations | 6:00 | [MP4](Space_Lesson06_Translations_Review_1080p.mp4) · [Captions](Space_Lesson06_Translations_Review_1080p.vtt) · [Transcript](Space_Lesson06_Translations_Review_1080p_transcript.txt) · [QA](Space_Lesson06_Translations_Review_1080p_qa.json) |
| 7 | Reflections | 5:57 | [MP4](Space_Lesson07_Reflections_Review_1080p.mp4) · [Captions](Space_Lesson07_Reflections_Review_1080p.vtt) · [Transcript](Space_Lesson07_Reflections_Review_1080p_transcript.txt) · [QA](Space_Lesson07_Reflections_Review_1080p_qa.json) |
| 8 | Rotations and Symmetry | 6:04 | [MP4](Space_Lesson08_Rotations_and_Symmetry_Review_1080p.mp4) · [Captions](Space_Lesson08_Rotations_and_Symmetry_Review_1080p.vtt) · [Transcript](Space_Lesson08_Rotations_and_Symmetry_Review_1080p_transcript.txt) · [QA](Space_Lesson08_Rotations_and_Symmetry_Review_1080p_qa.json) |
| 9 | Classification Algorithms | 6:21 | [MP4](Space_Lesson09_Classification_Algorithms_Review_1080p.mp4) · [Captions](Space_Lesson09_Classification_Algorithms_Review_1080p.vtt) · [Transcript](Space_Lesson09_Classification_Algorithms_Review_1080p_transcript.txt) · [QA](Space_Lesson09_Classification_Algorithms_Review_1080p_qa.json) |
| 10 | Integrated Spatial Design | 6:21 | [MP4](Space_Lesson10_Integrated_Spatial_Design_Review_1080p.mp4) · [Captions](Space_Lesson10_Integrated_Spatial_Design_Review_1080p.vtt) · [Transcript](Space_Lesson10_Integrated_Spatial_Design_Review_1080p_transcript.txt) · [QA](Space_Lesson10_Integrated_Spatial_Design_Review_1080p_qa.json) |

The lesson5 label overlap was corrected by encoding only445 scene frames. All8,552 original AAC packets and all other H.264 packets were preserved; [proof](lesson5-label-repair.json). The previous MP4, its original checksum and sidecars remain in [history](history/lesson5-before-label-repair/).

## Outstanding release gates

1. Recover the exact original8:49 representative from prior storage. Its source and checksum remain unchanged (`32f712baa2e9baa0b56d2569b53152289079d4d5caac5fb42ec9b0264d3547c1`); its outside-Git MP4 was absent from this fresh workspace.
2. An audio-capable evaluator must listen to and view all ten complete exact-byte videos, recording reviewer/date/hash. Check accent, natural warmth/expressiveness, pronunciation, pacing, teaching quality, actual captions and audio/visual synchronisation, transitions, examples, ending and every flagged interval. All these perceptual attributes remain UNVERIFIED; approximate offline ASR timings are not certified forced alignment.
3. Complete real Safari/iOS and real-device readability, native-control and caption QA. Chromium viewport playback is not that evidence.
4. Obtain authorised live Firebase scope and an approved test identity; inspect deployed rules and verify real approved/denied/signed-out access, cross-UID isolation, approval escalation rejection, completed-attempt save/restore across refresh/sign-in/devices, retries/concurrency and revocation, and private-session denial. Verify callable/App Check behaviour where applicable. Emulator fixtures and mocks do not certify production.

**Next release action:** complete those quality gates, resolve any resulting corrections against new exact hashes, then integrate only approved media into PR57, run the appropriate media/browser checks and CI on that changed integration SHA. No merge/deploy until mandatory gates pass.

Existing Measurement and Space emulator suites and the new boundary suite passed. Mocked Space progress and27 production-contract tests passed. The application and existing videos at7ac9fe7 are unchanged; CI was not rerun. See [Firebase evidence](firebase-boundaries.log), [original suites](firebase-emulator.log) and [production source instructions](../README-batch.md).
