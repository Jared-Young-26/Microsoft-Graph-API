---
name: graph-admin-handoff
description: Use this skill when ending, pausing, cleaning up, or re-seeding a Microsoft Graph Admin Studio thread and you need a concise baton-pass handoff. Use it to summarize the current state into /ai/handoff.md and a thread-log entry. Do not use it for primary implementation work.
---


# Graph Admin Handoff

Use this skill to cleanly end a thread or prepare a fresh successor thread.

## Read first

Always:
- `AGENTS.md`
- `/ai/active_task.md`

Usually:
- `/ai/handoff.md`
- `/ai/task_breakdown.md`
- `/ai/status.md`
- `/ai/reviews/test_report.md`
- `/ai/reviews/security_report.md`
- `/ai/reviews/refactor_report.md`

## Required workflow

Create or overwrite `/ai/handoff.md` with:

- objective
- current status
- confirmed facts
- ruled-out theories or dead ends
- files changed or most likely involved
- validation performed
- remaining risks or unknowns
- exact next step
- whether the task is resume-ready

Also append or prepare a concise entry for `/ai/thread_log.md`.

## Constraints

- Keep the handoff short, dense, and copy-paste ready.
- Do not dump raw logs unless they are essential.
- Preserve the signal; throw away the sludge.

## Output requirements

End with:
- one-paragraph summary of the baton pass
- recommended title for the next thread
- recommended mode for the next thread

