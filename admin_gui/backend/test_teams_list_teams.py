import unittest


class _StubResponse:
    def __init__(self, body):
        self._body = body

    def json(self):  # pragma: no cover - trivial
        return self._body


class _StubGraph:
    def __init__(self):
        self.calls = []

    def get(self, url, **kwargs):  # pragma: no cover - stub
        self.calls.append((url, kwargs))
        return _StubResponse({"value": [{"id": "team-1", "displayName": "Team One"}]})


class TestTeamsListTeams(unittest.TestCase):
    """Test Teams list teams (Graph)."""

    def test_list_teams_uses_group_filter(self):
        """Ensure list_teams hits /groups with the Teams provisioning filter."""
        from teams import TeamsClient

        graph = _StubGraph()
        client = TeamsClient(graph)

        result = client.list_teams(top=1, select="id,displayName")
        self.assertIsInstance(result, list)
        self.assertEqual(result[0]["id"], "team-1")
        self.assertEqual(len(graph.calls), 1)
        url, kwargs = graph.calls[0]
        self.assertEqual(url, "/groups")
        params = kwargs.get("params") or {}
        self.assertEqual(params.get("$top"), 1)
        self.assertIn("resourceProvisioningOptions", params.get("$filter", ""))
        self.assertEqual(params.get("$select"), "id,displayName")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()

