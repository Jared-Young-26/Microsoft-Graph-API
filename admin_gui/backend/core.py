import json
import os
import sys
import inspect
import time
import getpass
import socket
import base64
import secrets
import shutil
import uuid
import threading
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = Path(__file__).resolve().parent / "config.json"
TOPOLOGY_HISTORY_PATH = Path(__file__).resolve().parent / "topology_history.json"
TOPOLOGY_HISTORY_DEFAULT_LIMIT = 50
AUDIT_LOG_PATH = Path(__file__).resolve().parent / "audit_log.jsonl"
ACTION_SNAPSHOT_PATH = Path(__file__).resolve().parent / "action_snapshots.sqlite"
ACTION_SNAPSHOT_LEGACY_PATH = Path(__file__).resolve().parent / "action_snapshots.jsonl"
ARTIFACTS_DIR = Path(__file__).resolve().parent / "artifacts"
SNAPSHOT_DB_PATH = Path(__file__).resolve().parent / "snapshots.sqlite"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

load_dotenv(dotenv_path=ROOT / ".env")

ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

from microsoft import (
    GraphSession,
    PowerShellSession,
    GraphAPIError,
    PowerShellCommandError,
    is_powershell_envelope,
)
from .capabilities import (
    build_capability_registry,
    get_action_capability,
    SERVICE_MODULES,
    LOCAL_SERVICES,
)

try:
    import keyring
except Exception:
    keyring = None

try:
    from cryptography.fernet import Fernet, InvalidToken
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
except Exception:
    Fernet = None
    InvalidToken = Exception
    PBKDF2HMAC = None
    hashes = None

KEYCHAIN_SERVICE = "graph-admin-studio"
EXPORT_KEYCHAIN_PREFIX = "export"
CONFIG_EXPORT_VERSION = 1


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


def _export_keychain_key(tenant_id, client_id):
    tenant = tenant_id or "tenant"
    client = client_id or "client"
    return f"{EXPORT_KEYCHAIN_PREFIX}:{tenant}:{client}"


def _get_export_key(tenant_id, client_id):
    if not keyring:
        return None
    return keyring.get_password(KEYCHAIN_SERVICE, _export_keychain_key(tenant_id, client_id))


def _set_export_key(tenant_id, client_id, secret):
    if not keyring:
        raise RuntimeError("Keychain integration not available. Install keyring to enable it.")
    keyring.set_password(KEYCHAIN_SERVICE, _export_keychain_key(tenant_id, client_id), secret)


def _get_or_create_export_key(tenant_id, client_id):
    existing = _get_export_key(tenant_id, client_id)
    if existing:
        return existing
    if Fernet is None:
        raise RuntimeError("cryptography is required for secure exports.")
    new_key = Fernet.generate_key().decode("utf-8")
    _set_export_key(tenant_id, client_id, new_key)
    return new_key


def _derive_key(passphrase, salt):
    if Fernet is None or PBKDF2HMAC is None or hashes is None:
        raise RuntimeError("cryptography is required for secure exports.")
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=120_000,
    )
    return base64.urlsafe_b64encode(kdf.derive(passphrase.encode("utf-8")))


def _encrypt_payload(payload, passphrase=None, use_keychain=False, tenant_id=None, client_id=None):
    if Fernet is None:
        raise RuntimeError("cryptography is required for secure exports.")
    passphrase = passphrase or None
    if passphrase:
        salt = secrets.token_bytes(16)
        key = _derive_key(passphrase, salt)
        kdf = "pbkdf2-sha256"
        keychain_used = False
    else:
        if not use_keychain:
            raise RuntimeError("Passphrase required (or enable keychain fallback).")
        key = _get_or_create_export_key(tenant_id, client_id).encode("utf-8")
        salt = None
        kdf = "keychain"
        keychain_used = True
    token = Fernet(key).encrypt(json.dumps(payload).encode("utf-8"))
    return {
        "format": "graph-admin-studio-config",
        "version": CONFIG_EXPORT_VERSION,
        "kdf": kdf,
        "salt": base64.b64encode(salt).decode("utf-8") if salt else None,
        "token": token.decode("utf-8"),
        "keychain": keychain_used,
    }


def _decrypt_payload(blob, passphrase=None, tenant_id=None, client_id=None):
    if Fernet is None:
        raise RuntimeError("cryptography is required for secure imports.")
    if not isinstance(blob, dict):
        raise RuntimeError("Invalid config payload.")
    token = blob.get("token")
    if not token:
        raise RuntimeError("Encrypted payload missing token.")
    salt_b64 = blob.get("salt")
    passphrase = passphrase or None
    if salt_b64:
        if not passphrase:
            raise RuntimeError("Passphrase required to decrypt this export.")
        salt = base64.b64decode(salt_b64)
        key = _derive_key(passphrase, salt)
    else:
        key_string = _get_export_key(tenant_id, client_id)
        if not key_string:
            raise RuntimeError("Keychain export key not found. Provide a passphrase instead.")
        key = key_string.encode("utf-8")
    try:
        raw = Fernet(key).decrypt(token.encode("utf-8"))
    except InvalidToken as exc:
        raise RuntimeError("Failed to decrypt config payload. Check passphrase/keychain.") from exc
    return json.loads(raw.decode("utf-8"))
from exchange import ExchangeClient
from platform_core.snapshots import SnapshotStore, normalize_topology_snapshot
from platform_core.action_snapshots import SnapshotStore as ActionSnapshotStore, diff_json
from platform_core.snapshot_storage import SnapshotSqlStore
from platform_core.entity_resolution import EntityResolver
from platform_core.snapshot_engine import SnapshotEngine
from platform_core.symptom_templates import list_symptom_templates, get_symptom_template
from platform_core.interpreter import interpret_response
from platform_core.probe_handlers import build_probe_handlers
from platform_core.registry_watchlists import DEFAULT_WATCHLISTS
from onedrive import OneDriveClient
from sharepoint import SharePointClient
from teams import TeamsClient
from entra import EntraClient
from azure import AzureClient
from purview import PurviewClient
from local_ad import LocalADClient
from local_endpoint import LocalEndpointClient
from local_domain_controller import LocalDomainControllerClient
from local_printers import LocalPrinterClient
from local_network import LocalNetworkClient
from remote_ssh import RemoteSSHClient
from local_fileserver import LocalFileServerClient
from local_topology import LocalTopologyClient
from local_time import LocalTimeClient
from local_certificates import LocalCertificateClient
from local_processes import LocalProcessClient
from local_baselines import LocalBaselineClient
from local_event_logs import LocalEventLogsClient
from local_registry import LocalRegistryClient


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


def _read_snapshot_catalog():
    data = _read_config_file()
    return data.get("snapshot_catalog") or {}


def _normalize_catalog_entries(entries):
    if not entries:
        return []
    if isinstance(entries, str):
        return [entries]
    if isinstance(entries, list):
        return [entry for entry in entries if entry]
    return []


def _read_registry_watchlists():
    data = _read_config_file()
    stored = data.get("registry_watchlists")
    watchlists = {}
    if isinstance(stored, dict):
        watchlists.update(stored)
    elif isinstance(stored, list):
        for entry in stored:
            if not isinstance(entry, dict):
                continue
            key = entry.get("watchlist_id") or entry.get("id")
            if key:
                watchlists[key] = entry
    for key, default in DEFAULT_WATCHLISTS.items():
        if key not in watchlists:
            watchlists[key] = dict(default)
    return watchlists


def _normalize_watchlist_payload(payload):
    if not isinstance(payload, dict):
        raise ValueError("Watchlist payload must be an object.")
    watchlist_id = payload.get("watchlist_id") or payload.get("id")
    if not watchlist_id:
        raise ValueError("watchlist_id is required.")
    paths = payload.get("paths") or []
    if isinstance(paths, str):
        paths = [paths]
    paths = [path for path in paths if path]
    return {
        "watchlist_id": watchlist_id,
        "name": payload.get("name") or watchlist_id,
        "description": payload.get("description") or "",
        "paths": paths,
    }


def _list_registry_watchlists():
    watchlists = _read_registry_watchlists()
    return {"watchlists": list(watchlists.values())}


def _save_registry_watchlist(payload):
    watchlist = _normalize_watchlist_payload(payload)
    data = _read_config_file()
    existing = data.get("registry_watchlists")
    watchlists = {}
    if isinstance(existing, dict):
        watchlists.update(existing)
    elif isinstance(existing, list):
        for entry in existing:
            if isinstance(entry, dict) and entry.get("watchlist_id"):
                watchlists[entry["watchlist_id"]] = entry
    watchlists[watchlist["watchlist_id"]] = watchlist
    data["registry_watchlists"] = watchlists
    _write_config_file(data)
    return {"watchlist": watchlist}


def _delete_registry_watchlist(watchlist_id: str):
    if not watchlist_id:
        raise ValueError("watchlist_id is required.")
    data = _read_config_file()
    watchlists = data.get("registry_watchlists")
    if isinstance(watchlists, dict):
        watchlists.pop(watchlist_id, None)
        data["registry_watchlists"] = watchlists
    elif isinstance(watchlists, list):
        data["registry_watchlists"] = [entry for entry in watchlists if entry.get("watchlist_id") != watchlist_id]
    _write_config_file(data)
    return {"deleted": watchlist_id}


def _is_ip_address(value: str) -> bool:
    try:
        parts = str(value).split(".")
        if len(parts) != 4:
            return False
        for part in parts:
            if not part.isdigit():
                return False
            num = int(part)
            if num < 0 or num > 255:
                return False
        return True
    except Exception:
        return False


def _build_snapshot_context(extra=None):
    config = _read_config_file()
    time_thresholds = config.get("time_thresholds") or {"warn_ms": 300, "high_ms": 5000}
    mock_mode = bool(config.get("mock_mode", False))
    registry_watchlists = _read_registry_watchlists()
    tls_targets = config.get(
        "tls_endpoints", ["graph.microsoft.com", "login.microsoftonline.com"]
    )
    latency_targets = config.get(
        "latency_endpoints", ["graph.microsoft.com", "login.microsoftonline.com"]
    )
    dns_probe_targets = config.get("dns_probe_targets", ["graph.microsoft.com"])
    public_resolvers = config.get("public_dns_resolvers") or ["1.1.1.1", "8.8.8.8"]
    use_public_resolvers = bool(config.get("enable_public_resolvers", False))
    resolver_list = config.get("dns_resolvers") or []
    if use_public_resolvers:
        resolver_list = list(dict.fromkeys((resolver_list or []) + public_resolvers))
    cert_stores = config.get("cert_stores") or ["My", "Root", "CA"]
    cert_expiring_days = int(config.get("cert_expiring_days") or 30)
    ntp_servers = config.get("ntp_servers") or ["pool.ntp.org"]
    process_include_cmd = bool(config.get("process_include_command_line", False))
    process_max_items = int(config.get("process_max_items") or 200)
    zone_map = config.get("zone_map") or []
    probe_defaults = {
        "health.time.ntp_offset": {"servers": ntp_servers},
        "config.certificates.machine_inventory": {
            "stores": cert_stores,
            "expiring_days": cert_expiring_days,
        },
        "connectivity.tls_probe": {"targets": tls_targets, "port": 443},
        "connectivity.latency.external_endpoints": {"targets": latency_targets, "port": 443},
        "connectivity.dns.multi_resolver": {
            "targets": dns_probe_targets,
            "resolvers": resolver_list,
        },
        "health.process.inventory": {
            "include_command_line": process_include_cmd,
            "max_items": process_max_items,
        },
        "health.eventlog.summary": {
            "log_names": config.get("eventlog_default_logs") or ["System", "Application"],
            "levels": config.get("eventlog_default_levels") or ["Error", "Warning"],
            "time_window_hours": int(config.get("eventlog_default_hours") or 24),
            "max_events": int(config.get("eventlog_default_max_events") or 500),
            "sample_size": int(config.get("eventlog_default_sample") or 10),
        },
    }
    context = {
        "source": "portal",
        "service": "snapshot",
        "probe_handlers": build_probe_handlers(),
        "probe_defaults": probe_defaults,
        "time_thresholds": time_thresholds,
        "zone_map": zone_map,
        "registry_watchlists": registry_watchlists,
        "mock_mode": mock_mode,
    }
    if isinstance(extra, dict):
        context.update(extra)
    return context


ROLE_KIND_MAP = {
    "actor.user": "user",
    "actor.device": "device",
    "dependency.dc": "dc",
    "dependency.dns": "dns_server",
    "dependency.dhcp": "dhcp_server",
    "dependency.file_server": "file_server",
    "dependency.print_server": "print_server",
}


