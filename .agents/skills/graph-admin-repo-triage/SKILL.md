---
name: graph-admin-repo-triage
description: Use this skill for repo triage, health checks, nightly review, stale-doc detection, or automation-oriented scanning in Microsoft Graph Admin Studio. Use it when the goal is to inspect the repo state and update high-level /ai docs, not to implement product changes.
---


# Graph Admin Repo Triage

Use this skill for health checks, backlog shaping, and automation-friendly reviews.

## Read first

Always:
- `AGENTS.md`
- `/ai/status.md`
- `/ai/backlog.md`

Usually:
- `/ai/architecture.md`
- `/ai/repo_map.md`
- `/ai/active_task.md`
- `/ai/handoff.md`
- `/ai/decision_log.md`

## Required workflow

1. Inspect the repo state and current workstream if available.
2. Identify:
   - stale docs
   - obvious blockers
   - risky or unfinished areas
   - a good next concrete task
3. Update:
   - `/ai/status.md`
   - `/ai/backlog.md` when a concrete task or risk should be recorded
   - `/ai/thread_log.md` if the triage materially changes the next step
4. Keep code untouched unless the only edits are /ai documents.

## Output requirements

End with:
- top findings
- top risks
- best next action
- whether a fresh implementation, debug, or architecture thread should start next

