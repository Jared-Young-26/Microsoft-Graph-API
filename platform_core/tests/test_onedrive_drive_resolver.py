import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from microsoft import GraphAPIError

from platform_core.graph_error_transparency import build_graph_error_response
from platform_core.onedrive_drive_resolver import resolve_onedrive_drive_id
from platform_core.snapshot_storage import SnapshotSqlStore


class _FakeResponse:
    def __init__(self, payload):
        self._payload = payload
        self.status_code = 200

    def json(self):
        return dict(self._payload or {})


class _FakeGraph:
    def __init__(self, *, payload=None, error=None):
        self.payload = payload or {}
        self.error = error
        self.calls = []

    def get(self, path, params=None, max_attempts=None, max_budget_s=None, **kwargs):
        self.calls.append(
            {
                "path": path,
                "params": params,
                "max_attempts": max_attempts,
                "max_budget_s": max_budget_s,
            }
        )
        if self.error:
            raise self.error
        return _FakeResponse(self.payload)


class _FakeGraphRouting:
    def __init__(self, routes):
        self.routes = dict(routes or {})
        self.calls = []

    def get(self, path, params=None, max_attempts=None, max_budget_s=None, **kwargs):
        self.calls.append({"path": path, "params": params, "max_attempts": max_attempts, "max_budget_s": max_budget_s})
        handler = None
        for prefix, value in self.routes.items():
            if path.startswith(prefix):
                handler = value
                break
        if handler is None:
            return _FakeResponse({})
        if isinstance(handler, Exception):
            raise handler
        if callable(handler):
            result = handler(path, params)
            if isinstance(result, Exception):
                raise result
            return _FakeResponse(result)
        return _FakeResponse(handler)


