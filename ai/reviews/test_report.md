# Test Report

## 2026-03-08 Nightly Regression Triage Sweep

### Scope
- Re-run the canonical validation entrypoint for the currently active risky surface (frontend boot shell + backend allowlist/auth/cache-busting regression subset).
- Confirm no regressions after the latest local worktree changes.

### Environment
- Date: 2026-03-08 EST
- Workspace: `/Users/jaredyoung/Documents/Programs/GitHub/Microsoft-Graph-API`
- Node: `v24.9.0`
- Python: `3.11.6`

### Cases Executed
1. `npm run validate`
2. `node -e "try{require('playwright');...}catch(...)"` (availability probe)

### Results
- PASS: `npm run validate` completed with `failures=0 skipped=0`.
- PASS: Frontend Node suites passed (`help_center`, `investigation_summary`, `json_inspector`, `next_steps`, `persistence_security`, `portal_schema`, `service_shells`, `triage`).
- PASS: Frontend syntax checks passed (`app.js`, `portal_schema.js`, `service_shells.js`, `persistence_security.js`).
- PASS: Backend unittest hardening subset passed (`24` tests):
  - `admin_gui.backend.test_browser_allowlist`
  - `admin_gui.backend.test_operator_auth`
  - `admin_gui.backend.test_flask_app_cache_busting`
  - `admin_gui.backend.test_fastapi_app_cache_busting`

### Coverage Gaps
- Playwright/browser validation was not run because Playwright is not installed in this workspace (`PLAYWRIGHT_MISSING`).
- This sweep intentionally reused the canonical validation subset and did not expand into broader backend integration/e2e flows.

### Confidence
- High for the current active validation surface and known high-risk regression paths covered by the canonical runner.

## 2026-03-08 Validation Workflow Entrypoint Verification

### Scope
- Validate the new canonical validation workflow introduced by `scripts/validate.sh` and `npm run validate`.
- Confirm the entrypoint executes the expected frontend suites, frontend syntax checks, and backend unittest hardening subset with explicit outcome reporting.

### Environment
- Date: 2026-03-08 EST
- Workspace: `/Users/jaredyoung/Documents/Programs/GitHub/Microsoft-Graph-API`
- Node: `v24.9.0`
- Python: `3.11.6`

### Cases Executed
1. `npm run validate`

### Results
- PASS: Frontend Node suites passed:
  - `help_center.test.js`
  - `investigation_summary.test.js`
  - `json_inspector.test.js`
  - `next_steps.test.js`
  - `persistence_security.test.js`
  - `portal_schema.test.js`
  - `service_shells.test.js`
  - `triage.test.js`
- PASS: Frontend syntax checks passed for `app.js`, `portal_schema.js`, `service_shells.js`, and `persistence_security.js`.
- PASS: Backend unittest hardening subset passed (`24` tests):
  - `admin_gui.backend.test_browser_allowlist`
  - `admin_gui.backend.test_operator_auth`
  - `admin_gui.backend.test_flask_app_cache_busting`
  - `admin_gui.backend.test_fastapi_app_cache_busting`
- PASS: Runner summary reported `failures=0 skipped=0`.

### Notes
- This run verified the new validation entrypoint behavior itself; it did not add browser automation or broader backend suite coverage outside the chosen canonical subset.

## 2026-03-07 Nightly Regression Triage Validation Sweep

### Scope
- Re-validate the current active task area: `service_shells.js` help-item sink hardening (`RISK-005` mitigation).
- Confirm no immediate regression in the focused parser/render path and source syntax.

### Environment
- Date: 2026-03-07 EST
- Workspace: `/Users/jaredyoung/Documents/Programs/GitHub/Microsoft-Graph-API`
- Node: `v24.9.0`

### Cases Executed
1. `node admin_gui/service_shells.test.js`
2. `node --check admin_gui/service_shells.js`

### Results
- PASS: `service_shells.test.js` passed (`service shell tests passed`).
- PASS: `service_shells.js` passed Node syntax check.

### Coverage Gaps
- Playwright/browser automation was not executed because Playwright is not installed in this workspace (`require('playwright')` failed).
- This run did not re-execute broader frontend/backend suites because the active task scope is limited to `service_shells` sink hardening.

### Confidence
- High for the active-task scoped regression surface; medium for broader cross-module regressions not exercised in this sweep.

## 2026-03-07 Post-Implementation Verification Rerun

