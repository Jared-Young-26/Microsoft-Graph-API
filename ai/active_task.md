# Active Task

## Title
Restrict Flask and FastAPI browser-serving paths to an explicit frontend asset allowlist

## Goal
Close direct browser access to `admin_gui/backend/` runtime state and other non-frontend files by replacing the current Flask catch-all and FastAPI catch-all plus `/static` file-serving behavior with an explicit allowlist that still preserves the SPA shell, boot assets, and supported deep links.

## Why This Task Now
- `ai/risk_register.md` tracks this as `RISK-001`, a `P0` exposure that is already narrowed to one implementation-ready thread.
- The scope is bounded to the backend browser-serving boundary plus focused tests, so it is the smallest high-value step that can close a live trust-boundary gap.
- The other open `P0` on operator auth still needs a separate server-side trust-model decision and should not be bundled into this pass.

## In Scope
- `admin_gui/backend/flask_app.py`
- `admin_gui/backend/fastapi_app.py`
- a small shared helper only if it keeps allowlist behavior aligned across both transports
- focused backend tests for allowed frontend assets and denied backend/state paths
- `/ai/*` docs touched by the thread

## Out of Scope
- server-side operator auth/authorization for human mutation routes
- FastAPI cache-busting/version parity beyond what is required to keep current boot assets reachable
- moving runtime state out of `admin_gui/backend/`
- frontend redesign, DOM changes, or script-order changes

## Invariants
- Preserve current boot asset filenames and the `index.html` script order.
- Preserve `/`, `/help`, `/help/*`, `/investigations`, and `/workspaces` as supported browser entrypoints.
- Keep Flask and FastAPI aligned on which browser-served paths are allowed, including FastAPI's `/static/*` surface.
- Do not change API payload shapes, agent-token behavior, or WebSocket SSH behavior in this thread.

## Inputs
- `ai/reviews/security_report.md`
- `ai/architecture.md`
- `ai/repo_map.md`
- `admin_gui/index.html`
- `admin_gui/docs/help/`
- `admin_gui/install/windows.ps1`
- current browser-serving behavior in `admin_gui/backend/flask_app.py` and `admin_gui/backend/fastapi_app.py`, including FastAPI's `/static` mount

## Deliverables
- an explicit browser asset/deep-link allowlist for both backend entrypoints
- denied access to representative backend config/db/log/source paths
- focused regression tests covering allow vs. deny behavior
- updated status/handoff/docs as needed

## Done When
Requests such as `/backend/config.json`, `/backend/control_plane.sqlite`, `/static/backend/config.json`, and other non-frontend source/state paths are denied in both Flask and FastAPI, while `/`, `/help`, `/help/*`, `/investigations`, `/workspaces`, boot-critical JS/CSS assets, and required help/install files still resolve correctly.