def _subjects_from_roles(roles, issue, catalog):
    subjects = []
    if not roles:
        return subjects
    for role in roles:
        kind = ROLE_KIND_MAP.get(role)
        if not kind:
            continue
        if role.startswith("actor."):
            if role == "actor.user":
                user = issue.get("user") or issue.get("upn") or issue.get("user_id")
                if user:
                    subjects.append({"kind": "user", "identifiers": {"upn": user}})
            if role == "actor.device":
                device = issue.get("device") or issue.get("hostname") or issue.get("ip")
                if device:
                    alias_type = "ip" if _is_ip_address(str(device)) else "hostname"
                    subjects.append({"kind": "device", "identifiers": {alias_type: device}})
        if role.startswith("dependency."):
            catalog_key = None
            if role == "dependency.dc":
                catalog_key = "domain_controllers"
            elif role == "dependency.dns":
                catalog_key = "dns_servers"
            elif role == "dependency.dhcp":
                catalog_key = "dhcp_servers"
            elif role == "dependency.file_server":
                catalog_key = "file_servers"
            elif role == "dependency.print_server":
                catalog_key = "print_servers"
            if catalog_key:
                for entry in _normalize_catalog_entries(catalog.get(catalog_key)):
                    subjects.append({"kind": kind, "identifiers": {"hostname": entry}})
    return subjects


def _derive_subjects_from_issue(issue, template=None):
    if not isinstance(issue, dict):
        return []
    subjects = []
    user = issue.get("user") or issue.get("upn") or issue.get("user_id")
    device = issue.get("device") or issue.get("hostname") or issue.get("ip")
    symptom = issue.get("symptom") or ""
    symptom_lower = str(symptom).lower()
    catalog = _read_snapshot_catalog()

    if template:
        roles = template.get("default_subject_roles") or []
        subjects.extend(_subjects_from_roles(roles, issue, catalog))
        derived_rules = template.get("derived_subject_rules") or []
        for rule in derived_rules:
            role = rule.get("role")
            key = rule.get("key")
            if not role or not key:
                continue
            kind = ROLE_KIND_MAP.get(role)
            if not kind:
                continue
            for entry in _normalize_catalog_entries(catalog.get(key)):
                subjects.append({"kind": kind, "identifiers": {"hostname": entry}})
    else:
        if user:
            subjects.append({"kind": "user", "identifiers": {"upn": user}})
        if device:
            alias_type = "ip" if any(char.isdigit() for char in str(device)) and "." in str(device) else "hostname"
            subjects.append({"kind": "device", "identifiers": {alias_type: device}})

    def add_catalog_subjects(kind, key, alias_type="hostname"):
        for entry in _normalize_catalog_entries(catalog.get(key)):
            subjects.append({"kind": kind, "identifiers": {alias_type: entry}})

    if "print" in symptom_lower or "printer" in symptom_lower:
        add_catalog_subjects("print_server", "print_servers")
        add_catalog_subjects("dc", "domain_controllers")
    if "file" in symptom_lower or "share" in symptom_lower or "smb" in symptom_lower:
        add_catalog_subjects("file_server", "file_servers")
        add_catalog_subjects("dns_server", "dns_servers")
    if "login" in symptom_lower or "mfa" in symptom_lower or "signin" in symptom_lower or "auth" in symptom_lower:
        add_catalog_subjects("dc", "domain_controllers")
        add_catalog_subjects("dns_server", "dns_servers")
    if "onedrive" in symptom_lower or "sharepoint" in symptom_lower:
        add_catalog_subjects("dns_server", "dns_servers")
    if "dns" in symptom_lower:
        add_catalog_subjects("dns_server", "dns_servers")
    if "dhcp" in symptom_lower:
        add_catalog_subjects("dhcp_server", "dhcp_servers")

    # remove duplicate canonical identifiers by kind+identifier value
    seen = set()
    unique_subjects = []
    for subj in subjects:
        identifiers = subj.get("identifiers") or {}
        key = (subj.get("kind"), tuple(sorted(identifiers.items())))
        if key in seen:
            continue
        seen.add(key)
        unique_subjects.append(subj)
    return unique_subjects


TOPOLOGY_STORE = SnapshotStore(
    TOPOLOGY_HISTORY_PATH,
    normalizer=normalize_topology_snapshot,
    max_entries=TOPOLOGY_HISTORY_DEFAULT_LIMIT,
)
ACTION_SNAPSHOT_STORE = ActionSnapshotStore(ACTION_SNAPSHOT_PATH, legacy_path=ACTION_SNAPSHOT_LEGACY_PATH)


def _read_topology_history(limit=None):
    return TOPOLOGY_STORE.load(limit=limit)


def _append_topology_history(snapshot, limit=None):
    return TOPOLOGY_STORE.append(snapshot, limit=limit)


def _audit_user():
    try:
        return getpass.getuser()
    except Exception:
        return "unknown"


def _audit_host():
    try:
        return socket.gethostname()
    except Exception:
        return "unknown"


def _log_audit(entry):
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user": _audit_user(),
        "host": _audit_host(),
        **(entry or {}),
    }
    try:
        with AUDIT_LOG_PATH.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, default=str) + "\n")
    except Exception:
        return


def _parse_datetime(value):
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed
    except Exception:
        return None


def _read_audit_log(
    service=None,
    action=None,
    ok=None,
    user=None,
    since=None,
    until=None,
    query=None,
    limit=200,
    offset=0,
):
    if not AUDIT_LOG_PATH.exists():
        return {"items": [], "count": 0, "total": 0}
    try:
        lines = AUDIT_LOG_PATH.read_text(encoding="utf-8").splitlines()
    except Exception:
        return {"items": [], "count": 0, "total": 0}

    since_dt = _parse_datetime(since)
    until_dt = _parse_datetime(until)
    query_text = str(query).lower() if query else None
    service = service or None
    action = action or None
    user = user or None
    if isinstance(ok, str):
        if ok.strip() == "":
            ok = None
        else:
            ok = ok.lower() in ("true", "1", "yes", "ok")

    items = []
    total = 0
    skipped = 0
    for line in reversed(lines):
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
        except Exception:
            continue
        if service and entry.get("service") != service:
            continue
        if action and entry.get("action") != action:
            continue
        if ok is not None and bool(entry.get("ok")) != ok:
            continue
        if user and user.lower() not in str(entry.get("user", "")).lower():
            continue
        ts = _parse_datetime(entry.get("timestamp"))
        if since_dt and ts and ts < since_dt:
            continue
        if until_dt and ts and ts > until_dt:
            continue
        if query_text:
            hay = " ".join(
                str(entry.get(key, ""))
                for key in ("service", "action", "item_id", "user", "host", "error", "request_id")
            ).lower()
            if query_text not in hay:
                continue
        total += 1
        if skipped < (offset or 0):
            skipped += 1
            continue
        if limit and len(items) >= int(limit):
            continue
        items.append(entry)
    return {"items": items, "count": len(items), "total": total}


def _global_admin_check(user_id):
    if not user_id:
        raise ValueError("User ID or UPN is required for global admin check.")
    client = STATE.get_client("entra")
    resolved_user_id = None
    resolved_upn = None
    try:
        user = client.get_user(user_id)
        if isinstance(user, dict):
            resolved_user_id = user.get("id") or resolved_user_id
            resolved_upn = user.get("userPrincipalName") or resolved_upn
    except Exception:
        resolved_user_id = None

    target_id = resolved_user_id or user_id
    roles = client.list_role_definitions(top=200)
    global_roles = []
    for role in roles or []:
        name = str(role.get("displayName") or "").lower()
        if name in ("global administrator", "company administrator"):
            global_roles.append(role)
    role_ids = [role.get("id") for role in global_roles if role.get("id")]
    assignments = []
    for role_id in role_ids:
        try:
            assignments.extend(client.list_role_assignments(top=999, role_definition_id=role_id))
        except Exception:
            continue

    is_global_admin = any(
        assignment.get("principalId") == target_id for assignment in assignments if isinstance(assignment, dict)
    )
    return {
        "user_id": target_id,
        "user_principal_name": resolved_upn,
        "is_global_admin": is_global_admin,
        "role_ids": role_ids,
        "assignment_count": len(assignments),
    }


def _graph_permission_inventory(client_id):
    if not client_id:
        return {"ok": False, "error": "CLIENT_ID is not configured."}
    graph = STATE.get_graph()
    try:
        app_sp = graph.get(
            "/servicePrincipals",
            params={
                "$filter": f"appId eq '{client_id}'",
                "$select": "id,appId,displayName",
            },
        ).json()
    except Exception as exc:
        return {"ok": False, "error": f"Failed to query service principal: {exc}"}
    app_values = app_sp.get("value") or []
    if not app_values:
        return {"ok": False, "error": "Service principal for CLIENT_ID not found."}
    app_entry = app_values[0]
    app_sp_id = app_entry.get("id")

    try:
        graph_sp = graph.get(
            "/servicePrincipals",
            params={
                "$filter": "appId eq '00000003-0000-0000-c000-000000000000'",
                "$select": "id,appRoles,displayName",
            },
        ).json()
    except Exception as exc:
        return {"ok": False, "error": f"Failed to query Microsoft Graph service principal: {exc}"}
    graph_values = graph_sp.get("value") or []
    if not graph_values:
        return {"ok": False, "error": "Microsoft Graph service principal not found."}
    graph_entry = graph_values[0]
    graph_sp_id = graph_entry.get("id")
    graph_roles = {}
    for role in graph_entry.get("appRoles") or []:
        if role.get("allowedMemberTypes") and "Application" not in role.get("allowedMemberTypes"):
            continue
        role_id = role.get("id")
        if role_id:
            graph_roles[str(role_id)] = role.get("value") or role.get("displayName") or role_id

    try:
        assignments = graph.get(
            f"/servicePrincipals/{app_sp_id}/appRoleAssignments",
            params={"$top": 999},
        ).json()
    except Exception as exc:
        return {"ok": False, "error": f"Failed to list app role assignments: {exc}"}

    assigned = []
    for item in assignments.get("value") or []:
        if item.get("resourceId") != graph_sp_id:
            continue
        role_id = item.get("appRoleId")
        name = graph_roles.get(str(role_id)) if role_id else None
        assigned.append(
            {
                "id": role_id,
                "name": name or str(role_id),
            }
        )

    assigned_names = sorted({item.get("name") for item in assigned if item.get("name")})
    return {
        "ok": True,
        "app": {
            "id": app_sp_id,
            "app_id": app_entry.get("appId"),
            "display_name": app_entry.get("displayName"),
        },
        "graph_resource": {
            "id": graph_sp_id,
            "display_name": graph_entry.get("displayName"),
        },
        "assigned": assigned_names,
        "assigned_count": len(assigned_names),
    }


def _security_posture():
    cfg = STATE.config
    modules = _check_powershell_modules(sorted({m for mods in POWERSHELL_MODULES.values() for m in mods}))
    graph_permissions = _graph_permission_inventory(cfg.client_id)
    secrets_location = "OS keychain" if cfg.use_keychain else "config file (.env)"
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "app": {
            "tenant_id": cfg.tenant_id,
            "client_id": cfg.client_id,
            "graph_user_id": cfg.graph_user_id,
            "onedrive_drive_id": cfg.onedrive_drive_id,
        },
        "secrets": {
            "storage": secrets_location,
            "client_secret_set": bool(cfg.client_secret),
            "use_keychain": bool(cfg.use_keychain),
            "keychain_available": keyring is not None,
            "config_lock": bool(cfg.config_lock),
        },
        "permissions": {
            "graph_app_permissions": graph_permissions,
            "powershell_modules": modules,
        },
        "boundaries": {
            "local_only": [
                "localad",
                "printers",
                "network",
                "fileserver",
                "topology",
                "ssh",
                "time",
                "certificates",
                "processes",
                "baselines",
            ],
            "cloud_services": [
                "exchange",
                "onedrive",
                "sharepoint",
                "teams",
                "entra",
                "azure",
                "defender",
                "powerplatform",
                "purview",
                "reports",
            ],
            "cannot": [
                "Operate with delegated user context (app-only Graph only).",
                "Bypass MFA or conditional access policies.",
                "Execute remote PowerShell without local host access.",
                "Store secrets anywhere except local config/keychain.",
            ],
            "notes": [
                "Uses app-only Microsoft Graph permissions (no delegated user context).",
                "Local-only services run PowerShell on this host and require local module installs.",
                "Secrets are stored locally only (never transmitted beyond Microsoft Graph).",
            ],
        },
    }


