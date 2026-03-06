from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Optional
from contextlib import contextmanager
import hashlib
import hmac
import json
import os
import secrets
import sqlite3
import threading
import time


DEFAULT_DB_PATH = Path(__file__).resolve().parent / "control_plane.sqlite"


def _now() -> datetime:
    """Internal helper for now."""
    return datetime.now(timezone.utc)


def _now_iso() -> str:
    """Internal helper for now iso."""
    return _now().isoformat()


def _parse_iso(value: str | None) -> datetime | None:
    """Internal helper for parse iso."""
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed
    except Exception:
        return None


def _json_dumps(value: Any) -> str | None:
    """Internal helper for json dumps."""
    if value is None:
        return None
    try:
        return json.dumps(value, default=str)
    except Exception:
        return json.dumps({"error": "json_serialize_failed", "type": str(type(value))})


def _json_loads(value: str | None) -> Any:
    """Internal helper for json loads."""
    if not value:
        return None
    try:
        return json.loads(value)
    except Exception:
        return None


_FORBIDDEN_JOB_PARAM_SUBSTRINGS = (
    "secret",
    "token",
    "password",
    "client_secret",
    "access_key",
    "private_key",
)


def _validate_job_params_no_secrets(params: Any) -> None:
    """Reject job params that appear to contain secret material.

    The control plane DB must never store secret material (only references/ids).
    """

    def walk(value: Any) -> None:
        if value is None:
            return
        if isinstance(value, dict):
            for key, item in value.items():
                lowered = str(key).lower()
                if any(word in lowered for word in _FORBIDDEN_JOB_PARAM_SUBSTRINGS):
                    raise ValueError(f"Forbidden job param key: {key}")
                walk(item)
            return
        if isinstance(value, list):
            for item in value:
                walk(item)
            return

    walk(params)


def _token_hash(token: str) -> str:
    """Hash token for storage."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _token_matches(token: str, token_hash: str) -> bool:
    """Constant-time token compare."""
    if not token or not token_hash:
        return False
    return hmac.compare_digest(_token_hash(token), token_hash)


def _truthy(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in ("1", "true", "yes", "y", "on")


def _pairing_code_hash(code: str) -> str:
    """Hash pairing code for storage/lookup."""
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


_PAIRING_CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def _generate_pairing_code(*, groups: int = 2, group_len: int = 4) -> str:
    parts = []
    for _ in range(max(1, int(groups or 2))):
        token = "".join(secrets.choice(_PAIRING_CODE_ALPHABET) for _ in range(max(4, int(group_len or 4))))
        parts.append(token)
    return "-".join(parts)


def connect(db_path: Path | None = None) -> sqlite3.Connection:
    """Connect control plane database."""
    env_path = os.environ.get("CONTROL_PLANE_DB_PATH") or None
    path = Path(db_path) if db_path else Path(env_path) if env_path else DEFAULT_DB_PATH
    if not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path), timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = NORMAL")
    init_schema(conn)
    return conn


@contextmanager
def open_db(db_path: Path | None = None) -> sqlite3.Connection:
    """Context manager that opens/closes the control plane DB."""
    conn = connect(db_path)
    try:
        yield conn
    finally:
        try:
            conn.close()
        except Exception:
            pass


def init_schema(conn: sqlite3.Connection) -> None:
    """Initialize control plane schema."""
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS agents (
            agent_id TEXT PRIMARY KEY,
            tenant_id TEXT,
            workspace_id TEXT,
            name TEXT,
            hostname TEXT,
            os TEXT,
            arch TEXT,
            version TEXT,
            capabilities_json TEXT,
            last_seen TEXT,
            status TEXT,
            labels_json TEXT,
            created_at TEXT,
            updated_at TEXT
        );

        CREATE TABLE IF NOT EXISTS pairing_codes (
            code_hash TEXT PRIMARY KEY,
            tenant_id TEXT,
            workspace_id TEXT,
            created_at TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            consumed_at TEXT,
            consumed_agent_id TEXT
        );

        CREATE INDEX IF NOT EXISTS idx_pairing_codes_expires
        ON pairing_codes (expires_at);

        CREATE INDEX IF NOT EXISTS idx_pairing_codes_consumed
        ON pairing_codes (consumed_at);

        CREATE TABLE IF NOT EXISTS jobs (
            job_id TEXT PRIMARY KEY,
            agent_id TEXT NOT NULL,
            tenant_id TEXT,
            workspace_id TEXT,
            action_id TEXT NOT NULL,
            params_json TEXT,
            risk_level TEXT,
            requested_by TEXT,
            status TEXT NOT NULL,
            lease_expires_at TEXT,
            created_at TEXT,
            started_at TEXT,
            finished_at TEXT,
            error_json TEXT,
            FOREIGN KEY (agent_id) REFERENCES agents(agent_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS job_results (
            job_id TEXT PRIMARY KEY,
            agent_id TEXT NOT NULL,
            result_json TEXT,
            stdout TEXT,
            stderr TEXT,
            exit_code INTEGER,
            artifacts_json TEXT,
            duration_ms INTEGER,
            created_at TEXT,
            FOREIGN KEY (job_id) REFERENCES jobs(job_id) ON DELETE CASCADE,
            FOREIGN KEY (agent_id) REFERENCES agents(agent_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS artifacts (
            artifact_id TEXT PRIMARY KEY,
            agent_id TEXT NOT NULL,
            job_id TEXT,
            type TEXT,
            filename TEXT,
            sha256 TEXT,
            size_bytes INTEGER,
            storage_path TEXT,
            created_at TEXT,
            FOREIGN KEY (agent_id) REFERENCES agents(agent_id) ON DELETE CASCADE,
            FOREIGN KEY (job_id) REFERENCES jobs(job_id) ON DELETE SET NULL
        );

        CREATE INDEX IF NOT EXISTS idx_artifacts_agent_created
        ON artifacts (agent_id, created_at);

        CREATE INDEX IF NOT EXISTS idx_artifacts_job_created
        ON artifacts (job_id, created_at);

        CREATE TABLE IF NOT EXISTS agent_tokens (
            agent_id TEXT PRIMARY KEY,
            token_hash TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (agent_id) REFERENCES agents(agent_id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_agents_status_last_seen
        ON agents (status, last_seen);

        CREATE INDEX IF NOT EXISTS idx_jobs_agent_status_created
        ON jobs (agent_id, status, created_at);

        CREATE INDEX IF NOT EXISTS idx_jobs_lease_expires
        ON jobs (lease_expires_at);

        CREATE INDEX IF NOT EXISTS idx_job_results_agent_created
        ON job_results (agent_id, created_at);

        CREATE TABLE IF NOT EXISTS terminal_sessions (
            session_id TEXT PRIMARY KEY,
            agent_id TEXT NOT NULL,
            operator TEXT,
            started_at TEXT,
            expires_at TEXT,
            status TEXT,
            FOREIGN KEY (agent_id) REFERENCES agents(agent_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS terminal_audit (
            audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            kind TEXT NOT NULL,
            payload_json TEXT,
            FOREIGN KEY (session_id) REFERENCES terminal_sessions(session_id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_terminal_sessions_agent_status_started
        ON terminal_sessions (agent_id, status, started_at);

        CREATE INDEX IF NOT EXISTS idx_terminal_audit_session_time
        ON terminal_audit (session_id, timestamp);
        """
    )
    _apply_schema_migrations(conn)


