# MathMagic — canonical project agent instructions

## Authority, scope and first actions
This is the primary entry point and single canonical general instruction set for `initSrikanth/MathMagic`. It consolidates the former `AGENTS.md` and `MATHMAGIC_AGENT.md`; the latter is now a compatibility pointer. Preserve the existing architecture, branding, curriculum quality, accessibility, security and working functionality. Do not introduce a framework rewrite, unnecessary dependencies, paid services or unrelated changes.

The user's current request defines the scope and overrides repository workflow defaults. A request to build/revise/fix a module normally includes implementation, QA and the permitted PR/merge workflow; investigation or documentation requests do not authorise application changes or historical pending tasks. Complete authorised work end to end without repeated handoffs. Never claim tests, commits, merges, uploads, deployment or production verification without observed evidence.

Before work, inspect the branch, `git status`, repository structure, README, package manifests, workflows, these instructions and any nested `AGENTS.md`. Preserve existing work. Read applicable topic specifications in `docs/` and [video production rules](video-agent/VIDEO_PRODUCTION_RULES.md). Their domain-specific requirements supplement this file; this file explicitly resolves the previous general-policy conflicts. Do not use a topic exception to weaken unrelated security or QA requirements. Source establishes implemented behaviour, not proof that every requirement is satisfied. Record implementation gaps instead of silently treating them as compliant. Recheck production claims independently.

## Current structure and security architecture
- GitHub Pages serves static HTML, CSS and JavaScript. Login is `index.html` plus `js/login.js`; dashboard access is `js/auth-guard.js` (the obsolete `guard.js` reference is replaced). Topic access/progress modules are `js/<topic>-auth.js`; the denial page uses `js/access-required.js`.
- `js/firebase-config.js` identifies the Firebase project. Firebase Authentication uses Google popup sign-in; the Firebase SDK owns session persistence and token refresh. Firestore and callable SDKs carry the Firebase identity. Do not introduce custom token storage, expose service-account keys, private credentials or admin tokens, or treat the public Firebase web API key as an entitlement.
- Access requires a Firebase user and `access/{uid}.approved === true`. Signed-out users go to `index.html`; unapproved users go to `access-required.html`. Access/service validation failures must fail closed. Never add anonymous access, production test bypasses or a client-only substitute for server authorisation.
- Progress belongs at `progress/{uid}/topics/{topic}`; the UID/topic-scoped local-storage mirror is a cache, not an authorisation boundary or authoritative assessment proof. Firestore security rules must protect student-owned progress, prevent students granting their own approval, and deny direct client access to backend `challengeSessions` data. No Firestore rules file is currently tracked, and `firebase.json` configures only Functions: inspect deployed rules when authorised and report them unverified otherwise. Client hiding/redirects do not secure static content or replace database rules.
- Current source uses authenticated browser generators for Fractions, Whole Numbers, Decimals & Percentages, Addition & Subtraction, and Factors & Multiples. Multiplication & Division uses `httpsCallable` in `js/multiplication-division-auth.js` and fails closed without its protected service. Preserve this protected-only behaviour; do not add a client generator fallback or remove its fail-closed tests.
- Backend code is in `functions/index.js` and `functions/factors-multiples.js`, using Firebase Admin SDK runtime credentials. Backend source and static architecture checks do not prove deployment. Callable endpoints specify `enforceAppCheck:true`; no frontend App Check initialisation is currently present. Do not remove enforcement to make calls work. Registration, web-provider initialisation, allowed domains and real integration checks are deployment prerequisites.

### Operational baseline and protected-content target
The Fractions-style browser challenge is an explicit transitional baseline for existing browser topics. It protects user access/progress only; browser-delivered lessons, generators and answers are downloadable. The target for valuable/premium assessment logic remains server-side generation and marking, without unnecessarily publishing generators, answer banks or solutions.

