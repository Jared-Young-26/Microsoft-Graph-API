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


class TestPowerPlatformListEnvironments(unittest.TestCase):
    """Test Power Platform list environments."""

    def test_list_environments_returns_display_name_and_id(self):
        """Run test list environments returns normalized environments."""
        from powerplatform import PowerPlatformClient

        client = PowerPlatformClient(_StubGraphSession())

        def fake_request(method, url, params=None, headers=None, timeout=None):  # pragma: no cover - stub
            body = {
                "value": [
                    {
                        "id": "/providers/Microsoft.BusinessAppPlatform/scopes/admin/environments/0000",
                        "name": "0000",
                        "type": "Microsoft.BusinessAppPlatform/environments",
                        "properties": {
                            "displayName": "Contoso (Default)",
                            "location": "unitedstates",
                            "environmentType": "Production",
                        },
                    }
                ]
            }
            return _StubResponse(200, body, headers={"x-ms-request-id": "req-pp-1"})

        client._session.request = fake_request  # type: ignore[attr-defined]

        result = client.list_environments(max_items=10)
        self.assertEqual(result.get("count"), 1)
        self.assertIsInstance(result.get("value"), list)
        env = result["value"][0]
        self.assertEqual(env.get("displayName"), "Contoso (Default)")
        self.assertEqual(env.get("name"), "0000")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()