### Scope
- Re-verify the completed `service_shells.js` help-item sink hardening change.
- Add broader frontend regression confidence by re-running the full existing Node frontend suite.

### Environment
- Date: 2026-03-07 EST
- Workspace: `/Users/jaredyoung/Documents/Programs/GitHub/Microsoft-Graph-API`
- Node: `v24.9.0`

### Cases Executed
1. `node admin_gui/help_center.test.js`
2. `node admin_gui/investigation_summary.test.js`
3. `node admin_gui/json_inspector.test.js`
4. `node admin_gui/next_steps.test.js`
5. `node admin_gui/persistence_security.test.js`
6. `node admin_gui/portal_schema.test.js`
7. `node admin_gui/service_shells.test.js`
8. `node admin_gui/triage.test.js`
9. `node --check admin_gui/service_shells.js`

### Results
- PASS: All 8 frontend Node test files passed.
- PASS: `service_shells.test.js` still passes with the new constrained runner-info markup parser and no-`innerHTML` guard.
- PASS: `service_shells.js` passes Node syntax check.

### Coverage Gaps
- No browser-driven DOM verification was rerun in this pass; confidence relies on deterministic Node suites.
- No backend tests were rerun because this implementation did not touch backend code.

### Confidence
- High for the scoped frontend sink-hardening change and related frontend regression surface.

## 2026-03-07 Service-Shell Help-Item Sink Hardening Validation

### Scope
- Validate the `service_shells.js` help-item sink hardening change in `admin_gui/service_shells.js` and its focused tests in `admin_gui/service_shells.test.js`.
- Focus areas: replacing `innerHTML` insertion, preserving expected inline help formatting behavior, and syntax safety.

### Environment
- Date: 2026-03-07 EST
- Workspace: `/Users/jaredyoung/Documents/Programs/GitHub/Microsoft-Graph-API`
- Node: `v24.9.0`

### Cases Executed
1. `node admin_gui/service_shells.test.js`
2. `node --check admin_gui/service_shells.js`

### Results
- PASS: Runner help items no longer use `innerHTML` insertion in `service_shells.js`.
- PASS: Parser coverage confirms expected output for existing inline `<strong>`/`<code>` formatting and entity decoding.
- PASS: Source-level guard test confirms `innerHTML` is not present in `service_shells.js`.
- PASS: `service_shells.js` passes Node syntax check.

### Notes
- Validation here is intentionally focused and does not include a browser automation run because the change is isolated to deterministic DOM construction logic covered by the Node suite.

## 2026-03-07 FastAPI Boot-Asset Cache-Busting Parity Validation

### Scope
- Validate the FastAPI boot-asset cache-busting parity change across `admin_gui/backend/frontend_shell.py`, `admin_gui/backend/flask_app.py`, `admin_gui/backend/fastapi_app.py`, and the existing boot-contract tests.
- Focus areas: shared shell HTML versioning, preserved browser allowlist behavior, and regression safety for the current frontend boot path.

### Environment
- Date: 2026-03-07 EST
- Workspace: `/Users/jaredyoung/Documents/Programs/GitHub/Microsoft-Graph-API`
- Python: `3.11.6`
- Node: `v24.9.0`

### Cases Executed
1. `python3 -m unittest admin_gui.backend.test_flask_app_cache_busting admin_gui.backend.test_fastapi_app_cache_busting admin_gui.backend.test_browser_allowlist`
2. `node admin_gui/portal_schema.test.js`
3. `node admin_gui/service_shells.test.js`
4. `node --check admin_gui/app.js`

### Results
- PASS: Flask and FastAPI both served SPA shell HTML with one shared version token across `styles.css`, `portal_schema.js`, `service_shells.js`, `persistence_security.js`, and `app.js`.
- PASS: FastAPI kept the existing browser allowlist behavior while switching shell responses from raw `index.html` to the shared rendered shell.
- PASS: Existing `portal_schema` and `service_shells` contract tests still passed, so the shell-versioning change did not disturb the frontend boot path.
- PASS: `admin_gui/app.js` still passed a Node syntax check after the transport-only backend change.

### Notes
- The FastAPI test harness patched the local multipart dependency check during import because this workspace does not have `python-multipart`; product code and route behavior were not changed.
- This validation targeted backend shell rendering parity and boot-contract safety; it did not include a live browser hard-refresh smoke test against the FastAPI runtime.

## 2026-03-07 Frontend Secret-Persistence Validation

