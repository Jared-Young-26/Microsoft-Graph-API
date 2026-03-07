# Install and Use This Pack

This pack is designed to sit **on top of** the `/ai` folder structure you already created from the earlier pipeline guide.

## What this pack adds

- repo-root `AGENTS.md`
- project-scoped `.codex/config.toml`
- repo-local skills under `/.agents/skills`
- extra durable-memory docs under `/ai`
- templates for consistent task, handoff, and report files
- automation prompt templates
- an optional global `~/.codex/AGENTS.md` example

## Install steps

1. **Extract this pack at the root of your Microsoft Graph Admin Studio repo.**
2. Allow it to merge into your existing `/ai` folder.
3. Review these two files first:
   - `AGENTS.md`
   - `.codex/config.toml`
4. Optional but recommended:
   - copy `global/AGENTS.md.example` to `~/.codex/AGENTS.md`
5. Restart Codex if the new skills do not immediately appear.

## What you should stop doing

- Stop pasting giant role prompts into every new thread.
- Stop relying on one immortal megathread.
- Stop treating `/ai/prompts/*.md` as things to paste every time.

## What you should do now

### Most deterministic flow
Use explicit skills with very short prompts.

Examples:
- `$graph-admin-next-task`
- `$graph-admin-implement`
- `$graph-admin-debug`
- `$graph-admin-test-verify`
- `$graph-admin-handoff`

### Lowest-friction flow
Use normal language and let AGENTS plus implicit skill matching do the work.

Examples:
- "Implement the current active task."
- "Debug the current issue."
- "Update the repo docs after that refactor."
- "Pick the next concrete task."

## Recommended daily loop

1. `$graph-admin-next-task`
2. `$graph-admin-implement`
3. `$graph-admin-test-verify`
4. `$graph-admin-handoff`

## Recommended when the task is muddy

1. `$graph-admin-architect`
2. `$graph-admin-next-task`
3. `$graph-admin-implement`

## Thread mode defaults

- **Worktree** for code changes
- **Local** for doc-only sync, planning, and next-task prep

## Optional automations

See:
- `ai/automation_prompts/prepare_next_task.prompt.md`
- `ai/automation_prompts/nightly_repo_triage.prompt.md`
- `ai/automation_prompts/nightly_regression_triage.prompt.md`
- `ai/automation_prompts/weekly_doc_sync.prompt.md`

These are intended to be pasted into Codex app automations or used as reference prompts.

## First thing to do after install

Start one clean thread and run:

```text
$graph-admin-doc-sync
Refresh the /ai durable-memory files so they match the current real repository state.
```

Then start:

```text
$graph-admin-next-task
Pick the next concrete task and prepare the active task files.
```

That gets the new operating system aligned with the repo as it actually exists today.
