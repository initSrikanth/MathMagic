# Measurement voice and animation calibration — review candidate

Not approved production media. No published videos, lessons or production defaults changed. No next topic started.

## Candidate and licence

Kokoro v1.0 multilingual ONNX, 82M parameters; built-in `hf_alpha` female Hindi voice, speaker 31, English phonemization. This is an experimental cross-language candidate, **not a verified Indian-English voice**. No reference recording, real-person imitation or voice cloning was used. Bundled model licence: Apache-2.0, retained in MODEL-LICENSE.txt. Model source is the k2-fsa/sherpa-onnx tts-models release; source.json records the downloaded asset. Speaker mapping: https://github.com/k2-fsa/sherpa-onnx/blob/master/scripts/kokoro/v1.0/generate_voices_bin.py

## Runtime and output

Three x86-64 CPU cores, about 9 GB free RAM; no NVIDIA GPU detected. Existing sherpa-onnx, NumPy, SoundFile, SciPy, Pillow and FFmpeg suffice; no new Python dependencies installed. The 350 MB archive expands to the ONNX model, voice embeddings and language resources. Download/setup time is separate from timings below. Models are cached outside the repository.

40.403 seconds, 960x540 H.264/yuv420p 25fps, AAC. First synthesis: 21.89 seconds; preview render: 5.26 seconds. Six coherent utterances concatenated at native sample boundaries, no inserted silence or audio pitch/speed postprocessing. Native synthesis speeds 0.94–1.00 vary modestly by teaching purpose. This engine has no demonstrated reliable emotion/emphasis control in this workflow; punctuation/context and native voice prosody are being evaluated.

## Teaching and timing evidence

Ruler model is reused from production-v2/measurement_graphics.py. Hook, goal, guided prediction, progressive tracing, worked subtraction, misconception correction and recap are present. Students receive about 7 seconds of spoken prediction guidance, not an added silent gap. Trace progresses over 5.08 seconds. Subtraction symbols appear at independently recognised words. Fifteen caption cues use recorded audio and recognised sentence starts; transcript preserves actual synthesis input. Word timings are ASR token emissions and approximate, not certified forced alignment.

Independent offline Zipformer ASR raw word error rate: 8/106 (7.55%); differences include spelling/tokenisation and possible pronunciation/recognition errors. No claim of perfect pronunciation is made. ASR and pitch metrics cannot certify accent, warmth, naturalness or enthusiasm. A listening review is required before adopting the voice or producing replacements.

QA: all 1,010 decoded frames nonblank; complete decode, audio present, zero source clipping samples, AAC/source correlation 0.99998; mathematical 9−2=7 and reveal order checked. Chromium desktop/phone playback, seeking, captions, ending and responsive containment passed. Physical Safari/iOS and subjective lip-sync do not apply or were not tested (no presenter).

## Reproduction

Use synthesise.py, align.py, render.py and qa.py with the existing local Python dependencies. Their assets resolve beside these scripts. Download and unpack the model named in source.json and the sherpa-onnx-zipformer-small-en-2023-06-26 ASR release into this directory (large model binaries are deliberately not committed). Set MATHMAGIC_REPO to the MathMagic checkout for render.py. Cached utterance WAVs avoid repeated synthesis; narration.wav is the delivered exact source. Do not change global production defaults or rerender the published five videos until the candidate voice/teaching approach is approved.
