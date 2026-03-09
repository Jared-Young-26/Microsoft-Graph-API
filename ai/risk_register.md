# Risk Register

Tracks known technical and security risks in the project.

Fields:
- ID
- Risk description
- Severity (P0–P3)
- Area
- Status
- Mitigation
- Owner
- Last reviewed

## RISK-001
Description: Static file exposure through Flask and FastAPI routes.
Severity: P0
Area: admin_gui backend
Status: Mitigated
Mitigation: Shared explicit allowlist now governs Flask/FastAPI browser serving, and focused allow/deny tests cover backend/state/static probes.
Owner: completed 2026-03-07 allowlist thread
Last reviewed: 2026-03-07

## RISK-002
Description: Human privileged routes lacked a shared server-side operator authentication boundary.
Severity: P0
Area: authentication
Status: Mitigated
Mitigation: `admin_gui/backend/operator_auth.py` now enforces a shared `X-Operator-Token` guard in Flask and FastAPI, and focused protected/exempt regression tests cover the boundary.
Owner: completed 2026-03-07 operator-auth thread
Last reviewed: 2026-03-07

## RISK-004
Description: Frontend profile and Action Pack persistence can store secret-like values in `localStorage`.
Severity: P1
Area: frontend security
Status: Mitigated
Mitigation: `admin_gui/persistence_security.js` now strips `client_secret` and secret-like Action Pack keys from browser persistence and sanitizes existing stored data on load.
Owner: completed 2026-03-07 persistence-cleanup thread
Last reviewed: 2026-03-07

## RISK-003
Description: Inconsistent cache-busting between Flask and FastAPI asset routes.
Severity: P2
Area: frontend asset delivery
Status: Mitigated
Mitigation: Flask and FastAPI now share `admin_gui/backend/frontend_shell.py`, which renders the SPA shell with one shared boot-asset `?v=` version token, and focused regression tests cover both transports.
Owner: completed 2026-03-07 cache-busting parity thread
Last reviewed: 2026-03-07

## RISK-005
Description: `service_shells.js` renders runner help items with `innerHTML`.
Severity: P3
Area: frontend security
Status: Mitigated
Mitigation: `renderRunnerInfo()` now uses constrained DOM/text rendering via `parseRunnerInfoItemMarkup()`/`renderRunnerInfoItem()` and no longer inserts help items with `innerHTML`; focused tests cover formatting preservation and guard against `innerHTML` reintroduction.
Owner: completed 2026-03-07 sink-hardening thread
Last reviewed: 2026-03-07