AUDIT_ACTION_MAP = {
    "update_user": ("user_id", "updates"),
    "update_group": ("group_id", "updates"),
    "update_event": ("event_id", "updates"),
    "update_item": ("item_id", "updates"),
    "update_list_item_fields": ("item_id", "fields"),
    "update_site_permission": ("permission_id", "updates"),
    "update_channel": ("channel_id", "updates"),
}


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
        self.snapshot_store = SnapshotSqlStore(SNAPSHOT_DB_PATH)
        self.entity_resolver = EntityResolver(self.snapshot_store)
        self.snapshot_engine = SnapshotEngine(self.snapshot_store, self.entity_resolver)

    def reload(self):
        if self.powershell:
            self.powershell.close()
        self.config = _build_config()
        self.graph = None
        self.powershell = PowerShellSession()
        self.clients = {}
        self._topology_history = None
        self.snapshot_store = SnapshotSqlStore(SNAPSHOT_DB_PATH)
        self.entity_resolver = EntityResolver(self.snapshot_store)
        self.snapshot_engine = SnapshotEngine(self.snapshot_store, self.entity_resolver)
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
        cfg_file = _read_config_file()
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
            "time_thresholds": cfg_file.get("time_thresholds") or {"warn_ms": 300, "high_ms": 5000},
            "ntp_servers": cfg_file.get("ntp_servers") or ["pool.ntp.org"],
            "tls_endpoints": cfg_file.get("tls_endpoints") or [
                "graph.microsoft.com",
                "login.microsoftonline.com",
            ],
            "latency_endpoints": cfg_file.get("latency_endpoints") or [
                "graph.microsoft.com",
                "login.microsoftonline.com",
            ],
            "dns_probe_targets": cfg_file.get("dns_probe_targets") or ["graph.microsoft.com"],
            "dns_resolvers": cfg_file.get("dns_resolvers") or [],
            "enable_public_resolvers": bool(cfg_file.get("enable_public_resolvers", False)),
            "public_dns_resolvers": cfg_file.get("public_dns_resolvers") or ["1.1.1.1", "8.8.8.8"],
            "cert_stores": cfg_file.get("cert_stores") or ["My", "Root", "CA"],
            "cert_expiring_days": int(cfg_file.get("cert_expiring_days") or 30),
            "process_include_command_line": bool(cfg_file.get("process_include_command_line", False)),
            "process_max_items": int(cfg_file.get("process_max_items") or 200),
            "zone_map": cfg_file.get("zone_map") or [],
            "mock_mode": bool(cfg_file.get("mock_mode", False)),
            "diff_impact_overrides": cfg_file.get("diff_impact_overrides") or {},
            "registry_watchlists": _read_registry_watchlists(),
            "eventlog_default_logs": cfg_file.get("eventlog_default_logs") or ["System", "Application"],
            "eventlog_default_levels": cfg_file.get("eventlog_default_levels") or ["Error", "Warning"],
            "eventlog_default_hours": int(cfg_file.get("eventlog_default_hours") or 24),
            "eventlog_default_max_events": int(cfg_file.get("eventlog_default_max_events") or 500),
            "eventlog_default_sample": int(cfg_file.get("eventlog_default_sample") or 10),
        }

    def export_config_encrypted(self, passphrase=None, use_keychain=False):
        cfg_file = _read_config_file()
        cfg = self.config
        tenant_id = cfg.tenant_id or cfg_file.get("tenant_id")
        client_id = cfg.client_id or cfg_file.get("client_id")
        client_secret = cfg.client_secret or cfg_file.get("client_secret")
        if cfg_file.get("use_keychain") and not client_secret:
            try:
                client_secret = _get_keychain_secret(tenant_id, client_id)
            except Exception:
                client_secret = None
        cfg_file = dict(cfg_file)
        if client_secret:
            cfg_file["client_secret"] = client_secret
        payload = {
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "config": cfg_file,
        }
        return _encrypt_payload(payload, passphrase=passphrase, use_keychain=use_keychain, tenant_id=tenant_id, client_id=client_id)

    def import_config_encrypted(self, payload, passphrase=None):
        current = _read_config_file()
        locked = bool(current.get("config_lock"))
        if locked:
            raise RuntimeError("Environment is locked. Disable the lock to import configuration.")
        tenant_id = current.get("tenant_id")
        client_id = current.get("client_id")
        decrypted = _decrypt_payload(payload, passphrase=passphrase, tenant_id=tenant_id, client_id=client_id)
        config = decrypted.get("config")
        if not isinstance(config, dict):
            raise RuntimeError("Invalid config payload.")
        use_keychain = bool(config.get("use_keychain"))
        client_secret = config.get("client_secret")
        if use_keychain and client_secret:
            if keyring is not None:
                _set_keychain_secret(config.get("tenant_id"), config.get("client_id"), client_secret)
                config = dict(config)
                config.pop("client_secret", None)
            else:
                config = dict(config)
                config["use_keychain"] = False
        _write_config_file(config)
        self.reload()
        return self.get_config_public()

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
        elif service == "endpoint":
            client = LocalEndpointClient(powershell=ps_session)
        elif service == "domaincontroller":
            client = LocalDomainControllerClient(powershell=ps_session)
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
        elif service == "time":
            client = LocalTimeClient(
                powershell=ps_session,
                snapshot_store=self.snapshot_store,
                config=_read_config_file(),
            )
        elif service == "certificates":
            client = LocalCertificateClient(powershell=ps_session, config=_read_config_file())
        elif service == "processes":
            client = LocalProcessClient(powershell=ps_session, config=_read_config_file())
        elif service == "baselines":
            client = LocalBaselineClient(snapshot_store=self.snapshot_store)
        elif service == "eventlogs":
            client = LocalEventLogsClient(powershell=ps_session)
        elif service == "registry":
            client = LocalRegistryClient(powershell=ps_session)
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
SNAPSHOT_SCHEDULER = None
_SCHEDULER_STARTED = False


def ensure_snapshot_scheduler():
    global _SCHEDULER_STARTED
    global SNAPSHOT_SCHEDULER
    if _SCHEDULER_STARTED:
        return
    scheduler_cls = globals().get("SnapshotScheduler")
    if scheduler_cls is None:
        return
    try:
        if SNAPSHOT_SCHEDULER is None:
            SNAPSHOT_SCHEDULER = scheduler_cls(STATE)
        SNAPSHOT_SCHEDULER.start()
        _SCHEDULER_STARTED = True
    except Exception:
        return

POWERSHELL_MODULES = SERVICE_MODULES

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
            f"'{module}' | Select-Object -First 1 Name, Version"
        )
        try:
            result = session.run_json(cmd)
            if isinstance(result, dict) and not result.get("ok", True):
                results[module] = {"installed": False, "error": result.get("error")}
                continue
            data = result.get("data") if isinstance(result, dict) else None
            if data:
                version = data.get("Version") if isinstance(data, dict) else None
                results[module] = {"installed": True, "version": str(version) if version else None}
            else:
                results[module] = {"installed": False}
        except (PowerShellCommandError, FileNotFoundError) as exc:
            results[module] = {"installed": False, "error": str(exc)}
        except Exception as exc:
            results[module] = {"installed": False, "error": str(exc)}
    try:
        result = session.run_json("Get-Date | Select-Object -First 1")
        ok = isinstance(result, dict) and result.get("ok", True)
        if ok:
            results["PowerShell JSON runner"] = {"installed": True, "version": "ConvertTo-Json"}
        else:
            results["PowerShell JSON runner"] = {"installed": False, "error": result.get("error")}
    except Exception as exc:
        results["PowerShell JSON runner"] = {"installed": False, "error": str(exc)}
    ok = all(entry.get("installed") for entry in results.values()) if results else True
    return {"ok": ok, "modules": results}


def _check_admin_rights():
    session = STATE.powershell
    cmd = (
        "[Security.Principal.WindowsPrincipal] "
        "[Security.Principal.WindowsIdentity]::GetCurrent()"
        ".IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)"
    )
    try:
        result = session.run_json(cmd)
        if isinstance(result, dict) and not result.get("ok", True):
            return {"ok": False, "error": result.get("error")}
        data = result.get("data") if isinstance(result, dict) else None
        is_admin = bool(data) if isinstance(data, bool) else str(data).lower() == "true"
        return {"ok": True, "is_admin": is_admin}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def _check_domain_joined():
    session = STATE.powershell
    cmd = "Get-CimInstance Win32_ComputerSystem | Select-Object -ExpandProperty PartOfDomain"
    try:
        result = session.run_json(cmd)
        if isinstance(result, dict) and not result.get("ok", True):
            return {"ok": False, "error": result.get("error")}
        data = result.get("data") if isinstance(result, dict) else None
        joined = bool(data) if isinstance(data, bool) else str(data).lower() == "true"
        return {"ok": True, "joined": joined}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def _check_rsat_installed():
    session = STATE.powershell
    script = r"""
    $results = @()
    try {
      $capabilities = Get-WindowsCapability -Online -Name 'RSAT.ActiveDirectory.DS-LDS.Tools*','RSAT.GroupPolicy.Management.Tools*' -ErrorAction Stop
      $results = $capabilities | Select-Object Name,State
    } catch {
      try {
        $features = Get-WindowsFeature RSAT-AD-PowerShell,GPMC -ErrorAction Stop
        $results = $features | Select-Object Name,InstallState
      } catch {
        $results = @()
      }
    }
    $results
    """
    try:
        result = session.run_json(script)
        if isinstance(result, dict) and not result.get("ok", True):
            return {"ok": False, "error": result.get("error")}
        data = result.get("data") if isinstance(result, dict) else None
        items = data if isinstance(data, list) else ([data] if data else [])
        installed = False
        details = []
        for item in items:
            if not isinstance(item, dict):
                continue
            name = item.get("Name") or item.get("name")
            state = item.get("State") or item.get("InstallState") or item.get("state")
            details.append({"name": name, "state": state})
            if state and str(state).lower() == "installed":
                installed = True
        if not items:
            return {"ok": False, "error": "RSAT check returned no results."}
        return {"ok": True, "installed": installed, "details": details}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def _action_preflight(service, action):
    if service not in ACTIONS or action not in ACTIONS[service]:
        raise ValueError(f"Unknown action '{action}' for service '{service}'")

    capability = get_action_capability(CAPABILITY_REGISTRY, service, action)
    source_kind = get_action_source(service, action)
    diagnostics = []
    checks = {}
    ok = True
    warning = None

    if not capability:
        return {
            "ok": True,
            "warning": {"message": "Capability metadata not found."},
            "diagnostics": [
                {
                    "type": "capability_missing",
                    "level": "warn",
                    "message": f"No capability metadata for {service}.{action}.",
                }
            ],
            "capability": None,
            "checks": {},
        }

    if source_kind == "graph":
        graph_result = _graph_check(service)
        check = graph_result.get("checks", {}).get(service)
        checks["graph"] = check
        if check and not check.get("ok"):
            status = int(check.get("status") or 0)
            if status >= 500:
                warning = check
            else:
                ok = False
                diagnostics.append(
                    {
                        "type": "graph_error",
                        "level": "error",
                        "message": check.get("message") or "Graph preflight failed.",
                        "status": check.get("status"),
                        "code": check.get("code"),
                        "request_id": check.get("request_id"),
                    }
                )
        elif not check:
            diagnostics.append(
                {
                    "type": "graph_check_missing",
                    "level": "warn",
                    "message": "No graph check configured for this service.",
                }
            )

    if source_kind == "powershell":
        modules = capability.get("required_modules") or []
        module_result = _check_powershell_modules(modules)
        checks["modules"] = module_result
        if not module_result.get("ok", True):
            ok = False
            for module, info in module_result.get("modules", {}).items():
                if not info.get("installed"):
                    diagnostics.append(
                        {
                            "type": "missing_module",
                            "level": "error",
                            "module": module,
                            "message": info.get("error") or f"{module} is not installed.",
                        }
                    )

        if capability.get("requires_rsat"):
            rsat_check = _check_rsat_installed()
            checks["rsat"] = rsat_check
            if not rsat_check.get("ok", False):
                ok = False
                diagnostics.append(
                    {
                        "type": "rsat_check_failed",
                        "level": "error",
                        "message": rsat_check.get("error") or "RSAT check failed.",
                    }
                )
            elif not rsat_check.get("installed", False):
                ok = False
                diagnostics.append(
                    {
                        "type": "rsat_missing",
                        "level": "error",
                        "message": "RSAT tools are not installed. Install RSAT AD/GroupPolicy tools and retry.",
                    }
                )

        if capability.get("requires_admin"):
            admin_check = _check_admin_rights()
            checks["admin"] = admin_check
            if not admin_check.get("ok", False):
                ok = False
                diagnostics.append(
                    {
                        "type": "admin_check_failed",
                        "level": "error",
                        "message": "Failed to verify administrator privileges.",
                        "detail": admin_check.get("error"),
                    }
                )
            elif not admin_check.get("is_admin"):
                ok = False
                diagnostics.append(
                    {
                        "type": "insufficient_privileges",
                        "level": "error",
                        "message": "Administrator privileges are required for this action.",
                    }
                )

        if capability.get("requires_domain_join"):
            domain_check = _check_domain_joined()
            checks["domain_join"] = domain_check
            if not domain_check.get("ok", False):
                ok = False
                diagnostics.append(
                    {
                        "type": "domain_join_check_failed",
                        "level": "error",
                        "message": "Failed to verify domain join status.",
                        "detail": domain_check.get("error"),
                    }
                )
            elif not domain_check.get("joined"):
                ok = False
                diagnostics.append(
                    {
                        "type": "not_domain_joined",
                        "level": "error",
                        "message": "Host is not joined to a domain.",
                    }
                )

    return {
        "ok": ok,
        "warning": warning,
        "diagnostics": diagnostics,
        "capability": capability,
        "checks": checks,
    }


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


