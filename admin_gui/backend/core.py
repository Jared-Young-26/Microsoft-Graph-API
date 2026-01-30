import json
import os
import sys
import inspect
import time
from datetime import datetime, timezone
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = Path(__file__).resolve().parent / "config.json"
TOPOLOGY_HISTORY_PATH = Path(__file__).resolve().parent / "topology_history.json"
TOPOLOGY_HISTORY_DEFAULT_LIMIT = 50
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

load_dotenv(dotenv_path=ROOT / ".env")

from microsoft import GraphSession, PowerShellSession, GraphAPIError, PowerShellCommandError

try:
    import keyring
except Exception:
    keyring = None

KEYCHAIN_SERVICE = "graph-admin-studio"


def _keychain_key(tenant_id, client_id):
    tenant = tenant_id or "tenant"
    client = client_id or "client"
    return f"{tenant}:{client}"


def _get_keychain_secret(tenant_id, client_id):
    if not keyring:
        return None
    return keyring.get_password(KEYCHAIN_SERVICE, _keychain_key(tenant_id, client_id))


def _set_keychain_secret(tenant_id, client_id, secret):
    if not keyring:
        raise RuntimeError("Keychain integration not available. Install keyring to enable it.")
    keyring.set_password(KEYCHAIN_SERVICE, _keychain_key(tenant_id, client_id), secret)


def _delete_keychain_secret(tenant_id, client_id):
    if not keyring:
        return
    try:
        keyring.delete_password(KEYCHAIN_SERVICE, _keychain_key(tenant_id, client_id))
    except Exception:
        return
from exchange import ExchangeClient
from onedrive import OneDriveClient
from sharepoint import SharePointClient
from teams import TeamsClient
from entra import EntraClient
from azure import AzureClient
from purview import PurviewClient
from local_ad import LocalADClient
from local_printers import LocalPrinterClient
from local_network import LocalNetworkClient
from remote_ssh import RemoteSSHClient
from local_fileserver import LocalFileServerClient
from local_topology import LocalTopologyClient


def _read_config_file():
    if not CONFIG_PATH.exists():
        return {}
    try:
        return json.loads(CONFIG_PATH.read_text())
    except Exception:
        return {}


def _write_config_file(data):
    cleaned = {k: v for k, v in data.items() if v not in ("", None)}
    CONFIG_PATH.write_text(json.dumps(cleaned, indent=2))


def _normalize_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _read_topology_history(limit=None):
    if not TOPOLOGY_HISTORY_PATH.exists():
        return []
    try:
        data = json.loads(TOPOLOGY_HISTORY_PATH.read_text())
        history = data if isinstance(data, list) else []
    except Exception:
        history = []
    if limit:
        try:
            limit_val = int(limit)
            history = history[:limit_val]
        except Exception:
            pass
    return history


def _write_topology_history(history):
    TOPOLOGY_HISTORY_PATH.write_text(json.dumps(history, indent=2))


def _trim_topology_snapshot(data):
    if not isinstance(data, dict):
        return None
    timestamp = data.get("generated_at") or data.get("timestamp") or datetime.now(timezone.utc).isoformat()
    leases = _normalize_list(data.get("dhcp_leases"))
    dns_records = _normalize_list(data.get("dns_records"))
    trimmed_leases = []
    for lease in leases:
        if not isinstance(lease, dict):
            continue
        trimmed = {
            "HostName": lease.get("HostName") or lease.get("hostName"),
            "IPAddress": lease.get("IPAddress") or lease.get("IpAddress") or lease.get("ip"),
            "ClientId": lease.get("ClientId"),
            "LeaseExpiryTime": lease.get("LeaseExpiryTime"),
            "ScopeId": lease.get("ScopeId"),
        }
        if trimmed.get("HostName") or trimmed.get("IPAddress"):
            trimmed_leases.append(trimmed)
    trimmed_records = []
    for record in dns_records:
        if not isinstance(record, dict):
            continue
        trimmed = {
            "Zone": record.get("Zone"),
            "HostName": record.get("HostName"),
            "RecordType": record.get("RecordType"),
            "RecordData": record.get("RecordData"),
        }
        if trimmed.get("HostName") or trimmed.get("RecordData"):
            trimmed_records.append(trimmed)
    return {
        "timestamp": timestamp,
        "dhcp_leases": trimmed_leases,
        "dns_records": trimmed_records,
    }


