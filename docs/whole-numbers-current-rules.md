# Whole Numbers & Place Value — current-rule review

## Topic-exclusive Year 5 rules
The module assesses whole-number place value and representation, comparison and ordering; decimal place value through thousandths; decimal comparison, ordering and location; powers-of-ten place relationships; and whole-number rounding/estimation used for reasonableness. Question generators must preserve these boundaries and must not inherit fraction- or percentage-specific validation rules.

## Review findings
The five-page teaching sequence, 30-question six-band challenge, curated privacy-enhanced learning resources, authentication and Firestore topic progress were retained. A stale /20 progress/proficiency rule was corrected to /30. Generator QA now exposes and stress-tests 500 complete challenges (15,000 generated positions).

## Protected-content pilot
Callable start/submit endpoints require Firebase Auth, server-side approval and App Check. Sessions are UID- and topic-bound. Answers and solutions are stripped from learner question payloads and marking remains server-side.

## Production status
Repository/CI validation does not mean the protected backend is deployed. Production cutover still requires Firebase deployment, App Check registration/enforcement verification, authorised-user success, unauthorised-user rejection and real progress-persistence integration testing.
