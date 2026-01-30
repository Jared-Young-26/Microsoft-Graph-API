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

## Notes

- Graph is always preferred where supported.
- PowerShell helpers are optional and only used for features not exposed in Graph.
- The PowerShell session is reused to avoid repeated login prompts in a single Python session.
- The admin GUI is intended for local use only.
