$graph-admin-repo-triage

Run an autonomous repo triage pass.

Repo-local memory:
- Read `/ai/automation_memory/nightly_repo_triage.md` first if it exists.
- Use it to avoid repeating stale findings.
- Update it at the end with a concise summary, validation run, blockers, and next focus.

Goals:
- Read AGENTS.md and the durable-memory files.
- Inspect repo state, current diffs, and recent risky areas if available.
- Identify stale docs, obvious blockers, and good next actions.
- Update /ai/status.md and /ai/thread_log.md.
- Update /ai/backlog.md only if a new concrete task or risk should be recorded.
- Keep `/ai/automation_memory/nightly_repo_triage.md` aligned with the latest triage outcome.
- Do not change application code unless the only edits are /ai documentation updates.
