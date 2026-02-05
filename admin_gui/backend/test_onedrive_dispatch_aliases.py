import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path


class TestOneDriveDispatchAliases(unittest.TestCase):
    """Test One Drive Dispatch Aliases."""
    def test_get_user_drive_id_accepts_user_upn_or_id_without_graph_init(self):
        # Ensure dispatch_task() honors the `user_upn_or_id` alias and remains cache-first:
        # a cache hit must not require initializing Graph auth/network.
        """Run test get user drive id accepts user upn or id without graph init."""
        from admin_gui.backend import core
        from platform_core.snapshot_storage import SnapshotSqlStore

        original_state = core.STATE
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                db_path = Path(tmpdir) / "snapshots.sqlite"
                state = core.BackendState()
                state.snapshot_store = SnapshotSqlStore(db_path)
                # Re-wire resolver/engine to the temporary store so the test doesn't mutate repo DB.
                state.entity_resolver = core.EntityResolver(state.snapshot_store)
                state.snapshot_engine = core.SnapshotEngine(state.snapshot_store, state.entity_resolver)
                state.config.tenant_id = "tenant-1"
                state.config.graph_user_id = "default@contoso.com"

                # Fail the test if dispatch tries to initialize Graph for a cache hit.
                state.get_graph = lambda: (_ for _ in ()).throw(AssertionError("Graph init should not be required"))

                now = datetime.now(timezone.utc)
                expires = (now + timedelta(days=7)).isoformat()
                state.snapshot_store.upsert_onedrive_drive_cache(
                    tenant_id="tenant-1",
                    user_upn="alice@contoso.com",
                    user_object_id=None,
                    drive_id="drive-123",
                    web_url="https://example.com",
                    drive_type="business",
                    last_verified_at=now.isoformat(),
                    expires_at=expires,
                    source="primary",
                )

                core.STATE = state
                result = core.dispatch_task(
                    "onedrive",
                    "get_user_drive_id",
                    {"user_upn_or_id": "alice@contoso.com"},
                    None,
                )
                self.assertEqual(result.get("drive_id"), "drive-123")
                self.assertTrue(result.get("cached"))
                self.assertEqual(result.get("source"), "cache")
        finally:
            core.STATE = original_state


if __name__ == "__main__":  # pragma: no cover
    unittest.main()

