# MathMagic

Australian Curriculum v9 mathematics using the existing GitHub Pages static HTML/CSS/JavaScript architecture and Firebase Google authentication, approved-user access and topic-scoped progress.

Year 5 navigation is **Year → Strand → Topic → Lessons → Interactive activities → Assessment**. The dashboard links to six independent strand pages; existing topic URLs and progress keys remain stable. Other Years 1–10 are disabled until their verified development is authorised. No Year 6 work begins before all Year 5 strands are complete, verified and deployed.

- [Canonical project/security/QA instructions](AGENTS.md)
- [All 24 Year 5 descriptors and evidence](docs/year5/curriculum-coverage.md) / [JSON](docs/year5/curriculum-coverage.json)
- [Ordered strand backlog and effort](docs/year5/strand-completion-plan.md)
- [Navigation metadata](docs/year5/strand-topics.json) / [actual resource audit](docs/year5/resource-audit.json)
- [Framework QA and preview](docs/year5/framework-qa.md)
- [Canonical video contract](video-agent/video-production-contract.json)

Curriculum coverage describes resources; student attempts/best scores describe practice. Media approval and live deployment are separate. Public files and safe browser/emulator tests do not establish deployed Firebase rules, App Check or real sign-in/progress. Multiplication & Division retains its protected-only callable service and fails closed if unavailable; other browser generators remain the documented transitional baseline. Never publish credentials or add a production authentication bypass.

## Local preview and checks

```sh
npm ci
python3 tools/curriculum/build_pages.py
npm run test:curriculum
npm run test:protected
npx playwright install chromium webkit
npm run test:e2e
python3 tests/serve.py
```

Open `http://127.0.0.1:4173/dashboard.html` with normal approved-user authentication. The six landing pages are `year5-number.html`, `year5-algebra.html`, `year5-measurement.html`, `year5-space.html`, `year5-statistics.html` and `year5-probability.html`. Automated previews inject test-only Firebase SDK mocks at the network boundary; there is no production preview bypass.

GitHub Actions runs the existing browser, generator, security/emulator and media-contract gates on pull requests to main. Deployment remains the existing GitHub Pages workflow after authorised merge; this curriculum/navigation task requests a dedicated PR only.
