$graph-admin-test-verify

Run a validation sweep for the current active task or the most recently changed risky area.

Rules:
- Prefer the smallest adequate validation.
- Reuse existing test commands first.
- If browser behavior was touched and Playwright is available, run the smallest relevant Playwright coverage.
- Update /ai/reviews/test_report.md and /ai/handoff.md with findings.
- Do not perform broad refactors.
