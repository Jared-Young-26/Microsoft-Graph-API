# Test Report

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
