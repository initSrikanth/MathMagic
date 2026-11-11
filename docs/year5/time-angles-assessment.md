# Time and Angles correction — 11 November 2026

Recovered from PR #59 at `6520819d483214943d584daa132bc3e1796baece`, not conversation history. Existing Measurement verification and media remain preserved.

## Scope and teaching map

Checked government-supported Scootle v9 records on 11 November 2026:

- [AC9M5M03](https://www.scootle.edu.au/ec/search?accContentId=AC9M5M03): comparison and practical conversion of 12/24-hour systems.
- [AC9M5M04](https://www.scootle.edu.au/ec/search?accContentId=AC9M5M04): estimation, construction and measurement of angles with tools, connected to angle names.
- [AC9M6M03](https://www.scootle.edu.au/ec/search?accContentId=AC9M6M03): timetable/itinerary interpretation and journey planning are next-year extension.
- [AC9M6M04](https://www.scootle.edu.au/ec/search?accContentId=AC9M6M04): unknown-angle relationships on lines/at points are next-year extension.

The core no longer assesses kinds 2/3 (unknown angles), 4/8 (clock/full-turn arithmetic), 9 (signed angle differences), or multi-service timetable planning. Those slots now develop taught time-system comparison/conversion and protractor error analysis. Existing lesson 2 connection-planning/video content and lesson 5 unknown-angle material remain explicitly optional extension, outside proficiency marking. No video or voice is regenerated. Descriptor codes remain internal.

| Band / positions | Families | Teaching evidence / cognitive demand |
|---|---|---|
| Foundation 1–5 | 5, 6, 10, 5, 11 | Lessons 1/3: classify, benchmark, convert displays |
| Developing 6–10 | 0, 1, 12, 10, 11 | Lessons 1/3/4: elapsed-time prior learning, estimate, read a protractor |
| Developing+ 11–15 | 12, 13, 0, 1, 12 | Lessons 1/4: measurement and correcting a pm conversion |
| Proficient 16–20 | 7, 14, 15, 7, 14 | Lessons 1/4: compare systems, match equivalent displays, explain wrong-scale readings |
| Application 21–25 | 15, 16, 7, 14, 16 | Lessons 1/4/5: apply conversion with duration, identify a scale error |
| Challenge 26–30 | 16, 15, 14, 16, 7 | Combine conversion and time calculation; reconcile representations and misconceptions |

The 30-question attempt size, six bands, unique prompts/diagrams, marking/feedback and progress adapter remain intact. In the existing diagram family, a precise answer to an ungraduated estimate was unreliable: the revised question offers explicit benchmark choices. Protractor marks now include 5° ticks for 65°/115° readings. These corrections do not claim a complete redesign of difficulty differentiation.

Construction remains the keyboard/pointer lesson 4 studio and a real protractor activity, not evidence from a numeric-answer quiz. M03/M04 remain Partial until exact audiovisual/caption review, practical construction and production integration verification are complete.

Coverage research: the [IXL v9 Year 5 plan](https://au.ixl.com/maths/skill-plans/australian-curriculum-version-90-year-5) was consulted for coverage only; its rendered content was login-limited. No proprietary questions or graphics were copied. The government curriculum determines scope. Existing original exercises and approved videos remain the resource selection; no extra provider video is needed for this focused correction.

## Validation boundaries

`tests/time-angles-maths.test.cjs` independently derives answers from prompt numbers/time displays/diagram geometry across 1,000 seeded attempts (30,000 positions). It rejects out-of-scope families, checks unique normalised prompts plus diagram values, both am/pm conversions, and both A/B answer positions. It does not call the production answer validator. Browser tests cover all 30 positions, worked feedback, input formats and save retry/idempotence through an explicitly isolated test adapter. Live Firebase and physical-device behaviour remain separate gates.

The targeted axe audit exposed 3.04:1 teal/white text/button contrast. A page-scoped primary colour and visible focus outline correct it; shared styles and other topics are unchanged. Browser feedback checks assert the existing green (`#18794e`) and red (`#b42318`) states.
