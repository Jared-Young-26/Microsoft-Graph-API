from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import json
import sqlite3
import uuid


def _json_dumps(value: Any) -> str:
    """Internal helper for json dumps."""
    return json.dumps(value, default=str)


def _json_loads(value: str | None) -> Any:
    """Internal helper for json loads."""
    if not value:
        return None
    try:
        return json.loads(value)
    except Exception:
        return None


def _coerce_ok(value: Any) -> Optional[bool]:
    """Internal helper for coerce ok."""
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    try:
        return bool(int(value))
    except Exception:
        return None


def _get_diff_key(item: Any) -> Any:
    """Get diff key."""
    if not isinstance(item, dict):
        return None
    return (
        item.get("id")
        or item.get("userPrincipalName")
        or item.get("mail")
        or item.get("name")
        or item.get("displayName")
        or item.get("ipAddress")
        or item.get("IPAddress")
        or item.get("address")
        or item.get("Address")
        or item.get("hostName")
        or item.get("HostName")
        or item.get("deviceId")
        or item.get("deviceName")
    )


def diff_json(a: Any, b: Any, path: str = "", depth: int = 0, max_depth: int = 4) -> Dict[str, List[Dict[str, Any]]]:
    """Diff json."""
    diff = {"added": [], "removed": [], "changed": []}
    if depth > max_depth:
        if json.dumps(a, default=str) != json.dumps(b, default=str):
            diff["changed"].append({"path": path, "before": a, "after": b})
        return diff

    a_is_array = isinstance(a, list)
    b_is_array = isinstance(b, list)
    if a_is_array or b_is_array:
        arr_a = a if isinstance(a, list) else []
        arr_b = b if isinstance(b, list) else []
        map_a: Dict[str, Any] = {}
        map_b: Dict[str, Any] = {}
        has_stable_key = False
        for idx, item in enumerate(arr_a):
            key = _get_diff_key(item)
            if key:
                has_stable_key = True
            map_a[str(key) if key is not None else f"idx-{idx}"] = item
        for idx, item in enumerate(arr_b):
            key = _get_diff_key(item)
            if key:
                has_stable_key = True
            map_b[str(key) if key is not None else f"idx-{idx}"] = item

        for key, value in map_b.items():
            if key not in map_a:
                diff["added"].append({"path": path, "key": key, "value": value})
            else:
                before = map_a.get(key)
                if json.dumps(before, default=str) != json.dumps(value, default=str):
                    diff["changed"].append({"path": path, "key": key, "before": before, "after": value})
        for key, value in map_a.items():
            if key not in map_b:
                diff["removed"].append({"path": path, "key": key, "value": value})
        if not has_stable_key and len(arr_a) != len(arr_b):
            diff["changed"].append({"path": path, "before": len(arr_a), "after": len(arr_b)})
        return diff

    if isinstance(a, dict) and isinstance(b, dict):
        keys = set(a.keys()) | set(b.keys())
        for key in keys:
            next_path = f"{path}.{key}" if path else str(key)
            if key not in a:
                diff["added"].append({"path": next_path, "value": b.get(key)})
            elif key not in b:
                diff["removed"].append({"path": next_path, "value": a.get(key)})
            else:
                a_val = a.get(key)
                b_val = b.get(key)
                if isinstance(a_val, (dict, list)) or isinstance(b_val, (dict, list)):
                    nested = diff_json(a_val, b_val, next_path, depth + 1, max_depth)
                    diff["added"].extend(nested["added"])
                    diff["removed"].extend(nested["removed"])
                    diff["changed"].extend(nested["changed"])
                elif json.dumps(a_val, default=str) != json.dumps(b_val, default=str):
                    diff["changed"].append({"path": next_path, "before": a_val, "after": b_val})
        return diff

    if json.dumps(a, default=str) != json.dumps(b, default=str):
        diff["changed"].append({"path": path, "before": a, "after": b})
    return diff


