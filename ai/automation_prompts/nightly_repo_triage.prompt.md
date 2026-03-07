$graph-admin-repo-triage

Run an autonomous repo triage pass.

Goals:
- Read AGENTS.md and the durable-memory files.
- Inspect repo state, current diffs, and recent risky areas if available.
- Identify stale docs, obvious blockers, and good next actions.
- Update /ai/status.md and /ai/thread_log.md.
- Update /ai/backlog.md only if a new concrete task or risk should be recorded.
- Do not change application code unless the only edits are /ai documentation updates.