For new modules or migration, use protected generation only through a production-verified site-wide pipeline or a production-verified pilot/deployment path. Until then, do not introduce a topic-specific callable dependency that leaves a deployed browser topic unusable. Preserve the established browser pattern while documenting the deferred migration. Conversely, this transitional exception does not authorise downgrading existing protected-only topics. A migration must pass the rollout gate below before being declared live.

Protected endpoints must require valid Firebase Authentication, verify approval/entitlement server-side before returning protected assessment data, enforce App Check, return only the authorised learner's current safe question/session payload, and retain authoritative answers/marking server-side. Bind sessions to the UID and topic, enforce current-index/completion checks, use bounded sessions and appropriate rate/abuse controls, and reject wrong-owner access. Do not trust client-supplied scores as authoritative evidence. Keep Firestore rules authoritative for progress and backend session isolation. Preserve existing protections even where older endpoints have gaps.

Current code is not uniformly compliant with the target: some submit handlers do not recheck approval, the Fractions submit path lacks a topic check, and session expiry is not uniform (the Factors & Multiples backend has a two-hour check). Treat these as implementation gaps to address in authorised security work, not permission to weaken the target or a claim of full protection.

Before production cutover:
1. Confirm a Firebase plan supporting Functions and expected cost/budget alerts.
2. Register the web app for App Check, initialise its supported provider and verify allowed domains.
3. Deploy and verify the callable endpoints; verify Auth, approval and App Check rejection with real signed-out, unapproved and missing/invalid-App-Check requests.
4. Verify approved-user success, cross-UID session rejection, topic/session validity and direct-client denial of `challengeSessions` reads/writes.
5. Run the complete 30-question protected-adapter flow and real Firestore save/restore checks, including cross-device persistence where claimed.
6. Only then remove legacy client generation/answer logic for a migrating topic. Do not claim backend protection active merely because source or CI exists.

## Curriculum, assessment and progress invariants
Current priority is Year 5 Australian Curriculum v9, with planned Years 1–9 expansion and appropriate IB primary concepts. Verify descriptor codes against authoritative curriculum; keep codes internal. Teach clear concepts and worked strategies, with accurate, unambiguous, age-appropriate questions and feedback. No Year 5 algebra beyond appropriate patterns/missing-number reasoning unless explicitly requested.

The former generic 20-question default is superseded by the current source/topic specifications: the six established topic challenges use **30 questions**, including Fractions, and the standard progression below is six bands of five. Preserve topic-exclusive boundaries and do not import another topic's validation rules. A different future topic count requires an explicit topic specification and corresponding QA; do not silently shorten current quizzes.

Test boundary cases, valid ranges, unique multiple-choice distractors, numeric input, equivalent fractions, mixed-number normalisation and random seeds. Check duplicate normalised prompts and mathematically equivalent duplicates, not just duplicate IDs. Verify question answers and useful worked feedback as well as generator structure; one sampled attempt is insufficient.

Read [Whole Numbers](docs/whole-numbers-current-rules.md), [Decimals & Percentages](docs/protected-decimals-percentages-backend.md), [Addition & Subtraction](docs/addition-subtraction-year5.md), [Multiplication & Division](docs/multiplication-division-year5.md), and [Factors & Multiples](docs/factors-multiples-year5.md) for exact boundaries. In particular: decimals through thousandths; no percentage-of-quantity assessment in this Year 5 Decimals module; no decimal addition/subtraction in Addition & Subtraction; no decimal multiplication/division by natural numbers in Multiplication & Division; no formal prime/composite classification or prime factorisation in Factors & Multiples. Shared-factor/multiple reasoning does not imply a requirement for formal HCF/LCM procedures. Fractions' bracketed expressions remain outside its core assessed scope as recorded in `fractions.html`.

Preserve dashboard states Start, In Progress and Proficient; the minimum-five-attempt practice display; best/last scores; scoped intentional reset; and persistence across sessions/devices. Current topic code awards proficiency on a full 30/30 attempt (or preserves previously earned proficiency); five attempts are a practice target, not an extra prerequisite for that flag. Preserve any explicitly specified additional topic conditions. Check refresh/retry/interruption and duplicate-event handling so attempts are not double-counted.

