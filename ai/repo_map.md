# Repo Map

This is the current repo shape for Graph Admin Studio. Update it when file ownership,
boot order, or stable contracts change.

## Top Level

- `/.agents/skills/`
  - Repo-local Codex skills for architect/debug/doc-sync/test/handoff workflows.
  - Preferred deterministic entrypoint instead of pasting legacy role prompts.

- `/.codex/config.toml`
  - Repo-scoped Codex configuration for the installed workflow kit.

- `README.md`
  - Operator/dev overview and the main run commands.
  - Source of truth for the current FastAPI, Flask, agent, and Docker entrypoints.

- `README_INSTALL.md`
  - Install/use guide for the repo's Codex workflow kit.

- `manifest.json`
  - Metadata for the installed Codex autonomy pack files.

- `AGENTS.md`
  - Repo-specific Codex guardrails.
  - Reinforces vanilla frontend, stable DOM hooks, Observe-vs-Act separation, and no backend API churn unless required.

- `requirements.txt`
  - Python dependency set for the toolkit, backend, and agent.

- `package.json`, `package-lock.json`
  - Node-side dependency manifest for frontend contract tests.
  - Currently just `jsdom`; there is still no package-script wrapper.

- `docker-compose.yml`, `Dockerfile.controlplane`
  - Containerized control-plane/runtime entrypoints.

- `microsoft.py`
  - Shared Graph/PowerShell foundation.
  - Owns `GraphSession`, retry/circuit-breaker behavior, trace context, `ServiceClient`, and PowerShell session helpers.

- Cloud service clients
  - `exchange.py`, `onedrive.py`, `sharepoint.py`, `teams.py`, `entra.py`, `azure.py`, `defender.py`, `powerplatform.py`, `purview.py`
  - Service-specific adapters used by backend task dispatch.
  - Keep these as domain adapters; they are not frontend concerns.

- On-prem / local clients
  - `local_ad.py`, `local_endpoint.py`, `local_domain_controller.py`, `local_printers.py`, `local_network.py`, `local_fileserver.py`, `local_topology.py`, `local_time.py`, `local_certificates.py`, `local_processes.py`, `local_baselines.py`, `local_event_logs.py`, `local_registry.py`
  - Local and PowerShell-backed admin/troubleshooting actions.

- Remote execution helpers
  - `remote_ssh.py`
    - SSH command/session helper.
  - `remote_workflows.py`
    - Read-only, explainable endpoint workflows that run over SSH.
    - This is bespoke logic, not a generic service-shell candidate.

- `powershell_wrapper.ps1`
  - Local PowerShell execution helper.

- Capability and vision docs
  - `CAPABILITIES_*.md`, `VISION.md`, `GOVERNANCE.md`
  - Supporting product/context docs, not boot-critical runtime code.

- `global/AGENTS.md.example`
  - Optional user-level Codex guidance example for installation outside this repo.

- Generated/local-only folders commonly present in working trees
  - `.venv/`, `node_modules/`, `__pycache__/`
  - Treat as local/generated, not source.

## `admin_gui/`

### Core frontend shell

- `admin_gui/index.html`
  - Single static portal shell.
  - Contains:
    - all bespoke surfaces
    - `data-service-shell="..."` mount points for templated services
    - the service-shell templates at the end of the document
    - the authoritative script tag order
  - Stable frontend contracts live here:
    - `data-panel`
    - `data-section`
    - `data-service-shell`
    - `data-service`
    - `data-output`
    - `data-workspace-block`
    - many hard-coded IDs consumed directly by `app.js`

- `admin_gui/styles.css`
  - Shared visual system for the whole portal.
  - One stylesheet for both templated and bespoke surfaces.

- `admin_gui/app.js`
  - Main frontend runtime and current monolith.
  - Owns:
    - boot validation
    - section routing/history
    - `ACTIONS_UI`
    - report presets
    - built-in action packs
    - workspace persistence/layout
    - fetch orchestration
    - output renderers
    - help center loading
    - SSH/WebSocket wiring
    - control-plane tables
    - localStorage-backed history/state
  - Reuse existing registries and helper structures before adding new abstractions.

### Frontend support modules

- `admin_gui/portal_schema.js`
  - Canonical section/mode/shared-panel schema.
  - Boot-critical.
  - Defines which nav sections map to shared panels like `reports`, `settings`, and `controlplane`.

