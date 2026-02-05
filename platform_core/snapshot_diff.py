from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional, Tuple
import uuid

from .snapshot_storage import SnapshotSqlStore


def _now_iso() -> str:
    """Internal helper for now iso."""
    return datetime.now(timezone.utc).isoformat()


def _get_lens(snapshot: Any) -> Dict[str, Any]:
    """Get lens."""
    if not isinstance(snapshot, dict):
        return {}
    return snapshot.get("lens") or {}


def _get_subject_id(snapshot: Any) -> Optional[str]:
    """Get subject id."""
    if not isinstance(snapshot, dict):
        return None
    subject = snapshot.get("subject") or {}
    if isinstance(subject, dict):
        return subject.get("canonical_id")
    return None


def _diff_object(a: Any, b: Any, prefix: str = "") -> Dict[str, List[Dict[str, Any]]]:
    """Diff object."""
    diff = {"added": [], "removed": [], "changed": []}
    if a is None and b is None:
        return diff
    if isinstance(a, dict) and isinstance(b, dict):
        keys = set(a.keys()) | set(b.keys())
        for key in keys:
            path = f"{prefix}.{key}" if prefix else key
            if key not in a:
                diff["added"].append({"path": path, "value": b.get(key)})
            elif key not in b:
                diff["removed"].append({"path": path, "value": a.get(key)})
            else:
                before = a.get(key)
                after = b.get(key)
                if isinstance(before, dict) and isinstance(after, dict):
                    nested = _diff_object(before, after, path)
                    diff["added"].extend(nested["added"])
                    diff["removed"].extend(nested["removed"])
                    diff["changed"].extend(nested["changed"])
                elif before != after:
                    diff["changed"].append({"path": path, "before": before, "after": after})
        return diff
    if a != b:
        diff["changed"].append({"path": prefix, "before": a, "after": b})
    return diff


def _diff_list(
    before_list: Iterable[Dict[str, Any]],
    after_list: Iterable[Dict[str, Any]],
    key_fn,
) -> Dict[str, List[Dict[str, Any]]]:
    """Diff list."""
    before_items = [item for item in before_list if isinstance(item, dict)]
    after_items = [item for item in after_list if isinstance(item, dict)]
    before_map: Dict[str, Dict[str, Any]] = {}
    after_map: Dict[str, Dict[str, Any]] = {}
    for item in before_items:
        key = key_fn(item)
        if key:
            before_map[str(key)] = item
    for item in after_items:
        key = key_fn(item)
        if key:
            after_map[str(key)] = item

    added = []
    removed = []
    changed = []
    for key, item in after_map.items():
        if key not in before_map:
            added.append({"key": key, "item": item})
        else:
            before = before_map.get(key)
            if before != item:
                changed.append({"key": key, "before": before, "after": item})
    for key, item in before_map.items():
        if key not in after_map:
            removed.append({"key": key, "item": item})
    return {"added": added, "removed": removed, "changed": changed}


def _interface_key(item: Dict[str, Any]) -> Tuple[Optional[str], Optional[str]]:
    """Internal helper for interface key."""
    name = item.get("InterfaceAlias") or item.get("Name") or item.get("name")
    mac = item.get("MacAddress") or item.get("mac") or item.get("MACAddress")
    return (str(name).lower() if name else None, str(mac).lower() if mac else None)


