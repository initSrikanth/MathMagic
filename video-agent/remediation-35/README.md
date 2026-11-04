# Existing-library remediation — review candidates

**UNVERIFIED: no corrected teaching video has been deployed. New-topic production remains suspended.**

All 35 original published files and their hashes are preserved. [The complete 35-placement review set](review-set-35.json) records original/replacement filenames and release blockers; [the detailed audit](../../docs/video-quality-audit-35.md) and JSON/CSV distinguish completed measurements from unperformed listening/viewing.

## Thirty branding-edited videos

Twenty-nine cuts preserve exact original H.264 and AAC packet prefixes. Adding and Subtracting Fractions (#4) removes the internal branded invitation while retaining the optional LCM-extension notice: 215.7 seconds of original video packets are unchanged, only the 7.6-second tail is re-encoded; AAC is re-encoded without changing pitch or speed. All original narration characteristics are retained. Captions and transcripts are updated.

Full decode/composition checks, encoding, exact hashes, caption/transcript text and timing, audio RMS/clipping and ending ASR were checked. The internal edit also has strictly increasing frame timestamps and the expected 6,699 frames. ASR is not proof of accent or absence of all spoken errors. Silence flags still require context review.

| Inventory | Lesson | Download |
|---|---|---|
| 1 | Comparing and Ordering Fractions | [MP4](brandfree-review/fractions/meaning-brandfree-review.mp4) |
| 2 | Equivalent Fractions | [MP4](brandfree-review/fractions/equivalent-brandfree-review.mp4) |
| 3 | Mixed Numbers and Improper Fractions | [MP4](brandfree-review/fractions/mixed-brandfree-review.mp4) |
| 4 | Adding and Subtracting Fractions | [MP4](brandfree-review/fractions/addsub-brandfree-review.mp4) |
| 5 | Fraction Word Problems | [MP4](brandfree-review/fractions/problems-brandfree-review.mp4) |
| 6 | Understanding Place Value | [MP4](brandfree-review/whole-numbers/lesson1-brandfree-review.mp4) |
| 7 | Expanded Form & Representing Numbers | [MP4](brandfree-review/whole-numbers/lesson2-brandfree-review.mp4) |
| 8 | Comparing & Ordering Whole Numbers | [MP4](brandfree-review/whole-numbers/lesson3-brandfree-review.mp4) |
| 9 | Decimal Place Value | [MP4](brandfree-review/whole-numbers/lesson4-brandfree-review.mp4) |
| 10 | Compare, Order & Locate Decimals | [MP4](brandfree-review/whole-numbers/lesson5-brandfree-review.mp4) |
| 16 | Efficient Mental Strategies | [MP4](brandfree-review/addition-subtraction/lesson1-brandfree-review.mp4) |
| 17 | Written Addition and Subtraction | [MP4](brandfree-review/addition-subtraction/lesson2-brandfree-review.mp4) |
| 18 | Estimate and Check | [MP4](brandfree-review/addition-subtraction/lesson3-brandfree-review.mp4) |
| 19 | Missing Values and Inverses | [MP4](brandfree-review/addition-subtraction/lesson4-brandfree-review.mp4) |
| 20 | Model Practical Problems | [MP4](brandfree-review/addition-subtraction/lesson5-brandfree-review.mp4) |
| 21 | Multiply Efficiently | [MP4](brandfree-review/multiplication-division/lesson1-brandfree-review.mp4) |
| 22 | Multiply by Two-digit Numbers | [MP4](brandfree-review/multiplication-division/lesson2-brandfree-review.mp4) |
| 23 | Divide by a Single-digit Number | [MP4](brandfree-review/multiplication-division/lesson3-brandfree-review.mp4) |
| 24 | Interpret Remainders | [MP4](brandfree-review/multiplication-division/lesson4-brandfree-review.mp4) |
| 25 | Unknowns, Estimation and Modelling | [MP4](brandfree-review/multiplication-division/lesson5-brandfree-review.mp4) |
| 26 | Build Numbers from Factors | [MP4](brandfree-review/factors-multiples/lesson1-brandfree-review.mp4) |
| 27 | Recognise Multiples | [MP4](brandfree-review/factors-multiples/lesson2-brandfree-review.mp4) |
| 28 | Use Divisibility Rules | [MP4](brandfree-review/factors-multiples/lesson3-brandfree-review.mp4) |
| 29 | Follow an Algorithm | [MP4](brandfree-review/factors-multiples/lesson4-brandfree-review.mp4) |
| 30 | Connect and Reason | [MP4](brandfree-review/factors-multiples/lesson5-brandfree-review.mp4) |
| 31 | Choose Units and Measure Length | [MP4](brandfree-review/measurement/lesson1-brandfree-review.mp4) |
| 32 | Measure Mass and Capacity | [MP4](brandfree-review/measurement/lesson2-brandfree-review.mp4) |
| 33 | Trace and Calculate Perimeter | [MP4](brandfree-review/measurement/lesson3-brandfree-review.mp4) |
| 34 | Cover and Calculate Area | [MP4](brandfree-review/measurement/lesson4-brandfree-review.mp4) |
| 35 | Design with Irregular Shapes | [MP4](brandfree-review/measurement/lesson5-brandfree-review.mp4) |

[Packet/hash and automated evidence](brandfree-review/manifest.json) · [All 30 GitHub download checksum checks](all-brand-candidates-github-checksums.json). None of these edits changes enthusiasm or approves a previously unsuitable voice. The five Decimals originals have no source/caption brand match; their narration suitability remains unresolved.

[Internal edit frame samples](internal-brand-edit-seam.jpg) show consistent graphics across the removed invitation; this is sampled visual evidence, not full perceptual review.

## Two original-audio animated model previews

- [Midpoint number line](model-previews/14-model-original-audio.mp4): stacked one half, 0.5 and 50% at the same midpoint.
- [Equal-whole comparison bars](model-previews/15-model-original-audio.mp4): gradual filling to five tenths and four tenths; comparison answer withheld.

These are 854×480 scene previews, not full 1080p replacements. Models use independently checked exact fraction values; reveals follow existing local ASR word starts, with timing uncertainty documented in sidecars. Actual listening and full temporal review remain required.

## Voice calibration evidence

[32.53-second offline WAV](voice-calibration/native-curiosity-01.wav) · [Transcript](voice-calibration/transcript.txt) · [Configuration](voice-calibration/manifest.json).

Kokoro v1.0 hf_alpha, Apache-2.0, same installed Measurement baseline. No paid calls, unauthorised voice imitation, artificial pitch/time effects or inserted silence. Accent and increased enthusiasm remain UNVERIFIED pending meaningful listening. No replacement-narration batch was generated under an unverified expressive configuration.

[Candidate browser evidence](candidate-browser-playback.json): 90 Chromium checks passed (30 videos × phone, tablet and desktop widths), exercising playback, seeking, captions, ending and containment. These are local review-byte tests through unchanged player markup, not live replacement deployment or physical-device/Safari tests.

## Release blocker

The execution tools support waveform analysis, ASR, decoded images and browser automation, but no meaningful audio listening/full-motion perceptual assessment. None of the 35 videos has received every mandatory perceptual check. Actual full-video review bound to each exact final SHA-256, and validation of the requested enhanced delivery, are needed before publication. Founder authorisation is already recorded; no routine intermediate approval is being requested.

Source-only safeguards: [PR #52](https://github.com/initSrikanth/MathMagic/pull/52), commit `41dbb30`. Cross-year contract/tool refinements: [PR #53](https://github.com/initSrikanth/MathMagic/pull/53). Published lesson pages, quizzes, authentication and Firebase are unchanged.
