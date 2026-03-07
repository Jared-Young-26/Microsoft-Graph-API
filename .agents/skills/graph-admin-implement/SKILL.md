---
name: graph-admin-implement
description: "Implementation workflow for focused code changes in Microsoft Graph Admin Studio."
---

# Graph Admin Implement

Use this skill for normal feature work and scoped code changes.

## Read first

Always:
- `AGENTS.md`
- `/ai/constraints.md`
- `/ai/active_task.md`

Usually:
- `/ai/task_breakdown.md`
- `/ai/architecture.md`
- `/ai/repo_map.md`
- `/ai/handoff.md`

When relevant:
- `/ai/reviews/security_report.md`
- `/ai/decision_log.md`
- `/ai/risk_register.md`

## Purpose

Implement the current scoped task with the smallest effective change.

## Rules

- Respect all repo constraints in `AGENTS.md`
- Do not redesign architecture unless the task explicitly requires it
- Do not modify unrelated files
- Preserve existing behavior outside the scoped task
- Add or update focused tests when appropriate
- If blocked by ambiguity, state the blocker clearly instead of guessing

## Expected output

Provide:
- implementation summary
- files changed
- validation performed
- remaining risks or follow-ups