def _smoke_test(services=None):
    services = services or list(GRAPH_CHECKS.keys())
    targets = [svc for svc in services if svc in GRAPH_CHECKS]
    if not targets:
        targets = list(GRAPH_CHECKS.keys())
    graph_checks = {"ok": True, "checks": {}}
    for svc in targets:
        result = _graph_check(svc)
        graph_checks["checks"].update(result.get("checks", {}))
    graph_checks["ok"] = all(check.get("ok") for check in graph_checks["checks"].values()) if graph_checks["checks"] else True
    modules = _check_powershell_modules(sorted({m for svc in targets for m in POWERSHELL_MODULES.get(svc, [])}))
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "services": targets,
        "graph": graph_checks,
        "powershell": modules,
    }


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


def _summarize_signins(signins):
    if not isinstance(signins, list):
        return {}
    summary = {
        "total": len(signins),
        "success": 0,
        "failure": 0,
        "conditional_access": {},
        "error_codes": {},
        "failure_reasons": {},
        "apps": {},
    }
    for entry in signins:
        status = entry.get("status") if isinstance(entry, dict) else {}
        error_code = status.get("errorCode") if isinstance(status, dict) else None
        ca_status = entry.get("conditionalAccessStatus") if isinstance(entry, dict) else None
        app = entry.get("appDisplayName") if isinstance(entry, dict) else None
        if error_code in (0, "0", None):
            summary["success"] += 1
        else:
            summary["failure"] += 1
            reason = status.get("failureReason") if isinstance(status, dict) else None
            if reason:
                summary["failure_reasons"][reason] = summary["failure_reasons"].get(reason, 0) + 1
            summary["error_codes"][str(error_code)] = summary["error_codes"].get(str(error_code), 0) + 1
        if ca_status:
            summary["conditional_access"][ca_status] = summary["conditional_access"].get(ca_status, 0) + 1
        if app:
            summary["apps"][app] = summary["apps"].get(app, 0) + 1
    return summary


def _summarize_devices(devices):
    if not isinstance(devices, list):
        return {}
    summary = {
        "total": len(devices),
        "compliance": {},
        "operating_systems": {},
    }
    for device in devices:
        if not isinstance(device, dict):
            continue
        compliance = device.get("complianceState") or device.get("ComplianceState")
        os_name = device.get("operatingSystem") or device.get("OperatingSystem")
        if compliance:
            summary["compliance"][compliance] = summary["compliance"].get(compliance, 0) + 1
        if os_name:
            summary["operating_systems"][os_name] = summary["operating_systems"].get(os_name, 0) + 1
    return summary


def _summarize_ca_policies(policies):
    if not isinstance(policies, list):
        return {}
    summary = {"total": len(policies), "states": {}}
    for policy in policies:
        if not isinstance(policy, dict):
            continue
        state = policy.get("state")
        if state:
            summary["states"][state] = summary["states"].get(state, 0) + 1
    return summary


def _conditional_access_summary_report():
    graph = STATE.get_graph()
    response = graph.get(
        "/identity/conditionalAccess/policies",
        params={
            "$select": "id,displayName,state,conditions,grantControls,sessionControls",
        },
    )
    policies = response.json().get("value", [])
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "count": len(policies),
        "summary": _summarize_ca_policies(policies),
        "policies": policies,
    }


def _sign_in_summary_report(user_id=None, top=25, lookback_hours=None):
    graph = STATE.get_graph()
    cfg = STATE.config
    target_user = user_id or cfg.graph_user_id
    filters = []
    if target_user:
        filters.append(f"userId eq '{target_user}'")
    if lookback_hours:
        try:
            hours = int(lookback_hours)
            cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
            filters.append(f"createdDateTime ge {cutoff.isoformat()}")
        except Exception:
            pass
    params = {
        "$top": int(top) if top else 25,
        "$orderby": "createdDateTime desc",
    }
    if filters:
        params["$filter"] = " and ".join(filters)
    response = graph.get("/auditLogs/signIns", params=params)
    signins = response.json().get("value", [])
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "user_id": target_user,
        "count": len(signins),
        "summary": _summarize_signins(signins),
        "signIns": signins,
    }


def _device_compliance_report(user_id=None, top=50):
    graph = STATE.get_graph()
    cfg = STATE.config
    target_user = user_id or cfg.graph_user_id
    params = {
        "$top": int(top) if top else 50,
        "$select": "id,deviceName,userPrincipalName,complianceState,operatingSystem,lastSyncDateTime,managementAgent",
    }
    if target_user:
        params["$filter"] = f"userId eq '{target_user}'"
    response = graph.get("/deviceManagement/managedDevices", params=params)
    devices = response.json().get("value", [])
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "user_id": target_user,
        "count": len(devices),
        "summary": _summarize_devices(devices),
        "devices": devices,
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
    if is_powershell_envelope(gpos) and not gpos.get("ok", True):
        raise PowerShellCommandError(
            gpos.get("error", {}).get("message", "PowerShell command failed."),
            output=gpos,
        )
    gpos_payload = _extract_action_payload(gpos)
    if isinstance(gpos_payload, dict):
        gpos_list = [gpos_payload]
    else:
        gpos_list = gpos_payload or []
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
    if is_powershell_envelope(inheritance) and not inheritance.get("ok", True):
        raise PowerShellCommandError(
            inheritance.get("error", {}).get("message", "PowerShell command failed."),
            output=inheritance,
        )
    inheritance_payload = _extract_action_payload(inheritance)
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "ou_dn": ou_dn,
        "inheritance": inheritance_payload,
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
        "update_site_permission": lambda client, item, ctx: client.update_site_permission(
            ctx.get("site_id"), item["id"], updates=item["updates"]
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
        item_id = entry.get("id")
        updates = entry.get("updates") or {}
        try:
            if not item_id:
                raise ValueError("Missing item id for bulk update.")
            attempts = 0
            while True:
                attempts += 1
                try:
                    result = handlers[update_action](client, {"id": item_id, "updates": updates}, context)
                    results.append({"id": item_id, "ok": True, "data": _jsonable(result)})
                    _log_audit(
                        {
                            "service": service,
                            "action": update_action,
                            "item_id": item_id,
                            "updates": updates,
                            "context": context,
                            "ok": True,
                        }
                    )
                    break
                except GraphAPIError as exc:
                    status = exc.status_code or 0
                    if status in (429, 500, 502, 503, 504) and attempts < 3:
                        wait = exc.retry_after or min((2 ** attempts) + 0.2, 8)
                        time.sleep(wait)
                        continue
                    raise
        except Exception as exc:
            results.append({"id": entry.get("id"), "ok": False, "error": str(exc)})
            _log_audit(
                {
                    "service": service,
                    "action": update_action,
                    "item_id": item_id,
                    "updates": updates,
                    "context": context,
                    "ok": False,
                    "error": str(exc),
                }
            )
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
        "list_mailbox_permissions": {"method": "list_mailbox_permissions", "required": ["shared_mailbox"]},
        "add_mailbox_permission": {
            "method": "add_mailbox_permission",
            "required": ["shared_mailbox", "user_id"],
        },
        "remove_mailbox_permission": {
            "method": "remove_mailbox_permission",
            "required": ["shared_mailbox", "user_id"],
        },
        "list_send_as_permissions": {"method": "list_send_as_permissions", "required": ["shared_mailbox"]},
        "add_send_as_permission": {"method": "add_send_as_permission", "required": ["shared_mailbox", "user_id"]},
        "remove_send_as_permission": {
            "method": "remove_send_as_permission",
            "required": ["shared_mailbox", "user_id"],
        },
        "list_send_on_behalf": {"method": "list_send_on_behalf", "required": ["shared_mailbox"]},
        "add_send_on_behalf": {"method": "add_send_on_behalf", "required": ["shared_mailbox", "user_id"]},
        "remove_send_on_behalf": {
            "method": "remove_send_on_behalf",
            "required": ["shared_mailbox", "user_id"],
        },
        "list_mailbox_folder_permissions": {
            "method": "list_mailbox_folder_permissions",
            "required": ["shared_mailbox"],
        },
        "add_mailbox_folder_permission": {
            "method": "add_mailbox_folder_permission",
            "required": ["shared_mailbox", "folder_path", "user_id"],
        },
        "update_mailbox_folder_permission": {
            "method": "update_mailbox_folder_permission",
            "required": ["shared_mailbox", "folder_path", "user_id"],
        },
        "remove_mailbox_folder_permission": {
            "method": "remove_mailbox_folder_permission",
            "required": ["shared_mailbox", "folder_path", "user_id"],
        },
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
        "list_list_columns": {"method": "list_list_columns", "required": ["site_id", "list_id"]},
        "create_list_column": {
            "method": "create_list_column",
            "required": ["site_id", "list_id", "display_name"],
            "list_fields": ["choices"],
        },
        "update_list_column": {
            "method": "update_list_column",
            "required": ["site_id", "list_id", "column_id"],
            "list_fields": ["choices"],
        },
        "delete_list_column": {"method": "delete_list_column", "required": ["site_id", "list_id", "column_id"]},
        "list_site_permissions": {"method": "list_site_permissions", "required": ["site_id"]},
        "grant_site_permission": {
            "method": "grant_site_permission",
            "required": ["site_id", "principal_id"],
            "list_fields": ["roles"],
        },
        "delete_site_permission": {"method": "delete_site_permission", "required": ["site_id", "permission_id"]},
        "update_site_permission": {
            "method": "update_site_permission",
            "required": ["site_id", "permission_id"],
            "list_fields": ["roles"],
        },
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
        "list_groups": {"method": "list_groups", "defaults": {"top": 10}},
        "create_group": {
            "method": "create_group",
            "required": ["display_name"],
            "list_fields": ["group_types"],
        },
        "delete_group": {"method": "delete_group", "required": ["group_id"]},
        "update_group": {
            "method": "update_group",
            "required": ["group_id", "updates"],
            "update_fields": ["displayName", "description", "mailEnabled", "securityEnabled", "visibility"],
        },
        "add_group_member": {"method": "add_group_member", "required": ["group_id", "user_id"]},
        "list_group_members": {"method": "list_group_members", "required": ["group_id"], "defaults": {"top": 50}},
        "remove_group_member": {"method": "remove_group_member", "required": ["group_id", "member_id"]},
        "list_service_principals": {"method": "list_service_principals", "defaults": {"top": 10}},
        "list_applications": {"method": "list_applications", "defaults": {"top": 10}},
        "create_application": {"method": "create_application", "required": ["display_name"]},
        "update_application": {"method": "update_application", "required": ["app_id"]},
        "delete_application": {"method": "delete_application", "required": ["app_id"]},
        "create_service_principal": {"method": "create_service_principal", "required": ["app_id"]},
        "list_role_definitions": {"method": "list_role_definitions", "defaults": {"top": 20}},
        "list_role_assignments": {"method": "list_role_assignments", "defaults": {"top": 50}},
        "assign_role": {"method": "assign_role", "required": ["principal_id", "role_definition_id"]},
        "remove_role_assignment": {"method": "remove_role_assignment", "required": ["role_assignment_id"]},
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
        "gpo_links": {"method": "get_gpo_links", "required": ["ou_dn"]},
        "gpo_inheritance": {"method": "get_gpo_inheritance", "required": ["ou_dn"]},
        "gpo_report": {"method": "get_gpo_report", "required": ["name"]},
        "gppref_registry": {"method": "get_gppref_registry_value", "required": ["gpo_name", "key"]},
        "gpresult_report": {"method": "gpresult_report"},
        "link_gpo": {"method": "link_gpo", "required": ["gpo_name", "ou_dn"]},
        "unlink_gpo": {"method": "unlink_gpo", "required": ["gpo_name", "ou_dn"]},
        "backup_gpo": {"method": "backup_gpo", "required": ["gpo_name", "path"]},
        "restore_gpo": {"method": "restore_gpo", "required": ["gpo_name", "path"]},
    },
    "endpoint": {
        "computer_info": {"method": "get_computer_info"},
        "cim_summary": {"method": "get_cim_summary"},
        "systeminfo": {"method": "get_systeminfo"},
        "system_inventory": {"method": "get_system_inventory"},
        "list_processes": {"method": "list_processes", "defaults": {"top": 25}},
        "list_services": {"method": "list_services"},
        "query_event_logs": {"method": "query_event_logs"},
        "wevtutil_query": {"method": "wevtutil_query"},
        "legacy_event_log": {"method": "legacy_event_log"},
        "list_hotfixes": {"method": "list_hotfixes"},
        "list_dism_packages": {"method": "list_dism_packages"},
        "whoami_all": {"method": "whoami_all"},
        "gpresult_report": {"method": "gpresult_report"},
        "rsop_report": {"method": "gpresultant_set_of_policy"},
    },
    "eventlogs": {
        "eventlog_summary": {
            "method": "eventlog_summary",
            "list_fields": ["log_names", "levels", "event_ids", "providers"],
        },
        "eventlog_gpo_failures": {
            "method": "eventlog_summary",
            "defaults": {"log_names": ["Microsoft-Windows-GroupPolicy/Operational", "System"]},
            "list_fields": ["log_names"],
        },
        "eventlog_print_failures": {
            "method": "eventlog_summary",
            "defaults": {"log_names": ["Microsoft-Windows-PrintService/Operational", "System"]},
            "list_fields": ["log_names"],
        },
        "eventlog_rdp_failures": {
            "method": "eventlog_summary",
            "defaults": {"log_names": ["Security"], "event_ids": [4625, 4624]},
            "list_fields": ["log_names", "event_ids"],
        },
        "eventlog_windows_update_failures": {
            "method": "eventlog_summary",
            "defaults": {"log_names": ["Microsoft-Windows-WindowsUpdateClient/Operational", "System"]},
            "list_fields": ["log_names"],
        },
        "export_evtx": {"method": "export_evtx", "list_fields": ["log_names"]},
        "import_evtx": {"method": "import_evtx", "required": ["file_path"]},
    },
    "registry": {
        "list_watchlists": {"method": "list_watchlists"},
        "save_watchlist": {"method": "save_watchlist", "list_fields": ["paths"]},
        "delete_watchlist": {"method": "delete_watchlist", "required": ["watchlist_id"]},
        "capture_watchlist": {"method": "watchlist_snapshot"},
        "diff_watchlist": {"method": "diff_watchlist"},
        "export_reg": {"method": "export_reg", "required": ["path"]},
        "save_hive": {"method": "save_hive", "required": ["hive"]},
    },
    "domaincontroller": {
        "replication_health_summary": {"method": "get_replication_health_summary"},
        "show_replication_partners": {
            "method": "get_replication_partners_for_dc",
            "required": ["dc"],
        },
        "replication_queue": {"method": "get_replication_queue_for_dc", "required": ["dc"]},
        "force_replication_sync": {
            "method": "force_replication_sync_all",
            "required": ["dc"],
        },
        "dc_diagnostics": {"method": "run_dc_health_checks"},
        "list_dcs_nltest": {
            "method": "list_domain_controllers_via_nltest",
            "required": ["domain"],
        },
        "locate_active_dc": {"method": "get_current_dc_for_domain", "required": ["domain"]},
        "ad_replication_partner_metadata": {"method": "get_replication_partner_metadata"},
        "ad_replication_failures": {"method": "get_replication_failures"},
        "ad_replication_queue_operations": {"method": "get_replication_queue_operations"},
        "list_domain_controllers": {"method": "list_domain_controllers"},
        "get_forest_facts": {"method": "get_forest_facts"},
        "get_domain_facts": {"method": "get_domain_facts"},
        "list_fsmo_roles": {"method": "list_fsmo_role_holders"},
        "sysvol_migration_state": {"method": "get_sysvol_migration_state"},
        "time_sync_status": {"method": "get_time_sync_status"},
        "time_sync_monitor": {"method": "monitor_time_sync"},
        "time_sync_health": {"method": "get_time_sync_health"},
    },
    "printers": {
        "list_printers": {"method": "list_printers"},
        "list_gpo_printer_mappings": {"method": "list_gpo_printer_mappings"},
        "cross_reference_printers_gpo": {"method": "cross_reference_printers_gpo"},
    },
    "network": {
        "list_adapters": {"method": "list_adapters"},
        "get_adapter_config": {"method": "get_adapter_config", "required": ["name"]},
        "list_ip_configurations": {"method": "list_ip_configurations"},
        "list_ip_interfaces": {"method": "list_ip_interfaces"},
        "list_adapter_advanced": {"method": "get_adapter_advanced_properties"},
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
        "ping_host": {"method": "ping_host", "list_fields": ["hosts"]},
        "test_port": {"method": "test_port", "required": ["host", "port"]},
        "trace_route": {"method": "trace_route", "required": ["host"]},
        "pathping_analysis": {"method": "pathping_analysis", "required": ["host"]},
        "resolve_dns_name": {"method": "resolve_dns_name", "required": ["name"]},
        "list_dns_records": {"method": "list_dns_server_records", "required": ["zone"]},
        "dns_client_servers": {"method": "get_dns_client_server_addresses"},
        "dns_client_cache": {"method": "get_dns_client_cache"},
        "dns_cache_display": {"method": "get_dns_cache_display"},
        "netstat_connections": {"method": "get_netstat_connections"},
        "tcp_connections": {"method": "get_net_tcp_connections"},
        "list_routes": {"method": "list_routes"},
        "route_print": {"method": "route_print"},
        "list_neighbors": {"method": "list_net_neighbors"},
        "arp_table": {"method": "get_arp_table"},
        "firewall_profiles": {"method": "get_firewall_profiles"},
        "firewall_rules": {"method": "get_firewall_rules"},
        "firewall_ports": {"method": "get_firewall_port_filters"},
        "firewall_settings": {"method": "get_firewall_settings"},
        "firewall_quick_check": {"method": "firewall_quick_check"},
        "smb_test_path": {"method": "test_smb_path", "required": ["unc_path"]},
        "smb_connections": {"method": "get_smb_connections"},
        "smb_sessions": {"method": "get_smb_sessions"},
        "smb_open_files": {"method": "get_smb_open_files"},
        "smb_client_config": {"method": "get_smb_client_configuration"},
        "smb_status": {"method": "smb_status"},
        "net_use": {"method": "list_net_use"},
        "kerberos_tickets": {"method": "list_kerberos_tickets"},
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
    "time": {
        "time_chain": {"method": "time_chain", "list_fields": ["ntp_servers"]},
        "time_drift_history": {"method": "time_drift_history"},
    },
    "certificates": {
        "list_machine_certificates": {"method": "list_machine_certificates", "list_fields": ["stores"]},
        "tls_probe": {"method": "tls_probe", "list_fields": ["targets"]},
    },
    "processes": {
        "process_inventory": {"method": "process_inventory"},
        "service_process_map": {"method": "service_process_map"},
    },
    "baselines": {
        "list_golden": {"method": "list_golden"},
        "set_golden": {"method": "set_golden", "required": ["kind", "snapshot_id"]},
        "clear_golden": {"method": "clear_golden", "required": ["kind"]},
        "compare_golden": {"method": "compare_golden", "required": ["snapshot_id"]},
    },
}

