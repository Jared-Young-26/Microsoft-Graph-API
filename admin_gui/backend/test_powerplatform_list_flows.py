import unittest


class _StubMsalApp:
    def acquire_token_for_client(self, scopes=None):  # pragma: no cover - trivial stub
        return {"access_token": "stub", "expires_in": 3600}


class _StubGraphSession:
    tenant_id = "tenant"
    app = _StubMsalApp()


class _StubResponse:
    def __init__(self, status_code, body, headers=None):
        self.status_code = status_code
        self._body = body
        self.headers = headers or {}

    @property
    def text(self):  # pragma: no cover - trivial
        import json

        return json.dumps(self._body)

    def json(self):  # pragma: no cover - trivial
        return self._body


class TestPowerPlatformListFlows(unittest.TestCase):
    """Test Power Platform list flows."""

    def test_list_flows_returns_bounded_results(self):
        """Run test list flows returns normalized flow list."""
        from powerplatform import PowerPlatformClient

        client = PowerPlatformClient(_StubGraphSession())

        def fake_request(method, url, params=None, headers=None, timeout=None):  # pragma: no cover - stub
            body = {
                "value": [
                    {
                        "id": "/providers/Microsoft.ProcessSimple/scopes/admin/environments/0000/flows/flow-1",
                        "name": "flow-1",
                        "type": "Microsoft.ProcessSimple/flows",
                        "properties": {
                            "displayName": "My first flow",
                            "state": "Started",
                            "createdTime": "2026-01-01T00:00:00Z",
                            "lastModifiedTime": "2026-01-02T00:00:00Z",
                        },
                    }
                ]
            }
            return _StubResponse(200, body, headers={"x-ms-request-id": "req-flow-1"})

        # Patch both token and request flows so the method stays deterministic.
        client._get_flow_token = lambda: "stub"  # type: ignore[method-assign]
        client._session.request = fake_request  # type: ignore[attr-defined]

        result = client.list_flows("0000", max_items=50)
        self.assertEqual(result.get("environment_id"), "0000")
        self.assertEqual(result.get("count"), 1)
        self.assertIsInstance(result.get("value"), list)
        flow = result["value"][0]
        self.assertEqual(flow.get("displayName"), "My first flow")
        self.assertEqual(flow.get("name"), "flow-1")
        self.assertEqual(flow.get("status"), "Started")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()

