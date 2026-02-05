import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from microsoft import GraphAPIError

from platform_core.sharepoint_sites_resolver import list_sharepoint_sites_cached
from platform_core.snapshot_storage import SnapshotSqlStore


class _FakeGraph:
    def __init__(self, *, payload=None, error=None):
        self.payload = payload or {"value": []}
        self.error = error
        self.calls = []

    def paged_get(
        self,
        url,
        *,
        params=None,
        max_pages=None,
        max_items=None,
        return_meta=None,
        retry_budget_seconds=None,
        max_attempts=None,
        **kwargs,
    ):
        self.calls.append(
            {
                "url": url,
                "params": params,
                "max_pages": max_pages,
                "max_items": max_items,
                "return_meta": return_meta,
                "retry_budget_seconds": retry_budget_seconds,
                "max_attempts": max_attempts,
            }
        )
        if self.error:
            raise self.error
        return dict(self.payload)


class TestSharePointSitesResolver(unittest.TestCase):
    def _store(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        return SnapshotSqlStore(Path(tmp.name) / "snapshots.sqlite")

    def test_cache_hit_returns_without_graph_call(self):
        store = self._store()
        tenant_id = "tenant-1"
        term = "*"
        now = datetime.now(timezone.utc)
        store.upsert_sharepoint_sites_cache(
            tenant_id=tenant_id,
            search_term=term,
            sites=[{"id": "site-1", "name": "Root"}],
            last_verified_at=now.isoformat(),
            expires_at=(now + timedelta(hours=1)).isoformat(),
        )
        graph = _FakeGraph(payload={"value": [{"id": "site-live"}]})
        result = list_sharepoint_sites_cached(store=store, graph=graph, tenant_id=tenant_id, search_term=term)
        self.assertTrue(result.get("cached"))
        self.assertEqual(result.get("value")[0]["id"], "site-1")
        self.assertEqual(len(graph.calls), 0)

    def test_cache_miss_calls_graph_and_stores(self):
        store = self._store()
        tenant_id = "tenant-1"
        term = "contoso"
        graph = _FakeGraph(payload={"value": [{"id": "site-1"}], "partial": False})
        result = list_sharepoint_sites_cached(
            store=store,
            graph=graph,
            tenant_id=tenant_id,
            search_term=term,
            ttl_seconds=3600,
            max_pages=2,
            max_items=10,
            max_budget_s=30,
            max_attempts=4,
        )
        self.assertFalse(result.get("cached"))
        self.assertEqual(len(graph.calls), 1)
        self.assertEqual(graph.calls[0]["url"], "/sites")
        self.assertEqual(graph.calls[0]["params"], {"search": term})
        cached = store.get_sharepoint_sites_cache(tenant_id=tenant_id, search_term=term)
        self.assertIsNotNone(cached)
        self.assertEqual((cached or {}).get("sites")[0]["id"], "site-1")

    def test_503_uses_stale_cache_fallback(self):
        store = self._store()
        tenant_id = "tenant-1"
        term = "*"
        now = datetime.now(timezone.utc)
        store.upsert_sharepoint_sites_cache(
            tenant_id=tenant_id,
            search_term=term,
            sites=[{"id": "site-1"}],
            last_verified_at=(now - timedelta(hours=2)).isoformat(),
            expires_at=(now - timedelta(hours=1)).isoformat(),  # expired
        )
        error = GraphAPIError(
            "Transient Graph Error 503",
            status_code=503,
            request_id="req-1",
            response=None,
            code="UnknownError",
            retry_after=None,
            failure_origin="graph_upstream",
            method="GET",
            url="https://graph.microsoft.com/v1.0/sites?search=*",
            path="/sites",
            params={"search": "*"},
            request_headers={},
            response_headers={"request-id": "req-1"},
            response_body='{"error":{"code":"UnknownError","message":""}}',
            attempts=[{"attempt": 1, "status": 503, "wait_ms": None}],
            duration_ms=1000,
            total_attempts=4,
            tenant_id=tenant_id,
            queue_wait_ms=0,
        )
        graph = _FakeGraph(error=error)
        result = list_sharepoint_sites_cached(store=store, graph=graph, tenant_id=tenant_id, search_term=term, force_live=True)
        self.assertTrue(result.get("cached"))
        self.assertTrue(result.get("cache_fallback"))
        self.assertEqual(result.get("value")[0]["id"], "site-1")
        self.assertIsInstance(result.get("live_error"), dict)


if __name__ == "__main__":
    unittest.main()