Fractions must display numerator above a horizontal bar and denominator below in all student-visible pages, feedback, diagrams and video. Mixed numbers need clear whole/fraction separation. Internal slash strings are permitted only when converted before rendering and never leaked into student text. Use semantic MathML or accessible HTML/CSS; verify equivalents, simplification, mixed/improper conversion and comparisons. Do not use raw slash fallbacks.

Preserve responsive desktop/tablet/mobile layouts, branding/navigation and lesson flow. Use semantic elements, keyboard access, visible focus, accessible labels and contrast; avoid clipping, horizontal overflow, small touch targets and layout shifts. Give understandable non-colour feedback as well as the shared green `correct` and red `incorrect` states. Use local assets where suitable without overriding provider copyright constraints.

## Module build contract and detailed quality standards
`MathMagic: Build <topic>` includes curriculum/coverage research, teaching/assessment design, source/mathematical audit, generator stress QA, architecture QA, complete rule audit, Playwright student-flow QA, exact-head CI, correction/retest, final audit and permitted squash merge. Report the tested SHA and merge SHA. A green browser run alone does not authorise release.

## Mandatory workflow
1. Establish the current Australian Curriculum v9 scope and achievement expectations.
2. Research established learning platforms (for example IXL and Education Perfect) and credible resources to identify materially different question forms and representations. This is coverage research only: never copy proprietary questions, wording, graphics or question banks.
3. Create an internal question-coverage matrix before coding.
4. Design the teaching sequence before the challenge.
5. Map every assessed question family to something taught or reasonably developed in the learning pages.
6. Map question families to genuine cognitive-difficulty bands.
7. Implement using existing MathMagic architecture and preserve working authentication/progress features.
8. QA mathematical correctness, generator behaviour, notation, accessibility, responsive visuals, browser behaviour and progress persistence.
9. Use the release workflow below: branch -> PR -> merge for module work; an explicit request to commit documentation to main may use a permitted direct commit. Report exactly what was and was not tested.

## Golden rules
### Australian Curriculum is the authority
Australian Curriculum v9 defines the Year-level scope. Competitor breadth is a coverage benchmark, not permission to assess content outside the intended curriculum.

### Curriculum codes stay internal
Maintain content descriptor codes in planning/QA metadata when useful, but do not show codes such as AC9M5N03 to children. Child-facing pages use natural Year-level language.

### Student-language rule
Everything a child sees must be concise, clear and appropriate for the target Year level. Curriculum terminology may guide development internally, but curriculum administration language, implementation terminology, developer metadata and unnecessary educational jargon stay behind the scenes. Simplify the language, not the mathematical thinking.

### Question-type coverage rule
For every topic, identify all materially different question families used by the curriculum and strong learning platforms. The challenge must sample meaningful breadth, not cosmetic variations of the same calculation. Representations may include symbolic work, visual/area models, strips/bars, number lines, comparison, ordering, construction/input, missing values, reasoning/error analysis and contextual problems when appropriate to the topic.

### Originality rule
Research other platforms to detect coverage gaps only. MathMagic explanations, examples, diagrams, questions, distractors, solutions and feedback must be independently created.

### Representation diversity
A new picture or new numbers do not automatically make a new question type. Measure conceptual variety by distinct skills, representations and reasoning demands.

### Teaching-assessment alignment
Anything materially assessed must be taught, demonstrated or reasonably developed in the learning sequence. Important taught concepts must have an appropriate opportunity to appear in assessment.

### Genuine difficulty progression
Difficulty must rise through cognitive demand, not labels, arbitrary large numbers, excessive reading or tricks. Randomisation occurs within suitable bands and must not move an advanced question into an early band or an elementary question into the final challenge band.