def _append_topology_history(snapshot, limit=None):
    history = _read_topology_history()
    trimmed = _trim_topology_snapshot(snapshot)
    if not trimmed:
        return history
    history.insert(0, trimmed)
    try:
        limit_val = int(limit) if limit else TOPOLOGY_HISTORY_DEFAULT_LIMIT
        if limit_val > 0:
            history = history[:limit_val]
    except Exception:
        pass
    _write_topology_history(history)
    return history


def _value(key, env_key=None, default=None, data=None):
    env_key = env_key or key.upper()
    data = data or {}
    val = data.get(key)
    if val in ("", None):
        val = os.getenv(env_key, default)
    return val


@dataclass
class BackendConfig:
    tenant_id: str | None = None
    client_id: str | None = None
    client_secret: str | None = None
    spo_admin_url: str | None = None
    ps_user_principal_name: str | None = None
    ps_org: str | None = None
    ps_auth_mode: str | None = None
    azure_tenant_id: str | None = None
    azure_subscription_id: str | None = None
    graph_user_id: str | None = None
    onedrive_drive_id: str | None = None
    use_keychain: bool | None = None
    config_lock: bool | None = None


def _build_config():
    data = _read_config_file()
    use_keychain = bool(data.get("use_keychain"))
    tenant_id = _value("tenant_id", "TENANT_ID", data=data)
    client_id = _value("client_id", "CLIENT_ID", data=data)
    client_secret = _value("client_secret", "CLIENT_SECRET", data=data)
    if use_keychain:
        try:
            client_secret = _get_keychain_secret(tenant_id, client_id) or client_secret
        except Exception:
            pass
    return BackendConfig(
        tenant_id=tenant_id,
        client_id=client_id,
        client_secret=client_secret,
        spo_admin_url=_value("spo_admin_url", "SPO_ADMIN_URL", data=data),
        ps_user_principal_name=_value("ps_user_principal_name", "PS_USER_PRINCIPAL_NAME", data=data),
        ps_org=_value("ps_org", "PS_ORG", data=data),
        ps_auth_mode=_value("ps_auth_mode", "PS_AUTH_MODE", default="interactive", data=data),
        azure_tenant_id=_value("azure_tenant_id", "AZURE_TENANT_ID", data=data),
        azure_subscription_id=_value("azure_subscription_id", "AZURE_SUBSCRIPTION_ID", data=data),
        graph_user_id=_value("graph_user_id", "GRAPH_USER_ID", data=data),
        onedrive_drive_id=_value("onedrive_drive_id", "ONEDRIVE_DRIVE_ID", data=data),
        use_keychain=use_keychain,
        config_lock=bool(data.get("config_lock")),
    )


