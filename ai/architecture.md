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

## Backend Serving Notes

- Flask and FastAPI are intended to expose near-parity HTTP APIs over shared backend logic.
- FastAPI is required for the interactive SSH WebSocket flow.
- Flask currently rewrites `index.html` to add a shared `?v=` token to:
  - `styles.css`
  - `portal_schema.js`
  - `service_shells.js`
  - `triage.js`
  - `investigation_summary.js`
  - `next_steps.js`
  - `app.js`
- FastAPI currently serves raw `index.html` and static files without that rewrite path.
- Flask currently exposes browser files through its `/{path}` SPA fallback.
- FastAPI currently exposes browser files through both its `/{path}` SPA fallback and `app.mount("/static", StaticFiles(directory=ROOT, html=True))`.
- Both backend entrypoints currently resolve arbitrary existing paths under `admin_gui/`; on FastAPI the `/static` mount is a second path to the same tree.
- Because `admin_gui/backend/` also holds local config, SQLite DBs, and audit logs, static-file allowlisting is a backend trust-boundary requirement, not a cosmetic cleanup.
- There is already a focused Flask regression test for boot-asset cache busting; FastAPI does not yet have equivalent behavior.

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

## Secret and State Rules

- Secrets belong in:
  - `.env`
  - local `config.json` / keychain-backed config handling
  - agent-host files under `~/.gas`
- Secrets do not belong in the control-plane DB.
- Runtime state currently lives under `admin_gui/backend/`:
  - SQLite DBs
  - audit log
  - config JSON
- Treat those files as local state, not stable source modules.
- Do not assume path secrecy for those files.
  - Both backend entrypoints currently serve from the broader `admin_gui/` tree unless explicit allowlisting is added.
  - On FastAPI, both the catch-all browser route and `/static` mount currently point at that same tree.

## Repeated Shell Patterns

- Primary run commands:
  - `uvicorn admin_gui.backend.fastapi_app:app --reload --host 127.0.0.1 --port 8000`
  - `python -m admin_gui.backend.flask_app`
  - `python -m agent --config agent/config.example.json`
  - `docker compose up --build`

- Validation is split by runtime:
  - frontend contract tests are direct `node admin_gui/<name>.test.js`
  - Python/backend/platform tests are direct `pytest ...`
- There is no single package-script wrapper today; threads should call the specific command they need.

## Current Structural Risks Worth Remembering

- `admin_gui/app.js` is large and central.
  - Refactor in bounded slices only, with no selector/API churn.
- Human/operator mutation routes still rely on local-listener trust.
  - Observe-vs-Act is a UI distinction today, not a server-side permission boundary.
- Both backend entrypoints can currently expose arbitrary files under `admin_gui/` if reached directly.
- FastAPI currently has two browser file-serving surfaces to close or narrow together:
  - `/{path}`
  - `/static/*`
- FastAPI and Flask frontend asset handling are not fully aligned.
- `json_inspector.js` and `help_parser.js` exist as standalone modules while `app.js` still carries the live implementations.
- Shared-panel navigation depends on both schema metadata and DOM target IDs staying aligned.
