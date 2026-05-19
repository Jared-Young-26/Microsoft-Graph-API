# Architecture

This file describes the real current Graph Admin Studio architecture, not an aspirational rewrite.

## Product Shape Today

- Graph Admin Studio is a local-first admin and troubleshooting portal.
- The frontend is intentionally vanilla `index.html` + `styles.css` + `app.js`.
- The backend is a local API/server layer that can run under either Flask or FastAPI.
- Graph is preferred, PowerShell is used when Graph does not cover the action, and agents/control-plane jobs extend execution off-box when needed.
- Observe and Act remain visibly separate. Read-only surfaces must not hide mutation paths.

## Runtime Layers

### 1. Static portal shell

- `admin_gui/index.html` is the single HTML shell.
- `admin_gui/app.js` is the current main runtime.
- `admin_gui/portal_schema.js` defines section/mode/shared-panel metadata.
- `admin_gui/service_shells.js` renders the repeated toolkit/runner/output triplets for standard services.

### 2. Local backend

- `admin_gui/backend/core.py` is the shared backend brain.
- `admin_gui/backend/flask_app.py` and `admin_gui/backend/fastapi_app.py` are transport layers over the same backend/core/control-plane modules.
- `/api/task` is still the main local task-dispatch surface for direct portal actions.
- Snapshot, investigation, incident, audit, health, and control-plane routes live alongside task dispatch in the same backend family.

### 3. Optional control plane and agent runtime

- `admin_gui/backend/control_plane.py` stores agents/jobs/artifacts/terminal sessions in SQLite.
- `agent/` is the remote execution chassis.
- `admin_gui/backend/graph_runner_dispatch.py` can route selected Graph actions to a remote graph-runner agent instead of running locally.
- `admin_gui/backend/workflows_v2.py` runs manifest-driven Action Pack v2 jobs through the control plane.

### 4. Shared platform core

- `platform_core/` supplies the snapshot engine, probe registry, quality scoring, diffing, cache-backed dampers, and Graph error transparency.
- The backend and reporting/investigation flows depend on this layer heavily.

## Frontend Composition

### Shared-panel navigation

- Navigation sections are not always 1:1 with DOM panels.
- `portal_schema.js` maps nav sections onto real panels and optional `scrollTarget`s.
- Current shared-panel examples:
  - `incidents` -> panel `reports`
  - `snapshots` -> panel `reports`
  - `auditlog` -> panel `settings`
  - `healthcheck` -> panel `settings`
  - `quickactions` -> panel `dashboard`
  - `tools`, `actionrequests`, `agents`, `jobs`, `catalog`, `bootstrap`, `vision` -> panel `controlplane`
- If a section or panel changes, update both the schema and the matching DOM target IDs.

### Templated vs bespoke UI

- The service-shell triplet is the right abstraction for standard services with a simple:
  - toolkit card
  - runner card
  - output card
- That abstraction currently covers:
  - `exchange`
  - `onedrive`
  - `sharepoint`
  - `teams`
  - `entra`
  - `azure`
  - `defender`
  - `powerplatform`
  - `purview`
  - `localad`
  - `endpoint`
  - `domaincontroller`
  - `printers`
  - `network`
  - `fileserver`
  - `time`
  - `certificates`
  - `processes`
  - `baselines`
  - `eventlogs`
  - `registry`

- The following surfaces are intentionally bespoke and should not be flattened into the service-shell system:
  - `dashboard`
  - `remote_workflows`
  - `ssh`
  - `topology`
  - `reports`
  - `actionpacks`
  - `investigations`
  - `settings`
  - `controlplane`
  - `workspaces`
  - `help`

### Workspace contracts

- Workspaces persist card placement through stable `data-workspace-block` values.
- Templated services get canonical workspace block IDs from `service_shells.js`.
- `service_shells.js` also carries `legacyWorkspaceBlocks` to avoid breaking older saved layouts.
- Renaming workspace block IDs is a compatibility change, not a cosmetic refactor.

## Mandatory Boot / Load Assumptions

1. The backend must serve `admin_gui/index.html` as the SPA shell.
2. The DOM must already contain:
   - every `data-service-shell="..."` placeholder
   - `#service-shell-template`
   - `#service-shell-chip-template`
   - `#service-shell-note-template`
   - `#service-shell-info-item-template`
3. Script order in `index.html` is a hard contract:
   - `triage.js`
   - `investigation_summary.js`
   - `next_steps.js`
   - `portal_schema.js`
   - `service_shells.js`
   - `persistence_security.js`
   - `app.js`
