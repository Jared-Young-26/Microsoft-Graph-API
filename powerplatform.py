from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import requests

from microsoft import GraphAPIError, get_trace_context


def _now_iso() -> str:
    """Return current UTC time in ISO-8601 format."""

    return datetime.now(timezone.utc).isoformat()


def _redact_headers(headers: Dict[str, Any] | None) -> Dict[str, str]:
    """Redact sensitive headers for safe UI/audit rendering."""

    if not isinstance(headers, dict):
        return {}
    cleaned: Dict[str, str] = {}
    for key, value in headers.items():
        key_str = str(key)
        lowered = key_str.lower()
        if lowered in ("authorization", "cookie", "set-cookie"):
            cleaned[key_str] = "[redacted]"
        else:
            cleaned[key_str] = str(value)
    return cleaned


def _extract_request_id(headers: Dict[str, Any] | None) -> str | None:
    """Try to extract a request/correlation id from response headers."""

    if not isinstance(headers, dict):
        return None
    lowered = {str(k).lower(): v for k, v in headers.items()}
    for key in (
        "x-ms-request-id",
        "request-id",
        "client-request-id",
        "x-ms-correlation-request-id",
    ):
        value = lowered.get(key)
        if value:
            return str(value)
    return None


def _looks_like_invalid_api_version(body_text: str | None) -> bool:
    """Heuristic: does the response look like an invalid api-version error?"""

    if not body_text:
        return False
    lowered = str(body_text).lower()
    return "api-version" in lowered and ("invalid" in lowered or "not supported" in lowered)


