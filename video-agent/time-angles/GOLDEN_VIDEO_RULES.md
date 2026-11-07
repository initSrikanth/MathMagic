# MathMagic Golden Video Rules — founder-approved production brief

Applies to new MathMagic teaching videos, starting with Time and Angles. These are explicit founder instructions for new production. Do not silently alter previously approved videos or restart suspended unrelated production.

1. **Brand is mandatory.** Show the word **MathMagic** visibly, legibly, and tastefully in every new video, including the opening. Say “MathMagic” naturally in the spoken introduction. Do not add third-party brands, avatars, or distracting watermarks. This is a specific founder-authorised exception to the historical no-in-video-branding rule for newly produced videos. Any broader change to the global contract requires separate review.
2. **Story before lesson declaration.** Open with an intriguing, age-appropriate real-life situation, a mystery or an open question that creates curiosity. Do not begin abruptly with “Today we are learning”. Only **after the story**, say **“Today we are learning…”**, then state the learning goal and three student-friendly success criteria.
3. **Preserve the approved look.** 1920×1080, clean cream background, readable dark-blue type, animated mathematical models, teal/orange highlights, smooth meaningful transitions. Diagrams must explain the mathematics; no static equation wallpaper.
4. **Preserve the approved voice.** Kokoro v1.0 **hf_alpha**, speaker ID 31, natural and warm female Indian-English delivery. No HeyGen, espeak, voice substitutions, synthetic time-stretching, or paid API.
5. **Teach, do not just present.** Hook → “Today we are learning” → learning goal → three success criteria → concrete visual model → worked example → prediction and five-second thinking pause → reveal with reasoning → common misconception → second example → independent challenge → reflection.
6. **Full-length lessons.** Target 5–7 minutes for this strand. Check the final MP4 duration with ffprobe; reject under five minutes. Never pad with meaningless silence or static frames just to meet duration.
7. **Quality gates.** Render H.264 1080p with AAC and +faststart. Verify audio is present and non-silent, video decodes, lesson maths is correct, brand appears on opening frames, story precedes the learning declaration, and final output is the extended file. Preserve the earlier published version for rollback.
8. **Publish only verified output.** Use unique filenames and commit/upload the finished MP4. Check that the live file resolves and matches the rendered version. A green Actions check is not proof of perceptual quality or public availability. Never give the user an old or unverified link as a finished video.
9. **Reuse the proven workflow.** Use GitHub Actions, existing MathMagic visual primitives and approved Kokoro production practices. Avoid inventing a new pipeline for each lesson. No recurring automation or changes to unrelated topics without explicit authorisation.
10. **Apply consistently.** Use these rules for the remaining Time and Angles videos. Do not publish them until each individually passes its own media and teaching QA.

## Video 1 required opening

**Story first:** “Imagine you are waiting for a bus. It leaves at nine fifteen and reaches your destination at ten oh five. You glance at the clock and wonder, how long did the journey really take? Could it be ten minutes? Or is there something we are missing? Let us find out together.”

**Then:** “Today we are learning how to read time and calculate duration. Welcome to MathMagic…”

**Then:** learning goal, three success criteria, visual worked solution and challenges.

The founder-approved existing quality is the reference; new improvements must not degrade it.
