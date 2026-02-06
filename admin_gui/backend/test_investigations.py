import tempfile
import unittest
from pathlib import Path


class TestInvestigationsMVI(unittest.TestCase):
    """Validate minimum viable Investigation storage + timeline events."""

    def test_create_list_get_and_add_note(self):
        """Create an investigation, list it, fetch it, and append a note event."""

        from admin_gui.backend import core
        from platform_core.snapshot_storage import SnapshotSqlStore

        original_state = core.STATE
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                db_path = Path(tmpdir) / "snapshots.sqlite"
                state = core.BackendState()
                state.snapshot_store = SnapshotSqlStore(db_path)
                state.entity_resolver = core.EntityResolver(state.snapshot_store)
                state.snapshot_engine = core.SnapshotEngine(state.snapshot_store, state.entity_resolver)
                core.STATE = state

                created = core._create_investigation({"title": "Test investigation", "tags": ["mvi"]})
                self.assertIsInstance(created, dict)
                inv_id = created.get("investigation_id")
                self.assertTrue(inv_id)

                listed = core._list_investigations(limit=10)
                self.assertTrue(any(item.get("investigation_id") == inv_id for item in listed))

                detail = core._get_investigation(inv_id)
                self.assertEqual(detail.get("investigation_id"), inv_id)
                self.assertEqual(detail.get("title"), "Test investigation")
                self.assertIsInstance(detail.get("events"), list)

                note_evt = core._add_investigation_note(inv_id, {"note": "hello"})
                self.assertEqual(note_evt.get("kind"), "note")

                detail2 = core._get_investigation(inv_id)
                events = detail2.get("events") or []
                self.assertEqual(len(events), 1)
                self.assertEqual(events[0].get("kind"), "note")
                self.assertEqual((events[0].get("data") or {}).get("note"), "hello")

                # Manual event append (Chunk 1.2)
                evt = core._add_investigation_event(
                    inv_id,
                    {
                        "kind": "action_run",
                        "summary": "Attached output",
                        "data": {"service": "entra", "token": "super-secret"},
                    },
                )
                self.assertEqual(evt.get("kind"), "action_run")
                detail3 = core._get_investigation(inv_id)
                events3 = detail3.get("events") or []
                self.assertEqual(len(events3), 2)
                self.assertEqual(events3[1].get("kind"), "action_run")
                stored_data = events3[1].get("data") or {}
                # The backend must never persist secrets; sanitize_payload should redact this field.
                self.assertEqual(stored_data.get("token"), "[redacted]")

                # Context storage (Chunk 0.2)
                ctx_update = core._update_investigation_context(inv_id, {"context": {"user_upn": "alice@contoso.com"}})
                self.assertEqual(ctx_update.get("investigation_id"), inv_id)
                self.assertEqual((ctx_update.get("context") or {}).get("user_upn"), "alice@contoso.com")

                ctx_get = core._get_investigation_context(inv_id)
                self.assertEqual(ctx_get.get("investigation_id"), inv_id)
                self.assertEqual((ctx_get.get("context") or {}).get("user_upn"), "alice@contoso.com")
        finally:
            core.STATE = original_state


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
