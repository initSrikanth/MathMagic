# Factors & Multiples — Year 5

## Curriculum authority
Australian Curriculum v9 Year 5:
- AC9M5N02: express/decompose natural numbers as products of factors, recognise multiples and determine divisibility.
- AC9M5N10: create and use step-by-step algorithms and digital tools to experiment with factors, multiples and divisibility and describe emerging patterns.
- The Year 5 achievement standard expects students to express natural numbers as products of factors, identify multiples, and create/use algorithms to explain factor/multiple patterns.

## Topic-exclusive boundary
Included: factor pairs and complete factor sets; factor/multiple relationship; recognising and extending multiples; divisibility tests for 2, 3, 4, 5, 6, 9 and 10; shared factors/shared multiples as relationship reasoning; step-by-step factor/divisibility algorithms; interpreting number patterns.

Excluded from assessment: formal prime/composite classification and prime factorisation, which Australian Curriculum v9 places in Year 6. HCF/LCM terminology and procedures are not required for this module; shared-factor/shared-multiple reasoning is used instead.

## Coverage research
Coverage was compared with current IXL Australia Year 5 Factors, multiples and divisibility breadth and Khan Academy factor/multiple representations. Competitor/platform material was used only to detect question-family gaps; MathMagic wording, examples, generators, distractors and solutions are independently authored.

## Teaching sequence
1. Factor pairs and complete factor sets.
2. Multiples and the reciprocal factor/multiple relationship.
3. Divisibility tests and justification.
4. Algorithms: repeated steps/decisions for factors, multiples and divisibility patterns.
5. Shared factors/multiples and reasoning across representations.

## 30-question coverage matrix
| Family | Taught | Bands |
| --- | --- | --- |
| Factor recognition | Page 1 | Foundation–Developing |
| Missing factor / factor product | Page 1 | Foundation–Developing+ |
| Complete factor-set recognition | Page 1 | Developing–Proficient |
| Multiple recognition / sequence continuation | Page 2 | Foundation–Proficient |
| Factor ↔ multiple relationship | Page 2 | Foundation–Developing+ |
| Divisibility tests | Page 3 | Developing–Application |
| Explain/combine divisibility rules | Page 3 | Developing+–Challenge |
| Factor-finding algorithm steps | Page 4 | Developing+–Challenge |
| Multiple-pattern algorithms | Page 4 | Proficient–Challenge |
| Shared factors/shared multiples | Page 5 | Developing+–Application |
| Error analysis / reasoning | Pages 3–5 | Application–Challenge |

## Difficulty progression
Foundation recognises direct factors/multiples and completes one-step relationships. Developing applies complete factor sets and single divisibility rules. Developing+ connects factor/multiple relationships, shared properties and algorithm steps. Proficient applies rules with less scaffolding and pattern reasoning. Application chooses/combines tests and relationships in context. Challenge analyses algorithms, errors and multi-condition divisibility while remaining inside Year 5 scope.

## Architecture
The production challenge is protected-only. Generator, answers and marking remain in Firebase Functions; the public browser receives only the current safe question. Start and submit require Firebase Auth, server-side approval and App Check declarations; sessions are UID/topic/index bound and fail closed. CI uses an explicit test-only browser adapter.

## External resource pass
- Khan Academy original-provider factors/multiples article is linked.
- Math with Mr. J “Multiples vs. Factors” uses the same established MathMagic external-video pattern as Fractions and the other live modules: the provider-hosted `youtube-nocookie.com` player, lazy loading, accessible title, creator attribution and an original YouTube fallback link. The video is streamed from YouTube; MathMagic does not copy or re-host the media. Child-directed-site platform designation remains a separate site-level production configuration check.

## Production caveat
Repository/CI validation does not prove Firebase Functions deployment, live App Check enforcement, real authorised/unauthorised sessions or production Firestore rules/progress persistence.