from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Iterable, List, Optional

from .probe_registry import PROBE_REGISTRY
from .snapshot_models import ProbeResult


LENS_TEMPLATE: Dict[str, Any] = {
    "identity": {
        "platform": {},
        "ids": {},
        "principals": {"primary_user_upn": None},
        "join": {},
    },
    "connectivity": {
        "interfaces": [],
        "routes": {"default_gw": None},
        "probes": [],
        "context": {
            "zone": None,
            "site": None,
            "vpn_present": None,
            "proxy_present": None,
            "subnet": None,
            "gateway": None,
        },
    },
    "authz": {
        "access": {"group_memberships": [], "licenses": []},
        "signins": {"summary": {}, "recent_failures": []},
        "policy": {"ca_blocks": []},
    },
    "config": {
        "firewall": {"profiles": []},
        "dns": {"zones": []},
        "dhcp": {"scopes": []},
        "shares": [],
        "printers": [],
        "certificates": [],
        "registry_watchlist": {"watchlist_id": None, "items": []},
    },
    "health": {
        "uptime_seconds": None,
        "findings": [],
        "replication": {"summary": {}, "partners": []},
        "time": {},
        "services": [],
        "processes": {"summary": {}, "suspicious": []},
        "resources": {},
        "queues": {},
        "lease_summary": {},
        "smb": {"sessions": [], "open_files": []},
        "print_queues": [],
        "eventlog_summary": {},
    },
    "dependencies": {
        "directory": {"current_dc": None, "dc_candidates": []},
        "gpo_mappings": [],
    },
    "change": {},
    "activity": {},
}


def _get_template_value(path: str) -> Any:
    parts = [part for part in path.split(".") if part]
    node: Any = LENS_TEMPLATE
    for part in parts:
        if isinstance(node, dict) and part in node:
            node = node[part]
        else:
            return None
    return node


def _ensure_path(root: Dict[str, Any], path: List[str]) -> Dict[str, Any]:
    node = root
    for part in path:
        if part not in node or not isinstance(node.get(part), dict):
            node[part] = {}
        node = node[part]
    return node


def _merge_into(target: Any, data: Any, default: Any) -> Any:
    if data is None:
        return target
    if isinstance(target, list):
        if isinstance(data, list):
            target.extend(data)
        else:
            target.append(data)
        return target
    if isinstance(target, dict):
        if isinstance(data, dict):
            target.update(data)
            return target
        # preserve object shape if default expects object
        if isinstance(default, dict):
            target["value"] = data
            return target
        return data
    return data


def _apply_path(lens: Dict[str, Any], path: str, data: Any) -> None:
    parts = [part for part in path.split(".") if part]
    if not parts:
        return
    if parts[0] == "lens":
        parts = parts[1:]
    parent_path = parts[:-1]
    key = parts[-1]
    parent = _ensure_path(lens, parent_path)
    default_value = _get_template_value(".".join(parts))
    current_value = parent.get(key)
    if current_value is None and isinstance(default_value, list):
        current_value = []
    elif current_value is None and isinstance(default_value, dict):
        current_value = {}
    if current_value is None:
        parent[key] = data
        return
    parent[key] = _merge_into(current_value, data, default_value)


def _extract_probe_id(result: Any) -> Optional[str]:
    if isinstance(result, ProbeResult):
        return result.probe
    if isinstance(result, dict):
        return result.get("probe")
    return None


def _extract_probe_data(result: Any) -> Any:
    if isinstance(result, ProbeResult):
        return result.data
    if isinstance(result, dict):
        return result.get("data")
    return None


def assemble_lens(subject_kind: str, probe_results: Iterable[Any], registry: Optional[Iterable[Dict[str, Any]]] = None) -> Dict[str, Any]:
    lens = deepcopy(LENS_TEMPLATE)
    registry_items = list(registry or PROBE_REGISTRY)
    registry_map = {entry.get("probe_id"): entry for entry in registry_items if entry.get("probe_id")}

    for result in probe_results or []:
        probe_id = _extract_probe_id(result)
        if not probe_id:
            continue
        entry = registry_map.get(probe_id) or {}
        outputs_to = entry.get("outputs_to") or []
        data = _extract_probe_data(result)
        for path in outputs_to:
            if not path:
                continue
            apply_value = data
            if isinstance(data, dict):
                parts = [part for part in path.split(".") if part]
                if parts and parts[0] == "lens":
                    parts = parts[1:]
                if parts:
                    leaf = parts[-1]
                    template_value = _get_template_value(".".join(parts))
                    if leaf in data:
                        candidate = data.get(leaf)
                        if isinstance(template_value, dict) and isinstance(candidate, dict):
                            apply_value = candidate
                        elif isinstance(template_value, list) and isinstance(candidate, list):
                            apply_value = candidate
                        elif template_value is None and not isinstance(candidate, (dict, list)):
                            apply_value = candidate
            _apply_path(lens, path, apply_value)

    return lens
