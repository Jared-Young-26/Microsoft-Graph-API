# Active Task

## Title
Codify repeatable validation entrypoints for frontend and backend checks

## Goal
Create one lightweight, repo-native validation workflow that runs the canonical frontend Node suites and the key backend Python suites with clear prerequisites/fallback messaging, so implementation threads no longer guess which checks to run.

## Status
Completed on 2026-03-08.

## Why This Task Now
- `ai/risk_register.md` shows P0/P1 hardening risks as mitigated; the highest practical follow-through is reducing verification drift.
- `ai/status.md` identifies validation workflow codification as the next recommended task.
- The scope is small, low ambiguity, and can complete in one focused thread.

## In Scope
- a lightweight validation entrypoint (script and/or npm task) that orchestrates existing direct commands
- explicit frontend command set (`node admin_gui/*.test.js` and selected `node --check` guards)
- explicit backend command set (`python3 -m unittest ...`) with clear environment prerequisite notes
- brief docs updates that point contributors to the new canonical validation path

## Out of Scope
- product feature changes in `admin_gui/app.js` or backend route logic
- CI pipeline redesign
- dependency/platform migration work
- broad test refactors or new end-to-end suites

## Invariants
- Preserve existing test behavior and command semantics; wrap, do not reinterpret.
- Keep Flask/FastAPI coverage expectations aligned.
- Do not change stable frontend IDs/selectors/contracts.
- Do not introduce heavy new tooling.

## Deliverables
- One obvious command path to run the canonical validation subset for normal implementation threads.
- Clear pass/fail output that distinguishes skipped backend checks due to missing local prerequisites.
- `/ai` docs updated with the canonical validation path and known environment constraints.

### Delivered
- `scripts/validate.sh` now runs a canonical frontend suite, frontend syntax checks, and a backend unittest subset with explicit run/pass/fail/skip logging.
- `package.json` now provides `npm run validate`, `npm run validate:frontend`, and `npm run validate:backend`.
- `README.md` now documents the canonical validation entrypoint and backend prerequisites/skip behavior.
- validation evidence for the new entrypoint was recorded in `ai/reviews/test_report.md`.

## Validation
- Run the new validation entrypoint directly.
- Confirm it executes the expected frontend and backend suites in this environment (including prerequisite handling behavior).

## Done
- A fresh contributor can identify and run the canonical validation command without guessing.
- Frontend and backend verification commands are discoverable in one place and consistent with existing test files.
