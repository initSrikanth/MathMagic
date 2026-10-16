# LCM extension — review preparation, not a finished narrated video

Requested title: **Finding the Lowest Common Multiple (LCM)**. The lesson is an optional Year 5 extension. Year 5 AC9M5N05 requires calculation with same/related denominators, and AC9M5N02 includes multiples; a formal LCM procedure is not prescribed. Broader fraction calculations progress in Year 6 AC9M6N05.

Sources checked 16 October 2026:
- https://www.australiancurriculum.edu.au/resources/work-samples/mathematics/year-5/ws03-representing-and-adding-fractions
- https://www.mathematicshub.edu.au/search/factors-multiples-primes-year-5-planning-tool/
- https://www.mathematicshub.edu.au/search/fractions-year-6-planning-tool/

## Actual blocker

The active Codex environment has no ElevenLabs connector, no ElevenLabs secret binding, no configured provider voice ID/model/settings, and its enforced allowed-host list does not contain `api.elevenlabs.io`. Available HeyGen speech tools are not an authorised substitute. The HeyGen voice ID `2ec5ec7926eb471d9f33e1b7ba4bb77d` does not establish an ElevenLabs voice ID. The user-confirmed clone name is **Srikanth sogathur**.

To unblock narration, connect ElevenLabs or configure an `ELEVENLABS_API_KEY` secret with access to that clone and add `api.elevenlabs.io` to the environment's allowed hosts. Never send the key in chat or commit it. Then read the account's clone identity, model/settings and remaining speech allowance before synthesis. Verify the exact requested clone, use its approved configuration, and stop if additional paid credits are required. No speech-generation request has been made and no credits have been spent.

## Assets and reproducibility

- `lesson.json`: complete narration, scene sequence, exact mathematical objective and unresolved voice configuration.
- `narration.txt`: proposed full spoken script; no generic introduction or slash fraction notation.
- `render.py`: offline Python/Pillow/FFmpeg renderer; no network, HeyGen, speech-generation or upload calls.
- `../../reviews/lcm/MathMagic_LCM_SILENT_GRAPHICS_DRAFT_1080p.mp4`: 80-second **silent** 1080p visual draft. Its timing is illustrative, not actual narration alignment. The watermark states this throughout.
- `test_lcm.py`: exact arithmetic, notation, source-clock event, voice-identity and final-audio gate checks.
- `integration-after-approval.html`: proposed extension player, not inserted into the production lesson.

Draft command, from repository root:

```sh
python video-agent/lcm/render.py --draft --output reviews/lcm/MathMagic_LCM_SILENT_GRAPHICS_DRAFT_1080p.mp4
python -m unittest discover -s video-agent/lcm -p 'test_*.py'
```

Python needs Pillow; FFmpeg/FFprobe and DejaVu Sans fonts must be installed. Do not mistake the draft MP4 or its illustrative scene times for a finished narrated candidate.

## Complete after access is restored

1. Verify clone identity and provider configuration from ElevenLabs. Read allowance/cost eligibility before any synthesis; stop if additional paid credits are needed. Use one continuous narration track, with no pitch/speed changes or inserted silence.
2. Save high-quality original narration and the provider's character timestamps (or independently verified forced alignment). Keep reversible originals. Do not log secrets or expiring URLs.
3. Supply actual ElevenLabs `alignment`/`normalized_alignment` arrays: `characters`, `character_start_times_seconds`, `character_end_times_seconds`. The renderer checks every spoken word against the script and uses actual word anchors for mathematical reveals. Weighted draft timings cannot be used for final rendering.
4. Save verified voice provenance with `provider: ElevenLabs`, `verified_clone_name`, `verified_voice_id`, `approved_voice_id`, `model_id`, `actual_settings`, `approved_settings` and `audio_sha256`. These facts must come from real account/source evidence, not manually invented approval flags. Preserve approved natural speaking configuration.
5. Render with `--audio`, `--alignment`, `--provenance`, and an explicit final `--output`. No stretching, narration truncation, artificial padding or freezes are implemented. Review all boundaries and actual audio; verify output sample timing after any AAC encoding. Inspect mathematical states, readable persistence, complete decode and actual playback. Recheck sound quality and listening alignment; metadata is insufficient.
6. Upload the finished **narrated** review candidate to this review branch, compare downloaded size/SHA-256, then obtain user approval of voice and visuals. Only then insert the extension immediately below the approved Add & Subtract video with the requested heading, captions/transcript and consistent responsive player styling. Keep all other lesson/security/progress code unchanged.

## Present release status

**Blocked before speech generation.** The silent preview supports graphics review only. Human narration approval, actual word-level audiovisual synchronisation, final audio QA, narrated-video playback QA and publication are pending. No completed narrated LCM video is claimed.
