# Project Status

## Current milestone
Post-hardening verification hygiene established: canonical validation entrypoint is now in place for frontend and backend checks.

## Current active workstream
No active implementation thread. The validation-workflow codification task completed on 2026-03-08.

## Recently completed
- 2026-03-09: nightly triage reran `npm run validate` and confirmed canonical frontend + backend validation still passes in this environment (`failures=0`, `skipped=0`).
- 2026-03-08: added canonical validation entrypoints via `scripts/validate.sh` and `npm run validate` (`validate:frontend` / `validate:backend`), documented in `README.md`, and verified end-to-end in this environment.
- 2026-03-07: `service_shells.js` runner help-item rendering no longer uses `innerHTML`; it now renders via constrained structured DOM/text output, with focused parser coverage and a source-level guard against `innerHTML` reintroduction.
- 2026-03-07: FastAPI boot-asset cache-busting reached parity with Flask. Both transports now share `admin_gui/backend/frontend_shell.py`, serve versioned SPA shell assets, and have focused Flask/FastAPI cache-busting regression coverage.
- 2026-03-07: the frontend secret-persistence cleanup landed. `client_secret` was removed from profile save/export/import persistence, Action Pack saved params/history now strip secret-like keys, existing browser data is sanitized on load, and a small boot helper (`persistence_security.js`) plus focused regression coverage were added.
- 2026-03-07: the shared operator-token guard landed in `admin_gui/backend/operator_auth.py`, both backends now enforce `X-Operator-Token` on protected human mutation routes, the frontend sends the token from memory only, and focused protected/exempt tests passed in both transports.
- 2026-03-07: Flask and FastAPI browser serving were restricted to a shared explicit allowlist, FastAPI's broad `/static` mount was removed, and focused allow/deny regression tests landed.
- 2026-03-06: the frontend contract validation thread passed 7 direct Node suites plus a Playwright smoke check against Flask.
- 2026-03-07: readability refactors landed in `admin_gui/portal_schema.js`, `admin_gui/service_shells.js`, and `admin_gui/app.js` without changing stable frontend hooks.

## Current blockers
- There is a large uncommitted hardening/docs batch in the working tree; merge/review risk increases until it is split or committed.

## Next recommended tasks
- Start a fresh implementation thread on the highest-value remaining backlog item (`P1` boot-contract testing or `P1` `app.js` bounded split).
- Keep using `npm run validate` as the canonical pre-review verification path in implementation/debug threads.

## Docs that may need refresh
- Refresh `ai/active_task.md`, `ai/task_breakdown.md`, and `ai/handoff.md` when the next implementation thread is selected.

## Notes
- `ai/risk_register.md` currently documents all listed risks (`RISK-001` to `RISK-005`) as mitigated.
- `service_shells.js` still allows limited inline formatting semantics for local registry help text (`<strong>`, `<code>`, entities), but no longer performs raw HTML insertion.
