from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
import json


def _normalize_list(value):
    """Normalize list."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def normalize_topology_snapshot(data: dict | None) -> dict | None:
    """Normalize topology snapshot."""
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
        "dhcp_server": data.get("dhcp_server"),
        "dns_server": data.get("dns_server"),
        "print_server": data.get("print_server"),
        "smb_server": data.get("smb_server"),
        "dhcp_leases": trimmed_leases,
        "dns_records": trimmed_records,
    }


@dataclass
class SnapshotStore:
    """Snapshot Store."""
    path: Path
    normalizer: Callable[[dict | None], dict | None] | None = None
    max_entries: int = 100

    def load(self, limit: int | None = None) -> list[dict]:
        """Run load."""
        if not self.path.exists():
            return []
        try:
            data = json.loads(self.path.read_text())
            history = data if isinstance(data, list) else []
        except Exception:
            history = []
        if limit:
            try:
                history = history[: int(limit)]
            except Exception:
                pass
        return history

    def save(self, history: list[dict]) -> None:
        """Run save."""
        self.path.write_text(json.dumps(history, indent=2))

    def append(self, snapshot: dict | None, limit: int | None = None) -> list[dict]:
        """Run append."""
        history = self.load()
        normalized = self.normalizer(snapshot) if self.normalizer else snapshot
        if not normalized:
            return history
        history.insert(0, normalized)
        cap = self.max_entries
        try:
            cap = int(limit) if limit is not None else self.max_entries
        except Exception:
            cap = self.max_entries
        if cap and cap > 0:
            history = history[:cap]
        self.save(history)
        return history


def _key_tuple(record: dict, fields: list[str]) -> tuple:
    """Internal helper for key tuple."""
    return tuple(record.get(field) for field in fields)


def diff_records(
    before: list[dict] | None,
    after: list[dict] | None,
    key_fields: list[str],
    compare_fields: list[str] | None = None,
) -> dict:
    """Diff records."""
    before_list = [item for item in _normalize_list(before) if isinstance(item, dict)]
    after_list = [item for item in _normalize_list(after) if isinstance(item, dict)]
    before_index = {}
    for item in before_list:
        key = _key_tuple(item, key_fields)
        if any(key):
            before_index[key] = item
    after_index = {}
    for item in after_list:
        key = _key_tuple(item, key_fields)
        if any(key):
            after_index[key] = item

    added = []
    removed = []
    changed = []

    for key, item in after_index.items():
        if key not in before_index:
            added.append(item)

    for key, item in before_index.items():
        if key not in after_index:
            removed.append(item)

    for key, before_item in before_index.items():
        if key not in after_index:
            continue
        after_item = after_index[key]
        fields = compare_fields or sorted(set(before_item.keys()) | set(after_item.keys()))
        fields = [field for field in fields if field not in key_fields]
        diffs = {}
        for field in fields:
            before_value = before_item.get(field)
            after_value = after_item.get(field)
            if before_value != after_value:
                diffs[field] = {"before": before_value, "after": after_value}
        if diffs:
            changed.append(
                {
                    "key": key,
                    "before": before_item,
                    "after": after_item,
                    "changes": diffs,
                }
            )

    return {
        "added": added,
        "removed": removed,
        "changed": changed,
    }


def diff_topology_snapshots(before: dict | None, after: dict | None) -> dict:
    """Diff topology snapshots."""
    return {
        "dhcp_leases": diff_records(
            before.get("dhcp_leases") if isinstance(before, dict) else [],
            after.get("dhcp_leases") if isinstance(after, dict) else [],
            ["HostName", "IPAddress", "ClientId", "ScopeId"],
        ),
        "dns_records": diff_records(
            before.get("dns_records") if isinstance(before, dict) else [],
            after.get("dns_records") if isinstance(after, dict) else [],
            ["Zone", "HostName", "RecordType", "RecordData"],
        ),
        "snapshot_a": before.get("timestamp") if isinstance(before, dict) else None,
        "snapshot_b": after.get("timestamp") if isinstance(after, dict) else None,
    }