CAPABILITY_REGISTRY = build_capability_registry(ACTIONS)


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


SENSITIVE_KEYWORDS = (
    "password",
    "passphrase",
    "secret",
    "token",
    "credential",
    "private",
    "client_secret",
    "refresh_token",
    "access_token",
)


def _is_sensitive_key(key: str) -> bool:
    normalized = str(key or "").lower()
    if not normalized:
        return False
    if normalized.endswith("_key") or normalized.endswith("apikey"):
        return True
    return any(keyword in normalized for keyword in SENSITIVE_KEYWORDS)


def sanitize_payload(value, depth: int = 0):
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if depth > 6:
        return "[truncated]"
    if isinstance(value, list):
        return [sanitize_payload(item, depth + 1) for item in value]
    if isinstance(value, dict):
        sanitized = {}
        for key, val in value.items():
            if _is_sensitive_key(key):
                sanitized[key] = "[redacted]"
            else:
                sanitized[key] = sanitize_payload(val, depth + 1)
        return sanitized
    return str(value)


def _store_artifact(source_path, prefix="artifact"):
    if not source_path:
        return None
    source = Path(source_path)
    if not source.exists() or not source.is_file():
        return None
    safe_name = source.name.replace(" ", "_")
    token = uuid.uuid4().hex[:8]
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{timestamp}_{token}_{safe_name}"
    dest = ARTIFACTS_DIR / filename
    try:
        shutil.copyfile(source, dest)
    except Exception:
        return None
    return filename


def _hash_file(path: Path):
    try:
        import hashlib

        h = hashlib.sha256()
        size = 0
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                size += len(chunk)
                h.update(chunk)
        return h.hexdigest(), size
    except Exception:
        return None, None


def _record_evidence(kind, source_path, subject_ids=None, description=None, meta=None):
    if not source_path:
        return None
    artifact_name = _store_artifact(source_path, prefix=kind)
    if not artifact_name:
        return None
    artifact_path = ARTIFACTS_DIR / artifact_name
    sha256, size = _hash_file(artifact_path)
    evidence_id = uuid.uuid4().hex
    captured_at = datetime.now(timezone.utc).isoformat()
    meta_payload = dict(meta or {})
    if sha256:
        meta_payload["sha256"] = sha256
    if size is not None:
        meta_payload["size_bytes"] = size
    meta_payload["filename"] = artifact_name
    meta_payload["description"] = description
    meta_payload["source_path"] = str(source_path)
    STATE.snapshot_store.add_evidence(
        evidence_id,
        captured_at,
        kind,
        subject_ids or [],
        artifact_name,
        {"redacted": True},
        meta_payload,
    )
    return {
        "evidence_id": evidence_id,
        "kind": kind,
        "captured_at": captured_at,
        "artifact": {"name": artifact_name, "url": f"/api/artifacts/{artifact_name}"},
        "meta": meta_payload,
    }


def _extract_action_payload(result):
    if is_powershell_envelope(result):
        return result.get("data")
    return result


def classify_action_kind(action: str, service: str | None = None) -> str:
    if service in {"reports"}:
        return "read"
    if action.startswith("list_") or action.startswith("get_") or action.endswith("_report"):
        return "read"
    if action.startswith("eventlog_") or action.endswith("_summary"):
        return "read"
    if action in {"capture_watchlist", "diff_watchlist", "list_watchlists"}:
        return "read"
    if action.startswith(
        (
            "create_",
            "update_",
            "delete_",
            "add_",
            "remove_",
            "set_",
            "enable_",
            "disable_",
            "assign_",
            "link_",
            "unlink_",
            "reset_",
            "restore_",
        )
    ):
        return "write"
    return "event"


TARGET_KEYS = (
    "user_id",
    "user_principal_name",
    "upn",
    "shared_mailbox",
    "mailbox",
    "group_id",
    "member_id",
    "site_id",
    "list_id",
    "item_id",
    "drive_id",
    "event_id",
    "team_id",
    "channel_id",
    "device_id",
    "host",
    "printer",
    "ou_dn",
    "gpo_name",
    "unc_path",
    "id",
)


def _build_snapshot_target(params: dict | None, payload: dict | None = None) -> str:
    params = params or {}
    for key in TARGET_KEYS:
        value = params.get(key)
        if value:
            return str(value)
    if isinstance(payload, dict):
        for key in TARGET_KEYS:
            value = payload.get(key)
            if value:
                return str(value)
        if payload.get("id"):
            return str(payload.get("id"))
    return "global"


SNAPSHOT_READERS = {
    ("entra", "update_user"): {"method": "get_user", "params": ["user_id"]},
    ("entra", "delete_user"): {"method": "get_user", "params": ["user_id"]},
    ("entra", "create_user"): {"method": "get_user", "params": ["user_id"]},
    ("entra", "update_group"): {"method": "get_group", "params": ["group_id"]},
    ("entra", "delete_group"): {"method": "get_group", "params": ["group_id"]},
    ("entra", "create_group"): {"method": "get_group", "params": ["group_id"]},
    ("entra", "update_application"): {"method": "get_application", "params": ["app_id"]},
    ("entra", "delete_application"): {"method": "get_application", "params": ["app_id"]},
    ("entra", "create_application"): {"method": "get_application", "params": ["app_id"]},
    ("exchange", "update_event"): {"method": "get_event", "params": ["event_id", "user_id"]},
    ("teams", "update_channel"): {"method": "get_channel", "params": ["team_id", "channel_id"]},
    ("sharepoint", "update_list_item_fields"): {"method": "get_list_item", "params": ["site_id", "list_id", "item_id"]},
    ("onedrive", "update_item"): {"method": "get_item_metadata", "params": ["item_id"]},
}


def _resolve_snapshot_reader(service: str, action: str, params: dict | None, result: dict | None):
    entry = SNAPSHOT_READERS.get((service, action))
    if not entry:
        return None
    required = entry.get("params") or []
    call_params = {}
    params = params or {}
    for key in required:
        if key in params and params[key] is not None:
            call_params[key] = params[key]
    if result and isinstance(result, dict):
        if "user_id" in required and "user_id" not in call_params and result.get("id"):
            call_params["user_id"] = result.get("id")
        if "group_id" in required and "group_id" not in call_params and result.get("id"):
            call_params["group_id"] = result.get("id")
        if "app_id" in required and "app_id" not in call_params and result.get("id"):
            call_params["app_id"] = result.get("id")
        for key in required:
            if key not in call_params and key in result:
                call_params[key] = result.get(key)
    if not call_params and required:
        return None
    return entry.get("method"), call_params


