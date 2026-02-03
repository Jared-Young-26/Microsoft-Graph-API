from __future__ import annotations

from typing import Any, Dict

LOCAL_SERVICES = {
    "localad",
    "endpoint",
    "domaincontroller",
    "printers",
    "network",
    "ssh",
    "fileserver",
    "topology",
    "time",
    "certificates",
    "processes",
    "baselines",
    "eventlogs",
    "registry",
    "remote_workflows",
}

SERVICE_MODULES = {
    "exchange": ["ExchangeOnlineManagement"],
    "onedrive": ["Microsoft.Online.SharePoint.PowerShell"],
    "sharepoint": ["Microsoft.Online.SharePoint.PowerShell"],
    "teams": ["MicrosoftTeams"],
    "entra": ["Microsoft.Graph"],
    "azure": ["Az.Accounts"],
    "purview": ["ExchangeOnlineManagement"],
    "localad": ["ActiveDirectory", "GroupPolicy"],
    "endpoint": ["GroupPolicy"],
    "domaincontroller": ["ActiveDirectory"],
    "printers": ["PrintManagement", "GroupPolicy"],
    "network": ["NetAdapter", "NetTCPIP", "NetSecurity", "DnsServer", "SmbShare"],
    "fileserver": [],
    "topology": ["DhcpServer", "DnsServer", "PrintManagement", "SmbShare"],
    "ssh": [],
    "time": [],
    "certificates": [],
    "processes": [],
    "baselines": [],
    "eventlogs": [],
    "registry": [],
    "remote_workflows": [],
}

SERVICE_DEFAULTS = {
    "localad": {"requires_admin": True, "requires_domain_join": True},
    "domaincontroller": {"requires_admin": True, "requires_domain_join": True},
    "printers": {"requires_admin": False, "requires_domain_join": False},
    "network": {"requires_admin": False, "requires_domain_join": False},
    "endpoint": {"requires_admin": False, "requires_domain_join": False},
    "fileserver": {"requires_admin": False, "requires_domain_join": False},
    "topology": {"requires_admin": True, "requires_domain_join": False},
}

RSAT_REQUIRED_MODULES = {"ActiveDirectory", "GroupPolicy"}

ADMIN_REQUIRED_ACTIONS = {
    "network": {
        "enable_adapter",
        "disable_adapter",
        "rename_adapter",
        "set_dhcp",
        "set_static_ipv4",
        "set_dns_servers",
        "set_interface_metric",
        "set_mtu",
    },
    "printers": {"cross_reference_printers_gpo"},
    "domaincontroller": {
        "replication_health_summary",
        "show_replication_partners",
        "replication_queue",
        "force_replication_sync",
        "dc_diagnostics",
        "list_dcs_nltest",
        "locate_active_dc",
        "ad_replication_partner_metadata",
        "ad_replication_failures",
        "ad_replication_queue_operations",
        "list_domain_controllers",
        "get_forest_facts",
        "get_domain_facts",
        "list_fsmo_roles",
        "sysvol_migration_state",
        "time_sync_status",
        "time_sync_monitor",
    },
    "localad": {
        "create_user",
        "reset_password",
        "unlock_account",
        "enable_account",
        "disable_account",
        "create_group",
        "add_group_member",
        "remove_group_member",
        "move_user_to_ou",
        "link_gpo",
        "unlink_gpo",
        "backup_gpo",
        "restore_gpo",
    },
    "registry": {
        "save_hive",
    },
}

DOMAIN_REQUIRED_ACTIONS = {
    "printers": {"list_gpo_printer_mappings", "cross_reference_printers_gpo"},
    "localad": {"list_users", "list_groups", "list_ous", "list_gpos", "gpo_links", "gpo_inheritance"},
    "domaincontroller": set(),
}