- `admin_gui/service_shells.js`
  - Registry + DOM renderer for the repeated toolkit/runner/output triplet pattern.
  - Boot-critical.
  - Also owns compatibility aliases for workspace block IDs via `legacyWorkspaceBlocks`.

- `admin_gui/triage.js`
  - Deterministic diff triage logic for report/snapshot comparisons.

- `admin_gui/investigation_summary.js`
  - Deterministic investigation summary builder used by the investigation workspace.

- `admin_gui/next_steps.js`
  - Rules-based next-step suggestion engine used by investigation flows.

- `admin_gui/json_inspector.js`
  - Standalone JSON inspector utility with tests.
  - Current page boot still uses inlined inspector logic in `app.js`, so this can drift.

- `admin_gui/help_parser.js`
  - Standalone markdown/help parser utility with tests.
  - Current page boot still uses inlined help parsing logic in `app.js`, so this can drift.

- `admin_gui/docs/help/`
  - Markdown help content plus `help_manifest.json`.
  - Loaded dynamically by the Help surface.

- `admin_gui/install/windows.ps1`
  - Windows runner install/bootstrap helper served by the backend install flow.

- `admin_gui/*.test.js`
  - Frontend contract tests run directly with `node`.
  - There is no `npm test` wrapper today.

### Repeated service-shell surfaces

- The generated toolkit/runner/output triplet is currently the right pattern for:
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

### Bespoke frontend surfaces that should remain bespoke

- `dashboard`
  - Status cards, recent activity, quick actions, recent snapshots.

- `remote_workflows`
  - SSH-only read-only workflows with explainable guidance.

- `ssh`
  - Interactive terminal/session experience plus single-command runner.

- `topology`
  - Multi-card topology capture, incident intake, correlation report, diff, and timeline.

- `reports`
  - Report presets, queue, incident workspace, incident report builder, report history, snapshot history/diff/export.

- `actionpacks`
  - Action pack runner, builder, history, deleted packs, and v2 control-plane workflows.

- `investigations`
  - Timeline, context binding, next-step suggestions, summary generation, evidence pinning.

- `settings`
  - Environment config, keychain/export/import, tenant info, SSH targets, health, security transparency, audit log.

- `controlplane`
  - Vision signals, action requests, tools catalog, runner bootstrap, agents, jobs, action catalog.

- `workspaces`
  - Saved multi-tile dashboards backed by `data-workspace-block`.

- `help`
  - Dynamic markdown docs with search, TOC, anchors, and deep-link support.

## `admin_gui/backend/`

- `admin_gui/backend/core.py`
  - Shared backend state and most business logic.
  - Owns config loading/saving, task dispatch, audit logging, report helpers, snapshot/investigation/incident flows, schedulers, and artifact paths.

- `admin_gui/backend/flask_app.py`
  - Flask transport layer.
  - Serves the UI plus API routes.
  - Rewrites `index.html` to add a shared `?v=` token to:
    - `styles.css`
    - `portal_schema.js`
    - `service_shells.js`
    - `triage.js`
    - `investigation_summary.js`
    - `next_steps.js`
    - `app.js`
  - Has a focused regression test for that boot-asset versioning path.
  - The SPA fallback currently serves any existing file under `admin_gui/`, so local-only bind/trust assumptions are still doing security work until an allowlist lands.
  - Does not support the FastAPI WebSocket SSH terminal path.

- `admin_gui/backend/fastapi_app.py`
  - FastAPI transport layer.
  - Exposes near-parity API routes plus WebSocket-backed SSH terminal support.
  - Currently serves raw `index.html`/files instead of using Flask's cache-busting rewrite path.
  - Its SPA fallback also serves arbitrary existing files under `admin_gui/`.
  - It also mounts `/static` to the full `admin_gui/` tree today, so the allowlist thread must close or narrow both public file-serving surfaces.

- `admin_gui/backend/control_plane.py`
  - SQLite-backed control plane for agents, jobs, pairing codes, artifacts, and terminal sessions.
  - Explicitly rejects secret-like job params; the DB is metadata/jobs only.

- `admin_gui/backend/graph_runner_dispatch.py`
  - Maps selected UI actions to remote graph-runner jobs on an online agent.

