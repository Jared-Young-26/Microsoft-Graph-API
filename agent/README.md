# Graph Admin Studio Agent (v0)

A lightweight, cross-platform Python agent that:

- registers with the control plane (`/api/agents/register`)
- sends heartbeats (`/api/agents/heartbeat`)
- polls for work (`/api/agents/{agent_id}/next-job`)
- posts results (`/api/agents/{agent_id}/job-result`)
- optionally uploads artifacts (`/api/artifacts/upload`)

This is a **skeleton** intended to be extended via plugins.

## Run

From the repo root (after `pip install -r requirements.txt`):

```bash
python -m agent --config agent/config.example.json
```

## Config

Config is loaded from **env + JSON file** (env wins).

Supported env vars:

- `CONTROL_PLANE_URL` (ex: `http://127.0.0.1:8000`)
- `AGENT_NAME`
- `LABELS` (JSON object string or `k=v,k2=v2`)
- `TOKEN` (bootstrap agent token; persisted to local token store if present)
- `GAS_PAIRING_CODE` (one-time code for first-time register when pairing is required)
- `POLL_INTERVAL` (seconds)
- `BREAK_GLASS_ENABLED` (`true`/`false`)

One-time pairing (register and exit):

```bash
python -m agent --config agent/config.example.json --register-only
```

Or via explicit pair command:

```bash
python -m agent pair http://127.0.0.1:8000 ABCD-EFGH
```

### Log rotation

The agent writes JSON logs to stdout and (by default) to `~/.gas/agent.log.jsonl`.

Optional env vars:

- `GAS_LOG_MAX_BYTES` (default `5000000`)
- `GAS_LOG_BACKUP_COUNT` (default `5`)

## Local state (token storage)

The agent stores secrets outside the repo:

- Agent token: `~/.gas/agent_token`
- Agent id: `~/.gas/agent_id`

The token is never printed to logs.

## Plugins

Plugins live in `agent/plugins/` and are loaded via `agent/plugins/registry.py`.

Each plugin implements:

- `id`
- `capabilities()`
- `actions()`
- `handle(action_id, params) -> result`

See `agent/plugins/demo.py` for an example.

## Graph Runner plugin

The built-in `graph_runner` plugin executes selected Microsoft Graph actions as **control plane jobs**.

It advertises `graph.core` only when the runner is configured with local credentials.

### Credentials (local-only)

Credentials are loaded from **env + local file** (env wins):

- File: `~/.gas/graph_credentials.json` (override with `GAS_GRAPH_CREDENTIALS_PATH`)
- Env (recommended for CI/secrets managers):
  - `GRAPH_TENANT_ID` (or `TENANT_ID`)
  - `GRAPH_CLIENT_ID` (or `CLIENT_ID`)
  - `GRAPH_CLIENT_SECRET` / `CLIENT_SECRET` (client secret mode)
  - `GRAPH_AUTH_MODE=certificate` plus:
    - `GRAPH_CERT_THUMBPRINT`
    - `GRAPH_PRIVATE_KEY_PATH` (PEM) or `GRAPH_PRIVATE_KEY_PEM`

Example `~/.gas/graph_credentials.json` (client secret):

```json
{
  "tenant_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "client_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "mode": "client_secret",
  "client_secret": "VALUE"
}
```

Example `~/.gas/graph_credentials.json` (certificate):

```json
{
  "tenant_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "client_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "mode": "certificate",
  "cert_thumbprint": "THUMBPRINT",
  "private_key_path": "/path/to/private_key.pem"
}
```

The control plane never receives this secret material (only action params / identifiers).