def _normalize_environment(item: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize a Power Platform environment into stable fields for UI tables."""

    props = item.get("properties") if isinstance(item.get("properties"), dict) else {}
    env_id = item.get("name") or props.get("environmentId") or props.get("id")
    display_name = props.get("displayName") or props.get("display_name") or env_id
    location = props.get("location") or props.get("region") or props.get("azureRegion")
    env_type = props.get("environmentType") or props.get("environment_type") or props.get("type")
    sku = props.get("environmentSku") or props.get("sku") or props.get("environmentSkuType")

    return {
        "displayName": display_name,
        # Keep the canonical environment id in `name` so Table view prioritizes it.
        "name": env_id,
        "id": item.get("id"),
        "location": location,
        "environmentType": env_type,
        "sku": sku,
    }


class PowerPlatformClient:
    """Client for Power Platform admin operations (BAP management endpoint)."""

    BAP_SCOPE = ["https://api.bap.microsoft.com/.default"]
    BAP_BASE = "https://api.bap.microsoft.com"

    FLOW_SCOPES = [
        # Power Automate management APIs typically expect this resource.
        "https://service.flow.microsoft.com/.default",
        # Some tenants accept the api host as resource; try as fallback.
        "https://api.flow.microsoft.com/.default",
    ]
    FLOW_BASE = "https://api.flow.microsoft.com"

    DEFAULT_API_VERSIONS = [
        "2016-11-01",
        "2020-10-01",
    ]

    def __init__(self, graph_session):
        """Initialize the instance."""

        self._graph = graph_session
        self._session = requests.Session()
        self._bap_token: str | None = None
        self._bap_expires_at: float = 0
        self._flow_token: str | None = None
        self._flow_expires_at: float = 0

    def _emit_trace(self, trace: Dict[str, Any]) -> None:
        """Emit a request trace via the configured trace hook (if any)."""

        ctx = get_trace_context() or {}
        hook = ctx.get("trace_hook")
        if callable(hook):
            try:
                hook(trace)
            except Exception:
                pass

    def _get_bap_token(self) -> str:
        """Get (or refresh) a BAP access token using the configured app credentials."""

        if self._bap_token and time.time() < (self._bap_expires_at - 60):
            return self._bap_token

        started_at = _now_iso()
        start_perf = time.perf_counter()
        trace_ctx = get_trace_context() or {}
        ui_request_id = trace_ctx.get("ui_request_id")
        tenant_id = getattr(self._graph, "tenant_id", None)
        token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"

        try:
            result = self._graph.app.acquire_token_for_client(scopes=self.BAP_SCOPE)
        except Exception as exc:
            duration_ms = int(round((time.perf_counter() - start_perf) * 1000))
            trace = {
                "ui_request_id": ui_request_id,
                "tenant_id": tenant_id,
                "service": "powerplatform",
                "method": "POST",
                "url": token_url,
                "path": "/oauth2/v2.0/token",
                "params": {},
                "request_headers": {},
                "started_at": started_at,
                "ended_at": _now_iso(),
                "duration_ms": duration_ms,
                "attempts": [
                    {
                        "attempt": 1,
                        "time": _now_iso(),
                        "status": None,
                        "wait_ms": None,
                        "new_connection_used": False,
                        "duration_ms": duration_ms,
                        "error": str(exc),
                        "error_type": exc.__class__.__name__,
                    }
                ],
                "queue_wait_ms": 0,
                "failure_origin": "dashboard_http",
                "failure_outcome": "failed",
                "raw_graph": None,
                "error_class": "network",
            }
            self._emit_trace(trace)
            raise GraphAPIError(
                f"Failed to acquire Power Platform token: {exc}",
                status_code=None,
                request_id=None,
                response=None,
                code="bap_token_acquire_failed",
                retry_after=None,
                failure_origin="dashboard_http",
                method="POST",
                url=token_url,
                path="/oauth2/v2.0/token",
                params={},
                request_headers={},
                response_headers=None,
                response_body=None,
                attempts=trace["attempts"],
                duration_ms=duration_ms,
                ui_request_id=ui_request_id,
                correlation_id=str(ui_request_id) if ui_request_id else None,
                error_class="network",
                total_attempts=1,
                tenant_id=tenant_id,
                queue_wait_ms=0,
                failure_outcome="failed",
            ) from exc

        if not isinstance(result, dict) or "access_token" not in result:
            error = str((result or {}).get("error") or "bap_token_acquire_failed")
            description = str((result or {}).get("error_description") or "").strip()
            duration_ms = int(round((time.perf_counter() - start_perf) * 1000))
            trace = {
                "ui_request_id": ui_request_id,
                "tenant_id": tenant_id,
                "service": "powerplatform",
                "method": "POST",
                "url": token_url,
                "path": "/oauth2/v2.0/token",
                "params": {},
                "request_headers": {},
                "started_at": started_at,
                "ended_at": _now_iso(),
                "duration_ms": duration_ms,
                "attempts": [
                    {
                        "attempt": 1,
                        "time": _now_iso(),
                        "status": None,
                        "wait_ms": None,
                        "new_connection_used": False,
                        "duration_ms": duration_ms,
                        "error": description or error,
                        "error_type": "msal_error",
                    }
                ],
                "queue_wait_ms": 0,
                "failure_origin": "dashboard_config_error",
                "failure_outcome": "failed",
                "raw_graph": {"status": None, "headers": {}, "body": None},
                "error_class": "auth",
            }
            self._emit_trace(trace)
            message = "Could not acquire Power Platform token."
            if error:
                message = f"{message} [{error}]"
            if description:
                message = f"{message}: {description}"
            raise GraphAPIError(
                message,
                status_code=401 if error.lower() in ("invalid_client", "unauthorized_client") else None,
                request_id=None,
                response=None,
                code=error,
                retry_after=None,
                failure_origin="dashboard_config_error",
                method="POST",
                url=token_url,
                path="/oauth2/v2.0/token",
                params={},
                request_headers={},
                response_headers=None,
                response_body=None,
                attempts=trace["attempts"],
                duration_ms=duration_ms,
                ui_request_id=ui_request_id,
                correlation_id=str(ui_request_id) if ui_request_id else None,
                error_class="auth",
                total_attempts=1,
                tenant_id=tenant_id,
                queue_wait_ms=0,
                failure_outcome="failed",
            )

        self._bap_token = str(result["access_token"])
        self._bap_expires_at = time.time() + int(result.get("expires_in") or 0)
        return self._bap_token

    def _get_flow_token(self) -> str:
        """Get (or refresh) a Power Automate (Flow) access token using app credentials."""

        if self._flow_token and time.time() < (self._flow_expires_at - 60):
            return self._flow_token

        started_at = _now_iso()
        start_perf = time.perf_counter()
        trace_ctx = get_trace_context() or {}
        ui_request_id = trace_ctx.get("ui_request_id")
        tenant_id = getattr(self._graph, "tenant_id", None)
        token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"

        last_error: GraphAPIError | None = None
        for scope in self.FLOW_SCOPES:
            try:
                result = self._graph.app.acquire_token_for_client(scopes=[scope])
            except Exception as exc:
                last_error = GraphAPIError(
                    f"Failed to acquire Flow token: {exc}",
                    status_code=None,
                    request_id=None,
                    response=None,
                    code="flow_token_acquire_failed",
                    retry_after=None,
                    failure_origin="dashboard_http",
                    method="POST",
                    url=token_url,
                    path="/oauth2/v2.0/token",
                    params={},
                    request_headers={},
                    response_headers=None,
                    response_body=None,
                    attempts=[
                        {
                            "attempt": 1,
                            "time": _now_iso(),
                            "status": None,
                            "wait_ms": None,
                            "new_connection_used": False,
                            "duration_ms": int(round((time.perf_counter() - start_perf) * 1000)),
                            "error": str(exc),
                            "error_type": exc.__class__.__name__,
                        }
                    ],
                    duration_ms=int(round((time.perf_counter() - start_perf) * 1000)),
                    ui_request_id=ui_request_id,
                    correlation_id=str(ui_request_id) if ui_request_id else None,
                    error_class="network",
                    total_attempts=1,
                    tenant_id=tenant_id,
                    queue_wait_ms=0,
                    failure_outcome="failed",
                )
                continue

            if isinstance(result, dict) and "access_token" in result:
                self._flow_token = str(result["access_token"])
                self._flow_expires_at = time.time() + int(result.get("expires_in") or 0)
                return self._flow_token

            error = str((result or {}).get("error") or "flow_token_acquire_failed")
            description = str((result or {}).get("error_description") or "").strip()
            duration_ms = int(round((time.perf_counter() - start_perf) * 1000))
            message = "Could not acquire Flow token."
            if error:
                message = f"{message} [{error}]"
            if description:
                message = f"{message}: {description}"
            last_error = GraphAPIError(
                message,
                status_code=401 if error.lower() in ("invalid_client", "unauthorized_client") else None,
                request_id=None,
                response=None,
                code=error,
                retry_after=None,
                failure_origin="dashboard_config_error",
                method="POST",
                url=token_url,
                path="/oauth2/v2.0/token",
                params={},
                request_headers={},
                response_headers=None,
                response_body=None,
                attempts=[
                    {
                        "attempt": 1,
                        "time": _now_iso(),
                        "status": None,
                        "wait_ms": None,
                        "new_connection_used": False,
                        "duration_ms": duration_ms,
                        "error": description or error,
                        "error_type": "msal_error",
                    }
                ],
                duration_ms=duration_ms,
                ui_request_id=ui_request_id,
                correlation_id=str(ui_request_id) if ui_request_id else None,
                error_class="auth",
                total_attempts=1,
                tenant_id=tenant_id,
                queue_wait_ms=0,
                failure_outcome="failed",
            )
        if last_error:
            raise last_error
        raise GraphAPIError(
            "Could not acquire Flow token.",
            status_code=None,
            request_id=None,
            response=None,
            code="flow_token_acquire_failed",
            retry_after=None,
            failure_origin="dashboard_config_error",
            method="POST",
            url=token_url,
            path="/oauth2/v2.0/token",
            params={},
            request_headers={},
            response_headers=None,
            response_body=None,
            attempts=[],
            duration_ms=int(round((time.perf_counter() - start_perf) * 1000)),
            ui_request_id=ui_request_id,
            correlation_id=str(ui_request_id) if ui_request_id else None,
            error_class="auth",
            total_attempts=1,
            tenant_id=tenant_id,
            queue_wait_ms=0,
            failure_outcome="failed",
        )

    def _request(self, method: str, url: str, *, params: Dict[str, Any] | None = None) -> requests.Response:
        """Perform a BAP REST request and emit a trace for observability."""

        trace_ctx = get_trace_context() or {}
        ui_request_id = trace_ctx.get("ui_request_id")
        started_at = _now_iso()
        start_perf = time.perf_counter()
        token = self._get_bap_token()

        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }
        if ui_request_id:
            headers["client-request-id"] = str(ui_request_id)
            headers["return-client-request-id"] = "true"

        safe_req_headers = _redact_headers(headers)
        try:
            response = self._session.request(method=method, url=url, params=params, headers=headers, timeout=30)
        except requests.RequestException as exc:
            duration_ms = int(round((time.perf_counter() - start_perf) * 1000))
            trace = {
                "ui_request_id": ui_request_id,
                "tenant_id": getattr(self._graph, "tenant_id", None),
                "service": "powerplatform",
                "method": method,
                "url": url,
                "path": url.replace(self.BAP_BASE, ""),
                "params": params or {},
                "request_headers": safe_req_headers,
                "started_at": started_at,
                "ended_at": _now_iso(),
                "duration_ms": duration_ms,
                "attempts": [
                    {
                        "attempt": 1,
                        "time": _now_iso(),
                        "status": None,
                        "wait_ms": None,
                        "new_connection_used": False,
                        "duration_ms": duration_ms,
                        "error": str(exc),
                        "error_type": exc.__class__.__name__,
                    }
                ],
                "queue_wait_ms": 0,
                "failure_origin": "dashboard_http",
                "failure_outcome": "retry_exhausted",
                "raw_graph": None,
                "error_class": "network",
            }
            self._emit_trace(trace)
            raise GraphAPIError(
                "Power Platform request failed before receiving a response.",
                status_code=None,
                request_id=None,
                response=None,
                code=None,
                retry_after=None,
                failure_origin="dashboard_http",
                method=method,
                url=url,
                path=url.replace(self.BAP_BASE, ""),
                params=params or {},
                request_headers=safe_req_headers,
                response_headers=None,
                response_body=None,
                attempts=trace.get("attempts") or [],
                duration_ms=duration_ms,
                ui_request_id=ui_request_id,
                correlation_id=str(ui_request_id) if ui_request_id else None,
                error_class="network",
                total_attempts=1,
                tenant_id=getattr(self._graph, "tenant_id", None),
                queue_wait_ms=0,
                failure_outcome="retry_exhausted",
            ) from exc

        duration_ms = int(round((time.perf_counter() - start_perf) * 1000))
        raw_body: str | None
        try:
            raw_body = response.text
        except Exception:
            raw_body = None

        safe_resp_headers = _redact_headers(dict(response.headers or {}))
        trace = {
            "ui_request_id": ui_request_id,
            "tenant_id": getattr(self._graph, "tenant_id", None),
            "service": "powerplatform",
            "method": method,
            "url": url,
            "path": url.replace(self.BAP_BASE, ""),
            "params": params or {},
            "request_headers": safe_req_headers,
            "started_at": started_at,
            "ended_at": _now_iso(),
            "duration_ms": duration_ms,
            "attempts": [
                {
                    "attempt": 1,
                    "time": _now_iso(),
                    "status": response.status_code,
                    "wait_ms": None,
                    "new_connection_used": False,
                    "duration_ms": duration_ms,
                    "request_id": _extract_request_id(dict(response.headers or {})),
                }
            ],
            "queue_wait_ms": 0,
            "failure_origin": None,
            "failure_outcome": "success",
            "raw_graph": {
                "status": response.status_code,
                "headers": safe_resp_headers,
                "body": raw_body,
            },
        }
        if response.status_code >= 400:
            trace["failure_origin"] = "graph_upstream"
            trace["failure_outcome"] = "failed"
            trace["error_class"] = None
        self._emit_trace(trace)

        if response.status_code >= 400:
            request_id = _extract_request_id(dict(response.headers or {}))
            raise GraphAPIError(
                "Power Platform request failed.",
                status_code=response.status_code,
                request_id=request_id,
                response=response,
                code=None,
                retry_after=None,
                failure_origin="graph_upstream",
                method=method,
                url=url,
                path=url.replace(self.BAP_BASE, ""),
                params=params or {},
                request_headers=safe_req_headers,
                response_headers=safe_resp_headers,
                response_body=raw_body,
                attempts=trace.get("attempts") or [],
                duration_ms=duration_ms,
                ui_request_id=ui_request_id,
                correlation_id=str(ui_request_id) if ui_request_id else None,
                error_class=None,
                total_attempts=1,
                tenant_id=getattr(self._graph, "tenant_id", None),
                queue_wait_ms=0,
                failure_outcome="failed",
            )
        return response

    def _flow_request(self, method: str, url: str, *, params: Dict[str, Any] | None = None) -> requests.Response:
        """Perform a Flow (Power Automate) REST request and emit a trace for observability."""

        trace_ctx = get_trace_context() or {}
        ui_request_id = trace_ctx.get("ui_request_id")
        started_at = _now_iso()
        start_perf = time.perf_counter()
        token = self._get_flow_token()

        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }
        if ui_request_id:
            headers["client-request-id"] = str(ui_request_id)
            headers["return-client-request-id"] = "true"

        safe_req_headers = _redact_headers(headers)
        try:
            response = self._session.request(method=method, url=url, params=params, headers=headers, timeout=30)
        except requests.RequestException as exc:
            duration_ms = int(round((time.perf_counter() - start_perf) * 1000))
            trace = {
                "ui_request_id": ui_request_id,
                "tenant_id": getattr(self._graph, "tenant_id", None),
                "service": "powerplatform",
                "method": method,
                "url": url,
                "path": url.replace(self.FLOW_BASE, ""),
                "params": params or {},
                "request_headers": safe_req_headers,
                "started_at": started_at,
                "ended_at": _now_iso(),
                "duration_ms": duration_ms,
                "attempts": [
                    {
                        "attempt": 1,
                        "time": _now_iso(),
                        "status": None,
                        "wait_ms": None,
                        "new_connection_used": False,
                        "duration_ms": duration_ms,
                        "error": str(exc),
                        "error_type": exc.__class__.__name__,
                    }
                ],
                "queue_wait_ms": 0,
                "failure_origin": "dashboard_http",
                "failure_outcome": "retry_exhausted",
                "raw_graph": None,
                "error_class": "network",
            }
            self._emit_trace(trace)
            raise GraphAPIError(
                "Flow request failed before receiving a response.",
                status_code=None,
                request_id=None,
                response=None,
                code=None,
                retry_after=None,
                failure_origin="dashboard_http",
                method=method,
                url=url,
                path=url.replace(self.FLOW_BASE, ""),
                params=params or {},
                request_headers=safe_req_headers,
                response_headers=None,
                response_body=None,
                attempts=trace.get("attempts") or [],
                duration_ms=duration_ms,
                ui_request_id=ui_request_id,
                correlation_id=str(ui_request_id) if ui_request_id else None,
                error_class="network",
                total_attempts=1,
                tenant_id=getattr(self._graph, "tenant_id", None),
                queue_wait_ms=0,
                failure_outcome="retry_exhausted",
            ) from exc

        duration_ms = int(round((time.perf_counter() - start_perf) * 1000))
        raw_body: str | None
        try:
            raw_body = response.text
        except Exception:
            raw_body = None

        safe_resp_headers = _redact_headers(dict(response.headers or {}))
        trace = {
            "ui_request_id": ui_request_id,
            "tenant_id": getattr(self._graph, "tenant_id", None),
            "service": "powerplatform",
            "method": method,
            "url": url,
            "path": url.replace(self.FLOW_BASE, ""),
            "params": params or {},
            "request_headers": safe_req_headers,
            "started_at": started_at,
            "ended_at": _now_iso(),
            "duration_ms": duration_ms,
            "attempts": [
                {
                    "attempt": 1,
                    "time": _now_iso(),
                    "status": response.status_code,
                    "wait_ms": None,
                    "new_connection_used": False,
                    "duration_ms": duration_ms,
                    "request_id": _extract_request_id(dict(response.headers or {})),
                }
            ],
            "queue_wait_ms": 0,
            "failure_origin": None,
            "failure_outcome": "success",
            "raw_graph": {
                "status": response.status_code,
                "headers": safe_resp_headers,
                "body": raw_body,
            },
        }
        if response.status_code >= 400:
            trace["failure_origin"] = "graph_upstream"
            trace["failure_outcome"] = "failed"
            trace["error_class"] = None
        self._emit_trace(trace)

        if response.status_code >= 400:
            request_id = _extract_request_id(dict(response.headers or {}))
            raise GraphAPIError(
                "Flow request failed.",
                status_code=response.status_code,
                request_id=request_id,
                response=response,
                code=None,
                retry_after=None,
                failure_origin="graph_upstream",
                method=method,
                url=url,
                path=url.replace(self.FLOW_BASE, ""),
                params=params or {},
                request_headers=safe_req_headers,
                response_headers=safe_resp_headers,
                response_body=raw_body,
                attempts=trace.get("attempts") or [],
                duration_ms=duration_ms,
                ui_request_id=ui_request_id,
                correlation_id=str(ui_request_id) if ui_request_id else None,
                error_class=None,
                total_attempts=1,
                tenant_id=getattr(self._graph, "tenant_id", None),
                queue_wait_ms=0,
                failure_outcome="failed",
            )
        return response

    def list_flows(
        self,
        environment_id: str,
        *,
        max_items: int = 50,
        max_pages: int = 5,
        api_versions: List[str] | None = None,
    ) -> Dict[str, Any]:
        """List Power Automate flows in an environment (admin scope, bounded)."""

        env_id = str(environment_id or "").strip()
        if not env_id:
            raise ValueError("environment_id is required.")

        try:
            max_items_int = int(max_items)
        except Exception:
            max_items_int = 50
        max_items_int = max(1, min(500, max_items_int))
        try:
            max_pages_int = int(max_pages)
        except Exception:
            max_pages_int = 5
        max_pages_int = max(1, min(50, max_pages_int))

        versions = api_versions or list(self.DEFAULT_API_VERSIONS)
        url = f"{self.FLOW_BASE}/providers/Microsoft.ProcessSimple/scopes/admin/environments/{env_id}/flows"

        def _normalize_flow(item: Dict[str, Any]) -> Dict[str, Any]:
            props = item.get("properties") if isinstance(item.get("properties"), dict) else {}
            display_name = props.get("displayName") or props.get("display_name") or item.get("name")
            state = props.get("state") or props.get("status") or props.get("flowState")
            created = props.get("createdTime") or props.get("createdDateTime")
            modified = props.get("lastModifiedTime") or props.get("lastModifiedDateTime")
            return {
                "displayName": display_name,
                "name": item.get("name"),
                "id": item.get("id"),
                "type": item.get("type"),
                "status": state,
                "createdDateTime": created,
                "lastModifiedDateTime": modified,
            }

        last_error: GraphAPIError | None = None
        used_version: str | None = None
        items: List[Dict[str, Any]] = []
        partial = False

        for version in versions:
            try:
                page_url: str | None = url
                params: Dict[str, Any] | None = {"api-version": version}
                pages = 0
                results: List[Dict[str, Any]] = []
                while page_url and pages < max_pages_int and len(results) < max_items_int:
                    pages += 1
                    response = self._flow_request("GET", page_url, params=params)
                    body = response.json()
                    page_items = body.get("value") if isinstance(body, dict) else None
                    if isinstance(page_items, list):
                        for raw in page_items:
                            if not isinstance(raw, dict):
                                continue
                            results.append(_normalize_flow(raw))
                            if len(results) >= max_items_int:
                                break
                    next_link = body.get("nextLink") if isinstance(body, dict) else None
                    if next_link and isinstance(next_link, str):
                        page_url = next_link
                        params = None
                    else:
                        page_url = None
                partial = page_url is not None
                items = results
                used_version = version
                break
            except GraphAPIError as exc:
                last_error = exc
                if exc.status_code in (400, 404) and _looks_like_invalid_api_version(getattr(exc, "response_body", None)):
                    continue
                raise

        if used_version is None:
            if last_error:
                raise last_error
            raise GraphAPIError(
                "Unable to query Power Platform flows (no compatible api-version).",
                status_code=None,
                request_id=None,
                response=None,
                code="flow_api_version",
                retry_after=None,
                failure_origin="dashboard_config_error",
                method="GET",
                url=url,
                path=f"/providers/Microsoft.ProcessSimple/scopes/admin/environments/{env_id}/flows",
                params={},
                request_headers={},
                response_headers=None,
                response_body=None,
                attempts=[],
                duration_ms=0,
                ui_request_id=None,
                correlation_id=None,
                error_class="dashboard_config_error",
                total_attempts=1,
                tenant_id=getattr(self._graph, "tenant_id", None),
                queue_wait_ms=0,
                failure_outcome="failed",
            )

        return {
            "environment_id": env_id,
            "api_version": used_version,
            "count": len(items),
            "partial": partial,
            "value": items,
        }

    def list_environments(
        self,
        *,
        max_items: int = 200,
        api_versions: List[str] | None = None,
    ) -> Dict[str, Any]:
        """List Power Platform environments using the admin scope endpoint."""

        try:
            max_items_int = int(max_items)
        except Exception:
            max_items_int = 200
        max_items_int = max(1, min(2000, max_items_int))

        versions = api_versions or list(self.DEFAULT_API_VERSIONS)
        url = f"{self.BAP_BASE}/providers/Microsoft.BusinessAppPlatform/scopes/admin/environments"

        last_error: GraphAPIError | None = None
        used_version: str | None = None
        body: Dict[str, Any] | None = None

        for version in versions:
            try:
                response = self._request("GET", url, params={"api-version": version})
                body = response.json()
                used_version = version
                break
            except GraphAPIError as exc:
                last_error = exc
                if exc.status_code in (400, 404) and _looks_like_invalid_api_version(getattr(exc, "response_body", None)):
                    continue
                raise

        if used_version is None or body is None:
            if last_error:
                raise last_error
            raise GraphAPIError(
                "Unable to query Power Platform environments (no compatible api-version).",
                status_code=None,
                request_id=None,
                response=None,
                code="bap_api_version",
                retry_after=None,
                failure_origin="dashboard_config_error",
                method="GET",
                url=url,
                path="/providers/Microsoft.BusinessAppPlatform/scopes/admin/environments",
                params={},
                request_headers={},
                response_headers=None,
                response_body=None,
                attempts=[],
                duration_ms=0,
                ui_request_id=None,
                correlation_id=None,
                error_class="dashboard_config_error",
                total_attempts=1,
                tenant_id=getattr(self._graph, "tenant_id", None),
                queue_wait_ms=0,
                failure_outcome="failed",
            )

        items = body.get("value") if isinstance(body, dict) else None
        if not isinstance(items, list):
            items = []

        normalized = [_normalize_environment(item) for item in items if isinstance(item, dict)]
        if len(normalized) > max_items_int:
            normalized = normalized[:max_items_int]

        return {
            "api_version": used_version,
            "count": len(normalized),
            "value": normalized,
        }
