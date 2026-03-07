---
name: graph-admin-next-task
description: Use this skill when the user asks what to do next, asks to pick the next task, wants backlog grooming, or wants /ai/active_task.md and /ai/task_breakdown.md prepared for the next focused thread in Microsoft Graph Admin Studio. Do not use it for code changes.
---


# Graph Admin Next Task

Use this skill to turn backlog and status into one clean next work item.

## Read first

Always:
- `AGENTS.md`
- `/ai/backlog.md`
- `/ai/status.md`

Usually:
- `/ai/architecture.md`
- `/ai/repo_map.md`
- `/ai/active_task.md`
- `/ai/task_breakdown.md`
- `/ai/handoff.md`
- `/ai/decision_log.md`

## Required workflow

1. Choose one task that is:
   - high value
   - low to medium ambiguity
   - small enough for one focused thread
   - compatible with current constraints

2. Reject tasks that are too broad, too muddy, or too dependent on unknown prerequisites.

3. Update:
   - `/ai/active_task.md`
   - `/ai/task_breakdown.md`
   - `/ai/status.md`

4. If the chosen task depends on a durable design choice, note that in `/ai/decision_log.md` or recommend an architecture thread first.

5. Do not modify product code.

## Output requirements

End with:
- chosen task
- why it was chosen
- prerequisites
- recommended next thread type and mode