class TestOneDriveDriveResolver(unittest.TestCase):
    def _store(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        return SnapshotSqlStore(Path(tmp.name) / "snapshots.sqlite")

    def test_cache_hit_returns_without_graph_call(self):
        store = self._store()
        tenant_id = "tenant-1"
        upn = "alice@contoso.com"
        now = datetime.now(timezone.utc)
        store.upsert_onedrive_drive_cache(
            tenant_id=tenant_id,
            user_upn=upn,
            drive_id="DRIVE123",
            web_url="https://contoso-my.sharepoint.com/personal/alice",
            last_verified_at=now.isoformat(),
            expires_at=(now + timedelta(days=10)).isoformat(),
        )
        graph = _FakeGraph(payload={"id": "LIVE", "webUrl": "https://example.com"})
        result = resolve_onedrive_drive_id(
            store=store,
            graph=graph,
            tenant_id=tenant_id,
            user_upn_or_id=upn,
        )
        self.assertTrue(result.get("cached"))
        self.assertFalse(result.get("cache_fallback"))
        self.assertEqual(result.get("id"), "DRIVE123")
        self.assertEqual(len(graph.calls), 0)
        self.assertEqual(result.get("source"), "cache")

    def test_cache_miss_calls_graph_and_stores(self):
        store = self._store()
        tenant_id = "tenant-1"
        upn = "alice@contoso.com"
        routes = {
            "/users/alice%40contoso.com": {"id": "USER1", "userPrincipalName": upn},
            "/users/USER1/drive": {"id": "DRIVE999", "webUrl": "https://example.com", "driveType": "personal"},
        }
        graph = _FakeGraphRouting(routes)
        result = resolve_onedrive_drive_id(
            store=store,
            graph=graph,
            tenant_id=tenant_id,
            user_upn_or_id=upn,
            ttl_days=14,
            max_attempts=3,
            max_budget_s=45,
        )
        self.assertFalse(result.get("cached"))
        self.assertEqual(result.get("id"), "DRIVE999")
        self.assertEqual(len(graph.calls), 2)
        self.assertEqual(graph.calls[0]["path"], "/users/alice%40contoso.com")
        self.assertEqual(graph.calls[1]["path"], "/users/USER1/drive")
        self.assertEqual(result.get("source"), "primary")

        cached = store.get_onedrive_drive_cache(tenant_id=tenant_id, user_upn=upn)
        self.assertIsNotNone(cached)
        self.assertEqual(cached.get("drive_id"), "DRIVE999")
        self.assertEqual(cached.get("user_object_id"), "USER1")

    def test_503_retries_exhausted_keeps_failure_source_graph(self):
        store = self._store()
        tenant_id = "tenant-1"
        upn = "alice@contoso.com"
        error = GraphAPIError(
            "Transient Graph Error 503",
            status_code=503,
            request_id="req-1",
            response=None,
            code="UnknownError",
            retry_after=None,
            failure_origin="graph_upstream",
            method="GET",
            url="https://graph.microsoft.com/v1.0/users/x/drive",
            path="/users/x/drive",
            params={},
            request_headers={},
            response_headers={"request-id": "req-1"},
            response_body='{"error":{"code":"UnknownError","message":""}}',
            attempts=[{"attempt": i, "status": 503, "wait_ms": None} for i in range(1, 7)],
            duration_ms=45000,
            ui_request_id="ui-1",
            correlation_id="ui-1",
            error_class="transient_upstream_persistent",
            total_attempts=6,
            tenant_id=tenant_id,
            queue_wait_ms=0,
            circuit={"route_group": "onedrive.resolve_drive"},
        )
        payload = build_graph_error_response(error, service="onedrive", action="get_user_drive_id")
        self.assertEqual(payload.get("failure_source"), "graph_upstream")
        self.assertEqual(payload.get("failure_outcome"), "retry_exhausted")

    def test_404_maps_to_onedrive_not_provisioned(self):
        store = self._store()
        tenant_id = "tenant-1"
        upn = "alice@contoso.com"
        error = GraphAPIError(
            "Graph request failed (404) [itemNotFound]: Not found",
            status_code=404,
            request_id="req-404",
            response=None,
            code="itemNotFound",
            retry_after=None,
            failure_origin="graph_upstream",
            method="GET",
            url="https://graph.microsoft.com/v1.0/users/x/drive",
            path="/users/x/drive",
            params={},
            request_headers={},
            response_headers={"request-id": "req-404"},
            response_body='{"error":{"code":"itemNotFound","message":"Not found"}}',
            attempts=[{"attempt": 1, "status": 404, "wait_ms": None}],
            duration_ms=100,
            ui_request_id="ui-404",
            correlation_id="ui-404",
            error_class="unknown",
            total_attempts=1,
            tenant_id=tenant_id,
            queue_wait_ms=0,
        )
        routes = {
            "/users/alice%40contoso.com": {"id": "USER1", "userPrincipalName": upn},
            "/users/USER1/drive": error,
        }
        graph = _FakeGraphRouting(routes)
        with self.assertRaises(GraphAPIError) as ctx:
            resolve_onedrive_drive_id(store=store, graph=graph, tenant_id=tenant_id, user_upn_or_id=upn)
        self.assertEqual(getattr(ctx.exception, "error_class", None), "onedrive_not_provisioned")

    def test_circuit_open_uses_cache_fallback(self):
        store = self._store()
        tenant_id = "tenant-1"
        upn = "alice@contoso.com"
        now = datetime.now(timezone.utc)
        store.upsert_onedrive_drive_cache(
            tenant_id=tenant_id,
            user_upn=upn,
            drive_id="DRIVE123",
            web_url="https://example.com",
            last_verified_at=(now - timedelta(days=15)).isoformat(),
            expires_at=(now - timedelta(days=1)).isoformat(),  # expired
        )
        error = GraphAPIError(
            "Circuit breaker open for route group 'onedrive.resolve_drive'.",
            status_code=503,
            request_id=None,
            response=None,
            retry_after=30,
            failure_origin="dashboard_guardrail",
            error_class="circuit_open",
            circuit={"route_group": "onedrive.resolve_drive", "remaining_seconds": 30, "state": "open"},
        )
        routes = {
            "/users/alice%40contoso.com": {"id": "USER1", "userPrincipalName": upn},
            "/users/USER1/drive": error,
        }
        graph = _FakeGraphRouting(routes)
        result = resolve_onedrive_drive_id(
            store=store,
            graph=graph,
            tenant_id=tenant_id,
            user_upn_or_id=upn,
            force_live=True,
        )
        self.assertTrue(result.get("cached"))
        self.assertTrue(result.get("cache_fallback"))
        self.assertEqual(result.get("id"), "DRIVE123")
        self.assertIn("cached", (result.get("warning") or "").lower())
        self.assertIsInstance(result.get("circuit"), dict)
        self.assertEqual(result.get("source"), "cache")

    def test_step_b_503_no_cache_returns_pending_and_enqueues(self):
        store = self._store()
        tenant_id = "tenant-1"
        upn = "alice@contoso.com"
        error = GraphAPIError(
            "Transient Graph Error 503",
            status_code=503,
            request_id="req-503",
            response=None,
            code="UnknownError",
            retry_after=None,
            failure_origin="graph_upstream",
            error_class="transient_upstream_persistent",
            attempts=[{"attempt": 1, "status": 503, "wait_ms": 4000}],
            tenant_id=tenant_id,
        )
        routes = {
            "/users/alice%40contoso.com": {"id": "USER1", "userPrincipalName": upn},
            "/users/USER1/drive": error,
        }
        graph = _FakeGraphRouting(routes)
        result = resolve_onedrive_drive_id(
            store=store,
            graph=graph,
            tenant_id=tenant_id,
            user_upn_or_id=upn,
            force_live=True,
        )
        self.assertEqual(result.get("status"), "pending")
        self.assertIsInstance(result.get("pending"), dict)
        self.assertTrue(result.get("pending", {}).get("enqueued"))
        self.assertTrue(result.get("pending", {}).get("next_run_at"))
        self.assertEqual(result.get("pending", {}).get("max_attempts"), 10)
        pending_stats = store.get_onedrive_drive_pending_stats(tenant_id=tenant_id)
        self.assertEqual(pending_stats.get("total"), 1)

    def test_step_b_circuit_open_no_cache_returns_pending_and_enqueues(self):
        store = self._store()
        tenant_id = "tenant-1"
        upn = "alice@contoso.com"
        circuit = GraphAPIError(
            "Circuit breaker open for route group 'onedrive.resolve_drive'.",
            status_code=503,
            request_id=None,
            response=None,
            retry_after=30,
            failure_origin="dashboard_guardrail",
            error_class="circuit_open",
            circuit={"route_group": "onedrive.resolve_drive", "remaining_seconds": 30, "state": "open"},
        )
        routes = {
            "/users/alice%40contoso.com": {"id": "USER1", "userPrincipalName": upn},
            "/users/USER1/drive": circuit,
        }
        graph = _FakeGraphRouting(routes)
        result = resolve_onedrive_drive_id(store=store, graph=graph, tenant_id=tenant_id, user_upn_or_id=upn, force_live=True)
        self.assertEqual(result.get("status"), "pending")
        self.assertTrue(result.get("pending", {}).get("next_run_at"))
        pending_stats = store.get_onedrive_drive_pending_stats(tenant_id=tenant_id)
        self.assertEqual(pending_stats.get("total"), 1)

    def test_stale_cache_too_old_not_used(self):
        store = self._store()
        tenant_id = "tenant-1"
        upn = "alice@contoso.com"
        now = datetime.now(timezone.utc)
        store.upsert_onedrive_drive_cache(
            tenant_id=tenant_id,
            user_upn=upn,
            drive_id="DRIVE-OLD",
            web_url="https://example.com",
            last_verified_at=(now - timedelta(days=90)).isoformat(),
            expires_at=(now - timedelta(days=60)).isoformat(),  # expired too long ago
        )
        circuit = GraphAPIError(
            "Circuit breaker open for route group 'onedrive.resolve_drive'.",
            status_code=503,
            request_id=None,
            response=None,
            retry_after=30,
            failure_origin="dashboard_guardrail",
            error_class="circuit_open",
            circuit={"route_group": "onedrive.resolve_drive", "remaining_seconds": 30, "state": "open"},
        )
        routes = {
            "/users/alice%40contoso.com": {"id": "USER1", "userPrincipalName": upn},
            "/users/USER1/drive": circuit,
        }
        graph = _FakeGraphRouting(routes)
        result = resolve_onedrive_drive_id(
            store=store,
            graph=graph,
            tenant_id=tenant_id,
            user_upn_or_id=upn,
            force_live=True,
            stale_window_days=30,
        )
        self.assertEqual(result.get("status"), "pending")
        self.assertFalse(result.get("cached"))
