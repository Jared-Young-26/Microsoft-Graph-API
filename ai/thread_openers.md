# Thread Openers

Use these when you want deterministic behavior with almost no typing.

## Architecture
```text
$graph-admin-architect
Design the next phase of the current workstream. Update the durable-memory files but do not write product code unless clearly necessary.
```

## Implement
```text
$graph-admin-implement
Implement the current active task.
```

## Debug
```text
$graph-admin-debug
Debug the current issue described in /ai/active_task.md and /ai/handoff.md.
```

## Test
```text
$graph-admin-test-verify
Write or run the smallest adequate verification for the current active task and update /ai/reviews/test_report.md.
```

## Security review
```text
$graph-admin-security-review
Review the current task or diff for security issues and update /ai/reviews/security_report.md.
```

## Refactor
```text
$graph-admin-refactor
Perform a behavior-preserving cleanup for the current active task and update /ai/reviews/refactor_report.md.
```

## Doc sync
```text
$graph-admin-doc-sync
Refresh the /ai durable-memory files to match the current codebase state. Do not change product code.
```

## Next task
```text
$graph-admin-next-task
Pick the next concrete task and prepare /ai/active_task.md plus /ai/task_breakdown.md without changing product code.
```

## Handoff
```text
$graph-admin-handoff
Create a clean baton-pass handoff for a fresh thread and update /ai/handoff.md.
```

## Repo triage / automation
```text
$graph-admin-repo-triage
Perform a repo triage pass, update high-level /ai docs, and report the most important findings.
```