4. `service_shells.js` must run before `app.js`.
   - It renders the service-shell placeholders immediately when `document` is present.
5. `app.js` does not wait for `DOMContentLoaded`.
   - It executes immediately because scripts are placed at the end of `<body>`.
6. `app.js` hard-fails boot if either of these globals is missing or invalid:
   - `window.GraphAdminPortalSchema`
   - `window.GraphAdminServiceShells`
7. `app.js` also validates that service-shell mount points were replaced correctly before continuing.
8. Deep links rely on backend SPA fallback plus frontend route resolution:
   - `/help/...`
   - `/investigations`
   - `/workspaces`
9. A direct Node boot-contract suite now guards this boundary across `admin_gui/index.html`, `admin_gui/portal_schema.js`, and `admin_gui/service_shells.js`.
   - It checks script order, required service-shell templates/mounts, schema-to-nav/panel alignment, and rendered service-shell validity.

## Backend Serving Notes

- Flask and FastAPI are intended to expose near-parity HTTP APIs over shared backend logic.
- FastAPI is required for the interactive SSH WebSocket flow.
- Flask and FastAPI now share `admin_gui/backend/frontend_shell.py` to rewrite `index.html` with one shared `?v=` token across:
  - `styles.css`
  - `portal_schema.js`
  - `service_shells.js`
  - `persistence_security.js`
  - `triage.js`
  - `investigation_summary.js`
  - `next_steps.js`
  - `app.js`
- Flask and FastAPI now share an explicit browser allowlist via `admin_gui/backend/frontend_allowlist.py`.
- Supported SPA shell entrypoints are `/`, `/index.html`, `/help`, `/help/*`, `/investigations`, and `/workspaces`.
- Allowed browser-served files are restricted to the boot-critical root assets, `docs/help/help_manifest.json`, Markdown help pages under `docs/help/`, and `install/windows.ps1`.
- FastAPI no longer mounts `/static` to the full `admin_gui/` tree; `/static/*` is denied unless a future thread intentionally reintroduces a narrower, allowlist-governed surface.
- Non-frontend source/state paths such as `admin_gui/backend/`, SQLite DBs, config JSON, logs, and stray docs/helpers are denied by default.
- There are focused Flask and FastAPI cache-busting regression tests plus shared Flask/FastAPI browser allowlist regression coverage.

## Backend Boundaries

- `core.py` is the source of truth for:
  - config updates
  - task dispatch
  - audit logging
  - report helpers
  - snapshot capture/history/diff
  - investigations/incidents
  - status/health helpers
  - schedulers/reapers

- `control_plane.py` is the source of truth for:
  - agents
  - pairing codes
  - jobs + job results
  - artifacts
  - terminal sessions

- `workflows_v2.py` is the source of truth for:
  - Action Pack v2 validation
  - risk/capability enforcement
  - agent/job execution for v2 workflows

- `graph_runner_dispatch.py` is the bridge from selected portal actions to remote graph-runner jobs.

## Operator Auth Boundary

Graph Admin Studio now enforces one shared operator-auth layer for human privileged mutation routes in both backend transports.

### Objective

- Protect human/operator mutation and secret-export routes with one shared server-side rule in both Flask and FastAPI.
- Preserve the existing agent-token flows and the FastAPI terminal/WebSocket mechanics.
- Keep the frontend token in memory only and scoped to the current page session.

### Chosen Model

- Credential:
  - Use an explicit operator token supplied out-of-band through an environment variable such as `GAS_OPERATOR_TOKEN`.
  - Human privileged requests must send that token in a dedicated header such as `X-Operator-Token`.
  - The browser UI should prompt once per page load and keep the token in memory only.
  - Do not persist the operator token in `localStorage`, `sessionStorage`, saved profiles, or exported config.

- Server behavior:
  - `admin_gui/backend/operator_auth.py` is the shared helper/module for operator-token extraction, constant-time validation, and route classification.
  - Flask applies the guard via `@app.before_request`; FastAPI applies the same boundary via `@app.middleware("http")`.
  - Protected human requests fail closed with `401` for missing/invalid credentials and `503` when `GAS_OPERATOR_TOKEN` is not configured.

- Browser/CSRF posture:
  - Phase 1 remains header-based and cookie-free.
