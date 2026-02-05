from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional
import hashlib
import json
import sqlite3


def _now_iso() -> str:
    """Internal helper for now iso."""
    return datetime.now(timezone.utc).isoformat()


def _json_dumps(value: Any) -> str:
    """Internal helper for json dumps."""
    return json.dumps(value, default=str)


def _stable_jitter_seconds(key: str, *, max_jitter_s: int = 15) -> int:
    """Deterministic jitter for scheduling to reduce thundering-herd retries (no RNG)."""

    if not key:
        return 0
    try:
        digest = hashlib.sha256(key.encode("utf-8")).digest()
        return int(digest[0]) % (max(0, int(max_jitter_s)) + 1)
    except Exception:
        return 0


@dataclass
class SnapshotSqlStore:
    """Snapshot Sql Store."""
    path: Path
    _initialized: bool = field(default=False, init=False)

    def _connect(self) -> sqlite3.Connection:
        """Internal helper for connect."""
        if not self.path.parent.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self.path))
        conn.row_factory = sqlite3.Row
        self._init_schema(conn)
        return conn

    def _init_schema(self, conn: sqlite3.Connection) -> None:
        """Internal helper for init schema."""
        if self._initialized:
            return
        try:
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

            CREATE TABLE IF NOT EXISTS snapshot_signals (
                signal_name TEXT,
                provider_version TEXT,
                event_id TEXT,
                snapshot_id TEXT,
                endpoint_id TEXT,
                session_id TEXT,
                episode_id TEXT,
                timestamp_utc TEXT,
                monotonic_timestamp INTEGER,
                payload_json TEXT,
                PRIMARY KEY (signal_name, event_id)
            );

            CREATE INDEX IF NOT EXISTS idx_snapshot_signals_lookup
            ON snapshot_signals (signal_name, endpoint_id, episode_id, timestamp_utc);

            CREATE TABLE IF NOT EXISTS onedrive_drive_cache (
                tenant_id TEXT NOT NULL,
                user_upn TEXT NOT NULL,
                user_object_id TEXT,
                drive_id TEXT NOT NULL,
                web_url TEXT,
                drive_type TEXT,
                last_verified_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                source TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS onedrive_drive_pending (
                tenant_id TEXT NOT NULL,
                user_upn TEXT NOT NULL,
                attempts INTEGER NOT NULL DEFAULT 0,
                paused INTEGER NOT NULL DEFAULT 0,
                next_run_at TEXT,
                last_error TEXT,
                last_error_class TEXT,
                last_error_at TEXT,
                PRIMARY KEY (tenant_id, user_upn)
            );

            CREATE TABLE IF NOT EXISTS sharepoint_sites_cache (
                tenant_id TEXT,
                search_term TEXT,
                sites_json TEXT,
                last_verified_at TEXT,
                expires_at TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_sharepoint_sites_cache_lookup
            ON sharepoint_sites_cache (tenant_id, search_term);

            CREATE INDEX IF NOT EXISTS idx_sharepoint_sites_cache_expires_at
            ON sharepoint_sites_cache (expires_at);

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
            self._migrate_schema(conn)
            self._initialized = True
        except Exception:
            # If initialization fails (e.g., older DB missing columns referenced by indexes),
            # do not mark the store as initialized so a future call can retry after fixes.
            self._initialized = False
            raise

    def _table_columns(self, conn: sqlite3.Connection, table_name: str) -> set[str]:
        """Internal helper for table columns."""
        try:
            rows = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
        except Exception:
            return set()
        cols = set()
        for row in rows:
            try:
                cols.add(str(row["name"]))
            except Exception:
                continue
        return cols

    def _dedupe_onedrive_drive_cache(self, conn: sqlite3.Connection) -> None:
        """Best-effort de-dupe so UNIQUE indexes can be created on legacy databases."""

        cols = self._table_columns(conn, "onedrive_drive_cache")
        if not cols:
            return

        now_iso = _now_iso()

        def _parse_iso(value: Any) -> str:
            """Parse iso."""
            text = str(value or "").strip()
            # Keep as ISO-ish string; lexical sort works for UTC ISO formats.
            return text or now_iso

        def _dedupe(keys: list[str]) -> None:
            """Internal helper for dedupe."""
            order_cols = []
            if "last_verified_at" in cols:
                order_cols.append("last_verified_at DESC")
            order_cols.append("rowid DESC")
            order_by = ", ".join(keys + order_cols)
            where_parts = []
            for key in keys:
                where_parts.append(f"{key} IS NOT NULL AND {key} <> ''")
            where = " AND ".join(where_parts)
            rows = conn.execute(
                f"""
                SELECT rowid, {", ".join(keys)}, last_verified_at
                FROM onedrive_drive_cache
                WHERE {where}
                ORDER BY {order_by}
                """
            ).fetchall()
            seen = set()
            to_delete: list[int] = []
            for row in rows:
                key = tuple(str(row[k]) for k in keys)
                if key in seen:
                    try:
                        to_delete.append(int(row["rowid"]))
                    except Exception:
                        continue
                else:
                    seen.add(key)
            if not to_delete:
                return
            conn.executemany("DELETE FROM onedrive_drive_cache WHERE rowid = ?", [(rid,) for rid in to_delete])

        if "tenant_id" in cols and "user_upn" in cols:
            _dedupe(["tenant_id", "user_upn"])
        if "tenant_id" in cols and "user_object_id" in cols:
            _dedupe(["tenant_id", "user_object_id"])

    def _migrate_schema(self, conn: sqlite3.Connection) -> None:
        """Idempotent migrations for older snapshot DBs."""

        cols = self._table_columns(conn, "onedrive_drive_cache")
        if not cols:
            # Older DBs may not have the cache table yet.
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS onedrive_drive_cache (
                    tenant_id TEXT NOT NULL,
                    user_upn TEXT NOT NULL,
                    user_object_id TEXT,
                    drive_id TEXT NOT NULL,
                    web_url TEXT,
                    drive_type TEXT,
                    last_verified_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    source TEXT NOT NULL
                )
                """
            )
            cols = self._table_columns(conn, "onedrive_drive_cache")

        # Column migrations (idempotent).
        if "user_object_id" not in cols:
            try:
                conn.execute("ALTER TABLE onedrive_drive_cache ADD COLUMN user_object_id TEXT")
            except Exception:
                pass
            cols = self._table_columns(conn, "onedrive_drive_cache")
        if "drive_type" not in cols:
            try:
                conn.execute("ALTER TABLE onedrive_drive_cache ADD COLUMN drive_type TEXT")
            except Exception:
                pass
            cols = self._table_columns(conn, "onedrive_drive_cache")
        if "source" not in cols:
            # Make legacy rows safe by providing a default.
            try:
                conn.execute(
                    "ALTER TABLE onedrive_drive_cache ADD COLUMN source TEXT NOT NULL DEFAULT 'primary'"
                )
            except Exception:
                # Fall back to nullable column if SQLite rejects the constraint on some legacy DBs.
                try:
                    conn.execute("ALTER TABLE onedrive_drive_cache ADD COLUMN source TEXT")
                except Exception:
                    pass
            cols = self._table_columns(conn, "onedrive_drive_cache")

        # Backfill user_object_id from legacy user_id when present.
        if "user_id" in cols and "user_object_id" in cols:
            try:
                conn.execute(
                    """
                    UPDATE onedrive_drive_cache
                    SET user_object_id = COALESCE(NULLIF(user_object_id, ''), NULLIF(user_id, ''))
                    """
                )
            except Exception:
                pass

        # Ensure source is populated for legacy rows.
        if "source" in cols:
            try:
                conn.execute(
                    """
                    UPDATE onedrive_drive_cache
                    SET source = COALESCE(NULLIF(source, ''), 'primary')
                    """
                )
            except Exception:
                pass

        # Indexes (best effort, idempotent). Avoid crashing on duplicates; cache should still work.
        try:
            conn.execute(
                """
                CREATE UNIQUE INDEX IF NOT EXISTS idx_onedrive_drive_cache_upn_unique
                ON onedrive_drive_cache (tenant_id, user_upn)
                WHERE user_upn IS NOT NULL AND user_upn <> ''
                """
            )
        except Exception:
            # Fall back to non-unique index to avoid blocking runtime on legacy duplicate rows.
            try:
                conn.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_onedrive_drive_cache_upn
                    ON onedrive_drive_cache (tenant_id, user_upn)
                    WHERE user_upn IS NOT NULL AND user_upn <> ''
                    """
                )
            except Exception:
                pass
        try:
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_onedrive_drive_cache_object
                ON onedrive_drive_cache (tenant_id, user_object_id)
                WHERE user_object_id IS NOT NULL AND user_object_id <> ''
                """
            )
        except Exception:
            pass
        try:
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_onedrive_drive_cache_expires_at
                ON onedrive_drive_cache (expires_at)
                """
            )
        except Exception:
            pass

        # Pending queue migrations + indexes.
        pending_cols = self._table_columns(conn, "onedrive_drive_pending")
        if not pending_cols:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS onedrive_drive_pending (
                    tenant_id TEXT NOT NULL,
                    user_upn TEXT NOT NULL,
                    attempts INTEGER NOT NULL DEFAULT 0,
                    paused INTEGER NOT NULL DEFAULT 0,
                    next_run_at TEXT,
                    last_error TEXT,
                    last_error_class TEXT,
                    last_error_at TEXT,
                    PRIMARY KEY (tenant_id, user_upn)
                )
                """
            )
            pending_cols = self._table_columns(conn, "onedrive_drive_pending")
        if "attempts" not in pending_cols:
            try:
                conn.execute("ALTER TABLE onedrive_drive_pending ADD COLUMN attempts INTEGER NOT NULL DEFAULT 0")
            except Exception:
                try:
                    conn.execute("ALTER TABLE onedrive_drive_pending ADD COLUMN attempts INTEGER")
                except Exception:
                    pass
            pending_cols = self._table_columns(conn, "onedrive_drive_pending")
        if "next_run_at" not in pending_cols:
            try:
                conn.execute("ALTER TABLE onedrive_drive_pending ADD COLUMN next_run_at TEXT")
            except Exception:
                pass
            pending_cols = self._table_columns(conn, "onedrive_drive_pending")
        if "last_error" not in pending_cols:
            try:
                conn.execute("ALTER TABLE onedrive_drive_pending ADD COLUMN last_error TEXT")
            except Exception:
                pass
            pending_cols = self._table_columns(conn, "onedrive_drive_pending")
        if "paused" not in pending_cols:
            try:
                conn.execute(
                    "ALTER TABLE onedrive_drive_pending ADD COLUMN paused INTEGER NOT NULL DEFAULT 0"
                )
            except Exception:
                try:
                    conn.execute("ALTER TABLE onedrive_drive_pending ADD COLUMN paused INTEGER")
                except Exception:
                    pass
            pending_cols = self._table_columns(conn, "onedrive_drive_pending")
        if "last_error_class" not in pending_cols:
            try:
                conn.execute(
                    "ALTER TABLE onedrive_drive_pending ADD COLUMN last_error_class TEXT"
                )
            except Exception:
                pass
            pending_cols = self._table_columns(conn, "onedrive_drive_pending")
        if "last_error_at" not in pending_cols:
            try:
                conn.execute(
                    "ALTER TABLE onedrive_drive_pending ADD COLUMN last_error_at TEXT"
                )
            except Exception:
                pass
            pending_cols = self._table_columns(conn, "onedrive_drive_pending")

        # Backfill "stopped" legacy rows (next_run_at NULL/empty) so the scheduler can heal.
        # If attempts are already at/over the cap, treat as paused and retry slowly (6h).
        try:
            now = datetime.now(timezone.utc)
            now_iso = now.isoformat()
            pause_at = (now + timedelta(hours=6)).isoformat()
            soon_at = (now + timedelta(seconds=120)).isoformat()
            conn.execute(
                """
                UPDATE onedrive_drive_pending
                SET paused = CASE WHEN COALESCE(attempts, 0) >= 10 THEN 1 ELSE COALESCE(paused, 0) END,
                    next_run_at = CASE
                        WHEN COALESCE(attempts, 0) >= 10 THEN ?
                        ELSE ?
                    END,
                    last_error_at = COALESCE(NULLIF(last_error_at, ''), ?)
                WHERE next_run_at IS NULL OR next_run_at = ''
                """,
                (pause_at, soon_at, now_iso),
            )
        except Exception:
            pass
        try:
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_onedrive_drive_pending_due
                ON onedrive_drive_pending (tenant_id, next_run_at)
                """
            )
        except Exception:
            pass

        conn.commit()

    def upsert_entity(self, canonical_id: str, kind: str, display_name: Optional[str] = None, created_at: Optional[str] = None) -> None:
        """Run upsert entity."""
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
        """Add alias."""
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
        """Resolve alias."""
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
        """Add snapshot."""
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

    def get_sharepoint_sites_cache(
        self,
        *,
        tenant_id: str,
        search_term: str | None,
        allow_expired: bool = False,
        now_iso: str | None = None,
    ) -> Optional[Dict[str, Any]]:
        """Get sharepoint sites cache."""
        tenant_id = str(tenant_id or "").strip()
        term = str(search_term or "").strip()
        if not tenant_id or not term:
            return None
        now_iso = now_iso or _now_iso()
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT tenant_id, search_term, sites_json, last_verified_at, expires_at
                FROM sharepoint_sites_cache
                WHERE tenant_id = ? AND search_term = ?
                ORDER BY last_verified_at DESC
                LIMIT 1
                """,
                (tenant_id, term),
            ).fetchall()
        if not rows:
            return None
        row = rows[0]
        expires_at = row["expires_at"]
        if not allow_expired and expires_at and expires_at < now_iso:
            return None
        try:
            sites = json.loads(row["sites_json"]) if row["sites_json"] else []
        except Exception:
            sites = []
        if not isinstance(sites, list):
            sites = [sites]
        return {
            "tenant_id": row["tenant_id"],
            "search_term": row["search_term"],
            "sites": sites,
            "last_verified_at": row["last_verified_at"],
            "expires_at": expires_at,
        }

    def upsert_sharepoint_sites_cache(
        self,
        *,
        tenant_id: str,
        search_term: str,
        sites: list,
        last_verified_at: str,
        expires_at: str,
    ) -> None:
        """Run upsert sharepoint sites cache."""
        tenant_id = str(tenant_id or "").strip()
        term = str(search_term or "").strip()
        if not tenant_id or not term:
            return
        payload = _json_dumps(sites or [])
        with self._connect() as conn:
            cur = conn.execute(
                """
                UPDATE sharepoint_sites_cache
                SET sites_json = ?,
                    last_verified_at = ?,
                    expires_at = ?
                WHERE tenant_id = ? AND search_term = ?
                """,
                (payload, last_verified_at, expires_at, tenant_id, term),
            )
            rowcount = int(cur.rowcount or 0)
            if rowcount == 0:
                conn.execute(
                    """
                    INSERT INTO sharepoint_sites_cache (tenant_id, search_term, sites_json, last_verified_at, expires_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (tenant_id, term, payload, last_verified_at, expires_at),
                )
            conn.commit()

    def get_latest_snapshot_id(self, canonical_id: str) -> Optional[str]:
        """Get latest snapshot id."""
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
        """List snapshots."""
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
        """Get snapshot."""
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
        """List entities."""
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
        """Get entity."""
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
        """List events."""
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

    def list_events_by_signal(
        self,
        signal_name: str,
        canonical_id: Optional[str] = None,
        since: Optional[str] = None,
        until: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """List events by signal."""
        if not signal_name:
            return []
        params: List[Any] = [signal_name]
        sql = "SELECT event_json FROM events WHERE signal_name = ?"
        if canonical_id:
            sql += " AND canonical_ids_json LIKE ?"
            params.append(f"%{canonical_id}%")
        if since:
            sql += " AND time >= ?"
            params.append(since)
        if until:
            sql += " AND time <= ?"
            params.append(until)
        sql += " ORDER BY time DESC"
        if limit and limit > 0:
            sql += " LIMIT ?"
            params.append(int(limit))
        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        results = []
        for row in rows:
            try:
                results.append(json.loads(row["event_json"]))
            except Exception:
                continue
        return results

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
        """Add event."""
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

    def add_event_ignore(
        self,
        event_id: str,
        time: str,
        kind: str,
        source: Optional[str],
        service: Optional[str],
        signal_name: Optional[str],
        canonical_ids: Iterable[str],
        event: Dict[str, Any],
    ) -> bool:
        """Insert an event if it does not already exist (by event_id)."""
        if not event_id:
            return False
        canonical_ids_json = _json_dumps(list(canonical_ids or []))
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT OR IGNORE INTO events (event_id, time, kind, source, service, signal_name, canonical_ids_json, event_json)
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
            return cur.rowcount > 0

    def get_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Get event."""
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
        """Add evidence."""
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
        """Set golden snapshot."""
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
        """Get golden snapshot."""
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
        """List golden snapshots."""
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
        """Run clear golden snapshot."""
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
        """Create incident."""
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
        """Update incident."""
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
        """Get incident report."""
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
        """Run upsert incident report."""
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
        """Get incident."""
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
        """List incidents."""
        params: List[Any] = []
        sql = "SELECT * FROM incidents ORDER BY created_at DESC"
        if limit and limit > 0:
            sql += " LIMIT ?"
            params.append(int(limit))
        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [dict(row) for row in rows]

    def add_incident_subject(self, incident_id: str, canonical_id: str, role: str, kind: str) -> None:
        """Add incident subject."""
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
        """List incident subjects."""
        if not incident_id:
            return []
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT canonical_id, role, kind FROM incident_subjects WHERE incident_id = ?",
                (incident_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def link_incident_snapshot(self, incident_id: str, snapshot_id: str) -> None:
        """Run link incident snapshot."""
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
        """List incident snapshots."""
        if not incident_id:
            return []
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT snapshot_id FROM incident_snapshots WHERE incident_id = ?",
                (incident_id,),
            ).fetchall()
        return [row["snapshot_id"] for row in rows]

    def link_incident_event(self, incident_id: str, event_id: str) -> None:
        """Run link incident event."""
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
        """List incident events."""
        if not incident_id:
            return []
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT event_id FROM incident_events WHERE incident_id = ?",
                (incident_id,),
            ).fetchall()
        return [row["event_id"] for row in rows]


    def upsert_snapshot_signal(
        self,
        *,
        snapshot_id: str,
        signal_name: str,
        provider_version: str,
        payload: Dict[str, Any],
    ) -> None:
        """Run upsert snapshot signal."""
        if not snapshot_id or not signal_name or not isinstance(payload, dict):
            return
        event_id = payload.get("event_id")
        if not event_id:
            return
        endpoint_id = payload.get("endpoint_id")
        session_id = payload.get("session_id")
        episode_id = payload.get("episode_id")
        timestamp_utc = payload.get("timestamp_utc")
        monotonic_timestamp = payload.get("monotonic_timestamp")

        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO snapshot_signals
                (signal_name, provider_version, event_id, snapshot_id, endpoint_id, session_id, episode_id, timestamp_utc, monotonic_timestamp, payload_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(signal_name, event_id) DO UPDATE SET
                    provider_version = excluded.provider_version,
                    snapshot_id = excluded.snapshot_id,
                    endpoint_id = excluded.endpoint_id,
                    session_id = excluded.session_id,
                    episode_id = excluded.episode_id,
                    timestamp_utc = excluded.timestamp_utc,
                    monotonic_timestamp = excluded.monotonic_timestamp,
                    payload_json = excluded.payload_json
                """,
                (
                    signal_name,
                    provider_version,
                    event_id,
                    snapshot_id,
                    endpoint_id,
                    session_id,
                    episode_id,
                    timestamp_utc,
                    monotonic_timestamp,
                    _json_dumps(payload),
                ),
            )
            conn.commit()

    def list_signal_timeline(
        self,
        *,
        signal_name: str,
        endpoint_id: str,
        episode_id: str,
        limit: int = 200,
    ) -> List[Dict[str, Any]]:
        """List signal timeline."""
        if not signal_name or not endpoint_id or not episode_id:
            return []
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT payload_json
                FROM snapshot_signals
                WHERE signal_name = ? AND endpoint_id = ? AND episode_id = ?
                ORDER BY monotonic_timestamp ASC, timestamp_utc ASC
                LIMIT ?
                """,
                (signal_name, endpoint_id, episode_id, int(limit)),
            ).fetchall()

        out: List[Dict[str, Any]] = []
        for row in rows:
            try:
                out.append(json.loads(row["payload_json"]))
            except Exception:
                continue
        return out

    def get_onedrive_drive_cache(
        self,
        *,
        tenant_id: str,
        user_upn: Optional[str] = None,
        user_object_id: Optional[str] = None,
        allow_expired: bool = False,
        stale_window_days: int = 30,
    ) -> Optional[Dict[str, Any]]:
        """Return a cached OneDrive driveId entry when present and not expired (unless allow_expired)."""

        if not tenant_id or not (user_upn or user_object_id):
            return None

        def _parse_iso(value: Any) -> Optional[datetime]:
            """Parse iso."""
            if not value:
                return None
            try:
                parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
                if parsed.tzinfo is None:
                    parsed = parsed.replace(tzinfo=timezone.utc)
                return parsed
            except Exception:
                return None

        with self._connect() as conn:
            if user_upn:
                row = conn.execute(
                    """
                    SELECT tenant_id, user_upn, user_object_id, drive_id, web_url, drive_type, last_verified_at, expires_at, source
                    FROM onedrive_drive_cache
                    WHERE tenant_id = ? AND user_upn = ?
                    ORDER BY last_verified_at DESC
                    LIMIT 1
                    """,
                    (tenant_id, user_upn),
                ).fetchone()
            else:
                row = conn.execute(
                    """
                    SELECT tenant_id, user_upn, user_object_id, drive_id, web_url, drive_type, last_verified_at, expires_at, source
                    FROM onedrive_drive_cache
                    WHERE tenant_id = ? AND user_object_id = ?
                    ORDER BY last_verified_at DESC
                    LIMIT 1
                    """,
                    (tenant_id, user_object_id),
                ).fetchone()
        if not row:
            return None

        expires_at = row["expires_at"]
        expires_dt = _parse_iso(expires_at)
        now = datetime.now(timezone.utc)
        expired = bool(expires_dt and expires_dt <= now)
        if expired and not allow_expired:
            return None
        if expired and allow_expired:
            try:
                window_days = max(0, int(stale_window_days or 0))
            except Exception:
                window_days = 0
            if window_days > 0 and expires_dt is not None:
                too_old = now > (expires_dt + timedelta(days=window_days))
                if too_old:
                    return None

        return {
            "tenant_id": row["tenant_id"],
            "user_upn": row["user_upn"],
            "user_object_id": row["user_object_id"],
            "drive_id": row["drive_id"],
            "web_url": row["web_url"],
            "drive_type": row["drive_type"] if "drive_type" in row.keys() else None,
            "last_verified_at": row["last_verified_at"],
            "expires_at": row["expires_at"],
            "source": row["source"] if "source" in row.keys() else None,
            "expired": expired,
        }

    def upsert_onedrive_drive_cache(
        self,
        *,
        tenant_id: str,
        drive_id: str,
        user_upn: Optional[str] = None,
        user_object_id: Optional[str] = None,
        web_url: Optional[str] = None,
        drive_type: Optional[str] = None,
        last_verified_at: Optional[str] = None,
        expires_at: Optional[str] = None,
        source: str = "primary",
    ) -> None:
        """Run upsert onedrive drive cache."""
        if not tenant_id or not drive_id:
            return
        last_verified_at = last_verified_at or _now_iso()
        if not source:
            source = "primary"
        with self._connect() as conn:
            rowcount = 0
            if user_upn:
                cur = conn.execute(
                    """
                    UPDATE onedrive_drive_cache
                    SET user_object_id = COALESCE(?, user_object_id),
                        drive_id = ?,
                        web_url = COALESCE(?, web_url),
                        drive_type = COALESCE(?, drive_type),
                        last_verified_at = ?,
                        expires_at = COALESCE(?, expires_at),
                        source = COALESCE(?, source)
                    WHERE tenant_id = ? AND user_upn = ?
                    """,
                    (
                        user_object_id,
                        drive_id,
                        web_url,
                        drive_type,
                        last_verified_at,
                        expires_at,
                        source,
                        tenant_id,
                        user_upn,
                    ),
                )
                rowcount = int(cur.rowcount or 0)
            if rowcount == 0 and user_object_id:
                cur = conn.execute(
                    """
                    UPDATE onedrive_drive_cache
                    SET user_upn = COALESCE(?, user_upn),
                        drive_id = ?,
                        web_url = COALESCE(?, web_url),
                        drive_type = COALESCE(?, drive_type),
                        last_verified_at = ?,
                        expires_at = COALESCE(?, expires_at),
                        source = COALESCE(?, source)
                    WHERE tenant_id = ? AND user_object_id = ?
                    """,
                    (
                        user_upn,
                        drive_id,
                        web_url,
                        drive_type,
                        last_verified_at,
                        expires_at,
                        source,
                        tenant_id,
                        user_object_id,
                    ),
                )
                rowcount = int(cur.rowcount or 0)
            if rowcount == 0:
                # New rows require a UPN key for reliable lookup/export. If we only have an object id and
                # no existing row matched, skip inserting (the resolver can optionally fetch the UPN).
                if not user_upn:
                    conn.commit()
                    return
                try:
                    conn.execute(
                        """
                        INSERT INTO onedrive_drive_cache
                        (tenant_id, user_upn, user_object_id, drive_id, web_url, drive_type, last_verified_at, expires_at, source)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            tenant_id,
                            user_upn,
                            user_object_id,
                            drive_id,
                            web_url,
                            drive_type,
                            last_verified_at,
                            expires_at,
                            source,
                        ),
                    )
                except sqlite3.IntegrityError:
                    # If a legacy DB has unique indexes but the UPDATE didn't match (e.g., nulls),
                    # fall back to an upsert by UPN.
                    if user_upn:
                        conn.execute(
                            """
                            UPDATE onedrive_drive_cache
                            SET user_object_id = COALESCE(?, user_object_id),
                                drive_id = ?,
                                web_url = COALESCE(?, web_url),
                                drive_type = COALESCE(?, drive_type),
                                last_verified_at = ?,
                                expires_at = COALESCE(?, expires_at),
                                source = COALESCE(?, source)
                            WHERE tenant_id = ? AND user_upn = ?
                            """,
                            (
                                user_object_id,
                                drive_id,
                                web_url,
                                drive_type,
                                last_verified_at,
                                expires_at,
                                source,
                                tenant_id,
                                user_upn,
                            ),
                        )
            conn.commit()

    def get_onedrive_drive_cache_stats(
        self,
        *,
        tenant_id: str,
        stale_window_days: int = 30,
    ) -> Dict[str, Any]:
        """Get onedrive drive cache stats."""
        if not tenant_id:
            return {"total": 0, "valid": 0, "stale": 0, "expired": 0, "manual": 0, "by_source": {}}
        now_iso = _now_iso()
        cutoff_iso = None
        try:
            window_days = max(0, int(stale_window_days or 0))
        except Exception:
            window_days = 0
        if window_days:
            cutoff_iso = (datetime.now(timezone.utc) - timedelta(days=window_days)).isoformat()
        with self._connect() as conn:
            total = conn.execute(
                "SELECT COUNT(*) AS c FROM onedrive_drive_cache WHERE tenant_id = ?",
                (tenant_id,),
            ).fetchone()["c"]
            valid = conn.execute(
                "SELECT COUNT(*) AS c FROM onedrive_drive_cache WHERE tenant_id = ? AND expires_at > ?",
                (tenant_id, now_iso),
            ).fetchone()["c"]
            manual = 0
            by_source = {}
            try:
                manual = conn.execute(
                    "SELECT COUNT(*) AS c FROM onedrive_drive_cache WHERE tenant_id = ? AND source = ?",
                    (tenant_id, "manual"),
                ).fetchone()["c"]
                rows = conn.execute(
                    """
                    SELECT COALESCE(NULLIF(source, ''), 'primary') AS src, COUNT(*) AS c
                    FROM onedrive_drive_cache
                    WHERE tenant_id = ?
                    GROUP BY COALESCE(NULLIF(source, ''), 'primary')
                    """,
                    (tenant_id,),
                ).fetchall()
                by_source = {str(row["src"]): int(row["c"] or 0) for row in rows}
            except Exception:
                manual = 0
                by_source = {}
            if cutoff_iso:
                stale = conn.execute(
                    """
                    SELECT COUNT(*) AS c
                    FROM onedrive_drive_cache
                    WHERE tenant_id = ? AND expires_at <= ? AND expires_at >= ?
                    """,
                    (tenant_id, now_iso, cutoff_iso),
                ).fetchone()["c"]
                expired = conn.execute(
                    "SELECT COUNT(*) AS c FROM onedrive_drive_cache WHERE tenant_id = ? AND expires_at < ?",
                    (tenant_id, cutoff_iso),
                ).fetchone()["c"]
            else:
                stale = 0
                expired = conn.execute(
                    "SELECT COUNT(*) AS c FROM onedrive_drive_cache WHERE tenant_id = ? AND expires_at <= ?",
                    (tenant_id, now_iso),
                ).fetchone()["c"]
        return {
            "total": int(total),
            "valid": int(valid),
            "stale": int(stale),
            "expired": int(expired),
            "manual": int(manual),
            "by_source": by_source,
        }

    def get_onedrive_drive_pending(self, *, tenant_id: str, user_upn: str) -> Optional[Dict[str, Any]]:
        """Get onedrive drive pending."""
        tenant_id = str(tenant_id or "").strip()
        user_upn = str(user_upn or "").strip().lower()
        if not tenant_id or not user_upn:
            return None
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT user_upn, attempts, paused, next_run_at, last_error, last_error_class, last_error_at
                FROM onedrive_drive_pending
                WHERE tenant_id = ? AND user_upn = ?
                LIMIT 1
                """,
                (tenant_id, user_upn),
            ).fetchone()
        if not row:
            return None
        return {
            "user_upn": row["user_upn"],
            "attempts": int(row["attempts"] or 0),
            "paused": int(row["paused"] or 0),
            "next_run_at": row["next_run_at"],
            "last_error": row["last_error"],
            "last_error_class": row["last_error_class"],
            "last_error_at": row["last_error_at"],
        }

    def get_onedrive_drive_pending_stats(self, *, tenant_id: str) -> Dict[str, Any]:
        """Get onedrive drive pending stats."""
        if not tenant_id:
            return {"total": 0, "due": 0, "paused": 0, "stopped": 0}
        now_iso = _now_iso()
        with self._connect() as conn:
            total = conn.execute(
                "SELECT COUNT(*) AS c FROM onedrive_drive_pending WHERE tenant_id = ?",
                (tenant_id,),
            ).fetchone()["c"]
            due = conn.execute(
                """
                SELECT COUNT(*) AS c
                FROM onedrive_drive_pending
                WHERE tenant_id = ? AND next_run_at IS NOT NULL AND next_run_at <= ?
                """,
                (tenant_id, now_iso),
            ).fetchone()["c"]
            paused = 0
            try:
                paused = conn.execute(
                    """
                    SELECT COUNT(*) AS c
                    FROM onedrive_drive_pending
                    WHERE tenant_id = ? AND COALESCE(paused, 0) = 1
                    """,
                    (tenant_id,),
                ).fetchone()["c"]
            except Exception:
                paused = 0
            stopped = conn.execute(
                """
                SELECT COUNT(*) AS c
                FROM onedrive_drive_pending
                WHERE tenant_id = ? AND (next_run_at IS NULL OR next_run_at = '')
                """,
                (tenant_id,),
            ).fetchone()["c"]
        return {"total": int(total), "due": int(due), "paused": int(paused), "stopped": int(stopped)}

    def enqueue_onedrive_drive_pending(
        self,
        *,
        tenant_id: str,
        user_upn: str,
        delay_seconds: int = 60,
        last_error: Optional[str] = None,
        last_error_class: Optional[str] = None,
        max_attempts: int = 10,
        paused_cooldown_seconds: int = 21600,
    ) -> Dict[str, Any]:
        """Run enqueue onedrive drive pending."""
        tenant_id = str(tenant_id or "").strip()
        user_upn = str(user_upn or "").strip().lower()
        if not tenant_id or not user_upn:
            return {"enqueued": False, "error": "tenant_id and user_upn required"}
        try:
            delay = max(30, int(delay_seconds or 60))
        except Exception:
            delay = 60
        cap = int(max_attempts or 10)
        now = datetime.now(timezone.utc)
        now_iso = now.isoformat()
        last_error_at = now_iso
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT attempts, paused, next_run_at
                FROM onedrive_drive_pending
                WHERE tenant_id = ? AND user_upn = ?
                """,
                (tenant_id, user_upn),
            ).fetchone()
            if row:
                attempts = int(row["attempts"] or 0)
                paused = int(row["paused"] or 0)
                if attempts >= cap:
                    paused = 1
                    delay = max(int(paused_cooldown_seconds or 21600), 3600)
                else:
                    if str(last_error_class or "").strip().lower() == "circuit_open":
                        # Circuit open: schedule for the remaining cooldown (no exponential amplification).
                        delay = max(30, int(delay or 60))
                    else:
                        # Exponential backoff with deterministic jitter to avoid thundering herds.
                        exp = min(10, max(0, attempts))
                        delay = int(min(3600, max(30, delay * (2**exp))))
                        delay += _stable_jitter_seconds(
                            f"{tenant_id}:{user_upn}:{attempts}", max_jitter_s=15
                        )
                next_run_at = (now + timedelta(seconds=delay)).isoformat()
                conn.execute(
                    """
                    UPDATE onedrive_drive_pending
                    SET next_run_at = ?,
                        last_error = ?,
                        last_error_class = ?,
                        last_error_at = ?,
                        paused = ?
                    WHERE tenant_id = ? AND user_upn = ?
                    """,
                    (
                        next_run_at,
                        last_error,
                        last_error_class,
                        last_error_at,
                        paused,
                        tenant_id,
                        user_upn,
                    ),
                )
                conn.commit()
                return {
                    "enqueued": True,
                    "attempts": attempts,
                    "paused": bool(paused),
                    "next_run_at": next_run_at,
                    "last_error": last_error,
                    "last_error_class": last_error_class,
                    "last_error_at": last_error_at,
                    "updated_at": now_iso,
                }

            conn.execute(
                """
                INSERT INTO onedrive_drive_pending
                  (tenant_id, user_upn, attempts, paused, next_run_at, last_error, last_error_class, last_error_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    tenant_id,
                    user_upn,
                    0,
                    0,
                    (now + timedelta(seconds=delay)).isoformat(),
                    last_error,
                    last_error_class,
                    last_error_at,
                ),
            )
            conn.commit()
        return {
            "enqueued": True,
            "attempts": 0,
            "paused": False,
            "next_run_at": (now + timedelta(seconds=delay)).isoformat(),
            "last_error": last_error,
            "last_error_class": last_error_class,
            "last_error_at": last_error_at,
            "updated_at": now_iso,
        }

    def claim_due_onedrive_drive_pending(
        self,
        *,
        tenant_id: str,
        limit: int = 50,
        max_attempts: int = 10,
    ) -> List[Dict[str, Any]]:
        """Run claim due onedrive drive pending."""
        tenant_id = str(tenant_id or "").strip()
        if not tenant_id:
            return []
        now_iso = _now_iso()
        out: List[Dict[str, Any]] = []
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT user_upn, attempts, paused, next_run_at, last_error, last_error_class, last_error_at
                FROM onedrive_drive_pending
                WHERE tenant_id = ?
                  AND next_run_at IS NOT NULL
                  AND next_run_at <> ''
                  AND next_run_at <= ?
                ORDER BY next_run_at ASC
                LIMIT ?
                """,
                (tenant_id, now_iso, int(limit or 50)),
            ).fetchall()
            for row in rows:
                upn = str(row["user_upn"])
                attempts_before = int(row["attempts"] or 0)
                cap = int(max_attempts or 10)
                next_attempts = min(attempts_before + 1, cap)
                conn.execute(
                    """
                    UPDATE onedrive_drive_pending
                    SET attempts = ?
                    WHERE tenant_id = ? AND user_upn = ?
                    """,
                    (next_attempts, tenant_id, upn),
                )
                out.append(
                    {
                        "user_upn": upn,
                        "attempts": next_attempts,
                        "paused": int(row["paused"] or 0),
                        "next_run_at": row["next_run_at"],
                        "last_error": row["last_error"],
                        "last_error_class": row["last_error_class"],
                        "last_error_at": row["last_error_at"],
                    }
                )
            conn.commit()
        return out

    def clear_onedrive_drive_pending(self, *, tenant_id: str, user_upn: str) -> None:
        """Run clear onedrive drive pending."""
        tenant_id = str(tenant_id or "").strip()
        user_upn = str(user_upn or "").strip().lower()
        if not tenant_id or not user_upn:
            return
        with self._connect() as conn:
            conn.execute(
                "DELETE FROM onedrive_drive_pending WHERE tenant_id = ? AND user_upn = ?",
                (tenant_id, user_upn),
            )
            conn.commit()

    def requeue_onedrive_drive_pending(
        self,
        *,
        tenant_id: str,
        user_upn: str,
        delay_seconds: int = 5,
    ) -> Dict[str, Any]:
        """Run requeue onedrive drive pending."""
        tenant_id = str(tenant_id or "").strip()
        user_upn = str(user_upn or "").strip().lower()
        if not tenant_id or not user_upn:
            return {"ok": False, "error": "tenant_id and user_upn required"}
        try:
            delay = max(1, int(delay_seconds or 5))
        except Exception:
            delay = 5
        now = datetime.now(timezone.utc)
        now_iso = now.isoformat()
        next_run_at = (now + timedelta(seconds=delay)).isoformat()
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT user_upn
                FROM onedrive_drive_pending
                WHERE tenant_id = ? AND user_upn = ?
                """,
                (tenant_id, user_upn),
            ).fetchone()
            if row:
                conn.execute(
                    """
                    UPDATE onedrive_drive_pending
                    SET attempts = 0,
                        paused = 0,
                        next_run_at = ?,
                        last_error = NULL,
                        last_error_class = NULL,
                        last_error_at = NULL
                    WHERE tenant_id = ? AND user_upn = ?
                    """,
                    (next_run_at, tenant_id, user_upn),
                )
            else:
                conn.execute(
                    """
                    INSERT INTO onedrive_drive_pending
                      (tenant_id, user_upn, attempts, paused, next_run_at, last_error, last_error_class, last_error_at)
                    VALUES (?, ?, 0, 0, ?, NULL, NULL, NULL)
                    """,
                    (tenant_id, user_upn, next_run_at),
                )
            conn.commit()
        pending = self.get_onedrive_drive_pending(tenant_id=tenant_id, user_upn=user_upn) or {}
        return {"ok": True, "requeued": True, "pending": pending, "updated_at": now_iso}

    def list_onedrive_drive_cache_upns(self, *, tenant_id: str, limit: int = 50) -> List[str]:
        """List onedrive drive cache upns."""
        if not tenant_id:
            return []
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT user_upn
                FROM onedrive_drive_cache
                WHERE tenant_id = ? AND user_upn IS NOT NULL AND user_upn <> ''
                ORDER BY last_verified_at DESC
                LIMIT ?
                """,
                (tenant_id, int(limit)),
            ).fetchall()
        return [str(row["user_upn"]) for row in rows if row.get("user_upn")]
