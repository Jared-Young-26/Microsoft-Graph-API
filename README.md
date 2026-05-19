# Microsoft-Graph-API Toolkit

Python abstraction layer for Microsoft Graph plus on‑prem PowerShell tooling and a local admin portal. Graph calls are the default. When a feature is only available via PowerShell (e.g., shared mailbox sent‑items copy), the clients include PowerShell helpers that reuse a single authenticated session per Python process.

This toolkit assumes **application (app-only) permissions** for Microsoft Graph. Make sure required app permissions are granted and admin consent is applied.

## What’s included

- `microsoft.py`: `GraphSession` (auth + retry + helpers), `ServiceClient`, and a persistent `PowerShellSession`
- Service clients with Graph-first methods + PowerShell-only helpers when needed:
  - `exchange.py` (mail, calendar, contacts, shared mailbox settings)
  - `onedrive.py` (drives, items, permissions, mirroring)
  - `sharepoint.py` (sites, lists, pages)
  - `teams.py` (teams, channels, chats)
  - `entra.py` (users, groups, apps, service principals)
  - `azure.py` (Az PowerShell helpers for subscriptions/resources/infra inventory)
  - `purview.py` (Compliance/Purview PowerShell helpers)
- On‑prem PowerShell helpers:
  - `local_ad.py` (users, groups, OUs, GPOs, password reset)
  - `local_printers.py` (printer inventory + GPO cross‑reference)
  - `local_network.py` (adapters, DHCP/static IP, DNS, MTU, ping)
  - `local_fileserver.py` (UNC share enumeration with optional credentials)
- `remote_ssh.py` (single command SSH runner)
- `admin_gui/`: local-only web admin UI (static)
- `admin_gui/backend/`: Flask + FastAPI backend for local API routing
- `agent/`: cross-platform execution agent skeleton (plugins + polling loop)

## Setup

1) Create `.env` with your Graph app credentials:

```
TENANT_ID=...
CLIENT_ID=...
CLIENT_SECRET=...
```

2) Install Python dependencies:

```
pip install -r requirements.txt
```

3) Optional PowerShell requirements (for PowerShell-only features):

- PowerShell 7 (`pwsh`) on PATH
- Modules (as needed):
  - Exchange: `ExchangeOnlineManagement`
  - Teams: `MicrosoftTeams`
  - Entra: `Microsoft.Graph`
  - SharePoint/OneDrive admin: `Microsoft.Online.SharePoint.PowerShell`
- Azure: `Az.Accounts`
- On‑prem: `ActiveDirectory`, `GroupPolicy`, `PrintManagement`, `NetAdapter`, `NetTCPIP`

## Validation

Use one canonical repo command:

```
npm run validate
```

The validation runner (`scripts/validate.sh`) executes:
- the cross-file boot contract suite for `index.html`, `portal_schema.js`, and `service_shells.js`
- frontend Node suites under `admin_gui/*.test.js`
- frontend syntax guards (`node --check` for boot-critical JS)
- backend hardening subset via `python3 -m unittest`

Optional modes:

```
npm run validate:frontend
npm run validate:backend
```

Backend validation prerequisites:
- `python3` on PATH
- project Python dependencies installed (`pip install -r requirements.txt`)

If backend prerequisites are missing, the runner prints an explicit `SKIP` with a hint, while still reporting frontend results.

## Optional local UI env

Set the following (if you’re using the admin GUI):

```
GRAPH_USER_ID=user@contoso.com
ONEDRIVE_DRIVE_ID=...
SPO_ADMIN_URL=https://tenant-admin.sharepoint.com
PS_USER_PRINCIPAL_NAME=admin@contoso.com
PS_ORG=contoso.com
PS_AUTH_MODE=interactive
AZURE_TENANT_ID=...
AZURE_SUBSCRIPTION_ID=...
```

## Graph usage

```python
from microsoft import GraphSession
from exchange import ExchangeClient

graph = GraphSession()
exchange = ExchangeClient(graph)

messages = exchange.list_messages(top=5)
```

## PowerShell usage (single login per session)

