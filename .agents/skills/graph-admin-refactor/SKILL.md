---
name: graph-admin-refactor
description: Use this skill for behavior-preserving cleanup, simplification, or maintainability improvements in Microsoft Graph Admin Studio. Use it when the user asks to clean up, simplify, de-duplicate, or improve readability without changing behavior. Do not use it for debugging unknown bugs or major architecture redesign.
---


# Graph Admin Refactor

Use this skill when the goal is maintainability without behavior change.

## Read first

Always:
- `AGENTS.md`
- `/ai/constraints.md`
- `/ai/active_task.md`

Usually:
- `/ai/task_breakdown.md`
- `/ai/architecture.md`
- `/ai/repo_map.md`
- `/ai/reviews/refactor_report.md`
- `/ai/handoff.md`

## Required workflow

1. State what must stay behaviorally identical.
2. Identify the cleanup target:
   - duplication
   - naming clarity
   - file organization
   - function extraction
   - dead code removal
   - simplification

3. Keep the refactor scoped.
   - Do not mix in feature work.
   - Do not mix in speculative architecture changes.

4. Validate behavior after the refactor.
   - Reuse existing tests or targeted manual verification.

5. Update `/ai/reviews/refactor_report.md` with:
   - goal
   - preserved behavior
   - files changed
   - validation
   - remaining cleanup opportunities

6. Update `/ai/handoff.md`, `/ai/thread_log.md`, and `/ai/status.md` if needed.

## Output requirements

End with:
- what was cleaned up
- what behavior was preserved
- how it was validated
- remaining cleanup candidates