def _capture_state_snapshot(service: str, action: str, client, params: dict | None, result: dict | None):
    resolved = _resolve_snapshot_reader(service, action, params, result)
    if not resolved:
        return None
    method_name, call_params = resolved
    method = getattr(client, method_name, None)
    if not method:
        return None
    try:
        return method(**call_params)
    except Exception:
        return None


def _snapshot_meta(service: str, action: str, stage: str, ok: bool | None = None) -> dict:
    return {
        "service": service,
        "action": action,
        "stage": stage,
        "tenant": STATE.config.tenant_id or None,
        "tool_version": os.getenv("TOOL_VERSION") or "dev",
        "ok": ok,
    }


def _store_snapshot(
    snapshot_type: str,
    target: str,
    payload: dict | None,
    meta: dict,
    source: dict,
    inputs: dict | None = None,
):
    try:
        ACTION_SNAPSHOT_STORE.put(
            snapshot_type,
            target,
            payload,
            meta,
            source,
            inputs=inputs,
            action=meta.get("action") if isinstance(meta, dict) else None,
            ok=meta.get("ok") if isinstance(meta, dict) else None,
        )
    except Exception:
        return


def _infer_snapshot_entity(service: str, action: str, payload: dict | None, source: str) -> str:
    if service == "reports":
        return action or "report"
    try:
        normalized = interpret_response(service, action, payload, source=source)
        return normalized.get("entity") or "record"
    except Exception:
        return "record"


def _emit_additional_snapshots(service: str, action: str, params: dict | None, result: dict | None, source_kind: str):
    if not isinstance(result, dict):
        return
    meta = _snapshot_meta(service, action, "snapshot", ok=True)
    base_source = {"kind": source_kind, "service": service, "action": action}
    params = params or {}
    inputs = sanitize_payload(params)

    if service == "topology" and action == "collect_topology":
        generated = result.get("generated_at")
        errors = result.get("errors")
        dhcp_server = params.get("dhcp_server") or result.get("dhcp_server") or "local"
        dns_server = params.get("dns_server") or result.get("dns_server") or "local"
        smb_server = params.get("smb_server") or result.get("smb_server") or "local"
        print_server = params.get("print_server") or result.get("print_server") or "local"

        if result.get("dhcp_leases") is not None:
            payload = {
                "generated_at": generated,
                "server": dhcp_server,
                "leases": result.get("dhcp_leases"),
            }
            _store_snapshot(
                "network.dhcp_leases",
                str(dhcp_server),
                sanitize_payload(payload),
                meta,
                base_source,
                inputs=inputs,
            )
        if result.get("dns_records") is not None:
            payload = {
                "generated_at": generated,
                "server": dns_server,
                "records": result.get("dns_records"),
            }
            _store_snapshot(
                "network.dns_records",
                str(dns_server),
                sanitize_payload(payload),
                meta,
                base_source,
                inputs=inputs,
            )
        if result.get("smb_sessions") is not None:
            payload = {
                "generated_at": generated,
                "server": smb_server,
                "sessions": result.get("smb_sessions"),
            }
            _store_snapshot(
                "network.smb_sessions",
                str(smb_server),
                sanitize_payload(payload),
                meta,
                base_source,
                inputs=inputs,
            )
        if result.get("printers") is not None or result.get("print_jobs") is not None:
            payload = {
                "generated_at": generated,
                "server": print_server,
                "printers": result.get("printers"),
                "print_jobs": result.get("print_jobs"),
                "errors": errors,
            }
            _store_snapshot(
                "network.print_server",
                str(print_server),
                sanitize_payload(payload),
                meta,
                base_source,
                inputs=inputs,
            )

    if service == "reports":
        if action == "user_audit":
            user = result.get("user") or {}
            target = (
                user.get("userPrincipalName")
                or user.get("user_principal_name")
                or user.get("id")
                or params.get("user_id")
                or "user"
            )
            groups = result.get("memberOf") or []
            licenses = result.get("licenses") or []
            core = {
                "generated_at": result.get("generated_at"),
                "user_id": user.get("id"),
                "user_principal_name": user.get("userPrincipalName") or user.get("user_principal_name"),
                "display_name": user.get("displayName") or user.get("display_name"),
                "account_enabled": user.get("accountEnabled"),
                "groups": [
                    {
                        "id": g.get("id"),
                        "displayName": g.get("displayName") or g.get("display_name"),
                        "type": g.get("@odata.type"),
                    }
                    for g in groups
                    if isinstance(g, dict)
                ],
                "licenses": [
                    {
                        "skuId": l.get("skuId") if isinstance(l, dict) else None,
                        "skuPartNumber": l.get("skuPartNumber") if isinstance(l, dict) else None,
                    }
                    for l in licenses
                ],
            }
            _store_snapshot(
                "entra.user_core",
                str(target),
                sanitize_payload(core),
                meta,
                base_source,
                inputs=inputs,
            )

            signins = result.get("signIns")
            if isinstance(signins, list) and signins:
                summary = {
                    "generated_at": result.get("generated_at"),
                    "user_id": user.get("id"),
                    "summary": _summarize_signins(signins),
                }
                _store_snapshot(
                    "entra.signin_summary",
                    str(target),
                    sanitize_payload(summary),
                    meta,
                    base_source,
                    inputs=inputs,
                )

        if action == "sign_in_summary":
            target = result.get("user_id") or params.get("user_id") or "tenant"
            _store_snapshot(
                "entra.signin_summary",
                str(target),
                sanitize_payload(result),
                meta,
                base_source,
                inputs=inputs,
            )

        if action == "conditional_access_summary":
            tenant = STATE.config.tenant_id or "tenant"
            _store_snapshot(
                "entra.conditional_access",
                str(tenant),
                sanitize_payload(result),
                meta,
                base_source,
                inputs=inputs,
            )

        if action == "device_compliance":
            target = result.get("user_id") or params.get("user_id") or "tenant"
            _store_snapshot(
                "entra.device_compliance",
                str(target),
                sanitize_payload(result),
                meta,
                base_source,
                inputs=inputs,
            )


def _list_action_snapshots(snapshot_type=None, target=None, limit=50, prefix=None, action=None):
    return ACTION_SNAPSHOT_STORE.list(
        snapshot_type=snapshot_type,
        target=target,
        prefix=prefix,
        action=action,
        limit=limit,
    )


def _get_action_snapshot(snapshot_id):
    return ACTION_SNAPSHOT_STORE.get(snapshot_id)


def _diff_action_snapshots(snapshot_id_a: str, snapshot_id_b: str) -> dict | None:
    if not snapshot_id_a or not snapshot_id_b:
        return None
    snap_a = ACTION_SNAPSHOT_STORE.get(snapshot_id_a)
    snap_b = ACTION_SNAPSHOT_STORE.get(snapshot_id_b)
    if not snap_a or not snap_b:
        return None
    data_a = snap_a.get("data") if isinstance(snap_a, dict) else None
    data_b = snap_b.get("data") if isinstance(snap_b, dict) else None
    diff = diff_json(data_a, data_b)
    summary = {
        "added": len(diff.get("added") or []),
        "removed": len(diff.get("removed") or []),
        "changed": len(diff.get("changed") or []),
    }
    return {
        "type": "json",
        "summary": summary,
        "details": {
            "added": (diff.get("added") or [])[:10],
            "removed": (diff.get("removed") or [])[:10],
            "changed": (diff.get("changed") or [])[:10],
        },
        "snapshots": {
            "a": {"id": snap_a.get("id"), "collected_at": snap_a.get("collected_at")},
            "b": {"id": snap_b.get("id"), "collected_at": snap_b.get("collected_at")},
        },
    }


def _list_engine_snapshots(canonical_id=None, limit=50):
    return STATE.snapshot_store.list_snapshots(canonical_id=canonical_id, limit=limit)


def _get_engine_snapshot(snapshot_id):
    return STATE.snapshot_store.get_snapshot(snapshot_id)


def _list_snapshot_entities(limit=200):
    return STATE.snapshot_store.list_entities(limit=limit)


def _diff_engine_snapshots(snapshot_id_a: str, snapshot_id_b: str):
    from platform_core.snapshot_diff import diff_snapshots

    if not snapshot_id_a or not snapshot_id_b:
        return None
    snap_a = STATE.snapshot_store.get_snapshot(snapshot_id_a)
    snap_b = STATE.snapshot_store.get_snapshot(snapshot_id_b)
    if not snap_a or not snap_b:
        return None
    return diff_snapshots(snap_a, snap_b, store=STATE.snapshot_store)


def _resolve_snapshot_subject(alias_type: str, alias_value: str):
    if not alias_type or not alias_value:
        return None
    canonical_id = STATE.snapshot_store.resolve_alias(alias_type, alias_value)
    if not canonical_id:
        return None
    entity = STATE.snapshot_store.get_entity(canonical_id) or {"canonical_id": canonical_id}
    return entity


def _list_snapshot_events(canonical_ids=None, limit=50):
    return STATE.snapshot_store.list_events(canonical_ids=canonical_ids, limit=limit)


def _list_symptom_templates():
    return list_symptom_templates()


def _create_incident(payload: dict | None):
    if not isinstance(payload, dict):
        raise ValueError("Incident payload must be an object.")
    incident_id = payload.get("incident_id") or uuid.uuid4().hex
    created_at = payload.get("created_at") or datetime.now(timezone.utc).isoformat()
    symptom_id = payload.get("symptom_id")
    status = payload.get("status") or "open"
    title = payload.get("title") or None
    description = payload.get("description") or None
    time_window_start = payload.get("time_window_start") or payload.get("start") or None
    time_window_end = payload.get("time_window_end") or payload.get("end") or None
    STATE.snapshot_store.create_incident(
        incident_id=incident_id,
        created_at=created_at,
        symptom_id=symptom_id,
        status=status,
        title=title,
        description=description,
        time_window_start=time_window_start,
        time_window_end=time_window_end,
    )
    subjects = payload.get("subjects") or []
    for subject in subjects:
        if not isinstance(subject, dict):
            continue
        canonical_id = subject.get("canonical_id")
        role = subject.get("role") or "actor"
        kind = subject.get("kind") or "resource"
        STATE.snapshot_store.add_incident_subject(incident_id, canonical_id, role, kind)
    return {
        "incident_id": incident_id,
        "created_at": created_at,
        "symptom_id": symptom_id,
        "status": status,
        "title": title,
        "description": description,
        "time_window_start": time_window_start,
        "time_window_end": time_window_end,
        "subjects": STATE.snapshot_store.list_incident_subjects(incident_id),
    }


def _list_incidents(limit=50):
    return STATE.snapshot_store.list_incidents(limit=limit)


def _get_incident(incident_id: str):
    if not incident_id:
        return None
    incident = STATE.snapshot_store.get_incident(incident_id)
    if not incident:
        return None
    incident["subjects"] = STATE.snapshot_store.list_incident_subjects(incident_id)
    incident["snapshots"] = STATE.snapshot_store.list_incident_snapshots(incident_id)
    incident["events"] = STATE.snapshot_store.list_incident_events(incident_id)
    return incident


def _update_incident(incident_id: str, updates: dict | None):
    if not incident_id:
        raise ValueError("incident_id is required.")
    if not isinstance(updates, dict):
        raise ValueError("Updates must be an object.")
    STATE.snapshot_store.update_incident(incident_id, updates)
    return _get_incident(incident_id)


def _link_incident_snapshot(incident_id: str, snapshot_id: str):
    if not incident_id or not snapshot_id:
        raise ValueError("incident_id and snapshot_id are required.")
    STATE.snapshot_store.link_incident_snapshot(incident_id, snapshot_id)
    return {"incident_id": incident_id, "snapshot_id": snapshot_id}


def _link_incident_event(incident_id: str, event_id: str):
    if not incident_id or not event_id:
        raise ValueError("incident_id and event_id are required.")
    STATE.snapshot_store.link_incident_event(incident_id, event_id)
    return {"incident_id": incident_id, "event_id": event_id}


def _infer_node_kind(identifier: str | None):
    if not identifier:
        return "resource"
    if "@" in identifier:
        return "user"
    if _is_ip_address(identifier):
        return "ip"
    if str(identifier).lower().startswith("http"):
        return "url"
    return "resource"


