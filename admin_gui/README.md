# Graph Admin Studio (Local)

A local-only admin UI for the Microsoft Graph toolkit, now wired to a backend API. Choose either FastAPI or Flask to serve the UI and API locally.

## Run with FastAPI (recommended)

```
uvicorn admin_gui.backend.fastapi_app:app --reload --host 127.0.0.1 --port 8000
```

Then open `http://127.0.0.1:8000`.

## Run with Flask

```
python -m admin_gui.backend.flask_app
```

Then open `http://127.0.0.1:8001`.

## Environment

For local-only Graph (dev), set Graph credentials in the repo `.env` file.

For runner-backed Graph (recommended), run a `graph_runner` agent and keep secrets on the runner host (not in the control plane DB).

Optional PowerShell helpers use:

```
SPO_ADMIN_URL=https://tenant-admin.sharepoint.com
PS_USER_PRINCIPAL_NAME=admin@contoso.com
PS_ORG=contoso.com
PS_AUTH_MODE=interactive
AZURE_TENANT_ID=...
AZURE_SUBSCRIPTION_ID=...
GRAPH_USER_ID=user@contoso.com
ONEDRIVE_DRIVE_ID=...
```

### Runner-backed Graph

Set `GAS_GRAPH_RUNNER_MODE=controlplane` (or `auto`) for the backend process and run an agent with Graph credentials on the runner host.

Secrets are loaded by the agent from `~/.gas/graph_credentials.json` (override with `GAS_GRAPH_CREDENTIALS_PATH`) or env vars (`GRAPH_*` / `TENANT_ID` / `CLIENT_ID` / `CLIENT_SECRET`).

## Notes

- Actions are dispatched through `/api/task` with an allowlisted set of operations.
- PowerShell runs inside a persistent local session to reduce repeated logins.
- Graph calls use app-only permissions; set `GRAPH_USER_ID` for user-scoped actions.

## Control Plane (Agents + Jobs)

The backend also exposes a lightweight control plane for registering execution agents and leasing jobs.

- DB: `admin_gui/backend/control_plane.sqlite` (auto-created)
  - Override path: `CONTROL_PLANE_DB_PATH=/path/to/control_plane.sqlite`
- Lease reaper: requeues expired running jobs automatically
  - Configure interval: `CONTROL_PLANE_REAPER_INTERVAL_SECONDS=30`

Pairing codes (recommended):

- Create one-time pairing code: `POST /api/pairing-codes`
- Require pairing codes for first-time registration:
  - `CONTROL_PLANE_REQUIRE_PAIRING_CODE=true`
  - `CONTROL_PLANE_PAIRING_CODE_TTL_SECONDS=900`

Agent-facing APIs:

- `POST /api/agents/register` → `{agent_id, agent_token}`
- `POST /api/agents/heartbeat` (auth required) → sets `status=online`, updates `last_seen`
- `GET /api/agents/{agent_id}/next-job` (auth required) → leases one queued job, or `204`
- `POST /api/agents/{agent_id}/job-result` (auth required) → stores stdout/stderr/artifacts and completes/fails the job
- `POST /api/artifacts/upload` (auth required) → uploads a file, returns `{artifact_id, sha256, filename, url}`
- `GET /api/capabilities/catalog` → known agent actions + required capabilities

Install helpers:

- `GET /install/agent.zip` → downloads the `agent/` folder as a zip
- `GET /install/windows.ps1` → Windows runner quick install (service install via NSSM if present)

Auth:

- Use `Authorization: Bearer <agent_token>` (or `X-Agent-Token`) on heartbeat/lease/result calls.
