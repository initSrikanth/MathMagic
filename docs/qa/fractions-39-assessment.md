# Issue 39 — Assessment specialist evidence

Baseline: `bebf1528e2f5c816e070ba897a6a5872b3c52583`. Scope: browser Fractions generator and answer handling, not a protected-backend migration. No video bytes, authentication module or production workflows changed.

## Proven gaps and corrections

- `classProjectProblem()` independently combined denominator choices, producing unrelated pairs, e.g. one third plus one eighth (remaining thirteen twenty-fourths). Correlated choices now use thirds/sixths, fifths/fifths or eighths/eighths. The assessed challenge stays within same/related denominators.
- Garden/project questions could repeat the identical whole-minus-two-shares calculation under different topic/context strings. Their canonical fingerprint now reduces and sorts the two operand fractions before checking uniqueness.
- `partitionQ()` had both duplicate literal options (e.g. a two-part numerator split) and mathematically equivalent wrong options. The last distractor now has a distinct total; tests check all four option values, not only string uniqueness.
- `estimateReasonable()` used overlapping “less than 1”/“about 1” categories and an arbitrary three-quarter cutoff. It now asks an unambiguous benchmark question with mutually exclusive less/equal/greater-than-one options, marked by exact integer comparison.
- `stripSubtract()` said the removed fraction was “of that amount”, implying a fraction of the selected fraction. Both fractions now explicitly refer to the whole strip.
- Mixed values beyond one were not assessed on number lines. A mixed-number number-line family replaces the redundant same-whole/equal-denominator mixed comparison in Developing+. There are still exactly 30 positions, six bands of five; proper-fraction number lines and comparison/ordering remain assessed.
- Tank's former one-step subtraction was not challenge-level. It now asks for a subtraction followed by a refill addition, uses only related denominator sets, and consistently refers to total capacity.
- Non-finite number conversions could be accepted as equivalent (huge numerator and denominator both became Infinity); negative numerator/denominator pairs could pass. Input now requires safe nonnegative integers and positive denominators. Mixed fractional parts must be proper; equivalent positive forms remain accepted when simplification is not requested.
- An unanswered Next event is now ignored. This is UI reliability, not a claim that client assessment is tamper-proof.
- Feedback for equivalence, simplification, operations, conversion, ordering and missing numerators now includes the actual numeric working. Mixed-number answer displays are normalised.

## Executed checks

`node --check js/fractions.js` — PASS.

`node tests/generator-fractions.test.js` — PASS: seed `0x39f5a`, 1,000 complete attempts, **30,000 question positions**, 26 topic-labelled families, zero canonical garden/project repeats. Checks cover all active families' arithmetic/answers, 30/six-band positions, strict simplification, mixed normalisation, same/related denominator scope, distractor uniqueness (including mathematical partition values), worked-feedback presence, rendered notation, malformed and equivalent input, unanswered advancement.

`node tests/protected-fractions.test.js` — PASS: existing static protected-backend assertions only. This does not prove backend deployment, live Firestore rules, App Check, authentication or persistence.

The generator test executes the real current source in Node's VM with a seeded RNG and isolated DOM stubs. It does **not** certify browser rendering/accessibility or real Firebase services. Independent browser/QA review remains a release requirement. HTML practice feedback, live mobile/Safari, progress saving/retry and approved-video inventory are separate workstreams.

## Independent CEO arithmetic counterexample

After the initial safe-input fix, CEO independently found that safe integer inputs alone do not make Number cross-products exact: numerator `6004799503160659` / denominator `9007199254740988` was falsely equivalent to two thirds after multiplication rounded. `eq()` now validates integer pairs and uses BigInt cross-products. The regression rejects that unequal ratio while accepting a genuinely equivalent large safe-integer half. This is answer equality only; bounded lesson/generator arithmetic remains unchanged. The 30,000-position seeded suite and protected Fractions static checks passed again after this correction.

## Taught regrouping alignment follow-up

With CEO coordination, `mixedSameAdd()` now includes legitimate carry/regrouping outcomes in Proficient, matching the existing Add & Subtract teaching. It deliberately excludes exact-whole fractional sums so the mixed-number entry is unambiguous; every final fractional part is proper, nonzero and normalised. Numeric feedback explicitly shows the extra whole and the final mixed number. The fixed regression generates one and three quarters plus two quarters, checks the result two and one quarter, and checks the regrouping explanation. The final seeded run still covered 30,000 positions, with **503 regrouping questions**, zero canonical duplicate remainders and all 26 active topic-labelled families passing. Node syntax and existing protected Fractions static checks passed again.