- `admin_gui/backend/workflows_v2.py`
  - Action Pack v2 validation/compile/run logic.
  - Enforces capability checks, risk caps, and terminal-action exclusions.

- `admin_gui/backend/capabilities.py`
  - Capability/risk registry, service module requirements, local-service metadata, and action overrides.

- `admin_gui/backend/reporting.py`
  - Incident report rendering/export support.

- `admin_gui/backend/artifact_retention.py`
  - Artifact cleanup/reaper support.

- Runtime/local state under `admin_gui/backend/`
  - `config.example.json`
    - Template only.
  - `config.json`
    - Local runtime config.
  - `audit_log.jsonl`
    - Audit/event log output.
  - `action_snapshots.sqlite`
    - Action snapshot storage.
  - `snapshots.sqlite`
    - Snapshot/caching storage.
  - `control_plane.sqlite`, `control_plane.sqlite-wal`, `control_plane.sqlite-shm`
    - Local control-plane runtime state.
  - These are local/generated data files, not architecture documents.
  - They currently sit under the same `admin_gui/` tree the SPA fallbacks serve from, so path allowlisting matters.

## `agent/`

- `agent/__main__.py`
  - CLI entrypoint.

- `agent/config.py`
  - Env + JSON config loading.

- `agent/runtime.py`
  - Main polling loop.
  - Handles register, heartbeat, job lease, action execution, result posting, and artifact upload.

- `agent/control_plane_client.py`
  - HTTP client for the control plane.

- `agent/token_store.py`
  - Local state/token persistence under `~/.gas`.

- `agent/json_logger.py`, `agent/redaction.py`
  - Structured logging and token redaction.

- `agent/terminal.py`
  - Terminal/session support for agent-side terminal features.

- `agent/plugins/`
  - Plugin registry and implementations.
  - Current built-ins:
    - `demo.py`
    - `graph_runner.py`
    - `runner_core.py`
    - `vision_u_eye_runner.py`
    - `windows_powershell_runner.py`

- `agent/plugins/manifests/`
  - Manifest JSON for plugin actions/capabilities.

## `platform_core/`

- Probe catalog + execution
  - `probe_registry.py`, `probe_handlers.py`, `probe_runners.py`
  - Defines the probe model used by snapshots and health/investigation flows.

- Snapshot pipeline
  - `snapshot_engine.py`, `snapshot_storage.py`, `snapshots.py`, `action_snapshots.py`, `snapshot_diff.py`, `snapshot_models.py`
  - Snapshot capture, persistence, diffing, and action snapshot storage.

- Error/caching dampers
  - `graph_error_transparency.py`
    - Standardized upstream-vs-dashboard Graph failure classification.
  - `onedrive_drive_resolver.py`
    - Cache-first drive ID resolution and retry/circuit damping.
  - `sharepoint_sites_resolver.py`
    - Cache-first site listing and retry/circuit damping.

- Lens/quality/signals
  - `entity_resolution.py`, `lens.py`, `quality.py`, `signal_providers.py`, `signal_rules.py`, `symptom_templates.py`

- Fixtures/tests
  - `fixtures/`
  - `tests/`

## `contracts/`

- `contracts/visual_signal.v1.json`
  - Visual signal contract.

- `contracts/examples/vision_u_eye.sample.json`
  - Sample payload for the contract.

## `ai/`

- Current AI operating docs, backlog, plans, handoff, and review notes.

## Repeated Shell Patterns

- Python deps
  - `pip install -r requirements.txt`

- Node test deps
  - `npm install`

- Run the local UI/API with FastAPI (recommended; needed for interactive SSH/WebSockets)
  - `uvicorn admin_gui.backend.fastapi_app:app --reload --host 127.0.0.1 --port 8000`

- Run the local UI/API with Flask
  - `python -m admin_gui.backend.flask_app`

- Run/pair the agent
  - `python -m agent --config agent/config.example.json`
  - `python -m agent --config agent/config.example.json --register-only`
  - `python -m agent pair http://127.0.0.1:8000 ABCD-EFGH`

- Run the containerized control plane
  - `docker compose up --build`

- Frontend validation
  - Direct `node` execution of `admin_gui/*.test.js`
  - There is no package-script wrapper today.

- Python validation
  - Direct `pytest` runs against `admin_gui/backend/`, `platform_core/tests/`, and `agent/test_agent_chassis.py`
