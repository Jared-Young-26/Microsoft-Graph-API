import os
import unittest
from unittest import mock

from fastapi.testclient import TestClient

from admin_gui.backend.operator_auth import (
    AGENT_ROUTE,
    EXEMPT_ROUTE,
    OPERATOR_TOKEN_ENV,
    PROTECTED_ROUTE,
    classify_operator_route,
    require_operator_auth,
    OperatorAuthError,
)


VALID_OPERATOR_TOKEN = "operator-secret"


class TestOperatorAuthHelper(unittest.TestCase):
    def test_classifies_protected_agent_and_exempt_routes(self):
        self.assertEqual(classify_operator_route("POST", "/api/task"), PROTECTED_ROUTE)
        self.assertEqual(classify_operator_route("POST", "/api/agents/a1/job-result"), AGENT_ROUTE)
        self.assertEqual(classify_operator_route("POST", "/api/signals/visual"), EXEMPT_ROUTE)
        self.assertEqual(classify_operator_route("GET", "/api/jobs"), EXEMPT_ROUTE)

    def test_missing_operator_env_fails_closed(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop(OPERATOR_TOKEN_ENV, None)
            with self.assertRaises(OperatorAuthError) as ctx:
                require_operator_auth({})
        self.assertEqual(ctx.exception.status_code, 503)
        self.assertEqual(ctx.exception.error_code, "operator_token_not_configured")


class OperatorAuthTransportAssertions:
    client = None
    module_name = ""

    def request(self, method: str, path: str, **kwargs):
        raise NotImplementedError

    def close_response(self, response) -> None:
        close = getattr(response, "close", None)
        if callable(close):
            close()

    def response_json(self, response):
        try:
            if hasattr(response, "get_json"):
                return response.get_json()
            return response.json()
        finally:
            self.close_response(response)

    @mock.patch.dict(os.environ, {OPERATOR_TOKEN_ENV: VALID_OPERATOR_TOKEN}, clear=False)
    def test_protected_task_route_requires_token(self):
        response = self.request("POST", "/api/task", json={})
        payload = self.response_json(response)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(payload["error_code"], "operator_token_required")

    @mock.patch.dict(os.environ, {OPERATOR_TOKEN_ENV: VALID_OPERATOR_TOKEN}, clear=False)
    def test_protected_task_route_rejects_invalid_token(self):
        response = self.request("POST", "/api/task", json={}, headers={"X-Operator-Token": "wrong"})
        payload = self.response_json(response)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(payload["error_code"], "operator_token_invalid")

    @mock.patch.dict(os.environ, {OPERATOR_TOKEN_ENV: VALID_OPERATOR_TOKEN}, clear=False)
    def test_protected_task_route_allows_valid_token(self):
        with mock.patch(f"{self.module_name}.dispatch_task", return_value={"status": "ok"}) as dispatch_task:
            response = self.request(
                "POST",
                "/api/task",
                json={"service": "system", "action": "tenant_info", "params": {}},
                headers={"X-Operator-Token": VALID_OPERATOR_TOKEN},
            )
        payload = self.response_json(response)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(payload["ok"])
        dispatch_task.assert_called_once()

    @mock.patch.dict(os.environ, {OPERATOR_TOKEN_ENV: VALID_OPERATOR_TOKEN}, clear=False)
    def test_agent_register_route_remains_exempt(self):
        with mock.patch(f"{self.module_name}.control_plane.register_agent", return_value={"agent_id": "agent-1"}):
            response = self.request("POST", "/api/agents/register", json={"name": "agent"})
        payload = self.response_json(response)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["agent_id"], "agent-1")

    @mock.patch.dict(os.environ, {OPERATOR_TOKEN_ENV: VALID_OPERATOR_TOKEN}, clear=False)
    def test_machine_visual_ingest_route_remains_exempt(self):
        with mock.patch(
            f"{self.module_name}._ingest_vision_u_eye_visual_signal",
            return_value={"ok": True, "accepted": 1},
        ):
            response = self.request("POST", "/api/signals/visual", json={"endpoint_id": "ep-1"})
        payload = self.response_json(response)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(payload["ok"])

    @mock.patch.dict(os.environ, {OPERATOR_TOKEN_ENV: VALID_OPERATOR_TOKEN}, clear=False)
    def test_agent_terminal_session_lease_stays_on_agent_auth(self):
        with mock.patch(f"{self.module_name}.control_plane.authenticate_agent", return_value=True) as authenticate_agent:
            with mock.patch(f"{self.module_name}.control_plane.lease_next_terminal_session", return_value=None):
                response = self.request(
                    "GET",
                    "/api/terminal/agent-1/next-session",
                    headers={"Authorization": "Bearer agent-token"},
                )
        self.close_response(response)
        self.assertEqual(response.status_code, 204)
        authenticate_agent.assert_called_once_with("agent-1", "agent-token")

    @mock.patch.dict(os.environ, {OPERATOR_TOKEN_ENV: VALID_OPERATOR_TOKEN}, clear=False)
    def test_terminal_start_still_requires_interactive_scope_after_operator_auth(self):
        response = self.request(
            "POST",
            "/api/terminal/agent-1/start",
            json={},
            headers={"X-Operator-Token": VALID_OPERATOR_TOKEN},
        )
        payload = self.response_json(response)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(payload.get("error") or payload.get("detail"), "interactive_scope=true required")


class TestFlaskOperatorAuth(OperatorAuthTransportAssertions, unittest.TestCase):
    module_name = "admin_gui.backend.flask_app"

    @classmethod
    def setUpClass(cls):
        from admin_gui.backend import flask_app

        cls.client = flask_app.app.test_client()

    def request(self, method: str, path: str, **kwargs):
        return self.client.open(path, method=method, **kwargs)


class TestFastAPIOperatorAuth(OperatorAuthTransportAssertions, unittest.TestCase):
    module_name = "admin_gui.backend.fastapi_app"

    @classmethod
    def setUpClass(cls):
        import fastapi.dependencies.utils as fastapi_dependency_utils

        cls._multipart_patch = mock.patch.object(
            fastapi_dependency_utils,
            "ensure_multipart_is_installed",
            return_value=None,
        )
        cls._multipart_patch.start()
        from admin_gui.backend import fastapi_app

        cls.client = TestClient(fastapi_app.app)

    @classmethod
    def tearDownClass(cls):
        cls.client.close()
        cls._multipart_patch.stop()

    def request(self, method: str, path: str, **kwargs):
        return self.client.request(method, path, **kwargs)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