ACTION_OVERRIDES: Dict[str, Dict[str, Dict[str, Any]]] = {
    "domaincontroller": {
        "replication_health_summary": {
            "name": "Replication summary",
            "risk": "safe",
            "output_schema": {"type": "list"},
        },
        "show_replication_partners": {
            "name": "Replication partners",
            "risk": "safe",
            "output_schema": {"type": "list"},
        },
        "replication_queue": {
            "name": "Replication queue",
            "risk": "safe",
            "output_schema": {"type": "list"},
        },
        "force_replication_sync": {
            "name": "Force replication sync",
            "risk": "danger",
            "output_schema": {"type": "result"},
        },
        "dc_diagnostics": {
            "name": "DC diagnostics",
            "risk": "caution",
            "output_schema": {"type": "report"},
        },
        "list_domain_controllers": {
            "name": "List domain controllers",
            "risk": "safe",
            "output_schema": {"type": "list"},
        },
        "list_fsmo_roles": {
            "name": "List FSMO roles",
            "risk": "safe",
            "output_schema": {"type": "object"},
        },
        "time_sync_status": {
            "name": "Time sync status",
            "risk": "safe",
            "output_schema": {"type": "object"},
        },
        "time_sync_monitor": {
            "name": "Time sync monitor",
            "risk": "safe",
            "output_schema": {"type": "list"},
        },
    },
    "network": {
        "ping_host": {"name": "Ping host", "risk": "safe", "output_schema": {"type": "list"}},
        "test_port": {"name": "Test TCP port", "risk": "safe", "output_schema": {"type": "object"}},
        "trace_route": {"name": "Trace route", "risk": "safe", "output_schema": {"type": "list"}},
        "pathping_analysis": {"name": "Pathping analysis", "risk": "safe", "output_schema": {"type": "list"}},
        "resolve_dns_name": {"name": "Resolve hostname", "risk": "safe", "output_schema": {"type": "list"}},
        "list_dns_records": {"name": "DNS records", "risk": "safe", "output_schema": {"type": "list"}},
        "dns_client_cache": {"name": "DNS client cache", "risk": "safe", "output_schema": {"type": "list"}},
        "dns_cache_display": {"name": "DNS cache display", "risk": "safe", "output_schema": {"type": "list"}},
    },
    "fileserver": {
        "list_files": {"name": "List files", "risk": "safe", "output_schema": {"type": "list"}},
    },
    "endpoint": {
        "query_event_logs": {"name": "Query event logs", "risk": "safe", "output_schema": {"type": "list"}},
        "legacy_event_log": {"name": "Legacy event log", "risk": "safe", "output_schema": {"type": "list"}},
        "list_processes": {"name": "List processes", "risk": "safe", "output_schema": {"type": "list"}},
        "list_services": {"name": "List services", "risk": "safe", "output_schema": {"type": "list"}},
        "list_hotfixes": {"name": "List hotfixes", "risk": "safe", "output_schema": {"type": "list"}},
    },
    "eventlogs": {
        "eventlog_summary": {"name": "Event log summary", "risk": "safe", "output_schema": {"type": "object"}},
        "eventlog_gpo_failures": {"name": "GPO failures summary", "risk": "safe", "output_schema": {"type": "object"}},
        "eventlog_print_failures": {"name": "Print failures summary", "risk": "safe", "output_schema": {"type": "object"}},
        "eventlog_rdp_failures": {"name": "RDP/logon failures summary", "risk": "caution", "output_schema": {"type": "object"}},
        "eventlog_windows_update_failures": {"name": "Windows Update failures summary", "risk": "safe", "output_schema": {"type": "object"}},
        "export_evtx": {"name": "Export EVTX", "risk": "caution", "output_schema": {"type": "result"}},
        "import_evtx": {"name": "Import EVTX", "risk": "safe", "output_schema": {"type": "object"}},
    },
    "registry": {
        "list_watchlists": {"name": "List watchlists", "risk": "safe", "output_schema": {"type": "list"}},
        "save_watchlist": {"name": "Save watchlist", "risk": "caution", "output_schema": {"type": "result"}},
        "delete_watchlist": {"name": "Delete watchlist", "risk": "caution", "output_schema": {"type": "result"}},
        "capture_watchlist": {"name": "Capture watchlist snapshot", "risk": "safe", "output_schema": {"type": "object"}},
        "diff_watchlist": {"name": "Diff watchlist snapshots", "risk": "safe", "output_schema": {"type": "object"}},
        "export_reg": {"name": "Export .reg", "risk": "caution", "output_schema": {"type": "result"}},
        "save_hive": {"name": "Save registry hive", "risk": "danger", "output_schema": {"type": "result"}},
    },
    "topology": {
        "collect_topology": {"name": "Collect topology", "risk": "safe", "output_schema": {"type": "graph"}},
        "ping_targets": {"name": "Ping targets", "risk": "safe", "output_schema": {"type": "list"}},
    },
    "remote_workflows": {
        "get_endpoint_auth_reality": {
            "name": "Endpoint authentication reality check",
            "risk": "safe",
            "output_schema": {"type": "object"},
        },
        "get_effective_policy": {
            "name": "Effective policy vs intended policy",
            "risk": "safe",
            "output_schema": {"type": "object"},
        },
        "get_service_process_integrity": {
            "name": "Service-to-process integrity check",
            "risk": "safe",
            "output_schema": {"type": "object"},
        },
        "get_recent_failure_causality": {
            "name": "Recent failure causality",
            "risk": "safe",
            "output_schema": {"type": "object"},
        },
        "get_host_network_path": {
            "name": "Host-perspective network path check",
            "risk": "safe",
            "output_schema": {"type": "object"},
        },
    },
}