class BackendState:
    def __init__(self):
        self.config = _build_config()
        self.graph = None
        self.powershell = PowerShellSession()
        self.clients = {}
        self._topology_history = None

    def reload(self):
        if self.powershell:
            self.powershell.close()
        self.config = _build_config()
        self.graph = None
        self.powershell = PowerShellSession()
        self.clients = {}
        self._topology_history = None
        return self.config

    def get_topology_history(self, limit=None):
        return _read_topology_history(limit=limit)

    def append_topology_history(self, snapshot, limit=None):
        return _append_topology_history(snapshot, limit=limit)

    def update_config(self, payload):
        current = _read_config_file()
        locked = bool(current.get("config_lock"))
        if locked and not ("config_lock" in payload and payload.get("config_lock") is False):
            raise RuntimeError("Environment is locked. Disable the lock to update configuration.")

        if "use_keychain" in payload:
            desired_keychain = bool(payload.get("use_keychain"))
            if desired_keychain and not keyring:
                raise RuntimeError("Keychain integration not available. Install keyring to enable it.")
            if not desired_keychain and current.get("use_keychain"):
                if not payload.get("client_secret"):
                    tenant_id = payload.get("tenant_id") or current.get("tenant_id")
                    client_id = payload.get("client_id") or current.get("client_id")
                    try:
                        stored_secret = _get_keychain_secret(tenant_id, client_id)
                        if stored_secret:
                            current["client_secret"] = stored_secret
                    except Exception:
                        pass
            current["use_keychain"] = desired_keychain

        if "config_lock" in payload:
            current["config_lock"] = bool(payload.get("config_lock"))

        for key, value in payload.items():
            if key in ("use_keychain", "config_lock"):
                continue
            if key == "client_secret":
                if not value:
                    continue
                if current.get("use_keychain"):
                    tenant_id = payload.get("tenant_id") or current.get("tenant_id")
                    client_id = payload.get("client_id") or current.get("client_id")
                    _set_keychain_secret(tenant_id, client_id, value)
                    current[key] = None
                else:
                    current[key] = value
                continue
            current[key] = value if value not in ("", None) else None

        if current.get("use_keychain") and current.get("client_secret"):
            tenant_id = current.get("tenant_id")
            client_id = current.get("client_id")
            try:
                _set_keychain_secret(tenant_id, client_id, current.get("client_secret"))
                current["client_secret"] = None
            except Exception:
                pass
        _write_config_file(current)
        self.reload()
        return self.get_config_public()

    def get_config_public(self):
        cfg = self.config
        return {
            "tenant_id": cfg.tenant_id or "",
            "client_id": cfg.client_id or "",
            "client_secret_set": bool(cfg.client_secret),
            "use_keychain": bool(cfg.use_keychain),
            "keychain_available": keyring is not None,
            "config_lock": bool(cfg.config_lock),
            "graph_user_id": cfg.graph_user_id or "",
            "onedrive_drive_id": cfg.onedrive_drive_id or "",
            "spo_admin_url": cfg.spo_admin_url or "",
            "ps_user_principal_name": cfg.ps_user_principal_name or "",
            "ps_org": cfg.ps_org or "",
            "ps_auth_mode": cfg.ps_auth_mode or "interactive",
            "azure_tenant_id": cfg.azure_tenant_id or "",
            "azure_subscription_id": cfg.azure_subscription_id or "",
        }

    def get_graph(self):
        if self.graph is None:
            cfg = self.config
            self.graph = GraphSession(
                tenant_id=cfg.tenant_id,
                client_id=cfg.client_id,
                client_secret=cfg.client_secret,
            )
        return self.graph

    def get_client(self, service):
        if service in self.clients:
            return self.clients[service]

        ps_session = self.powershell
        cfg = self.config

        if service == "exchange":
            graph = self.get_graph()
            client = ExchangeClient(
                graph,
                powershell_options={
                    "session": ps_session,
                    "auth_mode": cfg.ps_auth_mode,
                    "user_principal_name": cfg.ps_user_principal_name,
                    "organization": cfg.ps_org,
                },
            )
        elif service == "onedrive":
            graph = self.get_graph()
            drive_id = cfg.onedrive_drive_id or ""
            if not drive_id:
                raise ValueError("ONEDRIVE_DRIVE_ID is required for OneDrive actions.")
            client = OneDriveClient(
                graph,
                drive_id=drive_id,
                powershell_options={
                    "session": ps_session,
                    "admin_url": cfg.spo_admin_url,
                },
            )
        elif service == "sharepoint":
            graph = self.get_graph()
            client = SharePointClient(
                graph,
                powershell_options={
                    "session": ps_session,
                    "admin_url": cfg.spo_admin_url,
                },
            )
        elif service == "teams":
            graph = self.get_graph()
            client = TeamsClient(graph, powershell_options={"session": ps_session})
        elif service == "entra":
            graph = self.get_graph()
            client = EntraClient(
                graph,
                powershell_options={
                    "session": ps_session,
                    "tenant_id": cfg.azure_tenant_id,
                },
            )
        elif service == "azure":
            graph = self.get_graph()
            client = AzureClient(
                graph,
                powershell_options={
                    "session": ps_session,
                    "tenant_id": cfg.azure_tenant_id,
                    "subscription_id": cfg.azure_subscription_id,
                },
            )
        elif service == "purview":
            graph = self.get_graph()
            client = PurviewClient(
                graph,
                powershell_options={
                    "session": ps_session,
                    "user_principal_name": cfg.ps_user_principal_name,
                    "organization": cfg.ps_org,
                },
            )
        elif service == "localad":
            client = LocalADClient(powershell=ps_session)
        elif service == "printers":
            client = LocalPrinterClient(powershell=ps_session)
        elif service == "network":
            client = LocalNetworkClient(powershell=ps_session)
        elif service == "ssh":
            client = RemoteSSHClient()
        elif service == "fileserver":
            client = LocalFileServerClient(powershell=ps_session)
        elif service == "topology":
            client = LocalTopologyClient(powershell=ps_session)
        else:
            raise ValueError(f"Unknown service: {service}")

        self.clients[service] = client
        return client

    def status(self):
        missing = []
        if not self.config.tenant_id:
            missing.append("TENANT_ID")
        if not self.config.client_id:
            missing.append("CLIENT_ID")
        if not self.config.client_secret:
            missing.append("CLIENT_SECRET")
        return {
            "graph_configured": len(missing) == 0,
            "missing_graph_env": missing,
            "graph_user_id": self.config.graph_user_id or "",
            "spo_admin_url": self.config.spo_admin_url or "",
            "ps_user_principal_name": self.config.ps_user_principal_name or "",
            "ps_auth_mode": self.config.ps_auth_mode,
        }