Default 30-question progression:
- Q1-5 Foundation: recognise, interpret, basic representations.
- Q6-10 Developing: straightforward procedures and models.
- Q11-15 Developing+: connect representations, equivalence, comparison and reasoning.
- Q16-20 Proficient: less-scaffolded curriculum operations/strategies.
- Q21-25 Application: choose and apply strategies in contexts.
- Q26-30 Challenge: multi-step, reasoning-rich and less-scaffolded work within Year-level scope.

### No artificial difficulty
Challenge comes from mathematics and reasoning, not obscure wording, unnecessarily awkward numbers or irrelevant literacy load.

### QCAA quality assessment rule
Every assessed question and every random generator must satisfy:
- Validity: assesses the intended taught curriculum knowledge/skill and provides appropriate challenge without construct-irrelevant demands.
- Accessibility: clear concise unambiguous instructions, age-appropriate language, readable layout/visual cues, equitable access and no unnecessary barriers.
- Reliability: one defensible interpretation, correct and stable marking logic, appropriate equivalent answers, and random variants that preserve the intended construct and difficulty.

A mathematically correct item that fails validity, accessibility or reliability must be revised or removed.

### Generator reliability
QA the generator, not one sample. Random variants must remain mathematically correct, unique enough for an attempt, inside curriculum scope, in the intended difficulty band and free from ambiguous/invalid states.

### Notation rule
Use conventional child-friendly mathematical notation. Fractions displayed to students must use stacked numerator/bar/denominator notation, never slash notation such as 3/4. Raw slash strings may exist internally only when immediately converted by the renderer and never exposed to the student.

### Visual integrity
Visual questions must convey the mathematics accurately and remain readable on desktop, tablet and mobile. Models may not collapse, distort the whole, misalign equal parts or provide unintended answer cues.

### Input/browser hygiene
Student answer fields should minimise browser autofill/saved-information interference, preserve appropriate mobile keyboards and have accessible labels.

### Feedback
Wrong answers should receive concise worked feedback that teaches the intended strategy without exposing implementation language. Correct-answer handling must accept mathematically valid equivalents when simplification is not explicitly required.

Student feedback must also use the established MathMagic visual language consistently: correct feedback uses the shared green `correct` state and incorrect feedback uses the shared red `incorrect` state in both lesson practice and challenge questions. Browser QA must verify the feedback state/class and rendered colour for substantial module changes; checking the wording alone is insufficient.

### Release QA
At minimum check: curriculum scope, coverage matrix, teaching-assessment alignment, difficulty-band integrity, mathematical answers, duplicate generation, notation leaks, visual layout, responsive behaviour, accessibility labels/instructions, browser input behaviour, authentication, progress saving/restoring and cache/version changes. Never claim a test was run unless it was actually executed.

### Rule-by-rule post-build compliance audit
After every MathMagic module build or module review/rebuild, perform a post-build compliance audit against the complete current `AGENTS.md` and applicable topic/video specifications. Record every applicable rule individually as PASS or FAIL with brief evidence. Any repository/CI-applicable FAIL blocks merge and must be corrected and retested. Only merge after all repository/CI-applicable rules pass and required automated QA passes on the exact final commit SHA. Report that exact tested SHA. Production-only Firebase deployment, App Check enforcement and real authorised/unauthorised session verification must remain explicitly separate and must never be falsely reported as CI-tested.

### Automated browser QA gate
Every substantial module change must pass automated end-to-end browser QA before production merge. The automated suite must exercise the complete student-facing challenge flow, not merely inspect source code. It must verify navigation, all challenge positions, answer controls, feedback/solutions, critical mathematical representations, responsive layout and the absence of obvious child-facing notation leaks. Failed browser QA blocks release.

Browser automation complements rather than replaces generator QA. Where authentication or external services are deliberately isolated in CI, the test must say so; authentication/progress integration must have separate checks and must never be falsely reported as browser-tested.

