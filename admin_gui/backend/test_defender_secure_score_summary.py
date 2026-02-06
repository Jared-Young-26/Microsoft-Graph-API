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


class TestDefenderSecureScoreSummary(unittest.TestCase):
    """Test Defender for Cloud secure score summary."""

    def test_secure_score_summary_returns_at_least_one_score_object(self):
        """Run test secure score summary returns at least one score object."""
        from defender import DefenderClient

        client = DefenderClient(_StubGraphSession(), subscription_id="sub-1")

        def fake_request(method, url, params=None, headers=None, timeout=None):  # pragma: no cover - stub
            body = {
                "value": [
                    {
                        "id": "/subscriptions/sub-1/providers/Microsoft.Security/secureScores/ascScore",
                        "name": "ascScore",
                        "type": "Microsoft.Security/secureScores",
                        "properties": {
                            "displayName": "Azure Secure Score",
                            "score": {"current": 42, "max": 100},
                        },
                    }
                ]
            }
            return _StubResponse(200, body, headers={"x-ms-request-id": "req-1"})

        client._session.request = fake_request  # type: ignore[attr-defined]

        result = client.secure_score_summary()
        self.assertEqual(result.get("subscription_id"), "sub-1")
        self.assertEqual(result.get("count"), 1)
        self.assertIsInstance(result.get("scores"), list)
        self.assertEqual(result["scores"][0]["name"], "ascScore")
        self.assertEqual(result["top"]["current"], 42)
        self.assertEqual(result["top"]["max"], 100)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()

