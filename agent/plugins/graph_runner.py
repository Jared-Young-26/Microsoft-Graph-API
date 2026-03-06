from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json
import os
import time
import urllib.parse
import urllib.request

from ..token_store import AgentTokenStore
from .interface import ActionDefinition, ActionResult
from .manifest import load_manifest_for_plugin


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _as_int(value: Any, default: int) -> int:
    if value is None:
        return default
    try:
        return int(value)
    except Exception:
        return default


def _parse_csv(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        return [str(v).strip() for v in value if str(v).strip()]
    text = str(value).strip()
    if not text:
        return []
    return [part.strip() for part in text.split(",") if part.strip()]


def _safe_select_fields(raw: Any, *, limit: int = 32) -> str | None:
    fields = _parse_csv(raw)
    cleaned: list[str] = []
    for field in fields:
        if not field:
            continue
        # Keep this strict: Graph $select should be basic property names (v0).
        if not field.replace("_", "").isalnum():
            continue
        cleaned.append(field)
        if len(cleaned) >= limit:
            break
    return ",".join(cleaned) if cleaned else None


def _load_json(path: Path) -> dict[str, Any]:
    try:
        if not path.exists():
            return {}
        parsed = json.loads(path.read_text(encoding="utf-8"))
        return parsed if isinstance(parsed, dict) else {}
    except Exception:
        return {}


def _read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return None


@dataclass
class _GraphCredential:
    tenant_id: str
    client_id: str
    mode: str
    client_secret: str | None = None
    cert_thumbprint: str | None = None
    private_key_pem: str | None = None


@dataclass
class GraphRunnerPlugin:
    """Graph runner plugin (cloud operations via Microsoft Graph)."""

    id: str = "graph_runner"
    _token: str | None = field(default=None, init=False, repr=False)
    _token_expires_at: float = field(default=0.0, init=False, repr=False)
    _msal_app: Any | None = field(default=None, init=False, repr=False)
    _msal_cred_fingerprint: str | None = field(default=None, init=False, repr=False)

    def capabilities(self) -> list[str]:
        # Only advertise graph.core when the runner is actually configured.
        if not self._msal_importable():
            return []
        try:
            self._load_credential("default")
        except Exception:
            return []
        return ["graph.core"]

    def actions(self) -> list[ActionDefinition]:
        manifest_actions = load_manifest_for_plugin(self.id)
        if manifest_actions:
            return manifest_actions
        return [
            ActionDefinition(
                action_id="graph.connection_test",
                title="Graph connection test",
                description="Validate Graph auth and latency (GET /me + GET /users?$top=1).",
                required_capabilities=["graph.core"],
                risk_level="safe",
            ),
            ActionDefinition(
                action_id="graph.list_users",
                title="List users",
                description="List users (table-ready) with $top and $select.",
                required_capabilities=["graph.core"],
                risk_level="safe",
            ),
            ActionDefinition(
                action_id="graph.get_user",
                title="Get user",
                description="Get a user by UPN or id (normalized identity record).",
                required_capabilities=["graph.core"],
                risk_level="safe",
            ),
            ActionDefinition(
                action_id="graph.exchange.list_mail_folders",
                title="List mail folders",
                description="List mail folders for a mailbox via Graph (Exchange).",
                required_capabilities=["graph.core"],
                risk_level="safe",
            ),
        ]

    def handle(self, action_id: str, params: dict | None) -> ActionResult:
        params = params or {}
        try:
            if action_id == "graph.connection_test":
                return self._connection_test(params)
            if action_id == "graph.list_users":
                return self._list_users(params)
            if action_id == "graph.get_user":
                return self._get_user(params)
            if action_id == "graph.exchange.list_mail_folders":
                return self._exchange_list_mail_folders(params)
            return ActionResult(ok=False, stderr=f"Unknown action_id: {action_id}", exit_code=2)
        except Exception as exc:
            return ActionResult(ok=False, stderr=str(exc), exit_code=1)

    # ---- Auth / config -----------------------------------------------------

    def _msal_importable(self) -> bool:
        try:
            import msal  # noqa: F401

            return True
        except Exception:
            return False

    def _credential_path(self) -> Path:
        store = AgentTokenStore()
        override = os.environ.get("GAS_GRAPH_CREDENTIALS_PATH") or None
        if override:
            return Path(override).expanduser()
        return store.state_dir / "graph_credentials.json"

    def _load_credential(self, credential_ref: str) -> _GraphCredential:
        # Env values (runner-local; never provided by the control plane).
        env_tenant = (os.environ.get("GRAPH_TENANT_ID") or os.environ.get("TENANT_ID") or "").strip()
        env_client = (os.environ.get("GRAPH_CLIENT_ID") or os.environ.get("CLIENT_ID") or "").strip()
        env_secret = (os.environ.get("GRAPH_CLIENT_SECRET") or os.environ.get("CLIENT_SECRET") or "").strip() or None
        env_thumb = (os.environ.get("GRAPH_CERT_THUMBPRINT") or "").strip() or None
        env_key_path = (os.environ.get("GRAPH_PRIVATE_KEY_PATH") or "").strip() or None
        env_key_pem = (os.environ.get("GRAPH_PRIVATE_KEY_PEM") or "").strip() or None
        env_mode = (os.environ.get("GRAPH_AUTH_MODE") or "").strip().lower() or None

        # File values (runner-local).
        cfg = _load_json(self._credential_path())
        creds_obj = cfg.get("credentials") if isinstance(cfg.get("credentials"), dict) else None
        selected = None
        if creds_obj and credential_ref:
            entry = creds_obj.get(credential_ref)
            if isinstance(entry, dict):
                selected = entry
        if selected is None and isinstance(cfg, dict) and cfg:
            # Back-compat: allow single credential at root.
            selected = cfg

        file_tenant = str(selected.get("tenant_id") or "").strip() if isinstance(selected, dict) else ""
        file_client = str(selected.get("client_id") or "").strip() if isinstance(selected, dict) else ""
        file_mode = str(selected.get("mode") or selected.get("auth_mode") or "").strip().lower() if isinstance(selected, dict) else ""
        file_secret = str(selected.get("client_secret") or "").strip() if isinstance(selected, dict) else ""
        file_thumb = str(selected.get("cert_thumbprint") or selected.get("thumbprint") or "").strip() if isinstance(selected, dict) else ""
        file_key_path = str(selected.get("private_key_path") or "").strip() if isinstance(selected, dict) else ""
        file_key_pem = str(selected.get("private_key_pem") or "").strip() if isinstance(selected, dict) else ""

        tenant_id = env_tenant or file_tenant
        client_id = env_client or file_client
        mode = env_mode or file_mode

        client_secret = env_secret or (file_secret or None)
        cert_thumbprint = env_thumb or (file_thumb or None)
        private_key_pem = env_key_pem or (file_key_pem or None)
        if not private_key_pem:
            key_path = env_key_path or file_key_path
            if key_path:
                private_key_pem = _read_text(Path(key_path).expanduser())

        if not tenant_id or not client_id:
            raise RuntimeError("Graph runner missing tenant_id/client_id (configure env or ~/.gas/graph_credentials.json).")

        # Infer mode when omitted.
        if not mode:
            if client_secret:
                mode = "client_secret"
            elif cert_thumbprint and private_key_pem:
                mode = "certificate"
            else:
                mode = "client_secret"

        if mode in ("client_secret", "secret"):
            if not client_secret:
                raise RuntimeError("Graph runner auth mode client_secret requires a client_secret (runner-local).")
            return _GraphCredential(tenant_id=tenant_id, client_id=client_id, mode="client_secret", client_secret=client_secret)

        if mode in ("certificate", "cert"):
            if not cert_thumbprint or not private_key_pem:
                raise RuntimeError(
                    "Graph runner auth mode certificate requires cert_thumbprint and private_key (runner-local)."
                )
            return _GraphCredential(
                tenant_id=tenant_id,
                client_id=client_id,
                mode="certificate",
                cert_thumbprint=cert_thumbprint,
                private_key_pem=private_key_pem,
            )

        raise RuntimeError(f"Unsupported GRAPH_AUTH_MODE: {mode}")

    def _msal_app_for_cred(self, cred: _GraphCredential):
        import msal

        # Cache MSAL app per credential fingerprint.
        fingerprint = f"{cred.tenant_id}:{cred.client_id}:{cred.mode}:{cred.cert_thumbprint or ''}"
        if self._msal_app is not None and self._msal_cred_fingerprint == fingerprint:
            return self._msal_app

        authority = f"https://login.microsoftonline.com/{cred.tenant_id}"
        if cred.mode == "client_secret":
            client_credential: Any = cred.client_secret
        else:
            client_credential = {"private_key": cred.private_key_pem, "thumbprint": cred.cert_thumbprint}

        self._msal_app = msal.ConfidentialClientApplication(
            client_id=cred.client_id,
            authority=authority,
            client_credential=client_credential,
        )
        self._msal_cred_fingerprint = fingerprint
        self._token = None
        self._token_expires_at = 0.0
        return self._msal_app

    def _acquire_token(self, cred: _GraphCredential) -> str:
        # Fast path: cached token.
        if self._token and self._token_expires_at and time.time() < (self._token_expires_at - 60):
            return self._token

        app = self._msal_app_for_cred(cred)
        result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
        token = result.get("access_token")
        if not token:
            error = result.get("error") or "token_acquire_failed"
            desc = result.get("error_description") or ""
            raise RuntimeError(f"Graph auth failed: {error}: {desc}".strip())

        expires_in = _as_int(result.get("expires_in"), 3600)
        self._token = str(token)
        self._token_expires_at = time.time() + max(60, expires_in)
        return self._token

    # ---- Graph calls -------------------------------------------------------

    def _graph_get(self, cred: _GraphCredential, path: str, params: dict[str, Any] | None = None, timeout_seconds: int = 30):
        base = "https://graph.microsoft.com/v1.0"
        clean_path = path if path.startswith("/") else f"/{path}"
        query = ""
        if params:
            query = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
        url = base + clean_path + (f"?{query}" if query else "")
        token = self._acquire_token(cred)
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
        req = urllib.request.Request(url, headers=headers, method="GET")
        started = time.time()
        try:
            with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
                raw = resp.read().decode("utf-8") if resp else ""
                data = json.loads(raw) if raw else None
                return {"ok": True, "status": int(getattr(resp, "status", 200)), "data": data, "latency_ms": int((time.time() - started) * 1000)}
        except Exception as exc:
            status = None
            raw = ""
            if hasattr(exc, "code"):
                try:
                    status = int(getattr(exc, "code"))
                except Exception:
                    status = None
            if hasattr(exc, "read"):
                try:
                    raw = exc.read().decode("utf-8")  # type: ignore[attr-defined]
                except Exception:
                    raw = ""
            payload = None
            try:
                payload = json.loads(raw) if raw else None
            except Exception:
                payload = {"raw": raw} if raw else None
            return {
                "ok": False,
                "status": status,
                "error": str(exc),
                "data": payload,
                "latency_ms": int((time.time() - started) * 1000),
            }

    # ---- Actions -----------------------------------------------------------

    def _connection_test(self, params: dict[str, Any]) -> ActionResult:
        cred = self._load_credential(str(params.get("credential_ref") or "default"))
        calls = []
        me_call = {"id": "me", "path": "/me", **self._graph_get(cred, "/me")}
        users_call = {"id": "users_top1", "path": "/users", **self._graph_get(cred, "/users", params={"$top": 1})}
        calls.append(me_call)
        calls.append(users_call)
        # App-only auth commonly cannot call /me; treat /users as the primary signal.
        ok = bool(users_call.get("ok"))
        report = {"timestamp": _now_iso(), "ok": ok, "calls": calls}
        return ActionResult(ok=ok, result=report, exit_code=0 if ok else 1)

    def _list_users(self, params: dict[str, Any]) -> ActionResult:
        cred = self._load_credential(str(params.get("credential_ref") or "default"))
        top = max(1, min(999, _as_int(params.get("top"), 10)))
        select = _safe_select_fields(params.get("select"))
        query: dict[str, Any] = {"$top": top}
        if select:
            query["$select"] = select
        resp = self._graph_get(cred, "/users", params=query, timeout_seconds=30)
        if not resp.get("ok"):
            return ActionResult(ok=False, result=resp.get("data"), stderr=str(resp.get("error") or "Graph request failed"), exit_code=1)
        data = resp.get("data") if isinstance(resp.get("data"), dict) else {}
        items = data.get("value") if isinstance(data, dict) else None
        if not isinstance(items, list):
            return ActionResult(ok=False, result=data, stderr="Unexpected Graph response shape", exit_code=1)
        return ActionResult(ok=True, result=items, exit_code=0)

    def _get_user(self, params: dict[str, Any]) -> ActionResult:
        cred = self._load_credential(str(params.get("credential_ref") or "default"))
        user_id = str(params.get("user_id") or params.get("upn") or params.get("id") or "").strip()
        if not user_id:
            return ActionResult(ok=False, stderr="user_id is required", exit_code=2)
        select = _safe_select_fields(params.get("select"))
        query: dict[str, Any] | None = {"$select": select} if select else None
        resp = self._graph_get(cred, f"/users/{urllib.parse.quote(user_id)}", params=query, timeout_seconds=30)
        if not resp.get("ok"):
            return ActionResult(ok=False, result=resp.get("data"), stderr=str(resp.get("error") or "Graph request failed"), exit_code=1)
        data = resp.get("data")
        if not isinstance(data, dict):
            return ActionResult(ok=False, result=data, stderr="Unexpected Graph response shape", exit_code=1)
        normalized = {
            "id": data.get("id"),
            "displayName": data.get("displayName"),
            "userPrincipalName": data.get("userPrincipalName"),
            "mail": data.get("mail"),
            "accountEnabled": data.get("accountEnabled"),
            "userType": data.get("userType"),
            "jobTitle": data.get("jobTitle"),
            "department": data.get("department"),
            "officeLocation": data.get("officeLocation"),
            "mobilePhone": data.get("mobilePhone"),
            "businessPhones": data.get("businessPhones"),
        }
        # Include raw so callers can choose their own fields when they pass $select.
        normalized["_raw"] = data
        return ActionResult(ok=True, result=normalized, exit_code=0)

    def _exchange_list_mail_folders(self, params: dict[str, Any]) -> ActionResult:
        cred = self._load_credential(str(params.get("credential_ref") or "default"))
        user_id = str(params.get("user_id") or "me").strip() or "me"
        include_hidden = bool(params.get("include_hidden") or params.get("includeHidden"))
        top = max(1, min(999, _as_int(params.get("top"), 100)))
        query: dict[str, Any] = {"$top": top}
        if include_hidden:
            query["includeHiddenFolders"] = "true"
        path = f"/users/{urllib.parse.quote(user_id)}/mailFolders" if user_id != "me" else "/me/mailFolders"
        resp = self._graph_get(cred, path, params=query, timeout_seconds=30)
        if not resp.get("ok"):
            return ActionResult(ok=False, result=resp.get("data"), stderr=str(resp.get("error") or "Graph request failed"), exit_code=1)
        data = resp.get("data") if isinstance(resp.get("data"), dict) else {}
        items = data.get("value") if isinstance(data, dict) else None
        if not isinstance(items, list):
            return ActionResult(ok=False, result=data, stderr="Unexpected Graph response shape", exit_code=1)
        return ActionResult(ok=True, result=items, exit_code=0)
