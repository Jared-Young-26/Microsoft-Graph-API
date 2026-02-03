from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional
import json
import sqlite3


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _json_dumps(value: Any) -> str:
    return json.dumps(value, default=str)


@dataclass
class SnapshotSqlStore:
    path: Path
    _initialized: bool = field(default=False, init=False)

    def _connect(self) -> sqlite3.Connection:
        if not self.path.parent.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self.path))
        conn.row_factory = sqlite3.Row
        self._init_schema(conn)
        return conn

    def _init_schema(self, conn: sqlite3.Connection) -> None:
        if self._initialized:
            return
        self._initialized = True
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS entities (
                canonical_id TEXT PRIMARY KEY,
                kind TEXT,
                display_name TEXT,
                created_at TEXT
            );

            CREATE TABLE IF NOT EXISTS entity_aliases (
                canonical_id TEXT,
                alias_type TEXT,
                alias_value TEXT,
                confidence REAL,
                last_seen TEXT
            );

            CREATE TABLE IF NOT EXISTS snapshots (
                snapshot_id TEXT PRIMARY KEY,
                canonical_id TEXT,
                kind TEXT,
                profile TEXT,
                captured_at TEXT,
                snapshot_json TEXT
            );

            CREATE TABLE IF NOT EXISTS events (
                event_id TEXT PRIMARY KEY,
                time TEXT,
                kind TEXT,
                source TEXT,
                service TEXT,
                signal_name TEXT,
                canonical_ids_json TEXT,
                event_json TEXT
            );

            CREATE TABLE IF NOT EXISTS evidence (
                evidence_id TEXT PRIMARY KEY,
                time TEXT,
                kind TEXT,
                subject_ids_json TEXT,
                content_ref TEXT,
                redaction_json TEXT,
                meta_json TEXT
            );

            CREATE TABLE IF NOT EXISTS golden_snapshots (
                kind TEXT PRIMARY KEY,
                snapshot_id TEXT,
                label TEXT,
                created_at TEXT
            );

            CREATE TABLE IF NOT EXISTS incidents (
                incident_id TEXT PRIMARY KEY,
                created_at TEXT,
                symptom_id TEXT,
                status TEXT,
                title TEXT,
                description TEXT,
                time_window_start TEXT,
                time_window_end TEXT
            );

            CREATE TABLE IF NOT EXISTS incident_subjects (
                incident_id TEXT,
                canonical_id TEXT,
                role TEXT,
                kind TEXT
            );

            CREATE TABLE IF NOT EXISTS incident_snapshots (
                incident_id TEXT,
                snapshot_id TEXT
            );

            CREATE TABLE IF NOT EXISTS incident_events (
                incident_id TEXT,
                event_id TEXT
            );

            CREATE TABLE IF NOT EXISTS incident_reports (
                incident_id TEXT PRIMARY KEY,
                created_at TEXT,
                updated_at TEXT,
                report_json TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_snapshots_entity_time ON snapshots (canonical_id, captured_at);
            CREATE INDEX IF NOT EXISTS idx_events_time ON events (time);
            CREATE INDEX IF NOT EXISTS idx_events_signal ON events (signal_name);
            CREATE INDEX IF NOT EXISTS idx_alias_lookup ON entity_aliases (alias_type, alias_value);
            CREATE INDEX IF NOT EXISTS idx_incidents_time ON incidents (created_at);
            CREATE INDEX IF NOT EXISTS idx_incident_subjects ON incident_subjects (incident_id, canonical_id);
            CREATE INDEX IF NOT EXISTS idx_incident_snapshots ON incident_snapshots (incident_id, snapshot_id);
            CREATE INDEX IF NOT EXISTS idx_incident_events ON incident_events (incident_id, event_id);
            CREATE INDEX IF NOT EXISTS idx_incident_reports_time ON incident_reports (updated_at);
            """
        )

    def upsert_entity(self, canonical_id: str, kind: str, display_name: Optional[str] = None, created_at: Optional[str] = None) -> None:
        if not canonical_id:
            return
        created_at = created_at or _now_iso()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO entities (canonical_id, kind, display_name, created_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(canonical_id) DO UPDATE SET
                    kind = excluded.kind,
                    display_name = COALESCE(excluded.display_name, entities.display_name)
                """,
                (canonical_id, kind, display_name, created_at),
            )
            conn.commit()

    def add_alias(
        self,
        canonical_id: str,
        alias_type: str,
        alias_value: str,
        confidence: Optional[float] = None,
        last_seen: Optional[str] = None,
    ) -> None:
        if not canonical_id or not alias_type or not alias_value:
            return
        last_seen = last_seen or _now_iso()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO entity_aliases (canonical_id, alias_type, alias_value, confidence, last_seen)
                VALUES (?, ?, ?, ?, ?)
                """,
                (canonical_id, alias_type, alias_value, confidence, last_seen),
            )
            conn.commit()

    def resolve_alias(self, alias_type: str, alias_value: str) -> Optional[str]:
        if not alias_type or not alias_value:
            return None
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT canonical_id
                FROM entity_aliases
                WHERE alias_type = ? AND alias_value = ?
                ORDER BY confidence DESC, last_seen DESC
                LIMIT 1
                """,
                (alias_type, alias_value),
            ).fetchone()
        if not row:
            return None
        return row["canonical_id"]

    def add_snapshot(
        self,
        snapshot_id: str,
        canonical_id: str,
        kind: str,
        profile: str,
        captured_at: str,
        snapshot: Dict[str, Any],
    ) -> None:
        if not snapshot_id:
            return
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO snapshots (snapshot_id, canonical_id, kind, profile, captured_at, snapshot_json)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    snapshot_id,
                    canonical_id,
                    kind,
                    profile,
                    captured_at,
                    _json_dumps(snapshot),
                ),
            )
            conn.commit()

    def get_latest_snapshot_id(self, canonical_id: str) -> Optional[str]:
        if not canonical_id:
            return None
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT snapshot_id
                FROM snapshots
                WHERE canonical_id = ?
                ORDER BY captured_at DESC
                LIMIT 1
                """,
                (canonical_id,),
            ).fetchone()
        if not row:
            return None
        return row["snapshot_id"]

    def list_snapshots(self, canonical_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        params: List[Any] = []
        clause = ""
        if canonical_id:
            clause = "WHERE canonical_id = ?"
            params.append(canonical_id)
        sql = f"SELECT snapshot_json FROM snapshots {clause} ORDER BY captured_at DESC"
        if limit and limit > 0:
            sql += " LIMIT ?"
            params.append(int(limit))
        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        snapshots = []
        for row in rows:
            try:
                snapshots.append(json.loads(row["snapshot_json"]))
            except Exception:
                continue
        return snapshots

    def get_snapshot(self, snapshot_id: str) -> Optional[Dict[str, Any]]:
        if not snapshot_id:
            return None
        with self._connect() as conn:
            row = conn.execute(
                "SELECT snapshot_json FROM snapshots WHERE snapshot_id = ?",
                (snapshot_id,),
            ).fetchone()
        if not row:
            return None
        try:
            return json.loads(row["snapshot_json"])
        except Exception:
            return None

    def list_entities(self, limit: int = 200) -> List[Dict[str, Any]]:
        params: List[Any] = []
        sql = "SELECT canonical_id, kind, display_name, created_at FROM entities ORDER BY created_at DESC"
        if limit and limit > 0:
            sql += " LIMIT ?"
            params.append(int(limit))
        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        results = []
        for row in rows:
            results.append(
                {
                    "canonical_id": row["canonical_id"],
                    "kind": row["kind"],
                    "display_name": row["display_name"],
                    "created_at": row["created_at"],
                }
            )
        return results

    def get_entity(self, canonical_id: str) -> Optional[Dict[str, Any]]:
        if not canonical_id:
            return None
        with self._connect() as conn:
            row = conn.execute(
                "SELECT canonical_id, kind, display_name, created_at FROM entities WHERE canonical_id = ?",
                (canonical_id,),
            ).fetchone()
        if not row:
            return None
        return {
            "canonical_id": row["canonical_id"],
            "kind": row["kind"],
            "display_name": row["display_name"],
            "created_at": row["created_at"],
        }

    def list_events(self, canonical_ids: Optional[List[str]] = None, limit: int = 50) -> List[Dict[str, Any]]:
        params: List[Any] = []
        sql = "SELECT event_json FROM events"
        if canonical_ids:
            clauses = []
            for cid in canonical_ids:
                clauses.append("canonical_ids_json LIKE ?")
                params.append(f"%{cid}%")
            sql += " WHERE " + " OR ".join(clauses)
        sql += " ORDER BY time DESC"
        if limit and limit > 0:
            sql += " LIMIT ?"
            params.append(int(limit))
        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        events = []
        for row in rows:
            try:
                events.append(json.loads(row["event_json"]))
            except Exception:
                continue
        return events

    def add_event(
        self,
        event_id: str,
        time: str,
        kind: str,
        source: Optional[str],
        service: Optional[str],
        signal_name: Optional[str],
        canonical_ids: Iterable[str],
        event: Dict[str, Any],
    ) -> None:
        if not event_id:
            return
        canonical_ids_json = _json_dumps(list(canonical_ids or []))
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO events (event_id, time, kind, source, service, signal_name, canonical_ids_json, event_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event_id,
                    time,
                    kind,
                    source,
                    service,
                    signal_name,
                    canonical_ids_json,
                    _json_dumps(event),
                ),
            )
            conn.commit()

    def get_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        if not event_id:
            return None
        with self._connect() as conn:
            row = conn.execute(
                "SELECT event_json FROM events WHERE event_id = ?",
                (event_id,),
            ).fetchone()
        if not row:
            return None
        try:
            return json.loads(row["event_json"])
        except Exception:
            return None

    def add_evidence(
        self,
        evidence_id: str,
        time: str,
        kind: str,
        subject_ids: Iterable[str],
        content_ref: Optional[str],
        redaction: Optional[Dict[str, Any]],
        meta: Optional[Dict[str, Any]],
    ) -> None:
        if not evidence_id:
            return
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO evidence (evidence_id, time, kind, subject_ids_json, content_ref, redaction_json, meta_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    evidence_id,
                    time,
                    kind,
                    _json_dumps(list(subject_ids or [])),
                    content_ref,
                    _json_dumps(redaction or {}),
                    _json_dumps(meta or {}),
                ),
            )
            conn.commit()

    def set_golden_snapshot(self, kind: str, snapshot_id: str, label: Optional[str] = None) -> None:
        if not kind or not snapshot_id:
            return
        created_at = _now_iso()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO golden_snapshots (kind, snapshot_id, label, created_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(kind) DO UPDATE SET
                    snapshot_id = excluded.snapshot_id,
                    label = COALESCE(excluded.label, golden_snapshots.label),
                    created_at = excluded.created_at
                """,
                (kind, snapshot_id, label, created_at),
            )
            conn.commit()

    def get_golden_snapshot(self, kind: str) -> Optional[Dict[str, Any]]:
        if not kind:
            return None
        with self._connect() as conn:
            row = conn.execute(
                "SELECT kind, snapshot_id, label, created_at FROM golden_snapshots WHERE kind = ?",
                (kind,),
            ).fetchone()
        if not row:
            return None
        return {
            "kind": row["kind"],
            "snapshot_id": row["snapshot_id"],
            "label": row["label"],
            "created_at": row["created_at"],
        }

    def list_golden_snapshots(self, limit: int = 200) -> List[Dict[str, Any]]:
        params: List[Any] = []
        sql = "SELECT kind, snapshot_id, label, created_at FROM golden_snapshots ORDER BY created_at DESC"
        if limit and limit > 0:
            sql += " LIMIT ?"
            params.append(int(limit))
        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        results = []
        for row in rows:
            results.append(
                {
                    "kind": row["kind"],
                    "snapshot_id": row["snapshot_id"],
                    "label": row["label"],
                    "created_at": row["created_at"],
                }
            )
        return results

    def clear_golden_snapshot(self, kind: str) -> None:
        if not kind:
            return
        with self._connect() as conn:
            conn.execute("DELETE FROM golden_snapshots WHERE kind = ?", (kind,))
            conn.commit()

    def create_incident(
        self,
        incident_id: str,
        created_at: str,
        symptom_id: Optional[str] = None,
        status: str = "open",
        title: Optional[str] = None,
        description: Optional[str] = None,
        time_window_start: Optional[str] = None,
        time_window_end: Optional[str] = None,
    ) -> None:
        if not incident_id:
            return
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO incidents (
                    incident_id,
                    created_at,
                    symptom_id,
                    status,
                    title,
                    description,
                    time_window_start,
                    time_window_end
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    incident_id,
                    created_at,
                    symptom_id,
                    status,
                    title,
                    description,
                    time_window_start,
                    time_window_end,
                ),
            )
            conn.commit()

    def update_incident(self, incident_id: str, updates: Dict[str, Any]) -> None:
        if not incident_id or not updates:
            return
        fields = []
        params: List[Any] = []
        for key in (
            "status",
            "title",
            "description",
            "time_window_start",
            "time_window_end",
            "symptom_id",
        ):
            if key in updates:
                fields.append(f"{key} = ?")
                params.append(updates.get(key))
        if not fields:
            return
        params.append(incident_id)
        with self._connect() as conn:
            conn.execute(
                f"UPDATE incidents SET {', '.join(fields)} WHERE incident_id = ?",
                params,
            )
            conn.commit()

    def get_incident_report(self, incident_id: str) -> Optional[Dict[str, Any]]:
        if not incident_id:
            return None
        with self._connect() as conn:
            row = conn.execute(
                "SELECT report_json FROM incident_reports WHERE incident_id = ?",
                (incident_id,),
            ).fetchone()
        if not row or not row["report_json"]:
            return None
        try:
            return json.loads(row["report_json"])
        except Exception:
            return None

    def upsert_incident_report(self, incident_id: str, report: Dict[str, Any]) -> None:
        if not incident_id:
            return
        now = _now_iso()
        payload = _json_dumps(report or {})
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO incident_reports (incident_id, created_at, updated_at, report_json)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(incident_id) DO UPDATE SET
                    updated_at = excluded.updated_at,
                    report_json = excluded.report_json
                """,
                (incident_id, now, now, payload),
            )
            conn.commit()

    def get_incident(self, incident_id: str) -> Optional[Dict[str, Any]]:
        if not incident_id:
            return None
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM incidents WHERE incident_id = ?",
                (incident_id,),
            ).fetchone()
        if not row:
            return None
        return dict(row)

    def list_incidents(self, limit: int = 50) -> List[Dict[str, Any]]:
        params: List[Any] = []
        sql = "SELECT * FROM incidents ORDER BY created_at DESC"
        if limit and limit > 0:
            sql += " LIMIT ?"
            params.append(int(limit))
        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [dict(row) for row in rows]

    def add_incident_subject(self, incident_id: str, canonical_id: str, role: str, kind: str) -> None:
        if not incident_id or not canonical_id:
            return
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO incident_subjects (incident_id, canonical_id, role, kind)
                VALUES (?, ?, ?, ?)
                """,
                (incident_id, canonical_id, role, kind),
            )
            conn.commit()

    def list_incident_subjects(self, incident_id: str) -> List[Dict[str, Any]]:
        if not incident_id:
            return []
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT canonical_id, role, kind FROM incident_subjects WHERE incident_id = ?",
                (incident_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def link_incident_snapshot(self, incident_id: str, snapshot_id: str) -> None:
        if not incident_id or not snapshot_id:
            return
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO incident_snapshots (incident_id, snapshot_id)
                VALUES (?, ?)
                """,
                (incident_id, snapshot_id),
            )
            conn.commit()

    def list_incident_snapshots(self, incident_id: str) -> List[str]:
        if not incident_id:
            return []
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT snapshot_id FROM incident_snapshots WHERE incident_id = ?",
                (incident_id,),
            ).fetchall()
        return [row["snapshot_id"] for row in rows]

    def link_incident_event(self, incident_id: str, event_id: str) -> None:
        if not incident_id or not event_id:
            return
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO incident_events (incident_id, event_id)
                VALUES (?, ?)
                """,
                (incident_id, event_id),
            )
            conn.commit()

    def list_incident_events(self, incident_id: str) -> List[str]:
        if not incident_id:
            return []
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT event_id FROM incident_events WHERE incident_id = ?",
                (incident_id,),
            ).fetchall()
        return [row["event_id"] for row in rows]