### Visual regression and diagnostic evidence
Critical instructional representations and layouts should receive automated visual/dimensional checks at representative desktop and mobile viewports. CI failures must preserve useful diagnostic evidence such as Playwright traces, screenshots and/or HTML reports. A human real-device check remains appropriate for major releases and browser-specific issues, but routine 30-question click-through should be automated. The GitHub browser-QA workflow is a required release check for substantial module changes.


### Original MathMagic explainer rule
For new explainers, the following Scrimba workflow is the default. An explicitly approved MathMagic presenter-video/MP4 replacement follows the approved-media rules below; do not regenerate it through Scrimba merely to satisfy this default.

Original MathMagic explainers are the preferred video resource when a short visual explanation would materially improve a lesson. For substantial topic builds and major revisions, the agent must deliberately decide whether one or more original explainers should be created. Do not default to third-party YouTube simply because a suitable external video exists.

When an original explainer is appropriate:
- create it through the connected Scrimba Explain / Explain Video Generator workflow;
- author the narration, examples, mathematics and diagrams specifically for the MathMagic lesson;
- keep the language suitable for the target Year level and aligned to the Australian Curriculum scope already established for the module;
- use MathMagic-authored examples and visuals only; do not copy third-party scripts, diagrams, transcripts or question wording;
- prefer a concise 2–4 minute explainer focused on one clear concept rather than a long survey;
- include at least one worked example and, where pedagogically useful, a visual model, misconception check or reasoning prompt;
- use mathematical notation suitable for the topic, including properly rendered fractions rather than slash notation in student-facing visuals;
- create the explainer as unlisted unless there is a deliberate reason to publish it publicly;
- use a landscape frame by default for lesson-page embeds unless another frame is clearly better for the concept.

After generation, embed the finished explainer directly in the relevant MathMagic learning page using Scrimba's supported iframe player. The embed must:
- use a `https://scrimba.com/explain/...` URL;
- preserve the complete share URL returned by the Explain generator, including required query/access parameters; never reduce it to the bare guide path unless that bare path has been separately verified as publicly playable;
- lazy-load;
- have an accessible title;
- allow fullscreen;
- be responsive on desktop and mobile;
- include a visible fallback link that opens the original Scrimba explainer;
- preserve the lesson flow rather than replacing the surrounding MathMagic explanation and practice.

Record each original explainer in `docs/explainers/<topic>.md` with its title, guide URL, lesson/page placement, teaching purpose and any regeneration notes. When an original MathMagic explainer exists for a concept, use it in preference to a generic third-party video unless the external resource adds a materially different learning benefit.

Third-party video remains acceptable when an original explainer would add little value, when the connected explainer service is unavailable, or when a specialist external source is pedagogically preferable. In those cases, document the reason and apply the external-resource/copyright rules below.

For CI/browser QA, any module containing a Scrimba explainer must verify the expected `scrimba.com/explain/` iframe, lazy loading, accessible title, fullscreen support, responsive containment and fallback link. Network playback itself is an external-service check and must not be falsely represented as CI-tested.

### External learning resources and copyright rule
Every substantial topic build or revision must research and curate useful external learning resources, including age-appropriate explanatory videos where they materially improve learning. External resources are part of the learning design and release QA, not an optional afterthought.

Use this order of preference:
1. Prefer an original MathMagic explainer when a short custom visual explanation would materially improve the lesson.
2. Otherwise link to the original authoritative or creator-hosted resource. Linking is the default because MathMagic does not make or host a copy.
3. Embed only when the provider explicitly supplies/supports embedding and the embed complies with the provider's current terms and child-directed/privacy requirements.
4. Attribute the creator/provider clearly and provide a direct fallback link when embedding.
5. Never download, screen-record, re-upload, mirror or redistribute third-party videos, worksheets, question banks, transcripts, graphics or other copyright material unless MathMagic has an explicit licence or the material is clearly licensed for that reuse.
6. Never copy competitor questions or proprietary learning content into MathMagic. External resources supplement MathMagic's independently created teaching and assessment.
7. Do not rely on school-only educational copyright exceptions for a public or commercial MathMagic release. If reuse rights are unclear, link rather than copy; if linking/embedding rights are unclear, omit the resource pending permission.
8. For child-facing video embeds, use privacy-enhanced/provider-supported settings where available and comply with any child-directed-site designation requirements.
9. Copyright and child-directed/privacy configuration are separate checks. An official provider-supported embed streams the provider's copy and must not be described as MathMagic copying or re-hosting the video. Site-wide child-directed platform designation is tracked and verified as production configuration; do not remove an otherwise approved embed from one topic while leaving the same established provider pattern across other MathMagic topics without a site-wide decision.
10. Release QA must check that external links still resolve, point to the intended resource, are age-appropriate, do not unexpectedly require payment/login, and have not been replaced by unsuitable content. Broken or unsuitable resources must be replaced or removed.

