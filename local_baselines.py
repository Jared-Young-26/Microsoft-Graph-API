from platform_core.snapshot_diff import diff_snapshots


class LocalBaselineClient:
    """Client for Local Baseline operations."""
    def __init__(self, snapshot_store=None):
        """Initialize the instance."""
        self._store = snapshot_store

    def list_golden(self):
        """List golden."""
        if not self._store:
            return []
        return self._store.list_golden_snapshots()

    def set_golden(self, kind, snapshot_id, label=None):
        """Set golden."""
        if not self._store:
            raise RuntimeError("Snapshot store unavailable.")
        self._store.set_golden_snapshot(kind, snapshot_id, label=label)
        return {"kind": kind, "snapshot_id": snapshot_id, "label": label}

    def clear_golden(self, kind):
        """Run clear golden."""
        if not self._store:
            raise RuntimeError("Snapshot store unavailable.")
        self._store.clear_golden_snapshot(kind)
        return {"kind": kind, "cleared": True}

    def compare_golden(self, snapshot_id):
        """Run compare golden."""
        if not self._store:
            raise RuntimeError("Snapshot store unavailable.")
        snapshot = self._store.get_snapshot(snapshot_id)
        if not snapshot:
            raise ValueError("Snapshot not found.")
        subject = snapshot.get("subject") or {}
        kind = subject.get("kind")
        if not kind:
            raise ValueError("Snapshot kind missing.")
        golden = self._store.get_golden_snapshot(kind)
        if not golden:
            raise ValueError("No golden baseline for this kind.")
        golden_snapshot = self._store.get_snapshot(golden.get("snapshot_id"))
        if not golden_snapshot:
            raise ValueError("Golden snapshot not found.")
        return {"golden": golden, "diff": diff_snapshots(golden_snapshot, snapshot, store=self._store)}
