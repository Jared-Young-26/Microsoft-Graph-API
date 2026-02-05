from platform_core.probe_handlers import (
    time_local_status_probe,
    time_dc_offset_probe,
    time_ntp_offset_probe,
)
from microsoft import is_powershell_envelope


def _unwrap(result):
    """Internal helper for unwrap."""
    if is_powershell_envelope(result):
        return result.get("data")
    return result


class LocalTimeClient:
    """Client for Local Time operations."""
    def __init__(self, powershell=None, snapshot_store=None, config=None):
        """Initialize the instance."""
        self._powershell = powershell
        self._snapshot_store = snapshot_store
        self._config = config or {}

    def _context(self):
        """Internal helper for context."""
        return {
            "powershell": self._powershell,
            "time_thresholds": self._config.get("time_thresholds") or {},
        }

    def time_chain(self, ntp_servers=None):
        """Run time chain."""
        context = self._context()
        local = time_local_status_probe(None, context, {})
        dc = time_dc_offset_probe(None, context, {})
        servers = ntp_servers or self._config.get("ntp_servers") or ["pool.ntp.org"]
        ntp = time_ntp_offset_probe(None, context, {"inputs": {"servers": servers}})
        return {
            "local": _unwrap(local),
            "dc": _unwrap(dc),
            "ntp": _unwrap(ntp),
        }

    def time_drift_history(self, canonical_id=None, limit=50):
        """Run time drift history."""
        try:
            limit = int(limit)
        except Exception:
            limit = 50
        store = self._snapshot_store
        if not store:
            return []
        target_id = canonical_id
        if not target_id:
            for entity in store.list_entities(limit=200):
                if entity.get("kind") == "admin_host":
                    target_id = entity.get("canonical_id")
                    break
        if not target_id:
            return []
        snapshots = store.list_snapshots(canonical_id=target_id, limit=limit)
        rows = []
        for snap in reversed(snapshots):
            time_info = ((snap.get("lens") or {}).get("health") or {}).get("time") or {}
            rows.append(
                {
                    "captured_at": snap.get("captured_at"),
                    "offset_ms": time_info.get("offset_ms"),
                    "dc_offset_ms": time_info.get("dc_offset_ms"),
                    "ntp_offset_ms": time_info.get("ntp_offset_ms"),
                }
            )
        return rows