READ_PREFIXES = (
    "list_",
    "get_",
    "query_",
    "resolve_",
    "ping_",
    "test_",
    "trace_",
    "pathping_",
    "whoami",
    "systeminfo",
    "route_",
    "dns_",
    "smb_",
)

DANGER_PREFIXES = (
    "delete_",
    "remove_",
    "disable_",
    "unlink_",
    "reset_",
    "restore_",
    "force_",
)

WRITE_PREFIXES = (
    "create_",
    "update_",
    "add_",
    "assign_",
    "link_",
    "enable_",
    "set_",
    "rename_",
    "move_",
    "backup_",
)


def _titleize(text: str) -> str:
    return " ".join(part.capitalize() for part in text.split())


def humanize_action(action: str) -> str:
    cleaned = action.replace("_", " ")
    cleaned = cleaned.replace("dc", "DC").replace("fsmo", "FSMO")
    return _titleize(cleaned)


def infer_source(service: str, spec: Dict[str, Any]) -> str:
    if service in LOCAL_SERVICES:
        return "powershell"
    method = (spec or {}).get("method", "") or ""
    if "powershell" in method:
        return "powershell"
    return "graph"


def infer_risk(action: str) -> str:
    if action.startswith(DANGER_PREFIXES):
        return "danger"
    if action.startswith(WRITE_PREFIXES):
        return "caution"
    return "safe"


def infer_output_schema(action: str) -> Dict[str, str]:
    lowered = action.lower()
    if lowered.endswith("_report") or "report" in lowered or "audit" in lowered or "summary" in lowered:
        return {"type": "report"}
    if action.startswith(READ_PREFIXES) or "list" in lowered:
        return {"type": "list"}
    if lowered.endswith("_status") or "status" in lowered or action.startswith("get_"):
        return {"type": "object"}
    return {"type": "result"}


def infer_requires_admin(service: str, action: str, source: str, risk: str) -> bool:
    if source != "powershell":
        return False
    if action in ADMIN_REQUIRED_ACTIONS.get(service, set()):
        return True
    if action.startswith(DANGER_PREFIXES) or action.startswith(WRITE_PREFIXES):
        return True
    return SERVICE_DEFAULTS.get(service, {}).get("requires_admin", False)


def infer_requires_domain_join(service: str, action: str, source: str) -> bool:
    if source != "powershell":
        return False
    if action in DOMAIN_REQUIRED_ACTIONS.get(service, set()):
        return True
    return SERVICE_DEFAULTS.get(service, {}).get("requires_domain_join", False)


def infer_required_modules(service: str, source: str) -> list[str]:
    if source != "powershell":
        return []
    return list(SERVICE_MODULES.get(service, []))


def infer_requires_rsat(required_modules: list[str]) -> bool:
    return bool(set(required_modules or []) & RSAT_REQUIRED_MODULES)


def build_capability_registry(actions: Dict[str, Dict[str, Dict[str, Any]]]) -> Dict[str, Dict[str, Dict[str, Any]]]:
    registry: Dict[str, Dict[str, Dict[str, Any]]] = {}
    for service, action_map in actions.items():
        registry[service] = {}
        for action, spec in action_map.items():
            source = infer_source(service, spec)
            risk = infer_risk(action)
            capability = {
                "service": service,
                "action": action,
                "name": humanize_action(action),
                "source": source,
                "risk": risk,
                "required_modules": infer_required_modules(service, source),
                "requires_admin": infer_requires_admin(service, action, source, risk),
                "requires_domain_join": infer_requires_domain_join(service, action, source),
                "requires_rsat": False,
                "output_schema": infer_output_schema(action),
            }
            allowed_targets = spec.get("allowed_targets")
            if not allowed_targets:
                allowed_targets = ["local", "graph"] if source == "graph" else ["local"]
            capability["allowed_targets"] = allowed_targets
            capability["requires_rsat"] = infer_requires_rsat(capability.get("required_modules"))
            override = ACTION_OVERRIDES.get(service, {}).get(action)
            if override:
                capability.update(override)
            registry[service][action] = capability
    return registry


def get_action_capability(registry: Dict[str, Dict[str, Dict[str, Any]]], service: str, action: str) -> Dict[str, Any] | None:
    return registry.get(service, {}).get(action)
