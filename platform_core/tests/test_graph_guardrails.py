import unittest
from contextlib import contextmanager
from unittest.mock import patch


class _FakeResponse:
    """Internal type: _ Fake Response."""
    def __init__(self, status_code=200, *, headers=None, json_data=None, text=None):
        """Initialize the instance."""
        self.status_code = int(status_code)
        self.headers = headers or {}
        self._json_data = json_data if json_data is not None else {}
        self._text = text

    @property
    def text(self):
        """Run text."""
        if self._text is not None:
            return self._text
        return ""

    def json(self):
        """Run json."""
        return self._json_data

    def raise_for_status(self):
        """Run raise for status."""
        return None


class _FakeSession:
    """Session wrapper for _ Fake operations."""
    def __init__(self, responses):
        """Initialize the instance."""
        self._responses = list(responses)
        self.calls = []

    def request(self, **kwargs):
        """Run request."""
        self.calls.append(kwargs)
        if not self._responses:
            return _FakeResponse(200, json_data={})
        return self._responses.pop(0)


class TestGraphGuardrails(unittest.TestCase):
    """Test Graph Guardrails."""
    def _make_graph(self):
        """Internal helper for make graph."""
        import microsoft
        from microsoft import GraphSession

        class _DummyMsalApp:
            """Internal type: _ Dummy Msal App."""
            def __init__(self, *args, **kwargs):
                """Initialize the instance."""
                pass

            def acquire_token_for_client(self, scopes=None):
                """Run acquire token for client."""
                return {"access_token": "token", "expires_in": 3600}

        with patch.object(microsoft.msal, "ConfidentialClientApplication", _DummyMsalApp):
            graph = GraphSession(tenant_id="t", client_id="c", client_secret="s")
        # Avoid MSAL token acquisition in tests.
        graph.token = "token"
        graph.expires_at = 10**10
        return graph

    def test_token_acquire_structured_error_wrapped_as_graph_api_error(self):
        """Run test token acquire structured error wrapped as graph api error."""
        import microsoft
        from microsoft import GraphSession, GraphAPIError
        from platform_core.graph_error_transparency import build_graph_error_response

        class _DummyMsalApp:
            """Internal type: _ Dummy Msal App."""
            def __init__(self, *args, **kwargs):
                """Initialize the instance."""
                pass

            def acquire_token_for_client(self, scopes=None):
                """Run acquire token for client."""
                return {"error": "invalid_client", "error_description": "bad secret"}

        with patch.object(microsoft.msal, "ConfidentialClientApplication", _DummyMsalApp):
            graph = GraphSession(tenant_id="t", client_id="c", client_secret="s")

        with self.assertRaises(GraphAPIError) as ctx:
            graph.get_headers()

        payload = build_graph_error_response(ctx.exception, service="system", action="graph_check")
        self.assertEqual(payload.get("failure_source"), "dashboard_config_error")
        self.assertEqual(payload.get("error_class"), "auth")
        self.assertEqual(payload.get("code"), "invalid_client")

    def test_token_acquire_exception_wrapped_as_graph_api_error(self):
        """Run test token acquire exception wrapped as graph api error."""
        import microsoft
        from microsoft import GraphSession, GraphAPIError
        from platform_core.graph_error_transparency import build_graph_error_response

        class _DummyMsalApp:
            """Internal type: _ Dummy Msal App."""
            def __init__(self, *args, **kwargs):
                """Initialize the instance."""
                pass

            def acquire_token_for_client(self, scopes=None):
                """Run acquire token for client."""
                raise RuntimeError("dns failure")

        with patch.object(microsoft.msal, "ConfidentialClientApplication", _DummyMsalApp):
            graph = GraphSession(tenant_id="t", client_id="c", client_secret="s")

        with self.assertRaises(GraphAPIError) as ctx:
            graph.get_headers()

        payload = build_graph_error_response(ctx.exception, service="system", action="graph_check")
        self.assertEqual(payload.get("failure_source"), "dashboard_http")
        self.assertEqual(payload.get("error_class"), "network")

    def test_msal_init_failure_wrapped_as_graph_api_error(self):
        """Run test msal init failure wrapped as graph api error."""
        import microsoft
        from microsoft import GraphSession, GraphAPIError
        from platform_core.graph_error_transparency import build_graph_error_response

        def _boom(*_args, **_kwargs):
            """Internal helper for boom."""
            raise RuntimeError("init failed")

        with patch.object(microsoft.msal, "ConfidentialClientApplication", _boom):
            with self.assertRaises(GraphAPIError) as ctx:
                GraphSession(tenant_id="t", client_id="c", client_secret="s")

        payload = build_graph_error_response(ctx.exception, service="system", action="graph_check")
        self.assertEqual(payload.get("failure_source"), "dashboard_http")
        self.assertEqual(payload.get("error_class"), "network")

    def test_concurrency_service_derived_from_route_group(self):
        """Run test concurrency service derived from route group."""
        import microsoft
        from microsoft import set_trace_context, reset_trace_context

        graph = self._make_graph()
        fake_session = _FakeSession([_FakeResponse(200, json_data={"ok": True})])

        graph._get_session = lambda: fake_session  # type: ignore[assignment]
        graph._reset_session = lambda: fake_session  # type: ignore[assignment]

        observed = {"service": None}

        @contextmanager
        def fake_gate(service):
            """Run fake gate."""
            observed["service"] = service
            yield 0

        token = set_trace_context({"service": None})
        try:
            with patch.object(microsoft, "_graph_concurrency_gate", fake_gate):
                graph.get("/users/example@contoso.com/drive")
        finally:
            reset_trace_context(token)

        self.assertEqual(observed["service"], "onedrive")

    def test_circuit_failure_recorded_per_attempt(self):
        """Run test circuit failure recorded per attempt."""
        import microsoft
        from microsoft import GraphAPIError, set_trace_context, reset_trace_context

        graph = self._make_graph()

        # 3 consecutive 503s should record 3 failures in the circuit window.
        fake_session = _FakeSession(
            [
                _FakeResponse(503, headers={"request-id": "a"}, text="{}"),
                _FakeResponse(503, headers={"request-id": "b"}, text="{}"),
                _FakeResponse(503, headers={"request-id": "c"}, text="{}"),
            ]
        )
        graph._get_session = lambda: fake_session  # type: ignore[assignment]
        graph._reset_session = lambda: fake_session  # type: ignore[assignment]

        microsoft._CIRCUIT_STATE.clear()

        token = set_trace_context({"service": "onedrive"})
        try:
            with patch.object(microsoft.time, "sleep", lambda *_args, **_kwargs: None), patch.object(
                microsoft.random, "random", lambda: 0.0
            ):
                with self.assertRaises(GraphAPIError):
                    graph.get("/users/example@contoso.com/drive", max_attempts=3, max_budget_s=None)
        finally:
            reset_trace_context(token)

        snapshot = microsoft._circuit_snapshot().get("onedrive.resolve_drive") or {}
        self.assertEqual(int(snapshot.get("failure_count_window") or 0), 3)

    def test_retry_budget_exhaustion_sets_failure_outcome(self):
        """Run test retry budget exhaustion sets failure outcome."""
        from microsoft import GraphAPIError, set_trace_context, reset_trace_context
        from platform_core.graph_error_transparency import build_graph_error_response

        graph = self._make_graph()

        # A tiny budget ensures budget exhaustion triggers before max_attempts is reached.
        fake_session = _FakeSession([_FakeResponse(503, headers={"request-id": "a"}, text="{}")])
        graph._get_session = lambda: fake_session  # type: ignore[assignment]
        graph._reset_session = lambda: fake_session  # type: ignore[assignment]

        token = set_trace_context({"service": "onedrive"})
        try:
            with patch("microsoft.time.sleep", lambda *_args, **_kwargs: None), patch(
                "microsoft.random.random", lambda: 0.0
            ):
                with self.assertRaises(GraphAPIError) as ctx:
                    graph.get(
                        "/users/example@contoso.com/drive",
                        max_attempts=6,
                        retry_budget_seconds=1,
                    )
        finally:
            reset_trace_context(token)

        payload = build_graph_error_response(ctx.exception, service="onedrive", action="get_user_drive_id")
        self.assertEqual(payload.get("failure_source"), "graph_upstream")
        self.assertEqual(payload.get("failure_outcome"), "retry_budget_exhausted")

    def test_paged_get_limits_and_meta(self):
        """Run test paged get limits and meta."""
        graph = self._make_graph()

        responses = [
            _FakeResponse(200, json_data={"value": [1, 2], "@odata.nextLink": "next"}),
            _FakeResponse(200, json_data={"value": [3, 4], "@odata.nextLink": None}),
        ]

        def fake_get(url, **kwargs):
            """Run fake get."""
            self.assertTrue(url)
            return responses.pop(0)

        graph.get = fake_get  # type: ignore[assignment]

        meta = graph.paged_get("/sites", max_pages=1, max_items=10, return_meta=True)
        self.assertEqual(meta.get("value"), [1, 2])
        self.assertTrue(meta.get("partial"))
        self.assertEqual(meta.get("reason"), "max_pages")


if __name__ == "__main__":
    unittest.main()