def _build_incident_graph(incident_id: str):
    incident = _get_incident(incident_id)
    snapshot_ids = STATE.snapshot_store.list_incident_snapshots(incident_id)
    snapshots = [STATE.snapshot_store.get_snapshot(sid) for sid in snapshot_ids]
    snapshots = [snap for snap in snapshots if snap]
    subjects = STATE.snapshot_store.list_incident_subjects(incident_id)
    nodes = {}
    edges = []

    def _add_node(node_id, kind=None, label=None, role=None):
        if not node_id:
            return
        if node_id not in nodes:
            node_kind = kind or _infer_node_kind(node_id)
            nodes[node_id] = {
                "id": node_id,
                "kind": node_kind,
                "type": node_kind,
                "label": label or node_id,
                "role": role,
            }
        else:
            if role and not nodes[node_id].get("role"):
                nodes[node_id]["role"] = role

    for subject in subjects:
        _add_node(
            subject.get("canonical_id"),
            kind=subject.get("kind"),
            label=subject.get("canonical_id"),
            role=subject.get("role"),
        )

    for snapshot in snapshots:
        subject = snapshot.get("subject") or {}
        _add_node(
            subject.get("canonical_id"),
            kind=subject.get("kind"),
            label=subject.get("display_name") or subject.get("canonical_id"),
        )
        for rel in snapshot.get("relationships") or []:
            if not isinstance(rel, dict):
                continue
            source = rel.get("source")
            target = rel.get("target")
            if source:
                _add_node(source)
            if target:
                _add_node(target)
            edges.append(
                {
                    "source": source,
                    "target": target,
                    "type": rel.get("type") or rel.get("relationship"),
                    "label": rel.get("type") or rel.get("relationship"),
                    "meta": {k: v for k, v in rel.items() if k not in ("source", "target", "type", "relationship")},
                }
            )

    return {
        "incident": incident,
        "nodes": list(nodes.values()),
        "edges": edges,
        "snapshots": snapshots,
    }


def _build_incident_timeline(incident_id: str):
    incident = _get_incident(incident_id)
    snapshot_ids = STATE.snapshot_store.list_incident_snapshots(incident_id)
    snapshots = [STATE.snapshot_store.get_snapshot(sid) for sid in snapshot_ids]
    snapshots = [snap for snap in snapshots if snap]
    event_ids = STATE.snapshot_store.list_incident_events(incident_id)
    events = [STATE.snapshot_store.get_event(eid) for eid in event_ids]
    events = [evt for evt in events if evt]
    timeline = []
    for snapshot in snapshots:
        timeline.append(
            {
                "time": snapshot.get("captured_at"),
                "kind": "snapshot",
                "snapshot_id": snapshot.get("snapshot_id"),
                "subject": snapshot.get("subject"),
            }
        )
    for event in events:
        timeline.append(
            {
                "time": event.get("emitted_at") or event.get("time"),
                "kind": event.get("signal") or event.get("kind") or "event",
                "event": event,
            }
        )
    timeline.sort(key=lambda item: item.get("time") or "")
    return {"incident": incident, "timeline": timeline}


def _list_golden_snapshots():
    return STATE.snapshot_store.list_golden_snapshots()


def _set_golden_snapshot(kind: str, snapshot_id: str, label: str | None = None):
    if not kind or not snapshot_id:
        raise ValueError("kind and snapshot_id are required.")
    STATE.snapshot_store.set_golden_snapshot(kind, snapshot_id, label=label)
    return {"kind": kind, "snapshot_id": snapshot_id, "label": label}


def _clear_golden_snapshot(kind: str):
    if not kind:
        raise ValueError("kind is required.")
    STATE.snapshot_store.clear_golden_snapshot(kind)
    return {"kind": kind, "cleared": True}


def _diff_golden_snapshot(snapshot_id: str):
    from platform_core.snapshot_diff import diff_snapshots

    snapshot = STATE.snapshot_store.get_snapshot(snapshot_id)
    if not snapshot:
        raise ValueError("Snapshot not found.")
    subject = snapshot.get("subject") or {}
    kind = subject.get("kind")
    if not kind:
        raise ValueError("Snapshot kind missing.")
    golden = STATE.snapshot_store.get_golden_snapshot(kind)
    if not golden:
        raise ValueError("No golden baseline for this kind.")
    golden_snapshot = STATE.snapshot_store.get_snapshot(golden.get("snapshot_id"))
    if not golden_snapshot:
        raise ValueError("Golden snapshot not found.")
    return {
        "golden": golden,
        "diff": diff_snapshots(golden_snapshot, snapshot, store=STATE.snapshot_store),
    }


def _get_symptom_template(symptom_id: str):
    return get_symptom_template(symptom_id)


def _snapshot_context_from_payload(payload):
    context = _build_snapshot_context(payload.get("context") if isinstance(payload, dict) else None)
    return context


def _capture_snapshots(payload):
    if not isinstance(payload, dict):
        raise ValueError("Snapshot payload must be an object.")
    profile = payload.get("profile") or "core"
    incident_id = payload.get("incident_id")
    subjects = []
    template = None
    symptom_id = None
    if payload.get("incident"):
        incident = payload.get("incident") or {}
        symptom_id = incident.get("symptom_id")
        if symptom_id:
            template = get_symptom_template(symptom_id)
        subjects = _derive_subjects_from_issue(incident, template=template)
    if payload.get("subjects"):
        subjects = list(payload.get("subjects") or [])
    elif payload.get("subject"):
        subjects = [payload.get("subject")]
    if not subjects:
        raise ValueError("No subjects provided for snapshot capture.")

    context = _snapshot_context_from_payload(payload)
    context.setdefault("graph", STATE.get_graph())
    context.setdefault("powershell", STATE.powershell)

    results = []
    tier0_probe_plan = None
    tier1_probe_plan = None
    tier0_profile = profile
    tier1_profile = "troubleshoot"
    if template:
        probe_plan = template.get("probe_plan") or {}
        tier0_probe_plan = probe_plan.get("tier0") or []
        tier1_probe_plan = probe_plan.get("tier1") or []
        snapshot_profiles = template.get("snapshot_profiles") or {}
        tier0_profile = snapshot_profiles.get("tier0") or profile
        tier1_profile = snapshot_profiles.get("tier1") or "troubleshoot"

    for subject in subjects:
        try:
            tier0_context = dict(context)
            if symptom_id:
                tier0_context["symptom_id"] = symptom_id
                tier0_context["symptom_tier"] = "tier0"
                tier0_context["probe_plan"] = tier0_probe_plan
            result = STATE.snapshot_engine.capture_snapshot(subject, tier0_profile, tier0_context)
            results.append({"ok": True, "subject": subject, "result": result})
            if incident_id and result.get("snapshot_id"):
                try:
                    STATE.snapshot_store.link_incident_snapshot(incident_id, result.get("snapshot_id"))
                except Exception:
                    pass
            if incident_id and result.get("event_id"):
                try:
                    STATE.snapshot_store.link_incident_event(incident_id, result.get("event_id"))
                except Exception:
                    pass

            if tier1_probe_plan:
                outcomes = result.get("probe_outcomes") or []
                should_escalate = any(
                    entry.get("severity") == "high" or entry.get("error_class")
                    for entry in outcomes
                    if isinstance(entry, dict)
                )
                if should_escalate:
                    tier1_context = dict(context)
                    if symptom_id:
                        tier1_context["symptom_id"] = symptom_id
                        tier1_context["symptom_tier"] = "tier1"
                        tier1_context["probe_plan"] = tier1_probe_plan
                        tier1_context["symptom_trigger"] = "tier0_failure"
                    escalation = STATE.snapshot_engine.capture_snapshot(subject, tier1_profile, tier1_context)
                    results.append({"ok": True, "subject": subject, "result": escalation, "escalated": True})
                    if incident_id and escalation.get("snapshot_id"):
                        try:
                            STATE.snapshot_store.link_incident_snapshot(incident_id, escalation.get("snapshot_id"))
                        except Exception:
                            pass
                    if incident_id and escalation.get("event_id"):
                        try:
                            STATE.snapshot_store.link_incident_event(incident_id, escalation.get("event_id"))
                        except Exception:
                            pass
        except Exception as exc:
            results.append({"ok": False, "subject": subject, "error": str(exc)})
    return {
        "profile": profile,
        "count": len(results),
        "results": results,
    }


class SnapshotScheduler:
    def __init__(self, state: "BackendState"):
        self.state = state
        self._thread = None
        self._stop = threading.Event()

    def _load_schedule(self):
        data = _read_config_file()
        schedule = data.get("snapshot_scheduler") or {}
        enabled = bool(schedule.get("enabled", False))
        interval = int(schedule.get("interval_minutes") or 1440)
        profile = schedule.get("profile") or "core"
        subjects = schedule.get("subjects") or data.get("snapshot_baseline_subjects") or []
        return enabled, interval, profile, subjects

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()

    def _run(self):
        while not self._stop.is_set():
            try:
                enabled, interval, profile, subjects = self._load_schedule()
                if enabled and subjects:
                    context = _build_snapshot_context({"source": "scheduler", "service": "snapshot"})
                    context.setdefault("graph", self.state.get_graph())
                    context.setdefault("powershell", self.state.powershell)
                    for subject in subjects:
                        if self._stop.is_set():
                            break
                        try:
                            self.state.snapshot_engine.capture_snapshot(subject, profile, context)
                        except Exception:
                            continue
                sleep_seconds = max(60, interval * 60)
            except Exception:
                sleep_seconds = 300
            self._stop.wait(timeout=sleep_seconds)

def get_action_source(service, action):
    if service in LOCAL_SERVICES:
        return "powershell"
    spec = ACTIONS.get(service, {}).get(action, {})
    method = spec.get("method", "") or ""
    if "powershell" in method:
        return "powershell"
    return "graph"


ACTION_ENDPOINTS = {
    ("entra", "list_users"): "/users",
    ("entra", "get_user"): "/users/{id}",
    ("entra", "update_user"): "/users/{id}",
    ("entra", "list_groups"): "/groups",
    ("entra", "get_group"): "/groups/{id}",
    ("entra", "update_group"): "/groups/{id}",
    ("entra", "list_service_principals"): "/servicePrincipals",
    ("entra", "list_applications"): "/applications",
    ("entra", "update_application"): "/applications/{id}",
    ("exchange", "list_mail_folders"): "/users/{id}/mailFolders",
    ("exchange", "list_messages"): "/users/{id}/messages",
    ("exchange", "list_events"): "/users/{id}/events",
    ("exchange", "update_event"): "/users/{id}/events/{event_id}",
    ("onedrive", "list_drive_items"): "/drives/{drive_id}/root/children",
    ("onedrive", "get_user_drive_id"): "/users/{id}/drive",
    ("sharepoint", "list_sites"): "/sites",
    ("sharepoint", "list_list_items"): "/sites/{site_id}/lists/{list_id}/items",
    ("sharepoint", "update_list_item_fields"): "/sites/{site_id}/lists/{list_id}/items/{item_id}",
    ("teams", "list_channels"): "/teams/{team_id}/channels",
    ("teams", "update_channel"): "/teams/{team_id}/channels/{channel_id}",
    ("reports", "user_audit"): "multi:/users,/memberOf,/licenseDetails,/auditLogs/signIns,/registeredDevices",
    ("reports", "sign_in_summary"): "/auditLogs/signIns",
    ("reports", "conditional_access_summary"): "/identity/conditionalAccess/policies",
    ("reports", "device_compliance"): "/deviceManagement/managedDevices",
    ("topology", "collect_topology"): "powershell:collect_topology",
}


def get_action_endpoint(service, action):
    return ACTION_ENDPOINTS.get((service, action))