```python
from microsoft import GraphSession
from exchange import ExchangeClient

graph = GraphSession()
exchange = ExchangeClient(
    graph,
    powershell_options={"auth_mode": "interactive", "user_principal_name": "admin@contoso.com"}
)

exchange.connect_powershell()  # one interactive sign-in for this session
exchange.enable_shared_mailbox_sent_items("shared@contoso.com", execute=True)
```

## Module quick start

```python
from microsoft import GraphSession
from onedrive import OneDriveClient
from sharepoint import SharePointClient
from teams import TeamsClient
from entra import EntraClient

graph = GraphSession()

onedrive = OneDriveClient(graph, drive_id="<drive-id>")
items = onedrive.list_drive_items()

sharepoint = SharePointClient(graph)
sites = sharepoint.list_sites()

teams = TeamsClient(graph)
joined = teams.list_joined_teams()

entra = EntraClient(graph)
users = entra.list_users(top=10)
```

## PowerShell helpers by module

- Exchange: shared mailbox sent items, advanced admin tasks
- SharePoint/OneDrive: site and personal site admin operations
- Teams: team and channel admin operations
- Entra: directory admin commands via `Microsoft.Graph` PowerShell
- Azure: subscription/context/resource queries, RG/storage/VM/VNet/Key Vault/app/SQL helpers via `Az`
- Purview: compliance/label/DLP + compliance search/action helpers via `ExchangeOnlineManagement`

## Admin GUI

The local admin UI is in `admin_gui/` and can be served by either FastAPI or Flask:

```
uvicorn admin_gui.backend.fastapi_app:app --reload --host 127.0.0.1 --port 8000
```

Or:

```
python -m admin_gui.backend.flask_app
```

### SSH in the Admin GUI

Interactive SSH terminals require the **FastAPI** backend (WebSocket). The Flask backend only supports single-command SSH runs.

### Control plane (Agents + Jobs)

The Admin GUI backend includes a lightweight control plane database and APIs for registering execution agents and leasing jobs.

- DB: `admin_gui/backend/control_plane.sqlite` (auto-created on first use)
  - Override path: `CONTROL_PLANE_DB_PATH=/path/to/control_plane.sqlite`
- Job lease reaper: requeues expired leases automatically
  - Configure interval: `CONTROL_PLANE_REAPER_INTERVAL_SECONDS=30`

Pairing codes (recommended for production-ish use):

- Create one-time pairing code: `POST /api/pairing-codes`
- Require pairing codes for first-time agent registration:
  - `CONTROL_PLANE_REQUIRE_PAIRING_CODE=true`
  - `CONTROL_PLANE_PAIRING_CODE_TTL_SECONDS=900` (default)

Agent-facing APIs:

- `POST /api/agents/register` → `{agent_id, agent_token}` (token returned on first register and when `rotate_token=true`)
- `POST /api/agents/heartbeat` (auth required) → updates `last_seen` + `status=online`
- `GET /api/agents/{agent_id}/next-job` (auth required) → leases one queued job, or `204` if none
- `POST /api/agents/{agent_id}/job-result` (auth required) → records output and marks job `completed`/`failed`
- `POST /api/artifacts/upload` (auth required) → uploads a file, returns `{artifact_id, sha256, filename, url}`

Install helpers:

- `GET /install/agent.zip` → downloads the `agent/` folder as a zip (v0 bootstrap helper)
- `GET /install/windows.ps1` → Windows runner quick-install script (service install via NSSM if present)

Auth:

- Send `Authorization: Bearer <agent_token>` (or `X-Agent-Token: <agent_token>`) on heartbeat/lease/result calls.

Admin/UI APIs:

- `GET /api/agents` (list agents)
- `GET /api/jobs` (list jobs)
- `GET /api/jobs/{job_id}` (job detail + result)
- `GET /api/capabilities/catalog` (known agent actions + required capabilities)

Connectivity test:

- Run `runner.connectivity_test` to verify the runner can reach the control plane and upload artifacts.

Docker (control plane):

- `docker compose up --build` (uses `docker-compose.yml`)

## Notes

- Graph is always preferred where supported.
- PowerShell helpers are optional and only used for features not exposed in Graph.
- The PowerShell session is reused to avoid repeated login prompts in a single Python session.
- The admin GUI is intended for local use only.
- Licensed under Apache 2.0. See `LICENSE`.