### Scope
- Validate the frontend secret-persistence cleanup across `admin_gui/app.js`, `admin_gui/persistence_security.js`, `admin_gui/index.html`, and the Flask/FastAPI boot-asset allowlist/cache-busting path.
- Focus areas: profile persistence/export/import sanitization, Action Pack param/history sanitization, helper boot wiring, and regression safety for existing frontend contracts.

### Environment
- Date: 2026-03-07 EST
- Workspace: `/Users/jaredyoung/Documents/Programs/GitHub/Microsoft-Graph-API`
- Python: `3.11.6`
- Node: `v24.9.0`

### Cases Executed
1. `node admin_gui/persistence_security.test.js`
2. `node --check admin_gui/app.js`
3. `python3 -m unittest admin_gui.backend.test_browser_allowlist admin_gui.backend.test_flask_app_cache_busting`
4. `node admin_gui/portal_schema.test.js`
5. `node admin_gui/service_shells.test.js`

### Results
- PASS: The persistence helper removed `client_secret` from profile config persistence and removed secret-like keys from Action Pack saved params/history while preserving non-secret values.
- PASS: `admin_gui/app.js` passed a syntax check after switching profile and Action Pack storage paths to sanitized persistence.
- PASS: Flask and FastAPI both served the new `persistence_security.js` boot asset through the existing allowlist, and Flask cache-busted it alongside the rest of the boot assets.
- PASS: Existing frontend contract tests for `portal_schema` and `service_shells` still passed after the new helper was added to the boot path.

### Notes
- The FastAPI test harness patched the local multipart dependency check during import because this workspace does not have `python-multipart`; product code and route behavior were not changed.
- The focused regression coverage here targets the persistence sanitization logic directly plus boot/syntax safety around `app.js`; it does not include a browser-driven profile/import/export interaction run.

## 2026-03-07 Operator Auth Validation

### Scope
- Validate the shared operator-token guard across `admin_gui/backend/operator_auth.py`, `admin_gui/backend/flask_app.py`, `admin_gui/backend/fastapi_app.py`, and the minimal frontend request-layer changes in `admin_gui/app.js`.
- Focus areas: protected human-route rejection, exempt agent/machine-ingest behavior, preserved terminal-session boundaries, and basic frontend boot/syntax safety.

### Environment
- Date: 2026-03-07 EST
- Workspace: `/Users/jaredyoung/Documents/Programs/GitHub/Microsoft-Graph-API`
- Python: `3.11.6`
- Node: `v24.9.0`

### Cases Executed
1. `python3 -m unittest admin_gui.backend.test_operator_auth`
2. `python3 -m unittest admin_gui.backend.test_browser_allowlist admin_gui.backend.test_flask_app_cache_busting`
3. `node admin_gui/portal_schema.test.js`
4. `node admin_gui/service_shells.test.js`
5. `node --check admin_gui/app.js`

### Results
- PASS: Flask and FastAPI both rejected protected `POST /api/task` requests when `X-Operator-Token` was missing or invalid.
- PASS: Flask and FastAPI both allowed protected `POST /api/task` requests with a valid operator token to reach the existing handler path.
- PASS: Exempt routes stayed separate from operator auth: agent registration, agent terminal-session lease, and machine visual-signal ingest still worked on their existing paths without an operator token.
- PASS: `POST /api/terminal/{agent_id}/start` still required `interactive_scope=true` even after operator auth succeeded, preserving the existing terminal-start boundary.
- PASS: Existing Flask/FastAPI browser allowlist and Flask cache-busting regression coverage still passed after the transport hooks were added.
- PASS: `admin_gui/app.js` passed a Node syntax check, and the existing `portal_schema` / `service_shells` frontend contract suites still passed.

### Notes
- The FastAPI test harness patched the local multipart dependency check during import because this workspace does not have `python-multipart`; product code and route behavior were not changed.
- The frontend unlock flow was validated here as request-layer behavior plus syntax/boot safety, not via a live browser prompt automation run.

## 2026-03-07 Backend Browser Allowlist Validation

### Scope
- Validate the explicit browser allowlist across `admin_gui/backend/flask_app.py`, `admin_gui/backend/fastapi_app.py`, and `admin_gui/backend/frontend_allowlist.py`.
- Focus areas: allowed SPA shell routes, allowed boot/help/install files, and denied backend/state/source/static-alias paths.

