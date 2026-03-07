# Constraints

These are hard rules for Codex work in this repository.

## Global Constraints

1. Do not rewrite the project into a framework unless explicitly instructed.
2. Preserve the current backend/API contracts unless the task explicitly requires backend changes.
3. Prefer incremental refactors over large rewrites.
4. Keep changes scoped to the active task.
5. Do not rename stable files, IDs, selectors, or interfaces without documenting the reason.
6. Preserve existing functionality unless the task explicitly changes behavior.
7. Avoid introducing new dependencies unless there is a strong justification.
8. Favor readability and maintainability over cleverness.
9. Update relevant AI documents when architecture or workflow assumptions change.
10. If the repo contains generated or mirrored content, do not manually edit those files unless explicitly told to do so.

## Graph Admin Studio Specific Constraints

1. Keep the portal in vanilla HTML/CSS/JS unless explicitly approved otherwise.
2. Do not churn backend plumbing unnecessarily.
3. Preserve stable workspace identifiers and data attributes.
4. Prefer templating only where repetition is real and semantics remain clear.
5. Preserve the distinct identity of bespoke modules that should not be flattened into generic shells.
6. Do not break boot order or initialization assumptions.
7. If a hard dependency exists between files, document it explicitly in `architecture.md` and `repo_map.md`.

## Safety Rules for Changes

Before making edits, verify:

- What files are in scope?
- What files are out of scope?
- What behavior must remain unchanged?
- What IDs/classes/selectors/contracts must remain stable?

If any of the above are unclear, document assumptions in the handoff instead of improvising.