# MathMagic Agent Development Standard

## Purpose
This file is the default operating specification for building, revising, fixing or redesigning MathMagic learning modules. A request to build/revise/fix/update MathMagic authorises the full workflow through implementation, QA, pull request and merge unless the user explicitly asks for investigation/design only.

## Mandatory workflow
1. Establish the current Australian Curriculum v9 scope and achievement expectations.
2. Research established learning platforms (for example IXL and Education Perfect) and credible resources to identify materially different question forms and representations. This is coverage research only: never copy proprietary questions, wording, graphics or question banks.
3. Create an internal question-coverage matrix before coding.
4. Design the teaching sequence before the challenge.
5. Map every assessed question family to something taught or reasonably developed in the learning pages.
6. Map question families to genuine cognitive-difficulty bands.
7. Implement using existing MathMagic architecture and preserve working authentication/progress features.
8. QA mathematical correctness, generator behaviour, notation, accessibility, responsive visuals, browser behaviour and progress persistence.
9. Branch -> PR -> merge after checks pass. Report exactly what was and was not tested.

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

### Release QA
At minimum check: curriculum scope, coverage matrix, teaching-assessment alignment, difficulty-band integrity, mathematical answers, duplicate generation, notation leaks, visual layout, responsive behaviour, accessibility labels/instructions, browser input behaviour, authentication, progress saving/restoring and cache/version changes. Never claim a test was run unless it was actually executed.


### Automated browser QA gate
Every substantial module change must pass automated end-to-end browser QA before production merge. The automated suite must exercise the complete student-facing challenge flow, not merely inspect source code. It must verify navigation, all challenge positions, answer controls, feedback/solutions, critical mathematical representations, responsive layout and the absence of obvious child-facing notation leaks. Failed browser QA blocks release.

Browser automation complements rather than replaces generator QA. Where authentication or external services are deliberately isolated in CI, the test must say so; authentication/progress integration must have separate checks and must never be falsely reported as browser-tested.

### Visual regression and diagnostic evidence
Critical instructional representations and layouts should receive automated visual/dimensional checks at representative desktop and mobile viewports. CI failures must preserve useful diagnostic evidence such as Playwright traces, screenshots and/or HTML reports. A human real-device check remains appropriate for major releases and browser-specific issues, but routine 30-question click-through should be automated. The GitHub browser-QA workflow is a required release check for substantial module changes.


### External learning resources and copyright rule
Every substantial topic build or revision must research and curate useful external learning resources, including age-appropriate explanatory videos where they materially improve learning. External resources are part of the learning design and release QA, not an optional afterthought.

Use this order of preference:
1. Link to the original authoritative or creator-hosted resource. Linking is the default because MathMagic does not make or host a copy.
2. Embed only when the provider explicitly supplies/supports embedding and the embed complies with the provider's current terms and child-directed/privacy requirements.
3. Attribute the creator/provider clearly and provide a direct fallback link when embedding.
4. Never download, screen-record, re-upload, mirror or redistribute third-party videos, worksheets, question banks, transcripts, graphics or other copyright material unless MathMagic has an explicit licence or the material is clearly licensed for that reuse.
5. Never copy competitor questions or proprietary learning content into MathMagic. External resources supplement MathMagic's independently created teaching and assessment.
6. Do not rely on school-only educational copyright exceptions for a public or commercial MathMagic release. If reuse rights are unclear, link rather than copy; if linking/embedding rights are unclear, omit the resource pending permission.
7. For child-facing video embeds, use privacy-enhanced/provider-supported settings where available and comply with any child-directed-site designation requirements.
8. Release QA must check that external links still resolve, point to the intended resource, are age-appropriate, do not unexpectedly require payment/login, and have not been replaced by unsuitable content. Broken or unsuitable resources must be replaced or removed.

Researching resources is mandatory; including a particular third-party resource is not. Only resources that materially support the topic and pass the copyright, child-safety, relevance and quality checks should appear on the student site.
