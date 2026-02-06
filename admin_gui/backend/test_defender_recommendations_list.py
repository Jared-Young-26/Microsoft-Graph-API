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


class TestDefenderRecommendationsList(unittest.TestCase):
    """Test Defender for Cloud recommendations list."""

    def test_recommendations_list_returns_rows_with_severity_and_category(self):
        """Run test recommendations list returns at least one normalized row."""
        from defender import DefenderClient

        client = DefenderClient(_StubGraphSession(), subscription_id="sub-1")

        def fake_request(method, url, params=None, headers=None, timeout=None):  # pragma: no cover - stub
            body = {
                "value": [
                    {
                        "id": "/subscriptions/sub-1/providers/Microsoft.Security/assessments/abc",
                        "name": "abc",
                        "type": "Microsoft.Security/assessments",
                        "properties": {
                            "displayName": "Enable MFA for admin accounts",
                            "status": {"code": "Unhealthy"},
                            "metadata": {"severity": "High", "categories": ["Identity"]},
                        },
                    }
                ]
            }
            return _StubResponse(200, body, headers={"x-ms-request-id": "req-2"})

        client._session.request = fake_request  # type: ignore[attr-defined]

        result = client.recommendations_list(max_items=10)
        self.assertEqual(result.get("subscription_id"), "sub-1")
        self.assertEqual(result.get("count"), 1)
        self.assertIsInstance(result.get("value"), list)
        row = result["value"][0]
        self.assertEqual(row.get("displayName"), "Enable MFA for admin accounts")
        self.assertEqual(row.get("severity"), "High")
        self.assertEqual(row.get("category"), "Identity")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()

