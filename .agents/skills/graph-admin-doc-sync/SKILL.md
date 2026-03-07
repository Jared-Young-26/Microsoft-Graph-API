---
name: graph-admin-doc-sync
description: Use this skill when the Microsoft Graph Admin Studio durable-memory files are stale or when the user asks to update architecture, repo map, status, backlog, decision log, or other /ai documentation to match current codebase truth. Do not use it for product code changes.
---


# Graph Admin Doc Sync

Use this skill for documentation and durable-memory maintenance only.

## Read first

Always:
- `AGENTS.md`

Then read whichever docs are relevant:
- `/ai/architecture.md`
- `/ai/repo_map.md`
- `/ai/status.md`
- `/ai/backlog.md`
- `/ai/decision_log.md`
- `/ai/handoff.md`
- `/ai/plans/current_plan.md`
- `/ai/active_task.md`

## Required workflow

1. Identify which docs are stale relative to the current codebase or workstream.
2. Update only what the evidence supports.
3. Keep changes factual, concise, and current.
4. Do not speculate about architecture that does not exist yet unless the user explicitly asked for forward-looking design.
5. Do not change product code.

## Preferred outputs

Use this skill to keep the repo memory healthy:
- refresh `status.md`
- refresh `repo_map.md`
- refresh `architecture.md`
- refresh `backlog.md`
- append to `decision_log.md`
- clean up `handoff.md` after a thread ends

## Output requirements

End with:
- docs updated
- what truth changed
- any docs still suspected stale

