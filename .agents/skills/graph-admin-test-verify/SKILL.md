---
name: graph-admin-test-verify
description: Use this skill for writing, updating, or running tests and validation in Microsoft Graph Admin Studio, especially when asked to verify behavior, add coverage, use Playwright, or produce a test report. Do not use it for primary feature implementation or architecture-only planning.
---


# Graph Admin Test & Verify

Use this skill for verification, coverage, and confidence-building.

## Read first

Always:
- `AGENTS.md`
- `/ai/active_task.md`

Usually:
- `/ai/task_breakdown.md`
- `/ai/handoff.md`
- `/ai/reviews/test_report.md`
- `/ai/architecture.md`
- `/ai/repo_map.md`

## Required workflow

1. Define what must be proven.
   - behavior
   - edge cases
   - failure modes
   - regression risk

2. Choose the smallest adequate validation strategy.
   Preferred order:
   - existing focused tests
   - existing project scripts
   - new targeted automated tests
   - manual verification steps when automation is unavailable

3. Use Playwright when:
   - browser behavior or DOM behavior is central, and
   - Playwright or equivalent tooling is available

4. Avoid brittle or ceremonial tests.
   - Do not add broad end-to-end coverage if a smaller test proves the same thing.
   - Do not pretend coverage exists when it does not.

5. Update `/ai/reviews/test_report.md` with:
   - scope
   - commands or validations used
   - result
   - coverage gaps
   - confidence level

6. Update `/ai/handoff.md` and `/ai/thread_log.md` if the verification changes the next step.

## Output requirements

End with:
- what was verified
- automated validation run
- manual validation, if any
- coverage gaps
- confidence level

