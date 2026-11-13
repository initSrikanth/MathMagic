# Versioned media registry

`registry.json` is the canonical topic index referenced by `video-production-contract.json`. Version1 currently declares nine topics and105 media variants:104 preserved variants plus one pending replacement. Historical approval records are preserved; `retained` does not grant a new quality approval. All original media, source checksums, rollback assets and the35-record audit remain unchanged.

Each topic has a separate JSON manifest, an explicit inventory of global record IDs, and page/section placements. Registration checks the exact record set against that inventory, rejects duplicate IDs/paths and missing files, verifies hashes and encoded packets, and checks actual HTML players and their caption tracks. Both `<source>` and direct `<video src>` are inspected. New player pages and changed video files cannot evade registration by moving outside `videos/` or using another media extension.

## Register a topic or revision

1. Preserve every existing record and asset. Add a topic manifest under `topics/`, with `schema_version:1`, a unique topic ID, and records. Add the topic/page, complete inventory, empty `legacy_numbers` and manifest file descriptor to `registry.json`. Existing topics add records to their inventory. No Python count or topic whitelist changes are needed. `legacy_numbers` is only the adapter to the immutable historical audit.
2. Use unique global record IDs and unique video paths. A changed media/script/caption asset needs a new revision ID; a replacement references its exact preserved original in `replaces`. Keep rollback originals registered. Do not turn a new asset into `unchanged` or change preservation anchors.
3. Record each asset's repository-relative path, SHA-256 and byte length. Record ordered per-packet fingerprints/counts for both audio and video with `tools/video-quality/registry.py:packet_fingerprint`. Asset and topic-manifest hashes must match actual bytes. Unsafe paths, symlink escapes and duplicate JSON keys fail closed.
4. For replacement/new records, declare `status:pending` and `human_approval:{"status":"pending"}`. Supply the video, captions, transcript, poster, proposed script, actual-word alignment and producer provenance. Verification may be incomplete while pending. Run `python tools/video-quality/registry.py` to validate registration. This command cannot approve or release anything.
5. Produce a separate verification artifact using the `verification` schema: bind every subject asset hash, identify an independent verifier and its source hash, record all mandatory checks, real audio metrics and every unresolved flag. The verifier must differ from the producer. Keep earlier evidence unchanged when appending a new receipt; known flags cannot disappear. A pending review may add a new verification artifact without changing media/script/caption bytes.
6. Only after actual explicit human approval, record the real reviewer, date and HTTPS evidence reference; exact hashes of every asset (including verification); and affirmative full-audio, full-video, script and flagged-interval review. This is manual attestation, never a generated consequence of tests. Set record/review status to `approved` only with that genuine evidence. CI checks completeness/binding; it cannot authenticate a person's identity or certify that they actually listened. PR review must verify the referenced human record.
7. Run registry/schema/contract and relevant topic/media/curriculum tests. The canonical release gate remains `python tools/video-quality/ci_check.py BASE_SHA`. It validates registrations and the historical gates, then refuses active or newly introduced pending media. A pending artifact registered on a PR is not approved publication.

## Three policies

| Policy | Required protection |
|---|---|
| `unchanged` / `retained` | Only explicitly declared preservation-baseline IDs. Exact baseline bytes and ordered encoded video/audio packet hashes/counts; immutable record bindings. Existing contract/Space approval gates still apply. This preserves prior status rather than declaring full-quality approval. |
| `replacement` | Preserved original in the same topic; complete independent integrity report; actual script/alignment/caption consistency, approved Kokoro configuration, branding/graphics/native-speech/maths checks; explicit hash-bound human approval. AAC re-encoding may be verified independently; it is never represented as original packet identity. Newly approved bytes are actually decoded again by the guard, with faststart/RMS/clipping checks. |
| `new` | All replacement quality/evidence/human requirements, plus the existing new-media production/release hold must be explicitly lifted. Registration itself grants no generation or publication authority. |

The pre-existing full-release voice calibration approval gate also remains: the canonical `enhanced_enthusiasm_approval` is currently absent. Historical scoped/Space approvals retain their original exceptions; a new registry approval cannot silently waive this policy.

Approval cannot be inferred from `status`, a checksum, a voice identifier, ASR/OCR or a successful workflow. Unapproved replacements and incomplete/UNVERIFIED evidence fail. Human approval is bound to the exact script, video, captions, transcript, poster, alignment, producer and verification hashes. Changed script/caption text or caption timing cannot inherit a prior approval. The human full review must cover the actual mathematical graphics, speech, branding, pacing and mobile readability.

## Version and migration safety

`schema.json` uses JSON Schema Draft2020-12. The dependency-free runtime implements every keyword used here and rejects unknown keywords. Independent Draft2020-12 validation was also run during migration. Unknown versions/fields fail. The schema hash, preservation commit and preserved record-set digest are pinned in the canonical policy. A deliberate schema-version/trust-anchor migration needs a reviewed code/policy change; ordinary topic additions need only data.

The CI workflow explicitly fetches the pinned preservation commit, so shallow PR checkouts have the baseline objects required for byte validation. Local verification likewise needs that commit in Git.

The preservation anchor is commit `62c595d50696e393959ed34a77794137f7139fa0`. The initial inventories include the35 historical originals,32 scoped corrections,20 narration variants, the LCM extension, ten Space videos, six original/archive Time & Angles files and the pending Lesson1 candidate. The canonical policy pins all104 retained record bindings, and their actual files must match the anchor. Future PR-base comparison forbids deleting topics/records, changing preserved assets/approvals, silently dropping players, or rewriting prior evidence. Previously approved, byte-identical records can reuse their bound verification without repeat full decoding; their checksums/packets are still rechecked.

The Space exception and `assert_owner_approved_space_release` verifier remain intact, including their exact owner attestation, voice, caption, player and byte checks. They are not removed in this migration. Space is also covered by registry packet/baseline checks. No new owner approval, perceptual pass, physical iOS pass, merge or deployment is recorded.

## Time & Angles Lesson1

`time-angles-lesson1-repaired` is a **pending replacement** of `time-angles-lesson1-original`. Its committed MP4 checksum remains `3f6501d5fe8cfedff8cb266fe3b464c027bc19fece62c832aa75c0686610b0e1`. The proposed script uses the exact retained recording wording, including “By the end” rather than the saved renderer's “By the end of this lesson”. Its Kokoro profile metadata is preserved; no synthesis or regenerated video is involved.

Technical evidence is retained and independently rechecked. Script/audio perceptual alignment and caption fidelity remain UNVERIFIED; ten caption and twenty static-model flags remain open. No human approval is populated. The registry passes registration; the release guard must exit nonzero with `time-angles-lesson1-repaired: PENDING_HUMAN_APPROVAL`. It must not revert to an unknown-file error, approve it automatically, or relax unrelated protections.
