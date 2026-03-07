---
name: graph-admin-debug
description: Use this skill for debugging regressions, broken flows, failing behavior, runtime errors, test failures, or root-cause analysis in Microsoft Graph Admin Studio. Do not use it for greenfield feature work, architecture-only planning, or doc-only sync.
---


# Graph Admin Debug

Use this skill when behavior is broken, unclear, or failing.

## Read first

Always:
- `AGENTS.md`
- `/ai/constraints.md`
- `/ai/active_task.md`

Usually:
- `/ai/handoff.md`
- `/ai/task_breakdown.md`
- `/ai/architecture.md`
- `/ai/repo_map.md`
- `/ai/status.md`
- `/ai/reviews/test_report.md` if a previous validation pass exists

## Required workflow

1. Define the symptom precisely.
   - What is expected?
   - What is actually happening?
   - What environment or conditions matter?

2. Reproduce if possible.
   - If you cannot reproduce, say so clearly and create a reproduction plan instead of bluffing.

3. Narrow the fault domain.
   - Prefer evidence over guessing.
   - Identify the smallest likely boundary where the bug lives.

4. State a root-cause theory before applying a fix.

5. Apply the smallest fix that addresses the confirmed cause.
   - Do not turn debugging into architecture churn.
   - Preserve stable interfaces unless the bug specifically requires changing them.

6. Verify the fix.
   - Re-run the reproduction path.
   - Add or update targeted validation if appropriate.

7. Update durable memory:
   - `/ai/handoff.md` with confirmed facts, ruled-out theories, files involved, and exact next step
   - `/ai/thread_log.md`
   - `/ai/reviews/test_report.md` if tests or validation were involved
   - `/ai/status.md` if blockers changed

## Output requirements

End with:
- root cause
- files changed
- validation performed
- ruled-out theories
- remaining unknowns
- next step

