# Quickstart — Zero-Boilerplate Codex Use

This repo no longer expects you to paste huge role prompts into every new thread.

The working stack is:

1. `AGENTS.md`
2. `/ai` durable-memory files
3. repo skills in `/.agents/skills`

## What changed

Your old `/ai/prompts/*.md` files are now **reference material**, not something you should manually paste every time.
For the smoothest workflow, either:

- start a thread with a **short natural-language prompt**, or
- use an explicit **`$skill-name`** for deterministic behavior

## The shortest prompts that should work

### Architecture
```text
$graph-admin-architect
Design the next phase of the current workstream and update the durable-memory files.
```

### Implement
```text
$graph-admin-implement
Implement the current active task.
```

### Debug
```text
$graph-admin-debug
Debug the current issue described in /ai/active_task.md and /ai/handoff.md.
```

### Test / Verify
```text
$graph-admin-test-verify
Verify the current task and update the test report.
```

### Security review
```text
$graph-admin-security-review
Review the current workstream for security and trust-boundary issues.
```

### Refactor
```text
$graph-admin-refactor
Perform a behavior-preserving cleanup for the current active task.
```

### Pick the next task
```text
$graph-admin-next-task
Pick the next concrete task and prepare /ai/active_task.md plus /ai/task_breakdown.md.
```

### Clean handoff
```text
$graph-admin-handoff
Create a clean handoff for a fresh thread.
```

## Lowest-friction natural prompts

These often work without explicit skill invocation because the skill descriptions are designed to match them:

- "Implement the current active task."
- "Debug the workspace rendering regression."
- "Write Playwright coverage for the current active task."
- "Security review the auth-related changes."
- "Update the repo docs after the last refactor."
- "Pick the next best task from backlog."

Explicit `$skill-name` usage is still more deterministic.

## Mode selection

- **Worktree**: implementation, debugging, testing, refactoring, security fixes
- **Local**: doc-only sync, repo mapping, next-task prep, planning-only work
- **Cloud**: only when the environment is configured and local-only tooling is not required

## Plan mode rules

Use Plan Mode when:
- architecture is changing
- more than 3 real files will change
- the root cause is unclear
- auth, schema, or boot order is involved
- you want milestones before code edits

Skip Plan Mode when:
- the change is tiny and obvious
- you are doing doc-only sync
- you are updating a single small file with low ambiguity

## Speed rules

- **Standard**: architecture, debugging, security review, nontrivial implementation
- **Fast**: doc sync, backlog grooming, tiny edits, simple reports

## Default human habit

When in doubt, start with one of these and let the repo files do the heavy lifting:

```text
$graph-admin-next-task
```

or

```text
$graph-admin-implement
Implement the current active task.
```
