import unittest
import json

import requests

from microsoft import GraphAPIError
from platform_core.graph_error_transparency import build_graph_error_response


def _response(status: int, body: str, headers: dict | None = None) -> requests.Response:
    resp = requests.Response()
    resp.status_code = status
    resp._content = body.encode("utf-8")
    resp.encoding = "utf-8"
    if headers:
        for key, value in headers.items():
            resp.headers[key] = value
    return resp


class GraphErrorTransparencyTests(unittest.TestCase):
    def test_503_unknown_error_empty_message_preserved(self):
        body = json.dumps(
            {
                "error": {
                    "code": "UnknownError",
                    "message": "",
                    "innerError": {
                        "request-id": "req-1",
                        "client-request-id": "cli-1",
                    },
                }
            }
        )
        resp = _response(
            503,
            body,
            headers={
                "Content-Type": "application/json",
                "request-id": "req-1",
                "client-request-id": "cli-1",
            },
        )
        exc = GraphAPIError(
            "Transient Graph Error 503",
            status_code=503,
            request_id="req-1",
            response=resp,
        )
        payload = build_graph_error_response(exc, service="onedrive", action="get_user_drive_id")
        self.assertEqual(payload["raw_graph"]["body_json"]["error"]["message"], "")
        self.assertEqual(payload["normalized"]["error_summary"], "Transient Graph Error 503")
        self.assertEqual(payload["failure_source"], "graph_upstream")

    def test_403_classified_missing_permission(self):
        body = json.dumps(
            {
                "error": {
                    "code": "Authorization_RequestDenied",
                    "message": "Insufficient privileges to complete the operation.",
                }
            }
        )
        resp = _response(403, body, headers={"Content-Type": "application/json"})
        exc = GraphAPIError(
            "Graph request failed (403) [Authorization_RequestDenied]: Insufficient privileges to complete the operation.",
            status_code=403,
            response=resp,
            code="Authorization_RequestDenied",
        )
        payload = build_graph_error_response(exc)
        self.assertEqual(payload["error_class"], "missing_permission")
        self.assertEqual(payload["failure_source"], "graph_upstream")

    def test_401_classified_auth(self):
        body = json.dumps({"error": {"code": "InvalidAuthenticationToken", "message": "Access token is empty."}})
        resp = _response(401, body, headers={"Content-Type": "application/json"})
        exc = GraphAPIError("Graph request failed (401)", status_code=401, response=resp, code="InvalidAuthenticationToken")
        payload = build_graph_error_response(exc)
        self.assertEqual(payload["error_class"], "auth")

    def test_429_retry_after_suggested_wait(self):
        body = json.dumps({"error": {"code": "TooManyRequests", "message": "Too many requests."}})
        resp = _response(429, body, headers={"Content-Type": "application/json", "Retry-After": "7"})
        exc = GraphAPIError("Transient Graph Error 429", status_code=429, response=resp, code="TooManyRequests")
        payload = build_graph_error_response(exc)
        self.assertEqual(payload["suggested_wait_seconds"], 7)
        self.assertEqual(payload["error_class"], "throttling")

    def test_malformed_json_body_classified_parse_error(self):
        resp = _response(503, "{not-json", headers={"Content-Type": "application/json"})
        exc = GraphAPIError("Transient Graph Error 503", status_code=503, response=resp)
        payload = build_graph_error_response(exc)
        self.assertEqual(payload["failure_source"], "dashboard_parse_error")
        self.assertIsNone(payload["raw_graph"]["body_json"])

    def test_503_retry_exhausted_is_graph_upstream(self):
        body = json.dumps({"error": {"code": "UnknownError", "message": ""}})
        resp = _response(503, body, headers={"Content-Type": "application/json", "request-id": "req-503"})
        exc = GraphAPIError(
            "Transient Graph Error 503",
            status_code=503,
            request_id="req-503",
            response=resp,
            path="/users/abc/drive",
            total_attempts=3,
            attempts=[
                {"attempt": 1, "time": "t1", "status": 503, "wait_ms": 2000, "duration_ms": 120},
                {"attempt": 2, "time": "t2", "status": 503, "wait_ms": 4000, "duration_ms": 140},
                {"attempt": 3, "time": "t3", "status": 503, "wait_ms": None, "duration_ms": 160},
            ],
        )
        payload = build_graph_error_response(exc, service="onedrive", action="get_user_drive_id")
        self.assertEqual(payload["failure_source"], "graph_upstream")
        self.assertEqual(payload["failure_outcome"], "retry_exhausted")
        self.assertEqual(payload["error_class"], "transient_upstream_persistent")
        self.assertEqual(payload.get("route_group"), "onedrive.resolve_drive")

    def test_circuit_open_is_dashboard_guardrail_and_has_no_raw_graph(self):
        exc = GraphAPIError(
            "Circuit breaker open for route group 'onedrive.resolve_drive'.",
            status_code=503,
            retry_after=30,
            failure_origin="dashboard_guardrail",
            error_class="circuit_open",
            attempts=[],
            circuit={
                "route_group": "onedrive.resolve_drive",
                "remaining_seconds": 30,
                "opened_reason": "repeated_upstream_5xx",
                "last_upstream_status": 503,
                "last_upstream_request_id": "req-1",
                "last_upstream_timestamp": "2026-01-01T00:00:00Z",
            },
        )
        payload = build_graph_error_response(exc, service="onedrive", action="get_user_drive_id")
        self.assertEqual(payload["failure_source"], "dashboard_guardrail")
        self.assertEqual(payload["failure_outcome"], "circuit_open")
        self.assertEqual(payload["error_class"], "circuit_open")
        self.assertIsNone(payload.get("raw_graph"))

    def test_config_error_source_classification(self):
        exc = GraphAPIError(
            "Graph handler not configured",
            status_code=None,
            failure_origin="dashboard_config_error",
            error_class="dashboard_config_error",
        )
        payload = build_graph_error_response(exc, service="system", action="graph_check")
        self.assertEqual(payload["failure_source"], "dashboard_config_error")

    def test_parse_error_source_when_status_200(self):
        resp = _response(200, "{not-json", headers={"Content-Type": "application/json"})
        exc = GraphAPIError("Parse error", status_code=200, response=resp)
        payload = build_graph_error_response(exc, service="system", action="graph_check")
        self.assertEqual(payload["failure_source"], "dashboard_parse_error")


if __name__ == "__main__":
    unittest.main()