@dataclass
class SnapshotStore:
    """Snapshot Store."""
    path: Path
    legacy_path: Optional[Path] = None
    _initialized: bool = field(default=False, init=False)

    def _ensure_parent(self) -> None:
        """Ensure parent."""
        if not self.path.parent.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)

    def _connect(self) -> sqlite3.Connection:
        """Internal helper for connect."""
        self._ensure_parent()
        conn = sqlite3.connect(str(self.path))
        conn.row_factory = sqlite3.Row
        self._init_schema(conn)
        self._maybe_migrate(conn)
        return conn

    def _init_schema(self, conn: sqlite3.Connection) -> None:
        """Internal helper for init schema."""
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS action_snapshots (
                id TEXT PRIMARY KEY,
                snapshot_type TEXT,
                target TEXT,
                collected_at TEXT,
                action TEXT,
                service TEXT,
                ok INTEGER,
                inputs_json TEXT,
                payload_json TEXT,
                meta_json TEXT,
                source_json TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_action_snapshots_type ON action_snapshots (snapshot_type);
            CREATE INDEX IF NOT EXISTS idx_action_snapshots_target ON action_snapshots (target);
            CREATE INDEX IF NOT EXISTS idx_action_snapshots_action ON action_snapshots (action);
            CREATE INDEX IF NOT EXISTS idx_action_snapshots_collected ON action_snapshots (collected_at);
            """
        )

    def _maybe_migrate(self, conn: sqlite3.Connection) -> None:
        """Internal helper for maybe migrate."""
        if self._initialized:
            return
        self._initialized = True
        if not self.legacy_path or not self.legacy_path.exists():
            return
        try:
            count = conn.execute("SELECT COUNT(1) FROM action_snapshots").fetchone()[0]
        except Exception:
            count = 0
        if count:
            return
        try:
            with self.legacy_path.open("r", encoding="utf-8") as handle:
                for line in handle:
                    try:
                        record = json.loads(line)
                    except Exception:
                        continue
                    self._insert_record(conn, record)
            conn.commit()
        except Exception:
            return

    def _insert_record(self, conn: sqlite3.Connection, record: Dict[str, Any]) -> None:
        """Internal helper for insert record."""
        snapshot_type = record.get("type")
        target = record.get("target")
        collected_at = record.get("collected_at")
        source = record.get("source") or {}
        meta = record.get("meta") or {}
        payload = record.get("payload")
        action = record.get("action") or meta.get("action") or source.get("action")
        service = record.get("service") or meta.get("service") or source.get("service")
        ok = record.get("ok")
        if ok is None:
            ok = meta.get("ok")
        inputs = record.get("inputs")
        if inputs is None and isinstance(payload, dict) and "request" in payload:
            inputs = payload.get("request")
        conn.execute(
            """
            INSERT OR IGNORE INTO action_snapshots
            (id, snapshot_type, target, collected_at, action, service, ok, inputs_json, payload_json, meta_json, source_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record.get("id") or uuid.uuid4().hex,
                snapshot_type,
                target,
                collected_at,
                action,
                service,
                int(ok) if isinstance(ok, bool) else (int(ok) if ok is not None else None),
                _json_dumps(inputs) if inputs is not None else None,
                _json_dumps(payload) if payload is not None else None,
                _json_dumps(meta) if meta else None,
                _json_dumps(source) if source else None,
            ),
        )

    def put(
        self,
        snapshot_type: str,
        target_id: str,
        payload: Any,
        meta: Optional[Dict[str, Any]] = None,
        source: Optional[Dict[str, Any]] = None,
        inputs: Optional[Dict[str, Any]] = None,
        action: Optional[str] = None,
        ok: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Run put."""
        entry = {
            "id": uuid.uuid4().hex,
            "type": snapshot_type,
            "target": target_id,
            "collected_at": datetime.now(timezone.utc).isoformat(),
            "source": source or {},
            "payload": payload,
            "meta": meta or {},
            "inputs": inputs,
        }
        action_value = action or entry["meta"].get("action") or entry["source"].get("action")
        service_value = entry["meta"].get("service") or entry["source"].get("service")
        ok_value = ok if ok is not None else entry["meta"].get("ok")
        entry["action"] = action_value
        entry["service"] = service_value
        entry["ok"] = ok_value

        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO action_snapshots
                (id, snapshot_type, target, collected_at, action, service, ok, inputs_json, payload_json, meta_json, source_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    entry["id"],
                    snapshot_type,
                    target_id,
                    entry["collected_at"],
                    action_value,
                    service_value,
                    int(ok_value) if isinstance(ok_value, bool) else (int(ok_value) if ok_value is not None else None),
                    _json_dumps(inputs) if inputs is not None else None,
                    _json_dumps(payload) if payload is not None else None,
                    _json_dumps(entry["meta"]) if entry["meta"] else None,
                    _json_dumps(entry["source"]) if entry["source"] else None,
                ),
            )
            conn.commit()
        return entry

    def _row_to_entry(self, row: sqlite3.Row) -> Dict[str, Any]:
        """Internal helper for row to entry."""
        payload = _json_loads(row["payload_json"]) if row["payload_json"] else None
        entry = {
            "id": row["id"],
            "type": row["snapshot_type"],
            "target": row["target"],
            "collected_at": row["collected_at"],
            "action": row["action"],
            "service": row["service"],
            "ok": _coerce_ok(row["ok"]),
            "inputs": _json_loads(row["inputs_json"]) if row["inputs_json"] else None,
            "payload": payload,
            "data": payload,
            "meta": _json_loads(row["meta_json"]) if row["meta_json"] else {},
            "source": _json_loads(row["source_json"]) if row["source_json"] else {},
        }
        return entry

    def list(
        self,
        snapshot_type: Optional[str] = None,
        target: Optional[str] = None,
        limit: int = 50,
        prefix: Optional[str] = None,
        action: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Run list."""
        clauses = []
        params: List[Any] = []
        if snapshot_type:
            clauses.append("snapshot_type = ?")
            params.append(snapshot_type)
        if prefix:
            clauses.append("snapshot_type LIKE ?")
            params.append(f"{prefix}%")
        if target:
            clauses.append("LOWER(target) = ?")
            params.append(str(target).lower())
        if action:
            clauses.append("action = ?")
            params.append(action)

        sql = "SELECT * FROM action_snapshots"
        if clauses:
            sql += " WHERE " + " AND ".join(clauses)
        sql += " ORDER BY collected_at DESC"
        if limit and limit > 0:
            sql += " LIMIT ?"
            params.append(int(limit))

        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [self._row_to_entry(row) for row in rows]

    def get(self, snapshot_id: str) -> Optional[Dict[str, Any]]:
        """Run get."""
        if not snapshot_id:
            return None
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM action_snapshots WHERE id = ?", (snapshot_id,)).fetchone()
        if not row:
            return None
        return self._row_to_entry(row)