STATE = BackendState()

POWERSHELL_MODULES = {
    "exchange": ["ExchangeOnlineManagement"],
    "onedrive": ["Microsoft.Online.SharePoint.PowerShell"],
    "sharepoint": ["Microsoft.Online.SharePoint.PowerShell"],
    "teams": ["MicrosoftTeams"],
    "entra": ["Microsoft.Graph"],
    "azure": ["Az.Accounts"],
    "purview": ["ExchangeOnlineManagement"],
    "localad": ["ActiveDirectory", "GroupPolicy"],
    "printers": ["PrintManagement", "GroupPolicy"],
    "network": ["NetAdapter", "NetTCPIP"],
    "fileserver": [],
    "topology": ["DhcpServer", "DnsServer", "PrintManagement", "SmbShare"],
}

GRAPH_CHECKS = {
    "exchange": {"path": "/users/{user_id}/mailFolders", "params": {"$top": 1}},
    "onedrive": {"path": "/users/{user_id}/drive", "params": {"$select": "id"}},
    "sharepoint": {"path": "/sites", "params": {"search": "*", "$top": 1}},
    "teams": {"path": "/teams", "params": {"$top": 1}},
    "entra": {"path": "/users", "params": {"$top": 1}},
}


def _check_powershell_modules(modules):
    results = {}
    session = STATE.powershell
    for module in modules:
        cmd = (
            "Get-Module -ListAvailable -Name "
            f"'{module}' | Select-Object -First 1 Name, Version | ConvertTo-Json -Depth 3"
        )
        try:
            output = session.run(cmd)
            if output:
                data = json.loads(output)
                version = data.get("Version") if isinstance(data, dict) else None
                results[module] = {"installed": True, "version": str(version) if version else None}
            else:
                results[module] = {"installed": False}
        except (PowerShellCommandError, FileNotFoundError) as exc:
            results[module] = {"installed": False, "error": str(exc)}
        except Exception as exc:
            results[module] = {"installed": False, "error": str(exc)}
    ok = all(entry.get("installed") for entry in results.values()) if results else True
    return {"ok": ok, "modules": results}