def dispatch_task(service, action, params=None):
    params = params or {}
    snapshot_enabled = True
    if isinstance(params, dict) and "_snapshot" in params:
        snapshot_enabled = bool(params.pop("_snapshot"))
    source_kind = get_action_source(service, action)
    source_meta = {
        "kind": source_kind,
        "endpoint": get_action_endpoint(service, action),
        "service": service,
        "action": action,
    }
    request_payload = sanitize_payload(params or {})
    target = _build_snapshot_target(params or {})
    action_kind = classify_action_kind(action, service)
    if service == "system":
        data = params or {}
        try:
            if action == "graph_check":
                result = _graph_check(data.get("service"))
            elif action == "check_powershell_modules":
                modules = data.get("modules") or POWERSHELL_MODULES.get(data.get("service"), [])
                result = _check_powershell_modules(modules)
            elif action == "action_preflight":
                result = _action_preflight(data.get("service"), data.get("action"))
            elif action == "health_check":
                result = _health_check()
            elif action == "smoke_test":
                result = _smoke_test(data.get("services"))
            elif action == "tenant_info":
                result = _tenant_info()
            elif action == "global_admin_check":
                result = _global_admin_check(data.get("user_id") or data.get("upn"))
            elif action == "security_posture":
                result = _security_posture()
            else:
                raise ValueError(f"Unknown action '{action}' for service '{service}'")
        except Exception as exc:
            if snapshot_enabled:
                _store_snapshot(
                    f"action.{service}.{action}",
                    target,
                    {"request": request_payload, "error": str(exc)},
                    _snapshot_meta(service, action, "event", ok=False),
                    source_meta,
                    inputs=request_payload,
                )
            raise
        if snapshot_enabled:
            _store_snapshot(
                f"action.{service}.{action}",
                target,
                {"request": request_payload, "response": sanitize_payload(result)},
                _snapshot_meta(service, action, "event", ok=True),
                source_meta,
                inputs=request_payload,
            )
        if action_kind == "read":
            entity = _infer_snapshot_entity(service, action, result, source_kind)
            if snapshot_enabled:
                _store_snapshot(
                    f"{service}.{entity}",
                    _build_snapshot_target(params, result if isinstance(result, dict) else None),
                    sanitize_payload(result),
                    _snapshot_meta(service, action, "snapshot", ok=True),
                    source_meta,
                    inputs=request_payload,
                )
                _emit_additional_snapshots(service, action, params, result, source_kind)
        return result

    if service == "reports":
        data = params or {}
        try:
            if action == "user_audit":
                result = _user_audit_report(
                    user_id=data.get("user_id"),
                    include_groups=bool(data.get("include_groups", True)),
                    include_licenses=bool(data.get("include_licenses", True)),
                    include_signins=bool(data.get("include_signins", False)),
                    include_devices=bool(data.get("include_devices", False)),
                    include_mailbox_stats=bool(data.get("include_mailbox_stats", False)),
                )
            elif action == "gpo_audit":
                result = _gpo_audit_report(name=data.get("name"))
            elif action == "gpo_link_audit":
                result = _gpo_link_audit_report(ou_dn=data.get("ou_dn"))
            elif action == "sign_in_summary":
                result = _sign_in_summary_report(
                    user_id=data.get("user_id"),
                    top=data.get("top", 25),
                    lookback_hours=data.get("lookback_hours"),
                )
            elif action == "conditional_access_summary":
                result = _conditional_access_summary_report()
            elif action == "device_compliance":
                result = _device_compliance_report(
                    user_id=data.get("user_id"),
                    top=data.get("top", 50),
                )
            else:
                raise ValueError(f"Unknown action '{action}' for service '{service}'")
        except Exception as exc:
            if snapshot_enabled:
                _store_snapshot(
                    f"action.{service}.{action}",
                    target,
                    {"request": request_payload, "error": str(exc)},
                    _snapshot_meta(service, action, "event", ok=False),
                    source_meta,
                    inputs=request_payload,
                )
            raise
        if snapshot_enabled:
            _store_snapshot(
                f"action.{service}.{action}",
                target,
                {"request": request_payload, "response": sanitize_payload(result)},
                _snapshot_meta(service, action, "event", ok=True),
                source_meta,
                inputs=request_payload,
            )
        if action_kind == "read":
            entity = _infer_snapshot_entity(service, action, result, source_kind)
            if snapshot_enabled:
                _store_snapshot(
                    f"{service}.{entity}",
                    _build_snapshot_target(params, result if isinstance(result, dict) else None),
                    sanitize_payload(result),
                    _snapshot_meta(service, action, "snapshot", ok=True),
                    source_meta,
                    inputs=request_payload,
                )
                _emit_additional_snapshots(service, action, params, result, source_kind)
        return result

    if action == "bulk_update":
        data = params or {}
        try:
            result = _bulk_update(
                service,
                data.get("update_action"),
                data.get("items") or [],
                data.get("context") or {},
            )
        except Exception as exc:
            if snapshot_enabled:
                _store_snapshot(
                    f"action.{service}.{action}",
                    target,
                    {"request": request_payload, "error": str(exc)},
                    _snapshot_meta(service, action, "event", ok=False),
                    source_meta,
                    inputs=request_payload,
                )
            raise
        if snapshot_enabled:
            _store_snapshot(
                f"action.{service}.{action}",
                target,
                {"request": request_payload, "response": sanitize_payload(result)},
                _snapshot_meta(service, action, "event", ok=True),
                source_meta,
                inputs=request_payload,
            )
        return result

    if service == "registry" and action in {"list_watchlists", "save_watchlist", "delete_watchlist", "diff_watchlist", "capture_watchlist"}:
        data = params or {}
        if action == "list_watchlists":
            return _list_registry_watchlists()
        if action == "save_watchlist":
            return _save_registry_watchlist(data)
        if action == "delete_watchlist":
            return _delete_registry_watchlist(data.get("watchlist_id") or data.get("id"))
        if action == "diff_watchlist":
            from platform_core.snapshot_diff import diff_snapshots

            snapshot_a = data.get("snapshot_a")
            snapshot_b = data.get("snapshot_b")
            watchlist_id = data.get("watchlist_id")
            canonical_id = data.get("canonical_id")
            if not canonical_id:
                suffix = f"registry-{watchlist_id}" if watchlist_id else "admin_host"
                canonical_id = f"admin_host:{suffix}"
            if not snapshot_a or not snapshot_b:
                history = STATE.snapshot_store.list_snapshots(canonical_id=canonical_id, limit=2)
                if len(history) >= 2:
                    snapshot_a = history[1].get("snapshot_id")
                    snapshot_b = history[0].get("snapshot_id")
            if not snapshot_a or not snapshot_b:
                return {"ok": False, "error": "Not enough snapshots to diff."}
            snap_a = STATE.snapshot_store.get_snapshot(snapshot_a)
            snap_b = STATE.snapshot_store.get_snapshot(snapshot_b)
            if not snap_a or not snap_b:
                return {"ok": False, "error": "Snapshot not found."}
            return {"ok": True, "diff": diff_snapshots(snap_a, snap_b, store=STATE.snapshot_store)}
        if action == "capture_watchlist":
            watchlist_id = data.get("watchlist_id") or "network.core"
            profile = data.get("profile") or "core"
            hostname = data.get("hostname") or f"registry-{watchlist_id}"
            subject = data.get("subject") or {"kind": "admin_host", "identifiers": {"hostname": hostname}}
            context = _build_snapshot_context({"source": "registry"})
            context.setdefault("graph", STATE.get_graph())
            context.setdefault("powershell", STATE.powershell)
            context["probe_plan"] = ["config.registry.watchlist_snapshot"]
            context["probe_options"] = {
                "config.registry.watchlist_snapshot": {
                    "inputs": {
                        "watchlist_id": watchlist_id,
                        "recurse_depth": data.get("recurse_depth", 0),
                        "max_items": data.get("max_items", 200),
                    }
                }
            }
            result = STATE.snapshot_engine.capture_snapshot(subject, profile, context)
            snapshot = STATE.snapshot_store.get_snapshot(result.get("snapshot_id"))
            return {"ok": True, "snapshot": snapshot, "result": result}

    if service not in ACTIONS:
        raise ValueError(f"Unknown service '{service}'")
    if action not in ACTIONS[service]:
        raise ValueError(f"Unknown action '{action}' for service '{service}'")

    spec = ACTIONS[service][action]
    required = spec.get("required", [])
    payload = _normalize_params(spec, params or {})
    update_fields = spec.get("update_fields") or []
    if update_fields and not payload.get("updates"):
        updates = {}
        for field in update_fields:
            if field in payload:
                updates[field] = payload.pop(field)
        if updates:
            payload["updates"] = updates
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
    request_payload = sanitize_payload(call_params)
    target = _build_snapshot_target(call_params)

    if action_kind == "write" and snapshot_enabled:
        pre_payload = _capture_state_snapshot(service, action, client, call_params, None)
        if pre_payload is not None:
            entity = _infer_snapshot_entity(service, action, pre_payload, source_kind)
            _store_snapshot(
                f"{service}.{entity}",
                _build_snapshot_target(call_params, pre_payload if isinstance(pre_payload, dict) else None),
                sanitize_payload(pre_payload),
                _snapshot_meta(service, action, "pre", ok=True),
                source_meta,
                inputs=request_payload,
            )
    try:
        result = method(**call_params)
    except Exception as exc:
        if snapshot_enabled:
            _store_snapshot(
                f"action.{service}.{action}",
                target,
                {"request": request_payload, "error": str(exc)},
                _snapshot_meta(service, action, "event", ok=False),
                source_meta,
                inputs=request_payload,
            )
        if action in AUDIT_ACTION_MAP:
            id_key, update_key = AUDIT_ACTION_MAP[action]
            _log_audit(
                {
                    "service": service,
                    "action": action,
                    "item_id": call_params.get(id_key),
                    "updates": call_params.get(update_key),
                    "context": {
                        key: call_params.get(key)
                        for key in ("user_id", "team_id", "site_id", "list_id")
                        if call_params.get(key) is not None
                    },
                    "ok": False,
                    "error": str(exc),
                }
            )
        raise
    if source_kind == "powershell" and is_powershell_envelope(result):
        if not result.get("ok", True):
            raise PowerShellCommandError(result.get("error", {}).get("message", "PowerShell command failed."), output=sanitize_payload(result))
        result = sanitize_payload(result)
    result_payload = _extract_action_payload(result)
    if action == "gpresult_report" and isinstance(result_payload, dict):
        report_path = result_payload.get("report_path")
        artifact_name = _store_artifact(report_path, prefix="gpresult")
        if artifact_name:
            artifact = {"name": artifact_name, "url": f"/api/artifacts/{artifact_name}"}
            if isinstance(result, dict):
                result.setdefault("meta", {})
                result["meta"]["artifact"] = artifact
            result_payload["artifact"] = artifact
    evidence_items = []
    if service == "eventlogs" and isinstance(result_payload, dict):
        if action == "export_evtx":
            exports = result_payload.get("exports") or []
            for export in exports:
                path = export.get("path") if isinstance(export, dict) else None
                if not path:
                    continue
                evidence = _record_evidence("evtx", path, description=f"EVTX export {export.get('log_name')}")
                if evidence:
                    export["artifact"] = evidence.get("artifact")
                    export["evidence_id"] = evidence.get("evidence_id")
                    evidence_items.append(evidence)
        elif action == "import_evtx":
            file_path = result_payload.get("file_path") or (params or {}).get("file_path")
            evidence = _record_evidence("evtx", file_path, description="EVTX import")
            if evidence:
                evidence_items.append(evidence)
    if service == "registry" and isinstance(result_payload, dict):
        if action == "export_reg":
            export_path = result_payload.get("export_path")
            evidence = _record_evidence("reg_export", export_path, description="Registry export")
            if evidence:
                result_payload["artifact"] = evidence.get("artifact")
                result_payload["evidence_id"] = evidence.get("evidence_id")
                evidence_items.append(evidence)
        elif action == "save_hive":
            hive_path = result_payload.get("hive_path")
            evidence = _record_evidence("registry_hive", hive_path, description="Registry hive save")
            if evidence:
                result_payload["artifact"] = evidence.get("artifact")
                result_payload["evidence_id"] = evidence.get("evidence_id")
                evidence_items.append(evidence)
    if evidence_items:
        result_payload.setdefault("evidence", evidence_items)
        artifacts = [item.get("artifact") for item in evidence_items if item.get("artifact")]
        if artifacts:
            result_payload["artifacts"] = artifacts
            if "artifact" not in result_payload:
                result_payload["artifact"] = artifacts[0]
    if snapshot_enabled:
        _store_snapshot(
            f"action.{service}.{action}",
            target,
            {"request": request_payload, "response": sanitize_payload(result_payload)},
            _snapshot_meta(service, action, "event", ok=True),
            source_meta,
            inputs=request_payload,
        )
    if action_kind == "read":
        entity = _infer_snapshot_entity(service, action, result_payload, source_kind)
        if snapshot_enabled:
            _store_snapshot(
                f"{service}.{entity}",
                _build_snapshot_target(call_params, result_payload if isinstance(result_payload, dict) else None),
                sanitize_payload(result_payload),
                _snapshot_meta(service, action, "snapshot", ok=True),
                source_meta,
                inputs=request_payload,
            )
            _emit_additional_snapshots(service, action, call_params, result_payload, source_kind)
    if action_kind == "write" and snapshot_enabled:
        post_payload = _capture_state_snapshot(service, action, client, call_params, result_payload if isinstance(result_payload, dict) else None)
        if post_payload is not None:
            entity = _infer_snapshot_entity(service, action, post_payload, source_kind)
            _store_snapshot(
                f"{service}.{entity}",
                _build_snapshot_target(call_params, post_payload if isinstance(post_payload, dict) else None),
                sanitize_payload(post_payload),
                _snapshot_meta(service, action, "post", ok=True),
                source_meta,
                inputs=request_payload,
            )
    if action in AUDIT_ACTION_MAP:
        id_key, update_key = AUDIT_ACTION_MAP[action]
        _log_audit(
            {
                "service": service,
                "action": action,
                "item_id": call_params.get(id_key),
                "updates": call_params.get(update_key),
                "context": {
                    key: call_params.get(key)
                    for key in ("user_id", "team_id", "site_id", "list_id")
                    if call_params.get(key) is not None
                },
                "ok": True,
            }
        )
    return _jsonable(result)
