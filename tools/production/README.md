# Measurement production pilot

A read-only, resumable verification workflow around existing MathMagic tools. It does not render, replace media, modify Firebase, merge, schedule production or deploy. Canonical instructions and video Golden Rules remain authoritative. First pilot: **Measuring Our World**, five existing owner-approved videos and M01/M02. Inventory also audits the five Time and Angles placements; its missing captions/transcripts remain explicitly blocked, not included in the pilot's PASS.

## One local command

With the repository's locked Node dependencies, Python requirements, FFmpeg/FFprobe, Chromium/WebKit, Java and isolated Firebase emulator installed:

```sh
python tools/production/pilot.py run --resume
python tools/production/pilot.py report --require-ready
```

Use `--stages curriculum mathematics` (or another stage list) for targeted work. `--work-dir` relocates checkpoints. No synthesis/model download is needed. Browser tests use the existing Playwright server/config; `PILOT_PLAYWRIGHT_CONFIG` permits an explicit local runtime configuration. Node/Python versions and the browser configuration are recorded; CI pins Node22/Python3.12 and installs actual H.264/AAC-capable Chrome and WebKit.

The report command exits **2** until every automated gate and required external review passes. A green automated workflow is **not** full release approval. Never fabricate the missing human/service evidence.

## GitHub Actions

`measurement-production-pilot.yml` runs on relevant PRs, manual dispatch or `workflow_call`. It coordinates source/curriculum/maths/media → emulator/browser/WCAG → production-byte verification → readiness report. Run the existing required Browser QA alongside this pilot before merge. There is no write token or publishing step.

Use GitHub **Re-run failed jobs**, not “Re-run all jobs”, after a transient infrastructure problem. Successful job artifacts remain intact. Receipt artifacts overwrite only that job's previous attempt; browser diagnostics are retained. Caches contain locked npm/pip dependencies, pinned browser bundles and emulator binaries, never release approvals or cached PASS results. Legacy rendering workflows are frozen and cannot automatically overwrite main.

## Checkpoint safety

Results and logs live under ignored `work/production-pilot/<profile>/`. A receipt is written as RUNNING before execution, then atomically changed to PASS/FAIL. Local resume requires matching source/rule/profile hashes, matching runtime and an intact evidence log. Changed or missing inputs invalidate the gate. Two unchanged failures stop blind local retries. A file lock prevents duplicate local execution. CI always executes gates fresh; its consolidated report rejects receipts from another run/commit. Native job retries provide CI resumption without trusting local caches.

## Evidence boundaries

- Curriculum mappings cite AC v9 records and actual lesson/assessment paths. Structural checks do not certify semantic teaching quality or practical student performance.
- Existing Python/SymPy validates 30,000 Measurement positions; a new independent prompt/diagram oracle checks 30,000 Time and Angles positions. Neither imports the client's answer-validation function.
- Media SHA-256, sidecar hashes, current FFprobe metadata and the existing canonical scoped-release guard bind reused full-decode/audio/frame evidence to unchanged files. No new decode/listening claim is inferred from an old record. New/changed media needs the canonical production/review process.
- Browser and axe-core WCAG2/2.1 AA checks cover all five lessons and the challenge. Chrome desktop/mobile emulation and Linux WebKit are distinct from physical Safari/iOS. UI auth isolation remains test-only.
- Emulator tests use `demo-mathmagic-year5` and test rules, never deployed rules. Live Google sign-in, real persistence and student-data isolation remain external gates.
- On PRs, deployment verification compares the **production base commit** with actual public bytes. It lists candidate files that are not yet deployed and does not require an unpublished PR to be live. Manual/non-PR runs compare working-tree topic assets. This workflow performs no deployment.

Mandatory external evidence goes in the profile's `manual_evidence` path, only after actual verification: reviewer, date, evidence URL and PASS per required check; complete listening/viewing additionally requires the exact five-video SHA-256 map. Live Firebase/rules checks bind `input_sha256` to the progress gate; physical Safari/iOS binds it to the browser gate, so a changed adapter/page cannot inherit an unrelated old approval. The report remains BLOCKED when any required evidence is absent, stale or when candidate site files remain unpublished. The file's absence is intentional until evidence exists.

## Reuse

A future verification profile declares its lesson count, existing release manifest, curriculum mappings, bounded inputs, existing test commands and public assets. Canonical rules are read directly, not duplicated. Extend approved scoped media handlers only with actual release evidence; never create an exception merely to turn a failing gate green.

## Current confirmed gaps

Time and Angles has five existing 1080p MP4s (505.2,347.8,339.1,334.4,348.1seconds) and five teaching pages, but none of its players has captions or a transcript. Renderers write utterance cue JSON into temporary production output, while the old workflows retained only MP4s. Recover trustworthy cue/audio-alignment evidence before generating caption sidecars; scripts alone do not prove actual speech timing. Existing scripts also need actual audiovisual review of their 0.6-second initial reveals and static holds. Preserve the MP4s; this pilot does not falsely certify their pedagogy.