- `admin_gui/app.js` now prompts for the operator token on the first protected request, stores it in memory only, and attaches it only to same-origin protected mutating `/api/*` requests.
- Passive page boot no longer auto-runs the background tenant-info `POST /api/task` call until the operator token has been entered, which avoids prompting on initial page load.
- `admin_gui/persistence_security.js` now strips `client_secret` and secret-like Action Pack param keys from browser persistence paths before data is written back to `localStorage`.

### Route Classes

- Human privileged routes that require operator auth in phase 1:
  - all human `POST` / `PUT` / `DELETE` `/api/...` routes except the explicit exemptions below
  - `POST /api/task`
  - config mutation and config import/export routes
  - job enqueue and Action Pack v2 compile/validate/run routes
  - investigation / incident / snapshot / topology mutation routes
  - `POST /api/terminal/{agent_id}/start`
  - transport-specific human mutation routes such as Flask `POST /api/exchange/send-mail`

- Agent-authenticated routes that remain separate:
  - agent register / heartbeat / next-job / job-result
  - artifact upload
  - terminal session lease for agents
  - agent-authenticated terminal WebSocket behavior

- Human read-only routes left unchanged in phase 1:
  - status, summary, public config, audits, job lists/details, traces, graph reliability, snapshots/history reads, investigations/incidents reads, and browser shell/static routes
  - these can be revisited later if the trust model needs to expand beyond mutation control

- Explicit phase-1 exemptions from operator auth because they are not human UI mutation routes:
  - `/ingest/perception`
  - `POST /api/signals/visual`
  - the operator side of `/ws/terminal/{session_id}` remains gated indirectly by the authenticated terminal-start route and the unguessable `session_id`

### Terminal / Interactive Flow

- `POST /api/terminal/{agent_id}/start` should require:
  - operator token auth
  - existing `interactive_scope=true`
  - existing localhost/operator allowlist checks

- `/ws/terminal/{session_id}` does not require the operator token directly in phase 1.
  - The authenticated start route is the human authorization boundary.
  - The existing agent Bearer-token behavior on the WebSocket stays unchanged.

### Rollout Constraints

- The implementation thread should avoid broad middleware that accidentally intercepts agent routes or browser file-serving paths.
- Route classification must be explicit enough that Flask and FastAPI do not drift.
- If `GAS_OPERATOR_TOKEN` is absent, protected routes should fail clearly rather than silently remaining open.
- Operator auth, browser-storage cleanup, and boot-asset versioning now land as separate completed hardening threads.

## Secret and State Rules

- Secrets belong in:
  - `.env`
  - local `config.json` / keychain-backed config handling
  - agent-host files under `~/.gas`
- Secrets do not belong in the control-plane DB.
- Secrets do not belong in frontend profile persistence, Action Pack param persistence, or exported profile files.
- Runtime state currently lives under `admin_gui/backend/`:
  - SQLite DBs
  - audit log
  - config JSON
- Treat those files as local state, not stable source modules.
- Do not assume path secrecy for those files.
  - Flask and FastAPI now enforce `frontend_allowlist.py` before serving browser files.
  - Backend/state paths and the old FastAPI `/static/*` alias are denied by default.

## Repeated Shell Patterns

- Primary run commands:
  - `uvicorn admin_gui.backend.fastapi_app:app --reload --host 127.0.0.1 --port 8000`
  - `python -m admin_gui.backend.flask_app`
  - `python -m agent --config agent/config.example.json`
  - `docker compose up --build`

- Canonical validation entrypoints:
  - `npm run validate`
  - `npm run validate:frontend`
  - `npm run validate:backend`
- Direct targeted validation still exists for focused threads:
  - `node admin_gui/boot_contract.test.js` guards the cross-file boot contract
  - frontend contract tests can still run via direct `node admin_gui/<name>.test.js`
  - broader Python/backend/platform work can still use direct targeted Python test commands when the canonical wrapper is not enough

## Current Structural Risks Worth Remembering

- `admin_gui/app.js` is large and central.
  - Refactor in bounded slices only, with no selector/API churn.
- `admin_gui/boot_contract.test.js` now guards the cross-file boot boundary spanning `index.html`, `portal_schema.js`, and `service_shells.js`.
  - Future frontend refactors should keep this suite green instead of weakening the boot contract.
- `json_inspector.js` and `help_parser.js` exist as standalone modules while `app.js` still carries the live implementations.
- Shared-panel navigation depends on both schema metadata and DOM target IDs staying aligned.
