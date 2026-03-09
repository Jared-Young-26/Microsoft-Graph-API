# AGENTS.md — Microsoft Graph Admin Studio

This repository uses **durable project memory** under `/ai` and **repo-local skills** under `/.agents/skills`.

Do **not** ask the user to re-paste role prompts or restate project context if the answer already lives in these files.
The old `/ai/prompts/*.md` files are reference material only. The active operating system is:

1. `AGENTS.md`
2. `/ai/*.md` durable-memory files
3. `/.agents/skills/*` specialized workflows

## Core rules

- Keep each thread focused on **one mission**.
- Default to **small, reviewable diffs**.
- Preserve stable APIs, selectors, IDs, boot order, and auth behavior unless the active task explicitly allows changing them.
- Prefer **incremental edits** over broad rewrites.
- Do not redesign architecture during a debug or test task unless the user explicitly requests it.
- Update durable-memory files when the truth changes.
- For recurring repo automations, prefer repo-local memory under `/ai/automation_memory/` when run-to-run context is needed and external automation storage is unavailable or blocked.
- Never ask the user to copy/paste old role prompts into a new thread. Use the repo files and skills instead.
- When selecting tasks, prioritize items that mitigate risks in ai/risk_register.md,
ordered by severity (P0–P3) and scope clarity.

## Read order at the start of a new thread

### Always read
1. `/ai/constraints.md`
2. `/ai/active_task.md`

### Read when relevant
- `/ai/handoff.md` when resuming prior work or inheriting a thread
- `/ai/task_breakdown.md` for implementation, debugging, testing, refactoring, or multi-step work
- `/ai/architecture.md` for design, implementation, refactor, or debugging
- `/ai/repo_map.md` when file ownership, boot order, or module boundaries matter
- `/ai/status.md` to understand the current project state
- `/ai/backlog.md` when selecting the next task
- `/ai/decision_log.md` when a durable design decision is relevant
- `/ai/plans/current_plan.md` for architecture work or any task that spans multiple milestones
- `/ai/reviews/test_report.md`, `/ai/reviews/security_report.md`, `/ai/reviews/refactor_report.md` when continuing those workstreams
- `/ai/automation_memory/*.md` when running or resuming a recurring repo automation

## Source-of-truth precedence

When documents disagree, use this precedence order and then **repair the stale document**:

1. Direct user instruction in the current thread
2. `/ai/constraints.md`
3. `/ai/active_task.md`
4. `/ai/handoff.md`
5. `/ai/task_breakdown.md`
6. `/ai/architecture.md`
7. `/ai/repo_map.md`
8. `/ai/status.md`
9. `/ai/backlog.md`

## Default operating loop

1. Frame the task as:
   - objective
   - in-scope files or modules
   - out-of-scope files or modules
   - invariants that must stay stable
2. Decide whether a **plan-first** step is required.
3. Make the smallest adequate change.
4. Verify with the smallest adequate validation that gives confidence.
5. Update durable-memory files.
6. End with a concise summary of:
   - what changed
   - what was verified
   - remaining risk
   - exact next step

## When plan-first is required

Plan first before changing code if **any** of these are true:

- the task changes architecture or file/module boundaries
- the task affects more than 3 substantive files
- the task touches boot order, auth flow, schema, or shared state
- the root cause is not yet understood
- the task requires coordinated changes across frontend and backend
- the task introduces or removes dependencies
- the task is large enough that a human would naturally want milestones

When planning, update `/ai/task_breakdown.md` and, for larger work, `/ai/plans/current_plan.md`.

## Thread and mode rules

### Prefer Worktree mode for
- implementation
- debugging
- testing that may modify files
- refactoring
- security fixes
- anything that changes code

### Prefer Local mode for
- doc-only sync
- repo mapping
- backlog grooming
- next-task preparation
- architecture writing that does not touch product code

### Cloud mode
Only use Cloud when the environment is configured and the task does not depend on local-only tools or files.

## Verification rules

- Use the smallest effective validation first.
- Reuse existing scripts and test commands before inventing new ones.
- Use Playwright only when browser behavior or DOM behavior needs real browser validation and the tool is available.
- If automated validation is not possible, provide manual verification steps and explain the gap.
- Do not claim something is fixed unless you have either:
  - reproduced and resolved it, or
  - explained clearly why reproduction was not possible and what evidence supports the proposed fix

## Durable-memory update rules

### Update `/ai/active_task.md`
- when a new task becomes the active workstream
- when scope materially changes

### Update `/ai/task_breakdown.md`
- when the task needs milestones or substeps
- when execution order changes

### Update `/ai/handoff.md`
- when pausing, ending, or cleaning up a thread
- when handing work to a fresh thread
- when the current thread has accumulated stale assumptions

### Update `/ai/status.md`
- when the repo's current milestone, blockers, or next best actions change

### Update `/ai/decision_log.md`
- when a durable design, workflow, or architecture decision is made

### Update `/ai/architecture.md` or `/ai/repo_map.md`
- when the actual codebase truth changed
- not for speculation

### Update review files
- `/ai/reviews/test_report.md` for verification and coverage findings
- `/ai/reviews/security_report.md` for security findings and trust-boundary notes
- `/ai/reviews/refactor_report.md` for behavior-preserving cleanup notes

## Available repo skills

These skills live under `/.agents/skills` and are the preferred replacement for manually pasted role prompts:

- `$graph-admin-architect`
- `$graph-admin-implement`
- `$graph-admin-debug`
- `$graph-admin-test-verify`
- `$graph-admin-security-review`
- `$graph-admin-refactor`
- `$graph-admin-doc-sync`
- `$graph-admin-next-task`
- `$graph-admin-handoff`
- `$graph-admin-repo-triage`

Use explicit `$skill-name` invocation when you want deterministic behavior.
Implicit triggering is also available for most skills, based on their descriptions.

## Output style

Be concise and operational.

At the start of meaningful work, prefer a short scope block.
At the end of meaningful work, report:

- changed files
- validation performed
- open risks or unknowns
- exact next step

Do not generate giant ceremonial summaries unless the user asked for one.
