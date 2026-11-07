# Year 5 Space (Geometry) — implementation specification (draft)

Status: development only; not approved for release. Scope: Australian Curriculum v9 Year 5 Space. Curriculum mapping below cross-checked against ACARA Year 5–6 scope and sequence (https://www.australiancurriculum.edu.au/media/7163/primary_scope_and_sequence_years_5-6.pdf); achievement standard and elaboration audit still required.

## Design principles
- Do not impose a five-lesson ceiling. Teach all relevant Year 5 Space outcomes, but avoid importing Year 6-only outcomes.
- Story/problem → learning goal → three success criteria → concrete or manipulable visual → worked solution → prediction → misconception → second example → independent challenge → reflection.
- Every lesson must include accessible, keyboard-usable representations and text alternatives, meaningful formative feedback, and precise geometry vocabulary.
- No video placeholder is represented as published. Any new videos must follow GOLDEN_VIDEO_RULES.md and video-production-contract.json, with separate perceptual QA.
- Preserve existing Firebase authentication, approval check, progress storage, and existing modules. Assessment is 30 unique, seeded questions across six genuine bands of five, with complete worked feedback, no repeated normalised prompts, and explicit coverage mapping.

## Curriculum coverage — required, not optional
- AC9M5SP01: connect 3D objects with nets; construct and reason about valid and invalid nets for prisms/pyramids. Provide interactive folding/unfolding or equivalent geometric net explorer.
- AC9M5SP02: construct first-quadrant coordinate grid; locate points and describe movement using coordinates and directions. Do not conflate grid cells with grid intersection coordinates.
- AC9M5SP03: describe and perform translations, reflections, rotations; explain invariants and identify rotational symmetry. Provide accurate direct-manipulation tool, centre of rotation and mirror geometry.
- AC9M5SP04: computational thinking and branching decision algorithms to classify 2D shapes and 3D objects by properties; test ambiguous and boundary cases.
- Do not require Year 6 four-quadrant Cartesian coordinates, tessellations or advanced conjecture as Year 5 outcomes.

## Revised lesson architecture — ten lessons, subject to detailed elaboration audit
1. Visualising 3D objects and their faces, edges, vertices.
2. Nets of prisms and pyramids: predict, fold, test and explain.
3. Designing and correcting nets for packaging and objects.
4. Building a coordinate grid: zero, horizontal-first ordered pairs and landmarks.
5. Following and constructing coordinate routes with directional language.
6. Translations: drag and measure changes and invariants.
7. Reflections: mirror line, paired points and perpendicular distances.
8. Rotations and rotational symmetry: centres, turns and invariants.
9. Classifying shapes and objects with yes/no branching algorithms and properties.
10. Integrated spatial reasoning challenge: nets, map routes, transformations and classification, with justified solutions.

## Implementation order and concrete deliverables
1. Complete descriptor/elaboration/achievement-standard audit and correct any scope gaps; commit coverage matrix.
2. Implement 10 substantive lessons with story, goal, 3 success criteria, manipulatives, examples, misconception, prediction and reflection; integrate dashboard and auth.
3. Build four independently testable interactive tools: nets folding, coordinate explorer, transformation lab, branching classifier; mouse/touch/keyboard and feedback.
4. Implement 30-question six-band seeded quiz, unique mathematical instances, full worked explanations, robust validation, Firebase-compatible approved-user progress and repeatable oracle tests.
5. Produce graphics-only narrated videos per lesson or justified grouping, each at least five minutes, no visible/spoken branding, Kokoro hf_alpha 31, 1080p, full perceptual QA before publication.
6. Run tests, review PR, merge after green gates, deploy and verify live. Never treat a successful CI or existing MP4 as perceptual playback evidence.

## Assessment coverage matrix — preliminary
Five questions per band, 30 total; cover all four curriculum descriptors, including nets and classification algorithms, with unique mathematical instances and contextual variety:
- Band 1: identify faces/edges/vertices and positions; follow one-step directions.
- Band 2: interpret map/grid conventions, route descriptions and basic nets.
- Band 3: recognise valid nets, perform translations and reflections.
- Band 4: identify rotations, rotational symmetry and properties for classification.
- Band 5: evaluate invalid nets, classification decision paths, transformations and invariant properties.
- Band 6: multi-step net construction, branching classification, navigation and transformation reasoning.

All assessed families must have explicit teaching coverage. Include multiple-choice and constructed responses where appropriate, diagram-based prompts, error analysis, and explanation of why distractors are wrong. Test reflection/rotation edge cases, grid boundaries, coordinate order, degenerate symmetries, accessibility, uniqueness and all 30 answer keys over many random seeds.

## Release gates
1. Verify exact AC v9 descriptors and exclusions.
2. Build lesson pages and reusable accessible visual models.
3. Implement deterministic 30-question generator and independent mathematical oracle tests.
4. Integrate with existing approved-user auth, Firestore progress and dashboard; do not weaken security.
5. Run unit, seed stress, Playwright desktop/mobile, keyboard, progress/reload, CI and exact-head tests.
6. Review PR and merge only when all gates pass. Verify live GitHub Pages separately.

No production status is implied by this planning file.