Researching resources is mandatory; including a particular third-party resource is not. Only resources that materially support the topic and pass the copyright, child-safety, relevance and quality checks should appear on the student site.

### Embedded learning resource requirement
Every substantial MathMagic topic build or full revision must include a deliberate external-resource pass before release. Where a suitable provider-supported educational video materially reinforces the taught concept, embed it in the relevant learning page using the provider's official mechanism. For YouTube, use the official privacy-enhanced `youtube-nocookie.com` player, lazy loading, an accessible title, fullscreen support, visible creator/provider attribution and a direct original-source fallback link. Do not autoplay.

Do not add videos simply to satisfy a quota. One high-quality resource may support more than one closely related concept; conversely, a topic may need several resources. The release decision is based on pedagogical relevance, age suitability, source quality, embedding permission, privacy/copyright compliance and page usability.

A substantial module revision is incomplete until the resource pass has been performed and the chosen resources have been implemented or the development record explicitly explains why no suitable embeddable resource should be used.

Automated browser QA for modules with embeds must verify that expected embedded-resource elements exist, use approved provider domains, have accessible titles and expose working original-source fallback links. Network playback itself may depend on the third-party provider and is not equivalent to verifying the educational content of the video.

## Specialised video production workflow

For authorised MathMagic presenter-video work, read [Video Production Agent](agents/VIDEO_PRODUCTION.md) and the [integration readiness report](docs/video-production-readiness.md). These supplement this canonical instruction set; they are not another master agent. An audit does not authorise paid rendering or lesson publication.

## Approved presenter videos and media replacement
The preference for original explainers and the Scrimba workflow above applies to new concept explainers. Existing or explicitly approved MathMagic presenter videos follow this production/replacement path. Self-host an owned/licensed approved MP4 where appropriate; this is not permission to copy third-party media or replace working embeds merely to standardise format. Preserve suitable provider embeds until the replacement is rendered, checked, uploaded and verified. Publish one lesson at a time and leave unrelated lessons, authentication and progress unchanged.

Follow `video-agent/VIDEO_PRODUCTION_RULES.md`: mathematics is the focus; keep the approved full-body, unframed teacher on the left and graphics on the right, with feet visible. Reuse approved HeyGen footage and voice without unnecessary generation/credits. Preserve approved appearance, height, position, colours, face and voice; a future newly authorised presenter prompt may request modest expression and subtle natural movement, not alter already approved footage. Draw equations, horizontal fraction bars and number lines programmatically, not with HeyGen. Keep reversible source footage and scene-generation code.

Use the correct lesson scene definitions. Check equal-size wholes, mathematical comparisons/equivalences and legibility on mobile. Every spoken mathematical change needs an appropriate visual scene; avoid frozen equations, distracting animation and sub-second flashes. Inspect actual audio, start, scene boundaries and ending; do not claim word-level synchronisation from estimated timestamps. Keep narration clear and slightly slower when requested. Avoid prohibited generic intros; trim existing audio only without damaging the explanation.

