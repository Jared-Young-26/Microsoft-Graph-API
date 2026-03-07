# Security Report

## Scope
- Reviewed the frontend refactor around `admin_gui/index.html`, `admin_gui/app.js`, `admin_gui/portal_schema.js`, and `admin_gui/service_shells.js`.
- Traced the backend trust boundary in `admin_gui/backend/flask_app.py` and `admin_gui/backend/control_plane.py`.
- Focused on unsafe DOM insertion, injection, auth/authorization assumptions, admin-action exposure, unvalidated inputs, and client-side trust.

## Findings
### High
- Server-side auth does not enforce the new Observe/Act boundary.
  - Evidence: `admin_gui/portal_schema.js:21` through `admin_gui/portal_schema.js:120` define `observe` and `act` as UI metadata, and `admin_gui/app.js:17613` through `admin_gui/app.js:17695` only use that metadata to change navigation/header state. Action execution is sent with a bare `fetch("/api/task", ...)` in `admin_gui/app.js:22923` through `admin_gui/app.js:22940`, with no operator credential attached. On the backend, mutating operator routes such as `POST /api/config`, `POST /api/config/reload`, `POST /api/pairing-codes`, `POST /api/jobs/enqueue`, `POST /api/actionpacks/v2/run`, and `POST /api/task` do not call any auth guard (`admin_gui/backend/flask_app.py:149` through `admin_gui/backend/flask_app.py:167`, `admin_gui/backend/flask_app.py:196` through `admin_gui/backend/flask_app.py:207`, `admin_gui/backend/flask_app.py:402` through `admin_gui/backend/flask_app.py:469`, `admin_gui/backend/flask_app.py:630` through `admin_gui/backend/flask_app.py:675`). By contrast, only agent routes call `_require_agent_auth()` (`admin_gui/backend/flask_app.py:179` through `admin_gui/backend/flask_app.py:182`, `admin_gui/backend/flask_app.py:211` through `admin_gui/backend/flask_app.py:231`). Agent registration also only requires a pairing code when `CONTROL_PLANE_REQUIRE_PAIRING_CODE` is enabled (`admin_gui/backend/control_plane.py:481` through `admin_gui/backend/control_plane.py:486`).
  - Impact: any process or user that can reach the local listener can mutate configuration, run admin tasks, enqueue control-plane jobs, or mint agent bootstrap material. The UI's Observe/Act split is presentational, not a permission boundary.
  - Remediation: add explicit operator auth/authorization middleware for all human/UI routes; reject mutating requests without an authenticated operator context; add CSRF and Origin protections if browser-based auth is introduced; require a server-side bootstrap policy for agent enrollment regardless of client behavior.

- The SPA fallback serves arbitrary files from `admin_gui/`, including backend code and local data stores.
  - Evidence: `ROOT = Path(__file__).resolve().parents[1]` points at `admin_gui` (`admin_gui/backend/flask_app.py:59`), and `spa_fallback()` returns any existing file under `ROOT` via `send_from_directory(str(ROOT), path, ...)` (`admin_gui/backend/flask_app.py:1369` through `admin_gui/backend/flask_app.py:1383`). The current tree under `admin_gui/backend/` includes `config.json`, `control_plane.sqlite`, `snapshots.sqlite`, `action_snapshots.sqlite`, and `audit_log.jsonl`.
  - Impact: a direct GET to paths like `/backend/config.json` or `/backend/control_plane.sqlite` would disclose local control-plane data, audit material, and potentially secrets if the service is reachable.
  - Remediation: restrict static serving to an allowlisted frontend asset set; explicitly deny `backend/`, source files, databases, logs, and config files; keep downloads behind authenticated routes instead of the SPA fallback.

### Medium
- None.

### Low
- `service_shells.js` adds a new HTML injection sink for runner help items.
  - Evidence: `renderRunnerInfo()` writes `infoMeta.items` into the DOM with `li.innerHTML = item` (`admin_gui/service_shells.js:808` through `admin_gui/service_shells.js:820`).
  - Impact: today the values are hard-coded strings in the local registry, so exploitability is limited. If those help items ever become imported, user-editable, or otherwise data-driven, this becomes a direct XSS path inside an admin portal.
  - Remediation: replace HTML strings with structured data rendered via `textContent` and DOM nodes, or sanitize against a very small allowlist of tags before insertion.

## Notes
- Validation run:
  - `node admin_gui/portal_schema.test.js`
  - `node admin_gui/service_shells.test.js`
- Both validation commands passed.
- A lightweight Flask test-client probe was attempted for runtime confirmation, but the active Python environment in this workspace does not have `flask` installed. Backend findings above are therefore based on static code review rather than executed requests.
- No additional change-specific DOM sinks stood out in the new schema boot path beyond the `service_shells.js` help-item insertion noted above.
