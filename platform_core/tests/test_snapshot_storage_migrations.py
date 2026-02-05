import sqlite3
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from platform_core.snapshot_storage import SnapshotSqlStore


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


class TestSnapshotStorageMigrations(unittest.TestCase):
    def _db_path(self) -> Path:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        return Path(tmp.name) / "snapshots.sqlite"

    def _create_legacy_onedrive_cache(self, path: Path) -> None:
        # Legacy schema: missing user_object_id, drive_type, source.
        with sqlite3.connect(str(path)) as conn:
            conn.execute(
                """
                CREATE TABLE onedrive_drive_cache (
                    tenant_id TEXT NOT NULL,
                    user_upn TEXT NOT NULL,
                    drive_id TEXT NOT NULL,
                    web_url TEXT,
                    last_verified_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                INSERT INTO onedrive_drive_cache
                (tenant_id, user_upn, drive_id, web_url, last_verified_at, expires_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    "tenant-1",
                    "alice@contoso.com",
                    "DRIVE1",
                    "https://example.com",
                    _now_iso(),
                    (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
                ),
            )
            conn.commit()

    def _create_legacy_onedrive_pending(self, path: Path) -> None:
        # Legacy schema: missing paused/last_error_class/last_error_at, next_run_at may be NULL.
        with sqlite3.connect(str(path)) as conn:
            conn.execute(
                """
                CREATE TABLE onedrive_drive_pending (
                    tenant_id TEXT NOT NULL,
                    user_upn TEXT NOT NULL,
                    attempts INTEGER NOT NULL DEFAULT 0,
                    next_run_at TEXT,
                    last_error TEXT,
                    PRIMARY KEY (tenant_id, user_upn)
                )
                """
            )
            conn.execute(
                """
                INSERT INTO onedrive_drive_pending
                (tenant_id, user_upn, attempts, next_run_at, last_error)
                VALUES (?, ?, ?, ?, ?)
                """,
                ("tenant-1", "alice@contoso.com", 10, None, "Transient Graph Error 503"),
            )
            conn.commit()

    def test_migrate_onedrive_cache_adds_user_object_id(self):
        path = self._db_path()
        self._create_legacy_onedrive_cache(path)

        store = SnapshotSqlStore(path)

        # Trigger init + migrations (legacy schema would raise without migration).
        cached = store.get_onedrive_drive_cache(tenant_id="tenant-1", user_upn="alice@contoso.com", allow_expired=True)
        self.assertIsNotNone(cached)
        self.assertEqual(cached.get("drive_id"), "DRIVE1")

        # Warmup-style writes should also work post-migration.
        store.upsert_onedrive_drive_cache(
            tenant_id="tenant-1",
            user_upn="alice@contoso.com",
            user_object_id="00000000-0000-0000-0000-000000000000",
            drive_id="DRIVE1",
            web_url="https://example.com",
            drive_type="personal",
            last_verified_at=_now_iso(),
            expires_at=(datetime.now(timezone.utc) + timedelta(days=14)).isoformat(),
            source="primary",
        )

        with sqlite3.connect(str(path)) as conn:
            cols = {row[1] for row in conn.execute("PRAGMA table_info(onedrive_drive_cache)").fetchall()}
            self.assertIn("user_object_id", cols)
            self.assertIn("drive_type", cols)
            self.assertIn("source", cols)
            row = conn.execute(
                "SELECT user_object_id, drive_type, source FROM onedrive_drive_cache WHERE tenant_id = ? AND user_upn = ?",
                ("tenant-1", "alice@contoso.com"),
            ).fetchone()
            self.assertIsNotNone(row)
            # Source should be populated for legacy rows/migrations.
            self.assertTrue(row[2] in ("primary", "fallback"))

    def test_onedrive_cache_table_created_when_missing(self):
        path = self._db_path()
        store = SnapshotSqlStore(path)

        now = datetime.now(timezone.utc)
        store.upsert_onedrive_drive_cache(
            tenant_id="tenant-1",
            user_upn="bob@contoso.com",
            drive_id="DRIVE2",
            web_url="https://example.com",
            last_verified_at=now.isoformat(),
            expires_at=(now + timedelta(days=14)).isoformat(),
            source="primary",
        )
        cached = store.get_onedrive_drive_cache(tenant_id="tenant-1", user_upn="bob@contoso.com")
        self.assertIsNotNone(cached)
        self.assertEqual(cached.get("drive_id"), "DRIVE2")

        with sqlite3.connect(str(path)) as conn:
            cols = {row[1] for row in conn.execute("PRAGMA table_info(onedrive_drive_cache)").fetchall()}
            self.assertIn("user_object_id", cols)
            self.assertIn("drive_type", cols)
            self.assertIn("source", cols)

    def test_migration_is_idempotent(self):
        path = self._db_path()
        self._create_legacy_onedrive_cache(path)

        store1 = SnapshotSqlStore(path)
        store1.get_onedrive_drive_cache(tenant_id="tenant-1", user_upn="alice@contoso.com", allow_expired=True)

        # Second instance should not crash running init/migration again.
        store2 = SnapshotSqlStore(path)
        store2.get_onedrive_drive_cache(tenant_id="tenant-1", user_upn="alice@contoso.com", allow_expired=True)

    def test_migrate_onedrive_pending_backfills_next_run_and_paused(self):
        path = self._db_path()
        self._create_legacy_onedrive_pending(path)

        store = SnapshotSqlStore(path)
        pending = store.get_onedrive_drive_pending(tenant_id="tenant-1", user_upn="alice@contoso.com")
        self.assertIsNotNone(pending)
        self.assertTrue(pending.get("next_run_at"))
        # Attempts are already at cap; migration should mark paused and schedule a future retry.
        self.assertEqual(int(pending.get("paused") or 0), 1)

        with sqlite3.connect(str(path)) as conn:
            cols = {row[1] for row in conn.execute("PRAGMA table_info(onedrive_drive_pending)").fetchall()}
            self.assertIn("paused", cols)
            self.assertIn("last_error_class", cols)
            self.assertIn("last_error_at", cols)