def _graph_check(service=None):
    cfg = STATE.config
    graph = STATE.get_graph()
    checks = {}
    targets = [service] if service else list(GRAPH_CHECKS.keys())
    for svc in targets:
        spec = GRAPH_CHECKS.get(svc)
        if not spec:
            checks[svc] = {"ok": False, "error": "No graph check configured"}
            continue
        user_id = cfg.graph_user_id
        if "{user_id}" in spec["path"] and not user_id:
            checks[svc] = {"ok": False, "error": "GRAPH_USER_ID is required for app-only checks."}
            continue
        path = spec["path"].format(user_id=user_id or "")
        start = time.monotonic()
        try:
            response = graph.get(path, params=spec.get("params"))
            elapsed_ms = int((time.monotonic() - start) * 1000)
            checks[svc] = {
                "ok": True,
                "status": response.status_code,
                "latency_ms": elapsed_ms,
            }
        except GraphAPIError as exc:
            elapsed_ms = int((time.monotonic() - start) * 1000)
            checks[svc] = {
                "ok": False,
                "status": exc.status_code,
                "message": str(exc),
                "request_id": exc.request_id,
                "code": exc.code,
                "latency_ms": elapsed_ms,
            }
        except Exception as exc:
            elapsed_ms = int((time.monotonic() - start) * 1000)
            checks[svc] = {"ok": False, "message": str(exc), "latency_ms": elapsed_ms}
    ok = all(check.get("ok") for check in checks.values()) if checks else True
    return {"ok": ok, "checks": checks}


def _health_check():
    graph = _graph_check()
    modules = _check_powershell_modules(sorted({m for mods in POWERSHELL_MODULES.values() for m in mods}))
    return {"graph": graph, "powershell": modules}


def _tenant_info():
    graph = STATE.get_graph()
    response = graph.get("/organization?$select=id,displayName,verifiedDomains")
    data = response.json().get("value", [])
    if not data:
        return {}
    org = data[0]
    domains = org.get("verifiedDomains") or []
    return {
        "tenant_id": org.get("id"),
        "display_name": org.get("displayName"),
        "verified_domains": [
            {
                "name": d.get("name"),
                "type": d.get("type"),
                "is_default": d.get("isDefault"),
                "is_initial": d.get("isInitial"),
                "is_verified": d.get("isVerified"),
            }
            for d in domains
        ],
    }


def _user_audit_report(
    user_id=None,
    include_groups=True,
    include_licenses=True,
    include_signins=False,
    include_devices=False,
    include_mailbox_stats=False,
):
    cfg = STATE.config
    target_user = user_id or cfg.graph_user_id
    if not target_user:
        raise ValueError("User ID is required for user audit reports.")
    entra = STATE.get_client("entra")
    errors = []

    def _capture_error(scope, exc):
        if isinstance(exc, GraphAPIError):
            errors.append(
                {
                    "scope": scope,
                    "status_code": exc.status_code,
                    "request_id": exc.request_id,
                    "code": exc.code,
                    "error": str(exc),
                }
            )
        else:
            errors.append({"scope": scope, "error": str(exc)})

    user = entra.get_user(target_user)
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "user": user,
    }
    if include_groups:
        try:
            report["memberOf"] = entra.list_user_member_of(target_user, top=100)
        except Exception as exc:
            _capture_error("memberOf", exc)
    if include_licenses:
        try:
            response = entra.get(f"/users/{target_user}/licenseDetails")
            report["licenses"] = response.json().get("value", [])
        except Exception as exc:
            _capture_error("licenses", exc)
    if include_signins:
        try:
            response = entra.get(
                "/auditLogs/signIns",
                params={
                    "$top": 25,
                    "$orderby": "createdDateTime desc",
                    "$filter": f"userId eq '{target_user}'",
                },
            )
            report["signIns"] = response.json().get("value", [])
        except Exception as exc:
            _capture_error("signIns", exc)
    if include_devices:
        try:
            response = entra.get(
                f"/users/{target_user}/registeredDevices",
                params={
                    "$select": "id,displayName,deviceId,operatingSystem,trustType,approximateLastSignInDateTime",
                },
            )
            report["devices"] = response.json().get("value", [])
        except Exception as exc:
            _capture_error("devices", exc)
    if include_mailbox_stats:
        try:
            inbox = entra.get(
                f"/users/{target_user}/mailFolders/inbox",
                params={"$select": "displayName,totalItemCount,unreadItemCount"},
            )
            settings = entra.get(f"/users/{target_user}/mailboxSettings")
            report["mailboxStats"] = {
                "inbox": inbox.json() if inbox.content else {},
                "settings": settings.json() if settings.content else {},
            }
        except Exception as exc:
            _capture_error("mailboxStats", exc)
    if errors:
        report["errors"] = errors
    return report


