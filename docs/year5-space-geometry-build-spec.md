# Year 5 Space (Geometry) — implementation specification (draft)

Status: development only; not approved for release. Scope: Australian Curriculum v9 Year 5 Space; verify descriptor wording and achievement-standard alignment against the authoritative ACARA site before marking complete.

## Design principles
- Do not impose a five-lesson ceiling. Teach all relevant Year 5 Space outcomes, but avoid importing Year 6-only outcomes.
- Story/problem → learning goal → three success criteria → concrete or manipulable visual → worked solution → prediction → misconception → second example → independent challenge → reflection.
- Every lesson must include accessible, keyboard-usable representations and text alternatives, meaningful formative feedback, and precise geometry vocabulary.
- No video placeholder is represented as published. Any new videos must follow GOLDEN_VIDEO_RULES.md and video-production-contract.json, with separate perceptual QA.
- Preserve existing Firebase authentication, approval check, progress storage, and existing modules. Assessment is 30 unique, seeded questions across six genuine bands of five, with complete worked feedback, no repeated normalised prompts, and explicit coverage mapping.

## Proposed lesson architecture (subject to curriculum audit)
1. **Spatial language and location:** describe position and directions in maps and plans; interpret landmarks and relative positions.
2. **Grid maps and coordinates:** read and describe positions using the coordinate conventions required by Year 5; distinguish row/column or horizontal/vertical ordering.
3. **Transformations — translation:** slide figures on a grid while retaining size, orientation and shape.
4. **Transformations — reflection:** identify and construct mirror images and their equal perpendicular distances from a mirror line.
5. **Transformations — rotation:** describe quarter-, half- and full-turns around a point; distinguish rotation from reflection.
6. **Symmetry and pattern:** identify and justify line symmetry; build patterns from transformations.
7. **Visualise and reason:** solve multi-step map/shape puzzles and explain invariant properties.
8. **Design challenge:** create a park/map or geometric motif using transformations; justify choices and test a peer's directions.

## Assessment coverage matrix — preliminary
Five questions per band, 30 total; distribute families across bands with unique mathematical instances and contextual variety:
- Band 1: locate and describe positions; follow one-step directions.
- Band 2: interpret map/grid conventions and route descriptions.
- Band 3: recognise and perform translations and reflections.
- Band 4: identify and describe rotations and symmetry.
- Band 5: compare composed transformations, detect misconceptions and explain invariant properties.
- Band 6: multi-step authentic spatial design, navigation and reasoning problems.

All assessed families must have explicit teaching coverage. Include multiple-choice and constructed responses where appropriate, diagram-based prompts, error analysis, and explanation of why distractors are wrong. Test reflection/rotation edge cases, grid boundaries, coordinate order, degenerate symmetries, accessibility, uniqueness and all 30 answer keys over many random seeds.

## Release gates
1. Verify exact AC v9 descriptors and exclusions.
2. Build lesson pages and reusable accessible visual models.
3. Implement deterministic 30-question generator and independent mathematical oracle tests.
4. Integrate with existing approved-user auth, Firestore progress and dashboard; do not weaken security.
5. Run unit, seed stress, Playwright desktop/mobile, keyboard, progress/reload, CI and exact-head tests.
6. Review PR and merge only when all gates pass. Verify live GitHub Pages separately.

No production status is implied by this planning file.
