# Year 5 v9 curriculum coverage

Baseline: `9420db7`, checked 4 November 2026. The six existing topics/30 videos are preserved. Labels assess instructional evidence, not live Firebase certification or student mastery. No Year 6 files are in scope.

Authority: [QCAA v9 Year 5 alignment](https://www.qcaa.qld.edu.au/downloads/aciqv9/mathematics/curriculum/ac9_maths_yr5_as_cd_alignment.pdf) and [QCAA curriculum plan](https://www.qcaa.qld.edu.au/downloads/aciqv9/mathematics/planning/ac9_maths_yr5_cap_example.pdf). Short focus labels below are paraphrases, not official wording. The older alignment PDF misprints N10 as N010; [QCAA's sequence](https://www.qcaa.qld.edu.au/downloads/aciqv9/mathematics/curriculum/ac9_maths_prep-yr10_as_cd_sequence_aspects.pdf) confirms AC9M5N10.

| Code | Focus | Baseline | Lesson/evidence | Remaining |
|---|---|---|---|---|
| AC9M5N01 | Decimal position | Covered | decimals-percentages.html#place; #compare; whole-numbers.html#lesson5 | — |
| AC9M5N02 | Factors and multiples | Covered | factors-multiples.html#lesson1–#lesson4 | — |
| AC9M5N03 | Fraction ordering | Covered | fractions.html#meaning; #mixed | — |
| AC9M5N04 | Percent connections | Covered | decimals-percentages.html#percent; #connect; #apply | — |
| AC9M5N05 | Fraction operations | Covered | fractions.html#addsub; #problems | — |
| AC9M5N06 | Whole-number products | Covered | multiplication-division.html#lesson1; #lesson2 | — |
| AC9M5N07 | Division and remainders | Covered | multiplication-division.html#lesson3; #lesson4 | — |
| AC9M5N08 | Estimation checks | Covered | addition-subtraction.html#lesson3; multiplication-division.html#lesson5 | — |
| AC9M5N09 | Practical modelling | Partial | addition-subtraction.html#lesson5; multiplication-division.html#lesson5 | Provided problems dominate; learner formulation and comparison of models need explicit evidence. |
| AC9M5N10 | Learner-created algorithms | Partial | factors-multiples.html#lesson4 | Execution and a digital divisibility explorer exist; learner-authored branching algorithms and testing need evidence. |
| AC9M5A01 | Inverse fact families | Covered | multiplication-division.html#lesson3; #lesson5 | — |
| AC9M5A02 | Unknown values | Covered | multiplication-division.html#lesson5 | — |
| AC9M5M01 | Metric measurement | Covered | measurement.html#lesson1–#lesson2; exact Python/SymPy assessment oracle; released media manifest. | Perceptual/live-service checks are separate. |
| AC9M5M02 | Perimeter and area | Covered | measurement.html#lesson3–#lesson5; exact Python/SymPy geometry; released media manifest. | Perceptual/live-service checks are separate. |
| AC9M5M03 | 12/24-hour time | Partial | time-angles.html#lesson1–#lesson2; 13-family independent assessment oracle. | Five Time and Angles videos lack captions/transcripts; audiovisual review unverified. |
| AC9M5M04 | Angles | Partial | time-angles.html#lesson3–#lesson5; draggable construction tool and protractor diagrams. | Video accessibility/review blockers; core quiz kinds2/3 use Year6 AC9M6M04 relationships without extension labels. |
| AC9M5SP01 | Objects and nets | Missing | No dedicated lesson/assessment implementation in baseline 9420db7. | — |
| AC9M5SP02 | Grid coordinates | Missing | No dedicated lesson/assessment implementation in baseline 9420db7. | — |
| AC9M5SP03 | Transformations and symmetry | Missing | No dedicated lesson/assessment implementation in baseline 9420db7. | — |
| AC9M5ST01 | Data and distributions | Missing | No dedicated lesson/assessment implementation in baseline 9420db7. | — |
| AC9M5ST02 | Line graphs | Missing | No dedicated lesson/assessment implementation in baseline 9420db7. | — |
| AC9M5ST03 | Statistical investigations | Missing | No dedicated lesson/assessment implementation in baseline 9420db7. | — |
| AC9M5P01 | Chance outcomes | Missing | No dedicated lesson/assessment implementation in baseline 9420db7. | — |
| AC9M5P02 | Repeated experiments | Missing | No dedicated lesson/assessment implementation in baseline 9420db7. | — |

Baseline result: **10 covered, 2 partial, 12 missing** across 24 descriptions. Source evidence includes lesson HTML/JS, corresponding generator tests and the six verified five-video release manifests. Number/Algebra pages were inspected by section/topic; unrelated videos were not regenerated. Practical measurements/investigations still require students to do and discuss the activities, not just complete a quiz.

## Coherent completion sequence

1. **Measuring Our World — M01–M02:** length/instruments; mass/capacity; perimeter; unit-square area; irregular designs. This release only.
2. **Time and Angles — M03–M04:** time representations; timetable conversions; angle estimates/names; protractor measurement; construction/design.
3. **Space and Shape — SP01–SP03:** nets/building; net reasoning; coordinate maps; transformations; symmetry/design.
4. **Data Detectives — ST01–ST03:** question/types; collection/validation; displays/mode; line graphs; investigation/reporting.
5. **Chance Investigators — P01–P02:** outcomes; fairness; likelihood; repeated trials; comparison/reflection.
6. **Mathematical Investigations — N09/N10:** formulate; compare strategies; financial decisions; design branching algorithms; test patterns/report. This strengthens the two partial descriptors rather than replacing completed media.

Each grouping supports five substantive lessons. No other topic starts until founder review of the deployed first topic. The coverage JSON records baseline; post-release evidence is added here without rewriting the baseline judgement.

## First topic candidate evidence

M01: `measurement.html#lesson1` and `#lesson2` (unit choice, instruments, equal graduations, finer/combined readings). M02: `#lesson3`–`#lesson5` (regular/equal-sided boundaries, tiled surfaces, irregular decomposition and practical designs). The 30-question challenge has independent Python/SymPy validation at `docs/year5/measurement-maths-qa.json`; five exact-byte media records are in `video-agent/production-v2/measurement-release.json`. These two descriptions are covered instructionally by this candidate; publication is certified only by the release PR/deployment evidence. The baseline matrix deliberately remains unchanged.

Measurement-only update (10 November 2026): M01–M04 checked against the [government-supported Scootle curriculum records](https://www.scootle.edu.au/ec/search?accContentId=AC9M5M01). Other rows retain the historical baseline; this update does not assert whole-Year-5 completion. The [production pilot](../../tools/production/README.md) distinguishes implementation coverage, automated QA, perception and deployment.