def _gpo_audit_report(name=None):
    localad = STATE.get_client("localad")
    gpos = localad.list_gpos(name=name)
    if isinstance(gpos, dict):
        gpos_list = [gpos]
    else:
        gpos_list = gpos or []
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "count": len(gpos_list),
        "gpos": gpos_list,
    }


def _gpo_link_audit_report(ou_dn):
    if not ou_dn:
        raise ValueError("OU DN is required for GPO link audit.")
    localad = STATE.get_client("localad")
    inheritance = localad.get_gpo_inheritance(ou_dn)
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "ou_dn": ou_dn,
        "inheritance": inheritance,
    }


def _bulk_update(service, update_action, items, context=None):
    if not update_action:
        raise ValueError("update_action is required for bulk updates.")
    if not items:
        raise ValueError("items are required for bulk updates.")
    context = context or {}

    def _get_client(name):
        if name == "onedrive":
            return STATE.get_client("onedrive")
        return STATE.get_client(name)

    handlers = {
        "update_event": lambda client, item, ctx: client.update_event(
            item["id"], item["updates"], user_id=ctx.get("user_id", "me")
        ),
        "update_item": lambda client, item, ctx: client.update_item(item["id"], item["updates"]),
        "update_list_item_fields": lambda client, item, ctx: client.update_list_item_fields(
            ctx.get("site_id"), ctx.get("list_id"), item["id"], item["updates"]
        ),
        "update_channel": lambda client, item, ctx: client.update_channel(
            ctx.get("team_id"), item["id"], item["updates"]
        ),
        "update_user": lambda client, item, ctx: client.update_user(item["id"], item["updates"]),
        "update_group": lambda client, item, ctx: client.update_group(item["id"], item["updates"]),
    }

    if update_action not in handlers:
        raise ValueError(f"Bulk update action '{update_action}' is not supported.")

    client = _get_client(service)
    results = []
    for entry in items:
        try:
            item_id = entry.get("id")
            updates = entry.get("updates") or {}
            if not item_id:
                raise ValueError("Missing item id for bulk update.")
            result = handlers[update_action](client, {"id": item_id, "updates": updates}, context)
            results.append({"id": item_id, "ok": True, "data": _jsonable(result)})
        except Exception as exc:
            results.append({"id": entry.get("id"), "ok": False, "error": str(exc)})
    ok = all(item.get("ok") for item in results) if results else True
    return {"ok": ok, "count": len(results), "results": results}