### Environment
- Date: 2026-03-07 EST
- Workspace: `/Users/jaredyoung/Documents/Programs/GitHub/Microsoft-Graph-API`
- Python: `3.11.6`

### Cases Executed
1. `python3 -m unittest admin_gui.backend.test_browser_allowlist admin_gui.backend.test_flask_app_cache_busting`

### Results
- PASS: Flask and FastAPI both served `/`, `/index.html`, `/help`, `/help/*`, `/investigations`, and `/workspaces`.
- PASS: Both backends served the boot-critical root assets, `docs/help/help_manifest.json`, `docs/help/security.md`, and `install/windows.ps1`.
- PASS: Both backends denied representative backend/state/source probes including `/backend/config.json`, `/backend/control_plane.sqlite`, `/backend/flask_app.py`, `/README.md`, `/json_inspector.js`, and the old `/static/*` alias paths.
- PASS: Flask's existing cache-busting regression still passed alongside the new allowlist coverage.

### Notes
- The FastAPI test harness patched the local multipart dependency check during import because this workspace does not have `python-multipart`; product code and route behavior were not changed.

## Scope
- Validate the schema-driven service-shell refactor across `admin_gui/index.html`, `admin_gui/app.js`, `admin_gui/styles.css`, `admin_gui/portal_schema.js`, and `admin_gui/service_shells.js`
- Focus areas: behavior correctness, regressions, DOM stability, workflow behavior, and output/render correctness

## Environment
- Date: 2026-03-06 EST
- Workspace: `/Users/jaredyoung/Documents/Programs/GitHub/Microsoft-Graph-API`
- Node: `v24.9.0`
- Repo dependency check: `jsdom@28.0.0`
- Browser validation: Playwright against Flask at `http://127.0.0.1:8001/`
- Backend launch command: `.venv/bin/python -m admin_gui.backend.flask_app`

## Cases Executed
1. Frontend JS tests:
   - `node admin_gui/help_center.test.js`
   - `node admin_gui/investigation_summary.test.js`
   - `node admin_gui/json_inspector.test.js`
   - `node admin_gui/next_steps.test.js`
   - `node admin_gui/portal_schema.test.js`
   - `node admin_gui/service_shells.test.js`
   - `node admin_gui/triage.test.js`
2. Browser boot validation in Playwright against the Flask app.
3. DOM stability check:
   - confirmed all `[data-service-shell]` mounts were replaced
   - confirmed `GraphAdminServiceShells.validateRenderedServiceShells(document, SERVICE_SHELLS)` returned `[]`
4. Shared-panel navigation checks:
   - `incidents` -> `reports`
   - `healthcheck` -> `settings`
5. Action-surface workflow checks:
   - `exchange` shell renders one runner, one action select, one field container, and one output surface
   - clicking the Exchange `list_messages` chip selects the matching runner action
6. Dashboard workflow check:
   - clicking `Open Help` transitions to Help and updates the route to `/help`

## Results
- PASS: All 7 frontend JS test files passed.
- PASS: Browser booted successfully against Flask with no Playwright console errors at `error` level.
- PASS: No leftover `[data-service-shell]` mounts remained after render.
- PASS: Shared-panel sections updated title, subtitle, mode, and focused-surface context correctly:
  - `incidents` showed `Reports`
  - `healthcheck` showed `Settings`
- PASS: Standalone action section `exchange` preserved runner/output hooks and chip-to-runner selection behavior.
- PASS: Dashboard quick action `Open Help` navigated to Help and updated the route to `/help`.
- FAIL: None in the target implementation.

## Notes
- An initial dry run under `python3 -m http.server` produced `/api/*` 404s because the static server does not implement backend routes. This was environment noise, not a product regression; browser validation was rerun against the Flask app.
- The single `POST /api/task` seen during the Flask browser session was traced to the existing `system.tenant_info` background request issued from `fetchConfig()` during load, not to a service-shell interaction regression.
- Live action execution against configured Graph credentials or PowerShell runners was not exercised in this thread.
- Recommended debugger thread prompt: Not needed for the validated implementation. Optional deeper follow-up if desired:
  `ROLE: Debug Engineer

  Run action-execution smoke tests for the schema/service-shell refactor using the Flask app and a configured local Graph/PowerShell environment. Focus on chip-triggered runner selection, run-now actions, output rendering, and any regressions between templated service shells and bespoke panels. Document any failures with exact repro steps and root cause.`
