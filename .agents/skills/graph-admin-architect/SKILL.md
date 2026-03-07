---
name: graph-admin-architect
description: Use this skill for architecture, design, planning, module-boundary, boot-order, schema-shape, or interface-definition work in the Microsoft Graph Admin Studio repository. Use it when the user asks to design, plan, map, restructure, or define the next phase of work. Do not use it for pure debugging, pure testing, or simple doc-only sync.
---


# Graph Admin Architect

Use this skill to produce a clean design or plan **before** coding.

## Inputs to read

Always read:
- `AGENTS.md`
- `/ai/constraints.md`
- `/ai/active_task.md`

Also read when relevant:
- `/ai/architecture.md`
- `/ai/repo_map.md`
- `/ai/status.md`
- `/ai/backlog.md`
- `/ai/plans/current_plan.md`
- `/ai/decision_log.md`
- `/ai/handoff.md`

## Required workflow

1. Restate the work as:
   - objective
   - non-goals
   - in-scope modules
   - out-of-scope modules
   - invariants that must stay stable

2. Map the affected modules, dependencies, and boot-order assumptions.

3. Decide whether the task should become:
   - one focused implementation thread, or
   - a multi-milestone plan

4. Produce or refresh:
   - `/ai/architecture.md` when the intended structure changed
   - `/ai/repo_map.md` when file ownership or module boundaries changed
   - `/ai/plans/current_plan.md` for milestone sequencing
   - `/ai/task_breakdown.md` for the immediate next execution thread
   - `/ai/decision_log.md` when a durable choice was made

5. Prefer explicit architecture over abstraction theater.
   - Do not introduce patterns that hide behavior without a clear gain.
   - Preserve the repo’s existing style unless a real architecture problem requires change.

## Output requirements

End with:
- key design decisions
- files/modules likely to change in implementation
- risks or unknowns
- the exact next thread to start

## Default constraint

Do **not** write product code unless the user explicitly asked for implementation along with planning.

