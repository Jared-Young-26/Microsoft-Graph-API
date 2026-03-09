# Automation Memory

This folder stores repo-local memory for recurring automations.

Use these files when an automation benefits from run-to-run context and external
automation memory under `~/.codex/automations/` is unavailable, blocked, or not
the desired source of truth.

Rules:
- Keep one memory file per recurring automation.
- Read the relevant memory file at the start of the automation run.
- Update it at the end with concise factual notes:
  - last run date
  - summary of what changed
  - validation performed
  - blockers or next focus
- Treat this folder as repo-scoped memory, not global app-scoped memory.
