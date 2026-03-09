# Security Report

## Scope
- Date: 2026-03-07 (EST)
- Reviewed the completed `service_shells.js` help-item sink hardening change in `admin_gui/service_shells.js` and focused coverage in `admin_gui/service_shells.test.js`.
- Focused on DOM injection/XSS risk, trust-boundary assumptions for help-item content, and regression risk of sink reintroduction.

## Trust Boundaries Reviewed
- Help-item source boundary:
  - Current source is static registry metadata in `SERVICE_SHELLS` inside `admin_gui/service_shells.js`.
  - No external/user-controlled source is currently wired into `runner.info.items`.
- Rendering boundary:
  - `renderRunnerInfo()` now delegates to `renderRunnerInfoItem()` and uses explicit DOM/text node creation.
  - No `innerHTML` path remains in this file.

## Findings
### High
- None.

### Medium
- None.

### Low
- None in current scoped implementation.

## Plausible Risks Needing Follow-Up
- If future threads make `runner.info.items` data-driven (config/API/user input), preserve the current constrained parser model and avoid generic HTML rendering.
- Current parser intentionally supports only `<strong>`, `<code>`, and specific entities for compatibility; any expansion of supported markup should receive security review before landing.

## Non-Issues Ruled Out
- Raw HTML injection via help-item strings in `service_shells.js` is no longer present.
- Unknown tags in help-item strings are rendered as text, not interpreted markup.

## Resolved Since Last Review
- 2026-03-07: closed the low-severity runner help-item HTML sink (`RISK-005`). `renderRunnerInfo()` no longer inserts `infoMeta.items` via `innerHTML`; help items now render through constrained DOM/text construction that supports the existing inline `<strong>` / `<code>` formatting and known entities.
- 2026-03-07: Flask and FastAPI share `admin_gui/backend/frontend_shell.py`, so both transports serve the SPA shell with the same versioned boot assets and no longer drift on cache behavior.
- 2026-03-07: frontend secret-persistence cleanup removed `client_secret` and secret-like Action Pack fields from browser persistence paths.
- 2026-03-07: shared operator-token enforcement for protected human mutation routes landed across Flask and FastAPI.
- 2026-03-07: shared explicit browser allowlist closed arbitrary frontend-file exposure in both transports.

## Notes
- Validation run for this review scope:
  - `node admin_gui/service_shells.test.js`
  - `node --check admin_gui/service_shells.js`
- Evidence references:
  - `admin_gui/service_shells.js`: `parseRunnerInfoItemMarkup()`, `renderRunnerInfoItem()`, and `renderRunnerInfo()` help-item path.
  - `admin_gui/service_shells.test.js`: parser behavior assertions + source guard asserting `innerHTML` absence.
- Residual risk:
  - Low. Risk is primarily future-regression risk if unconstrained HTML rendering is reintroduced.