Export MP4 with H.264 yuv420p and AAC for mobile Safari. Verify actual bytes, dimensions, duration, audio streams, representative frames and browser playback. Embed responsive HTML5 `<video controls playsinline preload="metadata">` with a `video/mp4` source, descriptive heading/accessible name and fallback link/text. Add captions/transcripts when available without fabrication. Use case-correct repository-relative paths for local assets, and verify the published URL and playback separately from a successful commit/workflow. Confirm the actual MP4 is on the target branch and referenced by the player before reporting publication.

### Historical Mixed Numbers replacement record
The former unconditional pending task is retained as a conditional media requirement, not an instruction to start a video task during unrelated work. If the user requests that publication, use the exact approved `MathMagic_Mixed_Numbers_CAREFULLY_TIMED.mp4` unchanged, never an older intermediate or regenerated substitute. Inspect `fractions.html` section `#mixed`; publish to `videos/MathMagic_Mixed_Numbers_FINAL.mp4`, ensuring Git tracking and no ignore/LFS blockage, and replace only that section's Scrimba player after the replacement is verified. Preserve surrounding teaching/style. Test local and deployed playback; report SHA and live URL, accounting for cache propagation. If the exact approved file is unavailable, request it once within that media task and keep the working embed. No approval of a video is inferred afresh from this historical record.

## Checks, audit and release workflow
Use existing checks without weakening assertions, deleting coverage, adding production auth bypasses or treating missing production access as a pass. `package.json` defines `npm run test:protected` and `npm run test:e2e`; there are no standalone lint/build scripts currently. The protected command covers architecture checks, deterministic generator stress tests and external-video/explainer audits. If it stops at a failure, run remaining independent checks separately and report each outcome. Stress accessible generators with a target of 10,000–20,000 or more positions and report actual sample counts, invalid/duplicate counts and failures only where measured; mathematical review remains necessary.

Playwright configuration covers desktop Chromium and Pixel 7 mobile Chromium with a local Python server. Tests deliberately abort Firebase auth modules and/or inject adapters to isolate UI flow: they do not establish real auth, Firestore rules, progress integration, App Check or provider playback. Preserve this explicit test-only isolation. Run all applicable generator, architecture, notation, browser/layout and media checks for the change. For substantial module work, a complete rule-by-rule PASS/FAIL audit and passing exact-final-head browser/CI gate are mandatory; repository/CI-applicable failures block module release. Real-device checks remain appropriate for major/browser-specific releases.

Documentation-only work uses a scoped audit: verify paths/links, instruction coverage and consistency, no secrets or unrelated changes, and applicable existing checks. Record unrelated baseline failures and environment blockers separately; they do not authorise application/test changes in a documentation-only task or permit a claim that the application passed release QA. This scoped treatment does not relax the module release gates above. A documentation change with its own unresolved contradiction or weakened security/QA rule must be corrected before completion.

The browser-QA workflow `.github/workflows/browser-qa.yml` runs on PRs to main or manual dispatch, using Node 20, the protected checks, Playwright Chromium and retained diagnostics. A direct main commit does not automatically trigger that workflow. Inspect actual branch protection/rules and checks; do not infer CI or deployment from a commit. Default module workflow is branch -> PR -> required checks on the exact final SHA -> squash merge when authorised and permitted. An explicit request for a main commit, especially scoped documentation work, may use a direct commit if branch rules allow. Never bypass protection, force-push, rewrite history or remove user work.

Before release, inspect the final diff for unrelated changes, secrets, broken links, notation leaks and accidental global styling. Fix introduced issues and retest. Keep existing failures distinct from regressions; do not claim every rule passed unless individually checked. Report exact changed paths/behaviour; checks passed, failed and not run; tested SHA and commit/merge SHA/branch or PR; deployment URL/status separately; and unresolved conflicts/blockers. Preserve functioning sign-in/approval, cross-device progress, asset paths, video playback and cache/version handling; previously reported bugs are regression risks, not proof of verification.

For the consolidation decisions and separately recorded baseline failures, see [instruction consolidation review](docs/agent-instructions-review.md). This is evidence, not a second instruction authority.