def _probe_key(item: Dict[str, Any]) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Internal helper for probe key."""
    name = item.get("name") or item.get("probe") or item.get("type")
    target = item.get("target") or item.get("host") or item.get("address") or item.get("ip")
    port = item.get("port")
    if port is None:
        ports = item.get("ports")
        if isinstance(ports, list):
            port = ",".join(str(p) for p in ports)
        elif ports is not None:
            port = str(ports)
    return (
        str(name).lower() if name else None,
        str(target).lower() if target else None,
        str(port).lower() if port else None,
    )


def _group_key(item: Dict[str, Any]) -> Optional[str]:
    """Internal helper for group key."""
    return item.get("id") or item.get("group_id")


def _printer_key(item: Dict[str, Any]) -> Optional[str]:
    """Internal helper for printer key."""
    return item.get("share_name") or item.get("ShareName") or item.get("name")


def _registry_key(item: Dict[str, Any]) -> Optional[str]:
    """Internal helper for registry key."""
    return item.get("path") or item.get("Path")


def diff_snapshots(snapshot_a: Dict[str, Any], snapshot_b: Dict[str, Any], store: SnapshotSqlStore | None = None) -> Dict[str, Any]:
    """Diff snapshots."""
    lens_a = _get_lens(snapshot_a)
    lens_b = _get_lens(snapshot_b)

    sections: Dict[str, Dict[str, Any]] = {}
    summary: Dict[str, Dict[str, int]] = {}

    # identity (object diff)
    identity_diff = _diff_object(lens_a.get("identity") or {}, lens_b.get("identity") or {}, "identity")
    sections["identity"] = identity_diff
    summary["identity"] = {
        "added": len(identity_diff["added"]),
        "removed": len(identity_diff["removed"]),
        "changed": len(identity_diff["changed"]),
    }

    # connectivity (lists + routes)
    connectivity = {}
    interfaces_diff = _diff_list(
        (lens_a.get("connectivity") or {}).get("interfaces") or [],
        (lens_b.get("connectivity") or {}).get("interfaces") or [],
        _interface_key,
    )
    probes_diff = _diff_list(
        (lens_a.get("connectivity") or {}).get("probes") or [],
        (lens_b.get("connectivity") or {}).get("probes") or [],
        _probe_key,
    )
    routes_diff = _diff_object(
        (lens_a.get("connectivity") or {}).get("routes") or {},
        (lens_b.get("connectivity") or {}).get("routes") or {},
        "connectivity.routes",
    )
    connectivity["interfaces"] = interfaces_diff
    connectivity["probes"] = probes_diff
    connectivity["routes"] = routes_diff
    sections["connectivity"] = connectivity
    summary["connectivity"] = {
        "added": len(interfaces_diff["added"]) + len(probes_diff["added"]) + len(routes_diff["added"]),
        "removed": len(interfaces_diff["removed"]) + len(probes_diff["removed"]) + len(routes_diff["removed"]),
        "changed": len(interfaces_diff["changed"]) + len(probes_diff["changed"]) + len(routes_diff["changed"]),
    }

    # authz (groups + licenses + signins)
    authz = {}
    groups_diff = _diff_list(
        ((lens_a.get("authz") or {}).get("access") or {}).get("group_memberships") or [],
        ((lens_b.get("authz") or {}).get("access") or {}).get("group_memberships") or [],
        _group_key,
    )
    licenses_diff = _diff_list(
        ((lens_a.get("authz") or {}).get("access") or {}).get("licenses") or [],
        ((lens_b.get("authz") or {}).get("access") or {}).get("licenses") or [],
        lambda item: item.get("skuId") or item.get("skuPartNumber"),
    )
    signins_diff = _diff_object(
        (lens_a.get("authz") or {}).get("signins") or {},
        (lens_b.get("authz") or {}).get("signins") or {},
        "authz.signins",
    )
    authz["groups"] = groups_diff
    authz["licenses"] = licenses_diff
    authz["signins"] = signins_diff
    sections["authz"] = authz
    summary["authz"] = {
        "added": len(groups_diff["added"]) + len(licenses_diff["added"]) + len(signins_diff["added"]),
        "removed": len(groups_diff["removed"]) + len(licenses_diff["removed"]) + len(signins_diff["removed"]),
        "changed": len(groups_diff["changed"]) + len(licenses_diff["changed"]) + len(signins_diff["changed"]),
    }

    # config (printers + firewall + dns/dhcp)
    config = {}
    printers_diff = _diff_list(
        (lens_a.get("config") or {}).get("printers") or [],
        (lens_b.get("config") or {}).get("printers") or [],
        _printer_key,
    )
    firewall_diff = _diff_object(
        (lens_a.get("config") or {}).get("firewall") or {},
        (lens_b.get("config") or {}).get("firewall") or {},
        "config.firewall",
    )
    dns_diff = _diff_object(
        (lens_a.get("config") or {}).get("dns") or {},
        (lens_b.get("config") or {}).get("dns") or {},
        "config.dns",
    )
    dhcp_diff = _diff_object(
        (lens_a.get("config") or {}).get("dhcp") or {},
        (lens_b.get("config") or {}).get("dhcp") or {},
        "config.dhcp",
    )
    registry_a = (lens_a.get("config") or {}).get("registry_watchlist") or {}
    registry_b = (lens_b.get("config") or {}).get("registry_watchlist") or {}
    registry_diff = _diff_list(
        registry_a.get("items") or [],
        registry_b.get("items") or [],
        _registry_key,
    )
    config["printers"] = printers_diff
    config["firewall"] = firewall_diff
    config["dns"] = dns_diff
    config["dhcp"] = dhcp_diff
    config["registry_watchlist"] = registry_diff
    sections["config"] = config
    summary["config"] = {
        "added": len(printers_diff["added"])
        + len(firewall_diff["added"])
        + len(dns_diff["added"])
        + len(dhcp_diff["added"])
        + len(registry_diff["added"]),
        "removed": len(printers_diff["removed"])
        + len(firewall_diff["removed"])
        + len(dns_diff["removed"])
        + len(dhcp_diff["removed"])
        + len(registry_diff["removed"]),
        "changed": len(printers_diff["changed"])
        + len(firewall_diff["changed"])
        + len(dns_diff["changed"])
        + len(dhcp_diff["changed"])
        + len(registry_diff["changed"]),
    }

    # health (services + replication + time)
    health = {}
    services_diff = _diff_list(
        (lens_a.get("health") or {}).get("services") or [],
        (lens_b.get("health") or {}).get("services") or [],
        lambda item: item.get("name") or item.get("DisplayName"),
    )
    replication_diff = _diff_object(
        (lens_a.get("health") or {}).get("replication") or {},
        (lens_b.get("health") or {}).get("replication") or {},
        "health.replication",
    )
    time_diff = _diff_object(
        (lens_a.get("health") or {}).get("time") or {},
        (lens_b.get("health") or {}).get("time") or {},
        "health.time",
    )
    eventlog_diff = _diff_object(
        (lens_a.get("health") or {}).get("eventlog_summary") or {},
        (lens_b.get("health") or {}).get("eventlog_summary") or {},
        "health.eventlog_summary",
    )
    health["services"] = services_diff
    health["replication"] = replication_diff
    health["time"] = time_diff
    health["eventlog_summary"] = eventlog_diff
    sections["health"] = health
    summary["health"] = {
        "added": len(services_diff["added"]) + len(replication_diff["added"]) + len(time_diff["added"]) + len(eventlog_diff["added"]),
        "removed": len(services_diff["removed"]) + len(replication_diff["removed"]) + len(time_diff["removed"]) + len(eventlog_diff["removed"]),
        "changed": len(services_diff["changed"]) + len(replication_diff["changed"]) + len(time_diff["changed"]) + len(eventlog_diff["changed"]),
    }

    # dependencies
    dependencies_diff = _diff_object(lens_a.get("dependencies") or {}, lens_b.get("dependencies") or {}, "dependencies")
    sections["dependencies"] = dependencies_diff
    summary["dependencies"] = {
        "added": len(dependencies_diff["added"]),
        "removed": len(dependencies_diff["removed"]),
        "changed": len(dependencies_diff["changed"]),
    }

    # change
    change_diff = _diff_object(lens_a.get("change") or {}, lens_b.get("change") or {}, "change")
    sections["change"] = change_diff
    summary["change"] = {
        "added": len(change_diff["added"]),
        "removed": len(change_diff["removed"]),
        "changed": len(change_diff["changed"]),
    }

    total_added = sum(entry["added"] for entry in summary.values())
    total_removed = sum(entry["removed"] for entry in summary.values())
    total_changed = sum(entry["changed"] for entry in summary.values())

    diff = {
        "summary": summary,
        "totals": {"added": total_added, "removed": total_removed, "changed": total_changed},
        "sections": sections,
        "snapshots": {
            "a": snapshot_a.get("snapshot_id"),
            "b": snapshot_b.get("snapshot_id"),
        },
        "quality": {
            "a": snapshot_a.get("quality") or {},
            "b": snapshot_b.get("quality") or {},
        },
    }

    if store:
        event_id = uuid.uuid4().hex
        canonical_ids = [
            _get_subject_id(snapshot_a),
            _get_subject_id(snapshot_b),
        ]
        canonical_ids = [cid for cid in canonical_ids if cid]
        store.add_event(
            event_id=event_id,
            time=_now_iso(),
            kind="snapshot.diff",
            source="snapshot_engine",
            service="snapshot",
            signal_name="snapshot_diff",
            canonical_ids=canonical_ids,
            event=diff,
        )

    return diff
