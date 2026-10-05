# Protected Fractions backend pilot

This repository now contains a Firebase callable-functions pilot for moving valuable Fractions assessment logic off the public GitHub Pages client.

## Security model
- Firebase Authentication is required by both callable endpoints.
- The server checks `access/{uid}.approved === true` before starting a challenge.
- Firebase App Check enforcement is configured on both callable endpoints.
- A challenge session is owned by one UID; another authenticated UID cannot submit against it.
- Correct answers and worked solutions are stripped from the question payload and retained server-side.
- The existing Firestore student-progress rules remain separate and authoritative for progress data.

## Safe rollout
The current public Fractions challenge remains on the existing client generator until the backend is deployed and verified. Do **not** switch the production frontend merely because these function files exist.

Before production cutover:
1. Ensure the Firebase project is on a plan that supports Cloud Functions deployment and confirm expected cost/budget alerts.
2. Register the MathMagic web app with Firebase App Check using the supported web provider and configure allowed domains.
3. Deploy the functions from this repository and confirm both callable endpoints are present.
4. Verify an approved signed-in user can start a session.
5. Verify signed-out and unapproved users are rejected.
6. Verify requests without valid App Check are rejected after enforcement is enabled.
7. Verify a different UID cannot use another student's session ID.
8. Add/verify rules so client SDKs cannot directly read or write `challengeSessions`; only the Admin SDK in Functions should access them.
9. Run the full 30-question browser suite against the protected adapter and verify Firestore progress persistence.
10. Only then remove the legacy client generator/answer logic from the public bundle.

The repository/CI checks prove architecture properties only. They do not prove that Firebase deployment or production App Check enforcement is active.