def _table_columns(conn: sqlite3.Connection, table: str) -> set[str]:
    """Return column names for a table."""
    try:
        rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    except Exception:
        return set()
    cols = set()
    for row in rows or []:
        try:
            name = row["name"]  # type: ignore[index]
        except Exception:
            try:
                name = row[1]
            except Exception:
                name = None
        if name:
            cols.add(str(name))
    return cols


def _ensure_column(conn: sqlite3.Connection, table: str, column: str, decl: str) -> None:
    cols = _table_columns(conn, table)
    if column in cols:
        return
    conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {decl}")


def _apply_schema_migrations(conn: sqlite3.Connection) -> None:
    """Apply additive schema migrations for existing DBs."""
    try:
        conn.execute("BEGIN IMMEDIATE")
        _ensure_column(conn, "agents", "tenant_id", "TEXT")
        _ensure_column(conn, "agents", "workspace_id", "TEXT")
        _ensure_column(conn, "jobs", "tenant_id", "TEXT")
        _ensure_column(conn, "jobs", "workspace_id", "TEXT")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_agents_scope ON agents (tenant_id, workspace_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_jobs_scope_created ON jobs (tenant_id, workspace_id, created_at)")
        conn.commit()
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass
        return


def create_pairing_code(
    *,
    tenant_id: str | None = None,
    workspace_id: str | None = None,
    ttl_seconds: int | None = None,
    db_path: Path | None = None,
) -> dict[str, Any]:
    """Create a one-time pairing code for bootstrapping a new agent."""

    now = _now()
    now_iso = now.isoformat()
    try:
        ttl = int(ttl_seconds or os.environ.get("CONTROL_PLANE_PAIRING_CODE_TTL_SECONDS") or 900)
    except Exception:
        ttl = 900
    ttl = max(60, min(86400, ttl))
    expires_at_iso = (now + timedelta(seconds=ttl)).isoformat()

    tenant_val = str(tenant_id).strip() if tenant_id is not None else None
    workspace_val = str(workspace_id).strip() if workspace_id is not None else None
    if tenant_val == "":
        tenant_val = None
    if workspace_val == "":
        workspace_val = None

    code = _generate_pairing_code()
    code_hash = _pairing_code_hash(code)

    with open_db(db_path) as conn:
        conn.execute("BEGIN IMMEDIATE")
        conn.execute(
            """
            INSERT INTO pairing_codes
            (code_hash, tenant_id, workspace_id, created_at, expires_at, consumed_at, consumed_agent_id)
            VALUES (?, ?, ?, ?, ?, NULL, NULL)
            """,
            (code_hash, tenant_val, workspace_val, now_iso, expires_at_iso),
        )
        conn.commit()

    return {
        "pairing_code": code,
        "tenant_id": tenant_val,
        "workspace_id": workspace_val,
        "created_at": now_iso,
        "expires_at": expires_at_iso,
        "ttl_seconds": ttl,
    }


def _consume_pairing_code(conn: sqlite3.Connection, code: str, *, consumed_agent_id: str) -> dict[str, Any]:
    """Consume a one-time pairing code within an existing transaction."""

    now_iso = _now_iso()
    code_hash = _pairing_code_hash(str(code or "").strip().upper())
    row = conn.execute(
        """
        SELECT code_hash, tenant_id, workspace_id, expires_at, consumed_at
        FROM pairing_codes
        WHERE code_hash = ?
        """,
        (code_hash,),
    ).fetchone()
    if not row:
        raise PermissionError("Invalid pairing code.")
    if row["consumed_at"]:
        raise PermissionError("Pairing code already used.")
    expires_at = _parse_iso(str(row["expires_at"] or ""))
    if expires_at and expires_at < _now():
        raise PermissionError("Pairing code expired.")

    cur = conn.execute(
        """
        UPDATE pairing_codes
        SET consumed_at = ?,
            consumed_agent_id = ?
        WHERE code_hash = ?
          AND consumed_at IS NULL
        """,
        (now_iso, consumed_agent_id, code_hash),
    )
    if cur.rowcount != 1:
        raise PermissionError("Pairing code unavailable.")

    return {
        "tenant_id": row["tenant_id"],
        "workspace_id": row["workspace_id"],
    }


def register_agent(
    payload: dict,
    *,
    db_path: Path | None = None,
    allow_create: bool = True,
    allow_update_without_token: bool = False,
) -> dict:
    """Register or re-register an agent (upsert) and return credentials."""
    requested_agent_id = payload.get("agent_id") or None
    provided_token = payload.get("agent_token") or None
    pairing_code = payload.get("pairing_code") or payload.get("pair_code") or None
    rotate_token = _truthy(payload.get("rotate_token") or payload.get("rotate_agent_token") or payload.get("rotate"))
    now = _now_iso()

    def make_new_agent_id() -> str:
        return secrets.token_hex(16)

    with open_db(db_path) as conn:
        conn.execute("BEGIN IMMEDIATE")
        agent_id = None
        existing = None
        token_ok = False

        if requested_agent_id:
            existing = conn.execute(
                "SELECT agent_id FROM agents WHERE agent_id = ?",
                (requested_agent_id,),
            ).fetchone()
            if existing and provided_token:
                token_row = conn.execute(
                    "SELECT token_hash FROM agent_tokens WHERE agent_id = ?",
                    (requested_agent_id,),
                ).fetchone()
                if token_row and _token_matches(str(provided_token), str(token_row["token_hash"])):
                    token_ok = True

        if requested_agent_id and existing and (token_ok or allow_update_without_token):
            agent_id = requested_agent_id
        elif requested_agent_id and not existing and allow_create:
            agent_id = requested_agent_id
        elif allow_create:
            agent_id = make_new_agent_id()
        else:
            raise PermissionError("Agent registration not permitted.")

        require_pairing = _truthy(os.environ.get("CONTROL_PLANE_REQUIRE_PAIRING_CODE"))
        pairing_scope = None
        if require_pairing and not token_ok:
            if not pairing_code:
                raise PermissionError("Pairing code required for new agent registration.")
            pairing_scope = _consume_pairing_code(conn, str(pairing_code), consumed_agent_id=str(agent_id))

        agent_row = conn.execute(
            "SELECT agent_id, created_at, tenant_id, workspace_id FROM agents WHERE agent_id = ?",
            (agent_id,),
        ).fetchone()
        created_at = agent_row["created_at"] if agent_row else now
        tenant_existing = agent_row["tenant_id"] if agent_row else None
        workspace_existing = agent_row["workspace_id"] if agent_row else None
        tenant_id = payload.get("tenant_id") or payload.get("tenant") or tenant_existing
        workspace_id = payload.get("workspace_id") or payload.get("workspace") or workspace_existing
        if pairing_scope:
            if not tenant_id:
                tenant_id = pairing_scope.get("tenant_id")
            if not workspace_id:
                workspace_id = pairing_scope.get("workspace_id")

        record = {
            "agent_id": agent_id,
            "tenant_id": tenant_id,
            "workspace_id": workspace_id,
            "name": payload.get("name"),
            "hostname": payload.get("hostname"),
            "os": payload.get("os"),
            "arch": payload.get("arch"),
            "version": payload.get("version"),
            "capabilities_json": _json_dumps(payload.get("capabilities") or payload.get("capabilities_json")),
            "labels_json": _json_dumps(payload.get("labels") or payload.get("labels_json")),
            "last_seen": now,
            "status": payload.get("status") or "online",
            "created_at": created_at,
            "updated_at": now,
        }

        conn.execute(
            """
            INSERT INTO agents
            (agent_id, tenant_id, workspace_id, name, hostname, os, arch, version, capabilities_json, last_seen, status, labels_json, created_at, updated_at)
            VALUES
            (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(agent_id) DO UPDATE SET
                tenant_id=excluded.tenant_id,
                workspace_id=excluded.workspace_id,
                name=excluded.name,
                hostname=excluded.hostname,
                os=excluded.os,
                arch=excluded.arch,
                version=excluded.version,
                capabilities_json=excluded.capabilities_json,
                last_seen=excluded.last_seen,
                status=excluded.status,
                labels_json=excluded.labels_json,
                updated_at=excluded.updated_at
            """,
            (
                record["agent_id"],
                record["tenant_id"],
                record["workspace_id"],
                record["name"],
                record["hostname"],
                record["os"],
                record["arch"],
                record["version"],
                record["capabilities_json"],
                record["last_seen"],
                record["status"],
                record["labels_json"],
                record["created_at"],
                record["updated_at"],
            ),
        )

        token_row = conn.execute(
            "SELECT token_hash FROM agent_tokens WHERE agent_id = ?",
            (agent_id,),
        ).fetchone()
        must_mint = (token_row is None) or (not token_ok) or rotate_token
        agent_token = None
        if must_mint:
            agent_token = secrets.token_urlsafe(32)
            conn.execute(
                """
                INSERT INTO agent_tokens (agent_id, token_hash, created_at, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(agent_id) DO UPDATE SET
                    token_hash=excluded.token_hash,
                    updated_at=excluded.updated_at
                """,
                (agent_id, _token_hash(agent_token), now, now),
            )
        conn.commit()
        output = {"agent_id": agent_id}
        if agent_token:
            output["agent_token"] = agent_token
        return output


def authenticate_agent(agent_id: str, token: str, *, db_path: Path | None = None) -> bool:
    """Authenticate agent."""
    if not agent_id or not token:
        return False
    with open_db(db_path) as conn:
        row = conn.execute(
            "SELECT token_hash FROM agent_tokens WHERE agent_id = ?",
            (agent_id,),
        ).fetchone()
        if not row:
            return False
        return _token_matches(token, str(row["token_hash"]))


def heartbeat_agent(
    agent_id: str,
    *,
    status: str | None = None,
    capabilities: Any | None = None,
    labels: Any | None = None,
    tenant_id: str | None = None,
    workspace_id: str | None = None,
    db_path: Path | None = None,
) -> dict:
    """Update agent heartbeat."""
    now = _now_iso()
    with open_db(db_path) as conn:
        conn.execute("BEGIN IMMEDIATE")
        existing = conn.execute(
            "SELECT agent_id FROM agents WHERE agent_id = ?",
            (agent_id,),
        ).fetchone()
        if not existing:
            raise KeyError("Unknown agent_id")
        updates = {
            "last_seen": now,
            "status": status or "online",
            "updated_at": now,
        }
        if capabilities is not None:
            updates["capabilities_json"] = _json_dumps(capabilities)
        if labels is not None:
            updates["labels_json"] = _json_dumps(labels)
        if tenant_id is not None:
            updates["tenant_id"] = str(tenant_id).strip() or None
        if workspace_id is not None:
            updates["workspace_id"] = str(workspace_id).strip() or None

        conn.execute(
            """
            UPDATE agents
            SET last_seen = ?,
                status = ?,
                capabilities_json = COALESCE(?, capabilities_json),
                labels_json = COALESCE(?, labels_json),
                tenant_id = COALESCE(?, tenant_id),
                workspace_id = COALESCE(?, workspace_id),
                updated_at = ?
            WHERE agent_id = ?
            """,
            (
                updates["last_seen"],
                updates["status"],
                updates.get("capabilities_json"),
                updates.get("labels_json"),
                updates.get("tenant_id"),
                updates.get("workspace_id"),
                updates["updated_at"],
                agent_id,
            ),
        )
        conn.commit()
        return {"agent_id": agent_id, "last_seen": now, "status": updates["status"]}


def list_agents(
    *,
    db_path: Path | None = None,
    status: str | None = None,
    query: str | None = None,
    tenant_id: str | None = None,
    workspace_id: str | None = None,
    limit: int = 200,
    offset: int = 0,
) -> dict:
    """List agents."""
    status = status or None
    query_text = (query or "").strip().lower() or None
    tenant_id = (tenant_id or "").strip() or None
    workspace_id = (workspace_id or "").strip() or None
    limit_val = max(1, min(1000, int(limit or 200)))
    offset_val = max(0, int(offset or 0))

    with open_db(db_path) as conn:
        clauses = []
        params: list[Any] = []
        if status:
            clauses.append("status = ?")
            params.append(status)
        if tenant_id:
            clauses.append("tenant_id = ?")
            params.append(tenant_id)
        if workspace_id:
            clauses.append("workspace_id = ?")
            params.append(workspace_id)
        if query_text:
            clauses.append("(LOWER(agent_id) LIKE ? OR LOWER(name) LIKE ? OR LOWER(hostname) LIKE ?)")
            like = f"%{query_text}%"
            params.extend([like, like, like])
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        total = conn.execute(f"SELECT COUNT(1) AS c FROM agents {where}", params).fetchone()["c"]
        rows = conn.execute(
            f"""
            SELECT agent_id, tenant_id, workspace_id, name, hostname, os, arch, version, capabilities_json, last_seen, status, labels_json, created_at, updated_at
            FROM agents
            {where}
            ORDER BY COALESCE(last_seen, created_at) DESC
            LIMIT ? OFFSET ?
            """,
            (*params, limit_val, offset_val),
        ).fetchall()
        items = []
        for row in rows:
            items.append(
                {
                    "agent_id": row["agent_id"],
                    "tenant_id": row["tenant_id"],
                    "workspace_id": row["workspace_id"],
                    "name": row["name"],
                    "hostname": row["hostname"],
                    "os": row["os"],
                    "arch": row["arch"],
                    "version": row["version"],
                    "capabilities": _json_loads(row["capabilities_json"]),
                    "last_seen": row["last_seen"],
                    "status": row["status"],
                    "labels": _json_loads(row["labels_json"]),
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                }
            )
        return {"items": items, "count": len(items), "total": int(total or 0)}


_ACTION_CATALOG_CACHE: dict[str, Any] = {"ts": 0.0, "by_id": {}}
_ACTION_CATALOG_CACHE_TTL_SECONDS = 60


def _action_catalog_by_id() -> dict[str, dict[str, Any]]:
    """Return action catalog keyed by action_id (cached).

    Source of truth is the agent plugin manifests (via agent.catalog).
    """

    now = time.time()
    cached = _ACTION_CATALOG_CACHE.get("by_id") or {}
    ts = float(_ACTION_CATALOG_CACHE.get("ts") or 0.0)
    if cached and (now - ts) < _ACTION_CATALOG_CACHE_TTL_SECONDS:
        return cached
    try:
        from agent.catalog import build_capabilities_catalog

        catalog = build_capabilities_catalog()
        actions = catalog.get("actions") if isinstance(catalog, dict) else None
        by_id: dict[str, dict[str, Any]] = {}
        if isinstance(actions, list):
            for action in actions:
                if not isinstance(action, dict):
                    continue
                action_id = str(action.get("action_id") or "").strip()
                if not action_id:
                    continue
                by_id[action_id] = action
        _ACTION_CATALOG_CACHE["ts"] = now
        _ACTION_CATALOG_CACHE["by_id"] = by_id
        return by_id
    except Exception:
        # Do not poison cache on failure; allow retries.
        return cached if isinstance(cached, dict) else {}


def get_action_spec(action_id: str) -> dict[str, Any]:
    """Return the action spec from the catalog."""
    action_id = str(action_id or "").strip()
    if not action_id:
        raise ValueError("action_id is required")
    spec = _action_catalog_by_id().get(action_id)
    if not spec:
        raise KeyError("Unknown action_id")
    return spec


def enqueue_action_job(
    *,
    agent_id: str,
    action_id: str,
    params: Any | None = None,
    requested_by: str | None = None,
    interactive_scope: bool = False,
    tenant_id: str | None = None,
    workspace_id: str | None = None,
    db_path: Path | None = None,
) -> dict:
    """Enqueue a job by action_id with catalog/capability validation."""

    spec = get_action_spec(action_id)
    required_caps = spec.get("required_capabilities") or []
    required_caps = [str(cap).strip() for cap in required_caps if str(cap).strip()]
    risk_level = str(spec.get("risk_level") or "safe").strip().lower() or "safe"
    if risk_level not in ("safe", "caution", "danger"):
        risk_level = "safe"

    agent_id = str(agent_id or "").strip()
    if not agent_id:
        raise ValueError("agent_id is required")

    # Validate agent capabilities against required capabilities.
    with open_db(db_path) as conn:
        agent = conn.execute(
            "SELECT agent_id, capabilities_json FROM agents WHERE agent_id = ?",
            (agent_id,),
        ).fetchone()
        if not agent:
            raise KeyError("Unknown agent_id")
        caps = _capability_set(_json_loads(agent["capabilities_json"]))
        missing = [cap for cap in required_caps if cap not in caps]
        if missing:
            raise PermissionError(f"Agent missing required capabilities: {', '.join(missing)}")

        if risk_level == "danger":
            if not interactive_scope:
                raise PermissionError("interactive_scope=true required for danger actions")
            if "break_glass.enabled" not in caps:
                raise PermissionError("Agent BREAK_GLASS_ENABLED required for danger actions")

    job = enqueue_job(
        agent_id=agent_id,
        action_id=action_id,
        params=params,
        risk_level=risk_level,
        requested_by=requested_by,
        tenant_id=tenant_id,
        workspace_id=workspace_id,
        db_path=db_path,
    )
    return {**job, "risk_level": risk_level}


def enqueue_job(
    *,
    agent_id: str,
    action_id: str,
    params: Any | None = None,
    risk_level: str | None = None,
    requested_by: str | None = None,
    job_id: str | None = None,
    tenant_id: str | None = None,
    workspace_id: str | None = None,
    db_path: Path | None = None,
) -> dict:
    """Enqueue a job for an agent."""
    jid = job_id or secrets.token_hex(16)
    now = _now_iso()
    _validate_job_params_no_secrets(params)
    with open_db(db_path) as conn:
        conn.execute("BEGIN IMMEDIATE")
        agent = conn.execute("SELECT agent_id, tenant_id, workspace_id FROM agents WHERE agent_id = ?", (agent_id,)).fetchone()
        if not agent:
            raise KeyError("Unknown agent_id")
        tenant_val = str(tenant_id).strip() if tenant_id else str(agent["tenant_id"] or "").strip() or None
        workspace_val = str(workspace_id).strip() if workspace_id else str(agent["workspace_id"] or "").strip() or None
        conn.execute(
            """
            INSERT INTO jobs
            (job_id, agent_id, tenant_id, workspace_id, action_id, params_json, risk_level, requested_by, status, lease_expires_at, created_at, started_at, finished_at, error_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                jid,
                agent_id,
                tenant_val,
                workspace_val,
                action_id,
                _json_dumps(params),
                risk_level,
                requested_by,
                "queued",
                None,
                now,
                None,
                None,
                None,
            ),
        )
        conn.commit()
        return {"job_id": jid}


def _lease_until(lease_seconds: int) -> str:
    """Internal helper for lease until."""
    seconds = max(5, int(lease_seconds or 0))
    return (_now() + timedelta(seconds=seconds)).isoformat()


def lease_next_job(
    agent_id: str,
    *,
    lease_seconds: int = 900,
    db_path: Path | None = None,
) -> dict | None:
    """Lease next queued job for an agent."""
    now = _now_iso()
    lease_expires_at = _lease_until(lease_seconds)
    with open_db(db_path) as conn:
        conn.execute("BEGIN IMMEDIATE")
        row = conn.execute(
            """
            SELECT job_id
            FROM jobs
            WHERE agent_id = ?
              AND status = 'queued'
            ORDER BY created_at ASC
            LIMIT 1
            """,
            (agent_id,),
        ).fetchone()
        if not row:
            conn.commit()
            return None
        job_id = str(row["job_id"])
        cur = conn.execute(
            """
            UPDATE jobs
            SET status = 'running',
                lease_expires_at = ?,
                started_at = ?
            WHERE job_id = ?
              AND agent_id = ?
              AND status = 'queued'
            """,
            (lease_expires_at, now, job_id, agent_id),
        )
        if cur.rowcount != 1:
            conn.commit()
            return None
        job = conn.execute(
            """
            SELECT job_id, agent_id, action_id, params_json, risk_level, requested_by, status, lease_expires_at, created_at, started_at, finished_at, error_json
            FROM jobs
            WHERE job_id = ?
            """,
            (job_id,),
        ).fetchone()
        conn.commit()
        if not job:
            return None
        return {
            "job_id": job["job_id"],
            "agent_id": job["agent_id"],
            "action_id": job["action_id"],
            "params": _json_loads(job["params_json"]),
            "risk_level": job["risk_level"],
            "requested_by": job["requested_by"],
            "status": job["status"],
            "lease_expires_at": job["lease_expires_at"],
            "created_at": job["created_at"],
            "started_at": job["started_at"],
        }


def record_job_result(
    agent_id: str,
    job_id: str,
    *,
    result: Any | None = None,
    stdout: str | None = None,
    stderr: str | None = None,
    exit_code: int | None = None,
    artifacts: Any | None = None,
    duration_ms: int | None = None,
    status: str | None = None,
    error: Any | None = None,
    db_path: Path | None = None,
) -> dict:
    """Record job result and finalize job."""
    now = _now_iso()
    normalized_status = status or None
    if normalized_status:
        normalized_status = str(normalized_status).lower().strip()
    if normalized_status not in (None, "completed", "failed"):
        raise ValueError("Invalid status (expected completed/failed)")

    inferred_failed = False
    if normalized_status is None:
        if exit_code is None:
            inferred_failed = False
        else:
            try:
                inferred_failed = int(exit_code) != 0
            except Exception:
                inferred_failed = True
        normalized_status = "failed" if inferred_failed else "completed"

    error_payload = error
    if normalized_status == "failed" and error_payload is None:
        if stderr:
            error_payload = {"error": "job_failed", "stderr": stderr[:10_000]}
        elif exit_code not in (None, 0):
            error_payload = {"error": "job_failed", "exit_code": exit_code}

    with open_db(db_path) as conn:
        conn.execute("BEGIN IMMEDIATE")
        job = conn.execute(
            "SELECT job_id, agent_id, status, action_id FROM jobs WHERE job_id = ?",
            (job_id,),
        ).fetchone()
        if not job:
            raise KeyError("Unknown job_id")
        if str(job["agent_id"]) != str(agent_id):
            raise PermissionError("Job belongs to a different agent")

        conn.execute(
            """
            INSERT INTO job_results
            (job_id, agent_id, result_json, stdout, stderr, exit_code, artifacts_json, duration_ms, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(job_id) DO UPDATE SET
                result_json=excluded.result_json,
                stdout=excluded.stdout,
                stderr=excluded.stderr,
                exit_code=excluded.exit_code,
                artifacts_json=excluded.artifacts_json,
                duration_ms=excluded.duration_ms
            """,
            (
                job_id,
                agent_id,
                _json_dumps(result),
                stdout,
                stderr,
                exit_code,
                _json_dumps(artifacts),
                duration_ms,
                now,
            ),
        )

        conn.execute(
            """
            UPDATE jobs
            SET status = ?,
                finished_at = ?,
                lease_expires_at = NULL,
                error_json = ?
            WHERE job_id = ?
            """,
            (normalized_status, now, _json_dumps(error_payload) if error_payload is not None else None, job_id),
        )
        conn.commit()
        return {"job_id": job_id, "agent_id": agent_id, "action_id": str(job["action_id"]), "status": normalized_status, "finished_at": now}


def record_artifact(
    *,
    artifact_id: str,
    agent_id: str,
    filename: str,
    sha256: str,
    size_bytes: int,
    storage_path: str,
    job_id: str | None = None,
    type: str | None = None,
    created_at: str | None = None,
    db_path: Path | None = None,
) -> dict[str, Any]:
    """Record an uploaded artifact in the control plane DB."""

    artifact_id = str(artifact_id or "").strip()
    if not artifact_id:
        raise ValueError("artifact_id is required")
    agent_id = str(agent_id or "").strip()
    if not agent_id:
        raise ValueError("agent_id is required")

    filename = str(filename or "").strip()
    storage_path = str(storage_path or "").strip()
    sha256 = str(sha256 or "").strip().lower()
    type_val = str(type or "").strip() or None
    job_val = str(job_id).strip() if job_id else None
    created_val = str(created_at or _now_iso())

    with open_db(db_path) as conn:
        conn.execute("BEGIN IMMEDIATE")
        agent = conn.execute("SELECT agent_id FROM agents WHERE agent_id = ?", (agent_id,)).fetchone()
        if not agent:
            raise KeyError("Unknown agent_id")
        if job_val:
            job = conn.execute("SELECT job_id FROM jobs WHERE job_id = ?", (job_val,)).fetchone()
            if not job:
                job_val = None

        conn.execute(
            """
            INSERT INTO artifacts
            (artifact_id, agent_id, job_id, type, filename, sha256, size_bytes, storage_path, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(artifact_id) DO UPDATE SET
                agent_id=excluded.agent_id,
                job_id=excluded.job_id,
                type=excluded.type,
                filename=excluded.filename,
                sha256=excluded.sha256,
                size_bytes=excluded.size_bytes,
                storage_path=excluded.storage_path
            """,
            (
                artifact_id,
                agent_id,
                job_val,
                type_val,
                filename,
                sha256,
                int(size_bytes or 0),
                storage_path,
                created_val,
            ),
        )
        conn.commit()

    return {
        "artifact_id": artifact_id,
        "agent_id": agent_id,
        "job_id": job_val,
        "type": type_val,
        "filename": filename,
        "sha256": sha256,
        "size_bytes": int(size_bytes or 0),
        "storage_path": storage_path,
        "created_at": created_val,
    }


def list_jobs(
    *,
    db_path: Path | None = None,
    agent_id: str | None = None,
    status: str | None = None,
    query: str | None = None,
    tenant_id: str | None = None,
    workspace_id: str | None = None,
    limit: int = 200,
    offset: int = 0,
) -> dict:
    """List jobs."""
    agent_id = agent_id or None
    status = status or None
    query_text = (query or "").strip().lower() or None
    tenant_id = (tenant_id or "").strip() or None
    workspace_id = (workspace_id or "").strip() or None
    limit_val = max(1, min(1000, int(limit or 200)))
    offset_val = max(0, int(offset or 0))

    with open_db(db_path) as conn:
        clauses = []
        params: list[Any] = []
        if agent_id:
            clauses.append("agent_id = ?")
            params.append(agent_id)
        if status:
            clauses.append("status = ?")
            params.append(status)
        if tenant_id:
            clauses.append("tenant_id = ?")
            params.append(tenant_id)
        if workspace_id:
            clauses.append("workspace_id = ?")
            params.append(workspace_id)
        if query_text:
            clauses.append("(LOWER(job_id) LIKE ? OR LOWER(action_id) LIKE ? OR LOWER(requested_by) LIKE ?)")
            like = f"%{query_text}%"
            params.extend([like, like, like])
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        total = conn.execute(f"SELECT COUNT(1) AS c FROM jobs {where}", params).fetchone()["c"]
        rows = conn.execute(
            f"""
            SELECT job_id, agent_id, tenant_id, workspace_id, action_id, params_json, risk_level, requested_by, status, lease_expires_at, created_at, started_at, finished_at, error_json
            FROM jobs
            {where}
            ORDER BY COALESCE(created_at, '') DESC
            LIMIT ? OFFSET ?
            """,
            (*params, limit_val, offset_val),
        ).fetchall()
        items = []
        for row in rows:
            items.append(
                {
                    "job_id": row["job_id"],
                    "agent_id": row["agent_id"],
                    "tenant_id": row["tenant_id"],
                    "workspace_id": row["workspace_id"],
                    "action_id": row["action_id"],
                    "params": _json_loads(row["params_json"]),
                    "risk_level": row["risk_level"],
                    "requested_by": row["requested_by"],
                    "status": row["status"],
                    "lease_expires_at": row["lease_expires_at"],
                    "created_at": row["created_at"],
                    "started_at": row["started_at"],
                    "finished_at": row["finished_at"],
                    "error": _json_loads(row["error_json"]),
                }
            )
        return {"items": items, "count": len(items), "total": int(total or 0)}


def get_job_detail(job_id: str, *, db_path: Path | None = None) -> dict:
    """Get job detail (including results if present)."""
    with open_db(db_path) as conn:
        job = conn.execute(
            """
            SELECT job_id, agent_id, tenant_id, workspace_id, action_id, params_json, risk_level, requested_by, status, lease_expires_at, created_at, started_at, finished_at, error_json
            FROM jobs
            WHERE job_id = ?
            """,
            (job_id,),
        ).fetchone()
        if not job:
            raise KeyError("Unknown job_id")
        result = conn.execute(
            """
            SELECT job_id, agent_id, result_json, stdout, stderr, exit_code, artifacts_json, duration_ms, created_at
            FROM job_results
            WHERE job_id = ?
            """,
            (job_id,),
        ).fetchone()
        payload = {
            "job_id": job["job_id"],
            "agent_id": job["agent_id"],
            "tenant_id": job["tenant_id"],
            "workspace_id": job["workspace_id"],
            "action_id": job["action_id"],
            "params": _json_loads(job["params_json"]),
            "risk_level": job["risk_level"],
            "requested_by": job["requested_by"],
            "status": job["status"],
            "lease_expires_at": job["lease_expires_at"],
            "created_at": job["created_at"],
            "started_at": job["started_at"],
            "finished_at": job["finished_at"],
            "error": _json_loads(job["error_json"]),
            "result": None,
        }
        if result:
            payload["result"] = {
                "created_at": result["created_at"],
                "result": _json_loads(result["result_json"]),
                "stdout": result["stdout"],
                "stderr": result["stderr"],
                "exit_code": result["exit_code"],
                "artifacts": _json_loads(result["artifacts_json"]),
                "duration_ms": result["duration_ms"],
            }
        return payload


def requeue_expired_leases(*, db_path: Path | None = None) -> int:
    """Requeue jobs whose lease expired."""
    now = _now()
    with open_db(db_path) as conn:
        conn.execute("BEGIN IMMEDIATE")
        rows = conn.execute(
            """
            SELECT job_id, lease_expires_at
            FROM jobs
            WHERE status = 'running'
              AND lease_expires_at IS NOT NULL
            """
        ).fetchall()
        expired = []
        for row in rows:
            lease = _parse_iso(row["lease_expires_at"])
            if lease and lease <= now:
                expired.append(str(row["job_id"]))
        if not expired:
            conn.commit()
            return 0
        conn.executemany(
            """
            UPDATE jobs
            SET status = 'queued',
                lease_expires_at = NULL,
                started_at = NULL
            WHERE job_id = ?
              AND status = 'running'
            """,
            [(jid,) for jid in expired],
        )
        conn.commit()
        return len(expired)


@dataclass
class JobLeaseReaper:
    """Background job lease reaper."""

    db_path: Path | None = None
    interval_seconds: int = 30
    _thread: Optional[threading.Thread] = field(default=None, init=False)
    _stop: threading.Event = field(default_factory=threading.Event, init=False)

    def start(self) -> None:
        """Start lease reaper."""
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop lease reaper."""
        self._stop.set()

    def _run(self) -> None:
        """Internal helper for run."""
        while not self._stop.is_set():
            try:
                requeue_expired_leases(db_path=self.db_path)
            except Exception:
                pass
            self._stop.wait(timeout=max(5, int(self.interval_seconds or 30)))


LEASE_REAPER: JobLeaseReaper | None = None
_LEASE_REAPER_STARTED = False


def ensure_lease_reaper(db_path: Path | None = None) -> None:
    """Ensure lease reaper started."""
    global LEASE_REAPER
    global _LEASE_REAPER_STARTED
    if _LEASE_REAPER_STARTED:
        return
    try:
        if LEASE_REAPER is None:
            interval = int(os.environ.get("CONTROL_PLANE_REAPER_INTERVAL_SECONDS") or 30)
            LEASE_REAPER = JobLeaseReaper(db_path=db_path, interval_seconds=interval)
        LEASE_REAPER.start()
        _LEASE_REAPER_STARTED = True
    except Exception:
        return


def _capability_set(value: Any) -> set[str]:
    if value is None:
        return set()
    if isinstance(value, list):
        return {str(v) for v in value if v}
    if isinstance(value, dict):
        return {str(k) for k, enabled in value.items() if enabled}
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return set()
        if text.startswith("[") or text.startswith("{"):
            parsed = _json_loads(text)
            return _capability_set(parsed)
        return {part.strip() for part in text.split(",") if part.strip()}
    return set()


def _expire_terminal_sessions_conn(conn: sqlite3.Connection, *, now: datetime) -> int:
    """Mark expired terminal sessions as expired."""
    rows = conn.execute(
        """
        SELECT session_id, expires_at, status
        FROM terminal_sessions
        WHERE status IN ('pending', 'claimed', 'active')
          AND expires_at IS NOT NULL
        """
    ).fetchall()
    expired: list[str] = []
    for row in rows:
        lease = _parse_iso(row["expires_at"])
        if lease and lease <= now:
            expired.append(str(row["session_id"]))
    if not expired:
        return 0
    conn.executemany(
        "UPDATE terminal_sessions SET status = 'expired' WHERE session_id = ? AND status IN ('pending', 'claimed', 'active')",
        [(sid,) for sid in expired],
    )
    return len(expired)


def create_terminal_session(
    *,
    agent_id: str,
    operator: str,
    ttl_seconds: int = 900,
    db_path: Path | None = None,
) -> dict:
    """Create a break-glass terminal session for an agent."""
    agent_id = str(agent_id or "").strip()
    operator = str(operator or "").strip()
    if not agent_id:
        raise ValueError("agent_id is required")
    if not operator:
        raise ValueError("operator is required")

    ttl = max(60, min(3600, int(ttl_seconds or 900)))
    now_dt = _now()
    now = now_dt.isoformat()
    expires_at = (_now() + timedelta(seconds=ttl)).isoformat()
    session_id = secrets.token_hex(16)

    with open_db(db_path) as conn:
        conn.execute("BEGIN IMMEDIATE")
        _expire_terminal_sessions_conn(conn, now=now_dt)
        agent = conn.execute(
            "SELECT agent_id, capabilities_json FROM agents WHERE agent_id = ?",
            (agent_id,),
        ).fetchone()
        if not agent:
            raise KeyError("Unknown agent_id")
        caps = _capability_set(_json_loads(agent["capabilities_json"]))
        if "break_glass.enabled" not in caps:
            raise PermissionError("Agent BREAK_GLASS_ENABLED required for terminal sessions.")

        active = conn.execute(
            """
            SELECT session_id
            FROM terminal_sessions
            WHERE agent_id = ?
              AND status IN ('pending', 'claimed', 'active')
            ORDER BY started_at DESC
            LIMIT 1
            """,
            (agent_id,),
        ).fetchone()
        if active:
            raise ValueError("Terminal session already active for agent.")

        conn.execute(
            """
            INSERT INTO terminal_sessions (session_id, agent_id, operator, started_at, expires_at, status)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (session_id, agent_id, operator, now, expires_at, "pending"),
        )
        conn.commit()
        return {
            "session_id": session_id,
            "agent_id": agent_id,
            "operator": operator,
            "started_at": now,
            "expires_at": expires_at,
            "status": "pending",
        }


def get_terminal_session(session_id: str, *, db_path: Path | None = None) -> dict:
    """Get a terminal session record."""
    sid = str(session_id or "").strip()
    if not sid:
        raise ValueError("session_id is required")
    with open_db(db_path) as conn:
        row = conn.execute(
            "SELECT session_id, agent_id, operator, started_at, expires_at, status FROM terminal_sessions WHERE session_id = ?",
            (sid,),
        ).fetchone()
        if not row:
            raise KeyError("Unknown session_id")
        return {
            "session_id": row["session_id"],
            "agent_id": row["agent_id"],
            "operator": row["operator"],
            "started_at": row["started_at"],
            "expires_at": row["expires_at"],
            "status": row["status"],
        }


def set_terminal_session_status(session_id: str, status: str, *, db_path: Path | None = None) -> dict:
    """Update terminal session status."""
    sid = str(session_id or "").strip()
    status = str(status or "").strip().lower()
    if not sid:
        raise ValueError("session_id is required")
    if status not in ("pending", "claimed", "active", "closed", "expired"):
        raise ValueError("Invalid terminal session status")
    with open_db(db_path) as conn:
        conn.execute("BEGIN IMMEDIATE")
        cur = conn.execute(
            "UPDATE terminal_sessions SET status = ? WHERE session_id = ?",
            (status, sid),
        )
        if cur.rowcount != 1:
            raise KeyError("Unknown session_id")
        conn.commit()
    return {"session_id": sid, "status": status}


def lease_next_terminal_session(agent_id: str, *, db_path: Path | None = None) -> dict | None:
    """Lease the next pending terminal session for an agent."""
    agent_id = str(agent_id or "").strip()
    if not agent_id:
        raise ValueError("agent_id is required")
    now_dt = _now()
    with open_db(db_path) as conn:
        conn.execute("BEGIN IMMEDIATE")
        _expire_terminal_sessions_conn(conn, now=now_dt)
        row = conn.execute(
            """
            SELECT session_id
            FROM terminal_sessions
            WHERE agent_id = ?
              AND status = 'pending'
            ORDER BY started_at ASC
            LIMIT 1
            """,
            (agent_id,),
        ).fetchone()
        if not row:
            conn.commit()
            return None
        sid = str(row["session_id"])
        cur = conn.execute(
            "UPDATE terminal_sessions SET status = 'claimed' WHERE session_id = ? AND status = 'pending'",
            (sid,),
        )
        if cur.rowcount != 1:
            conn.commit()
            return None
        session = conn.execute(
            "SELECT session_id, agent_id, operator, started_at, expires_at, status FROM terminal_sessions WHERE session_id = ?",
            (sid,),
        ).fetchone()
        conn.commit()
        if not session:
            return None
        return {
            "session_id": session["session_id"],
            "agent_id": session["agent_id"],
            "operator": session["operator"],
            "started_at": session["started_at"],
            "expires_at": session["expires_at"],
            "status": session["status"],
        }


def append_terminal_audit(
    session_id: str,
    *,
    kind: str,
    payload: Any | None = None,
    db_path: Path | None = None,
) -> dict:
    """Append a terminal audit entry."""
    sid = str(session_id or "").strip()
    kind = str(kind or "").strip().lower()
    if not sid:
        raise ValueError("session_id is required")
    if not kind:
        raise ValueError("kind is required")
    now = _now_iso()
    with open_db(db_path) as conn:
        conn.execute("BEGIN IMMEDIATE")
        existing = conn.execute("SELECT session_id FROM terminal_sessions WHERE session_id = ?", (sid,)).fetchone()
        if not existing:
            raise KeyError("Unknown session_id")
        conn.execute(
            "INSERT INTO terminal_audit (session_id, timestamp, kind, payload_json) VALUES (?, ?, ?, ?)",
            (sid, now, kind, _json_dumps(payload)),
        )
        conn.commit()
        return {"session_id": sid, "timestamp": now, "kind": kind}


def list_terminal_audit(session_id: str, *, limit: int = 500, db_path: Path | None = None) -> dict:
    """List terminal audit entries for a session."""
    sid = str(session_id or "").strip()
    if not sid:
        raise ValueError("session_id is required")
    limit_val = max(1, min(5000, int(limit or 500)))
    with open_db(db_path) as conn:
        rows = conn.execute(
            """
            SELECT audit_id, timestamp, kind, payload_json
            FROM terminal_audit
            WHERE session_id = ?
            ORDER BY audit_id ASC
            LIMIT ?
            """,
            (sid, limit_val),
        ).fetchall()
        items = []
        for row in rows:
            items.append(
                {
                    "audit_id": row["audit_id"],
                    "timestamp": row["timestamp"],
                    "kind": row["kind"],
                    "payload": _json_loads(row["payload_json"]),
                }
            )
        return {"session_id": sid, "items": items, "count": len(items)}
