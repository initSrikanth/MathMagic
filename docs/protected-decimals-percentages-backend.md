# Protected Decimals & Percentages pilot

## Scope
This pilot extends the protected-content pattern to the existing Year 5 Decimals & Percentages module without cutting production over before Firebase deployment and App Check verification.

Topic-exclusive boundaries:
- decimal place value through thousandths, including equivalent decimal notation;
- compare, order and locate decimals using place value and number-line reasoning;
- percent as “out of 100” and as a common scale for relative size;
- familiar fraction–decimal–percentage equivalences used in the existing Year 5 learning sequence;
- percentage-of-quantity calculations are excluded from this Year 5 module.

## Protection
The callable start/submit endpoints require Firebase Authentication, server-side MathMagic approval and App Check. A UID-bound Firestore session stores authoritative answers and marking logic. Question payloads strip answers and worked solutions. Submission returns only feedback for the submitted item plus the next safe question.

## Release status
This is repository-level architecture only. Do not describe the protected Decimals & Percentages backend as live until functions are deployed, the web app is registered for App Check, enforcement is verified, and authorised/unauthorised production integration tests pass. The existing browser module remains the production UI until that cutover is explicitly completed.