ACTIONS = {
    "exchange": {
        "enable_shared_sent_items": {
            "method": "enable_shared_mailbox_sent_items",
            "defaults": {"execute": True},
            "required": ["shared_mailbox"],
        },
        "list_mail_folders": {"method": "list_mail_folders"},
        "list_messages": {"method": "list_messages", "defaults": {"top": 10}},
        "list_events": {"method": "list_events", "defaults": {"top": 10}},
        "update_event": {"method": "update_event", "required": ["event_id", "updates"]},
    },
    "onedrive": {
        "list_drive_items": {"method": "list_drive_items"},
        "get_user_drive_id": {"method": "get_user_drive_id"},
        "create_upload_session": {"method": "create_upload_session", "required": ["item_path"]},
        "list_personal_sites": {"method": "list_personal_sites_powershell"},
        "update_item": {"method": "update_item", "required": ["item_id", "updates"]},
    },
    "sharepoint": {
        "list_sites": {"method": "list_sites"},
        "create_list": {"method": "create_list", "required": ["site_id", "display_name"]},
        "list_list_items": {"method": "list_list_items", "required": ["site_id", "list_id"]},
        "list_sites_admin": {"method": "list_sites_powershell"},
        "update_list_item_fields": {
            "method": "update_list_item_fields",
            "required": ["site_id", "list_id", "item_id", "fields"],
        },
    },
    "teams": {
        "list_joined_teams": {"method": "list_joined_teams"},
        "list_channels": {"method": "list_channels", "required": ["team_id"]},
        "create_channel": {"method": "create_channel", "required": ["team_id", "display_name"]},
        "list_chat_messages": {"method": "list_chat_messages", "required": ["chat_id"]},
        "list_teams_admin": {"method": "list_teams_powershell"},
        "update_channel": {"method": "update_channel", "required": ["team_id", "channel_id", "updates"]},
    },
    "entra": {
        "list_users": {"method": "list_users", "defaults": {"top": 10}},
        "create_user": {
            "method": "create_user",
            "required": ["user_principal_name", "display_name", "password"],
        },
        "update_user": {"method": "update_user", "required": ["user_id", "updates"]},
        "update_group": {"method": "update_group", "required": ["group_id", "updates"]},
        "add_group_member": {"method": "add_group_member", "required": ["group_id", "user_id"]},
        "list_service_principals": {"method": "list_service_principals", "defaults": {"top": 10}},
        "set_user_license": {
            "method": "set_user_license_powershell",
            "required": ["user_id"],
            "list_fields": ["add_sku_ids", "remove_sku_ids"],
        },
    },
    "azure": {
        "list_subscriptions": {"method": "list_subscriptions_powershell"},
        "list_resource_groups": {"method": "list_resource_groups_powershell"},
        "list_virtual_machines": {"method": "list_virtual_machines_powershell"},
        "list_key_vaults": {"method": "list_key_vaults_powershell"},
    },
    "purview": {
        "list_retention_policies": {"method": "list_retention_policies_powershell"},
        "create_compliance_search": {
            "method": "create_compliance_search_powershell",
            "required": ["name"],
            "list_fields": ["exchange_locations", "sharepoint_locations"],
        },
        "list_dlp_policies": {"method": "list_dlp_policies_powershell"},
        "list_compliance_actions": {"method": "list_compliance_search_actions_powershell"},
    },
    "localad": {
        "list_users": {"method": "list_users"},
        "create_user": {
            "method": "create_user",
            "required": ["name", "sam_account_name", "user_principal_name", "password"],
        },
        "reset_password": {"method": "reset_password", "required": ["user_dn", "password"]},
        "unlock_account": {"method": "unlock_account", "required": ["user_dn"]},
        "enable_account": {"method": "enable_account", "required": ["user_dn"]},
        "disable_account": {"method": "disable_account", "required": ["user_dn"]},
        "list_groups": {"method": "list_groups"},
        "create_group": {"method": "create_group", "required": ["name"]},
        "add_group_member": {"method": "add_group_member", "required": ["group_dn", "member_dn"]},
        "remove_group_member": {"method": "remove_group_member", "required": ["group_dn", "member_dn"]},
        "move_user_to_ou": {"method": "move_user_to_ou", "required": ["user_dn", "ou_dn"]},
        "list_ous": {"method": "list_ous"},
        "list_gpos": {"method": "list_gpos"},
        "link_gpo": {"method": "link_gpo", "required": ["gpo_name", "ou_dn"]},
        "unlink_gpo": {"method": "unlink_gpo", "required": ["gpo_name", "ou_dn"]},
        "backup_gpo": {"method": "backup_gpo", "required": ["gpo_name", "path"]},
        "restore_gpo": {"method": "restore_gpo", "required": ["gpo_name", "path"]},
    },
    "printers": {
        "list_printers": {"method": "list_printers"},
        "list_gpo_printer_mappings": {"method": "list_gpo_printer_mappings"},
        "cross_reference_printers_gpo": {"method": "cross_reference_printers_gpo"},
    },
    "network": {
        "list_adapters": {"method": "list_adapters"},
        "get_adapter_config": {"method": "get_adapter_config", "required": ["name"]},
        "enable_adapter": {"method": "enable_adapter", "required": ["name"]},
        "disable_adapter": {"method": "disable_adapter", "required": ["name"]},
        "rename_adapter": {"method": "rename_adapter", "required": ["name", "new_name"]},
        "set_dhcp": {"method": "set_dhcp", "required": ["name"]},
        "set_static_ipv4": {
            "method": "set_static_ipv4",
            "required": ["name", "ip_address", "prefix_length"],
            "list_fields": ["dns_servers"],
        },
        "set_dns_servers": {"method": "set_dns_servers", "required": ["name"], "list_fields": ["servers"]},
        "set_interface_metric": {"method": "set_interface_metric", "required": ["name", "metric"]},
        "set_mtu": {"method": "set_mtu", "required": ["name", "mtu"]},
        "ping_host": {"method": "ping_host", "required": ["host"]},
    },
    "ssh": {
        "run_command": {"method": "run_command", "required": ["host", "command"]},
    },
    "fileserver": {
        "list_files": {"method": "list_files", "required": ["unc_path"]},
    },
    "topology": {
        "collect_topology": {
            "method": "collect_topology",
            "list_fields": ["dns_zones", "record_types"],
        },
        "ping_targets": {"method": "ping_targets", "required": ["targets"], "list_fields": ["targets"]},
    },
}


