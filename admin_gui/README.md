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

Set Graph credentials in the repo `.env` file. Optional PowerShell helpers use:

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

## Notes

- Actions are dispatched through `/api/task` with an allowlisted set of operations.
- PowerShell runs inside a persistent local session to reduce repeated logins.
- Graph calls use app-only permissions; set `GRAPH_USER_ID` for user-scoped actions.
