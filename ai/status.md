# Project Status

## Current milestone
Post-frontend-refactor backend hardening staged into focused, reviewable threads.

## Current active workstream
Restrict Flask and FastAPI browser-serving paths to an explicit frontend asset allowlist. This remains the next implementation thread because it closes the clearest `P0` trust-boundary gap without waiting on a new architecture decision. See `/ai/active_task.md`.

## Recently completed
- 2026-03-06: Flask boot-asset cache busting was expanded to `portal_schema.js` and `service_shells.js`, and a focused regression test was added.
- 2026-03-06: the frontend contract validation thread passed 7 direct Node suites plus a Playwright smoke check against Flask.
- 2026-03-07: readability refactors landed in `admin_gui/portal_schema.js`, `admin_gui/service_shells.js`, and `admin_gui/app.js` without changing stable frontend hooks.
- 2026-03-07: the repo-root AGENTS/skills operating system was installed and the durable-memory docs were synced to the live repo state.

## Current blockers
- Flask SPA fallback plus FastAPI SPA fallback and `/static` mount all resolve arbitrary files under `admin_gui/`, while local runtime state still lives under `admin_gui/backend/`.
- Human/operator mutation routes still rely on local-listener trust, but the smallest shared server-side auth model is still undecided.
- FastAPI still lacks Flask's shared `?v=` boot-asset rewrite behavior.

## Next recommended tasks
- Land the static-file allowlist thread first in Worktree mode.
- Then run a separate architecture thread for shared server-side operator auth/authorization on human mutation routes.
- After that, bring FastAPI boot-asset versioning to parity with Flask and keep focused backend tests beside the Node boot-contract coverage.

## Docs that may need refresh
- Refresh `architecture.md`, `repo_map.md`, and `handoff.md` after the allowlist thread lands, especially if the final allowed asset/deep-link set differs from current assumptions.
- Refresh the security report state after the arbitrary-file exposure finding is closed.

## Notes
- The highest-severity known risks are documented in `/ai/reviews/security_report.md`.
- The broader backend-hardening umbrella was intentionally narrowed on 2026-03-07 so the next implementation thread can close one P0 exposure in a single pass.