def _normalize_params(spec, params):
    data = dict(params or {})
    for key in list(data.keys()):
        if isinstance(data[key], str) and data[key].strip() == "":
            data[key] = None

    for field in spec.get("list_fields", []):
        value = data.get(field)
        if isinstance(value, str):
            parts = [v.strip() for v in value.split(",") if v.strip()]
            data[field] = parts or None
    return data


def _jsonable(value):
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, dict):
        return {k: _jsonable(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_jsonable(v) for v in value]
    try:
        json.dumps(value)
        return value
    except TypeError:
        return str(value)


def dispatch_task(service, action, params=None):
    if service == "system":
        data = params or {}
        if action == "graph_check":
            return _graph_check(data.get("service"))
        if action == "check_powershell_modules":
            modules = data.get("modules") or POWERSHELL_MODULES.get(data.get("service"), [])
            return _check_powershell_modules(modules)
        if action == "health_check":
            return _health_check()
        if action == "tenant_info":
            return _tenant_info()
        raise ValueError(f"Unknown action '{action}' for service '{service}'")

    if service == "reports":
        data = params or {}
        if action == "user_audit":
            return _user_audit_report(
                user_id=data.get("user_id"),
                include_groups=bool(data.get("include_groups", True)),
                include_licenses=bool(data.get("include_licenses", True)),
                include_signins=bool(data.get("include_signins", False)),
                include_devices=bool(data.get("include_devices", False)),
                include_mailbox_stats=bool(data.get("include_mailbox_stats", False)),
            )
        if action == "gpo_audit":
            return _gpo_audit_report(name=data.get("name"))
        if action == "gpo_link_audit":
            return _gpo_link_audit_report(ou_dn=data.get("ou_dn"))
        raise ValueError(f"Unknown action '{action}' for service '{service}'")

    if action == "bulk_update":
        data = params or {}
        return _bulk_update(
            service,
            data.get("update_action"),
            data.get("items") or [],
            data.get("context") or {},
        )

    if service not in ACTIONS:
        raise ValueError(f"Unknown service '{service}'")
    if action not in ACTIONS[service]:
        raise ValueError(f"Unknown action '{action}' for service '{service}'")

    spec = ACTIONS[service][action]
    required = spec.get("required", [])
    payload = _normalize_params(spec, params or {})
    for key in required:
        if not payload.get(key):
            raise ValueError(f"Missing required parameter: {key}")

    if service == "onedrive" and action == "get_user_drive_id":
        cfg = STATE.config
        client = OneDriveClient(
            STATE.get_graph(),
            drive_id=cfg.onedrive_drive_id or "",
            powershell_options={"session": STATE.powershell, "admin_url": cfg.spo_admin_url},
        )
    else:
        client = STATE.get_client(service)
    method = getattr(client, spec["method"])
    call_params = {**spec.get("defaults", {}), **payload}
    if "user_id" in inspect.signature(method).parameters and "user_id" not in call_params:
        if STATE.config.graph_user_id:
            call_params["user_id"] = STATE.config.graph_user_id
        else:
            raise ValueError("GRAPH_USER_ID is required for app-only Graph calls. Set GRAPH_USER_ID in .env.")
    result = method(**call_params)
    return _jsonable(result)
