from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

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
    """Try to extract a request/correlation id from ARM headers."""

    if not isinstance(headers, dict):
        return None
    lowered = {str(k).lower(): v for k, v in headers.items()}
    candidates = [
        "x-ms-request-id",
        "x-ms-correlation-request-id",
        "request-id",
        "client-request-id",
    ]
    for name in candidates:
        value = lowered.get(name)
        if value:
            return str(value)
    return None


def _looks_like_invalid_api_version(body_text: str | None) -> bool:
    """Heuristic: does the response look like an invalid api-version error?"""

    if not body_text:
        return False
    lowered = str(body_text).lower()
    return "api-version" in lowered and ("invalid" in lowered or "not supported" in lowered)


def _normalize_secure_score(item: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize an ARM secure score object into stable fields for UI tables."""

    properties = item.get("properties") if isinstance(item.get("properties"), dict) else {}
    score = properties.get("score") if isinstance(properties.get("score"), dict) else {}
    current = score.get("current")
    max_score = score.get("max")
    percentage = score.get("percentage")
    ratio = None
    try:
        if current is not None and max_score not in (None, 0, "0"):
            ratio = float(current) / float(max_score)
    except Exception:
        ratio = None
    # Some api versions return percentage as 0-1, some as 0-100. Keep it human-friendly.
    pct = None
    try:
        if percentage is not None:
            pct_val = float(percentage)
            pct = pct_val * 100.0 if 0 <= pct_val <= 1 else pct_val
        elif ratio is not None:
            pct = ratio * 100.0
    except Exception:
        pct = None

    return {
        "id": item.get("id"),
        "name": item.get("name"),
        "type": item.get("type"),
        "display_name": properties.get("displayName") or properties.get("display_name"),
        "environment": properties.get("environment"),
        "current": current,
        "max": max_score,
        "percentage": pct,
        "score_ratio": ratio,
    }


def _normalize_recommendation(item: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize an ARM Defender assessment into a recommendation row for tables.

    Defender for Cloud commonly exposes "recommendations" through the
    Microsoft.Security/assessments surface. Different api-versions vary slightly
    in where severity/category live (properties vs properties.metadata).
    """

    props = item.get("properties") if isinstance(item.get("properties"), dict) else {}
    metadata = props.get("metadata") if isinstance(props.get("metadata"), dict) else {}
    status = props.get("status") if isinstance(props.get("status"), dict) else {}

    display_name = props.get("displayName") or metadata.get("displayName") or item.get("name")
    severity = metadata.get("severity") or props.get("severity") or status.get("severity")

    category = (
        metadata.get("category")
        or props.get("category")
        or (metadata.get("categories")[0] if isinstance(metadata.get("categories"), list) and metadata.get("categories") else None)
    )

    return {
        "id": item.get("id"),
        "name": item.get("name"),
        "type": item.get("type"),
        # Keep Graph Admin Studio table defaults happy: `displayName` is a prioritized column.
        "displayName": display_name,
        "severity": severity,
        "category": category,
        "status": status.get("code") or status.get("status"),
    }


class DefenderClient:
    """Client for Microsoft Defender for Cloud (ARM REST) operations."""

    ARM_SCOPE = ["https://management.azure.com/.default"]
    ARM_BASE = "https://management.azure.com"

    # ARM api-versions for Microsoft.Security vary by tenant/region; try a small set.
    DEFAULT_API_VERSIONS = [
        "2020-01-01",
        "2022-01-01",
        "2023-01-01",
    ]

    def __init__(self, graph_session, *, subscription_id: str | None = None):
        """Initialize the instance."""

        self._graph = graph_session
        self.subscription_id = subscription_id
        self._session = requests.Session()
        self._arm_token: str | None = None
        self._arm_expires_at: float = 0

    def _emit_trace(self, trace: Dict[str, Any]) -> None:
        """Emit a request trace via the configured trace hook (if any)."""

        ctx = get_trace_context() or {}
        hook = ctx.get("trace_hook")
        if callable(hook):
            try:
                hook(trace)
            except Exception:
                pass

    def _get_arm_token(self) -> str:
        """Get (or refresh) an ARM access token using the configured app credentials."""

        if self._arm_token and time.time() < (self._arm_expires_at - 60):
            return self._arm_token

        started_at = _now_iso()
        start_perf = time.perf_counter()
        trace_ctx = get_trace_context() or {}
        ui_request_id = trace_ctx.get("ui_request_id")
        tenant_id = getattr(self._graph, "tenant_id", None)
        token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"

        try:
            result = self._graph.app.acquire_token_for_client(scopes=self.ARM_SCOPE)
        except Exception as exc:
            duration_ms = int(round((time.perf_counter() - start_perf) * 1000))
            trace = {
                "ui_request_id": ui_request_id,
                "tenant_id": tenant_id,
                "service": "defender",
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
                f"Failed to acquire ARM token: {exc}",
                status_code=None,
                request_id=None,
                response=None,
                code="arm_token_acquire_failed",
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
            error = str((result or {}).get("error") or "arm_token_acquire_failed")
            description = str((result or {}).get("error_description") or "").strip()
            duration_ms = int(round((time.perf_counter() - start_perf) * 1000))
            trace = {
                "ui_request_id": ui_request_id,
                "tenant_id": tenant_id,
                "service": "defender",
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
            message = "Could not acquire ARM token."
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

        self._arm_token = str(result["access_token"])
        self._arm_expires_at = time.time() + int(result.get("expires_in") or 0)
        return self._arm_token

    def _request(self, method: str, url: str, *, params: Dict[str, Any] | None = None) -> requests.Response:
        """Perform an ARM REST request and emit a trace for observability."""

        trace_ctx = get_trace_context() or {}
        ui_request_id = trace_ctx.get("ui_request_id")
        started_at = _now_iso()
        start_perf = time.perf_counter()
        token = self._get_arm_token()

        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }
        if ui_request_id:
            headers["client-request-id"] = str(ui_request_id)
            headers["return-client-request-id"] = "true"

        try:
            response = self._session.request(method=method, url=url, params=params, headers=headers, timeout=30)
        except requests.RequestException as exc:
            duration_ms = int(round((time.perf_counter() - start_perf) * 1000))
            trace = {
                "ui_request_id": ui_request_id,
                "tenant_id": getattr(self._graph, "tenant_id", None),
                "service": "defender",
                "method": method,
                "url": url,
                "path": url.replace(self.ARM_BASE, ""),
                "params": params or {},
                "request_headers": _redact_headers(headers),
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
                "ARM request failed before receiving a response.",
                status_code=None,
                request_id=None,
                response=None,
                code=None,
                retry_after=None,
                failure_origin="dashboard_http",
                method=method,
                url=url,
                path=url.replace(self.ARM_BASE, ""),
                params=params or {},
                request_headers=_redact_headers(headers),
                response_headers=None,
                response_body=None,
                attempts=trace["attempts"],
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
        safe_req_headers = _redact_headers(headers)
        safe_resp_headers = _redact_headers(dict(response.headers or {}))
        raw_body = None
        try:
            raw_body = response.text
        except Exception:
            raw_body = None
        trace = {
            "ui_request_id": ui_request_id,
            "tenant_id": getattr(self._graph, "tenant_id", None),
            "service": "defender",
            "method": method,
            "url": url,
            "path": url.replace(self.ARM_BASE, ""),
            "params": params or {},
            "request_headers": safe_req_headers,
            "started_at": started_at,
            "ended_at": _now_iso(),
            "duration_ms": duration_ms,
            "attempts": [{"attempt": 1, "time": _now_iso(), "status": response.status_code}],
            "queue_wait_ms": 0,
            "failure_origin": None if response.status_code < 400 else "graph_upstream",
            "failure_outcome": None if response.status_code < 400 else "failed",
            "raw_graph": {
                "status": response.status_code,
                "headers": safe_resp_headers,
                "body": raw_body,
            },
        }
        self._emit_trace(trace)

        if response.status_code >= 400:
            request_id = _extract_request_id(dict(response.headers or {}))
            raise GraphAPIError(
                "ARM request failed.",
                status_code=response.status_code,
                request_id=request_id,
                response=response,
                code=None,
                retry_after=None,
                failure_origin="graph_upstream",
                method=method,
                url=url,
                path=url.replace(self.ARM_BASE, ""),
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

    def secure_score_summary(
        self,
        *,
        subscription_id: str | None = None,
        api_versions: List[str] | None = None,
    ) -> Dict[str, Any]:
        """Return a summary of Defender for Cloud secure scores for a subscription (ARM REST).

        This is a lightweight, operator-friendly view:
        - fetch the secureScores list
        - normalize items
        - compute the top score (current/max)
        """

        sub_id = (subscription_id or self.subscription_id or "").strip()
        if not sub_id:
            raise ValueError(
                "AZURE_SUBSCRIPTION_ID is required for Defender for Cloud secure score queries. "
                "Set it in Settings (Azure subscription id) or provide subscription_id."
            )

        versions = api_versions or list(self.DEFAULT_API_VERSIONS)
        url = f"{self.ARM_BASE}/subscriptions/{sub_id}/providers/Microsoft.Security/secureScores"
        last_error: GraphAPIError | None = None
        body: Dict[str, Any] | None = None
        used_version: str | None = None

        for version in versions:
            try:
                response = self._request("GET", url, params={"api-version": version})
                body = response.json()
                used_version = version
                break
            except GraphAPIError as exc:
                last_error = exc
                # Wrong api-version commonly yields 400/404 with api-version text; try next.
                if exc.status_code in (400, 404) and _looks_like_invalid_api_version(getattr(exc, "response_body", None)):
                    continue
                raise

        if used_version is None or body is None:
            if last_error:
                raise last_error
            raise GraphAPIError(
                "Unable to query secure scores (no compatible api-version).",
                status_code=None,
                request_id=None,
                response=None,
                code="arm_api_version",
                retry_after=None,
                failure_origin="dashboard_config_error",
                method="GET",
                url=url,
                path=f"/subscriptions/{sub_id}/providers/Microsoft.Security/secureScores",
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

        normalized = [_normalize_secure_score(item) for item in items if isinstance(item, dict)]
        top = None
        if normalized:
            def score_key(row: Dict[str, Any]) -> Tuple[float, float]:
                ratio = row.get("score_ratio")
                pct = row.get("percentage")
                if isinstance(pct, (int, float)):
                    return (float(pct), float(ratio) if isinstance(ratio, (int, float)) else 0.0)
                if isinstance(ratio, (int, float)):
                    return (float(ratio) * 100.0, float(ratio))
                return (0.0, 0.0)

            top = max(normalized, key=score_key)

        return {
            "subscription_id": sub_id,
            "api_version": used_version,
            "count": len(normalized),
            "top": top,
            "scores": normalized,
        }

    def recommendations_list(
        self,
        *,
        subscription_id: str | None = None,
        max_items: int = 50,
        max_pages: int = 5,
        api_versions: List[str] | None = None,
    ) -> Dict[str, Any]:
        """Return a bounded list of Defender for Cloud recommendations (ARM assessments).

        The ARM "assessments" surface is a practical source for operator-friendly
        recommendation data. This method returns items in a `value` array to make
        Table mode render naturally without special-casing.
        """

        sub_id = (subscription_id or self.subscription_id or "").strip()
        if not sub_id:
            raise ValueError(
                "AZURE_SUBSCRIPTION_ID is required for Defender for Cloud recommendations queries. "
                "Set it in Settings (Azure subscription id) or provide subscription_id."
            )

        # Keep this bounded; large subscriptions can have thousands of assessments.
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

        versions = api_versions or [
            "2020-01-01",
            "2021-06-01",
            "2022-01-01",
        ]
        url = f"{self.ARM_BASE}/subscriptions/{sub_id}/providers/Microsoft.Security/assessments"

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
                    response = self._request("GET", page_url, params=params)
                    body = response.json()
                    page_items = body.get("value") if isinstance(body, dict) else None
                    if isinstance(page_items, list):
                        for raw in page_items:
                            if not isinstance(raw, dict):
                                continue
                            results.append(_normalize_recommendation(raw))
                            if len(results) >= max_items_int:
                                break
                    next_link = body.get("nextLink") if isinstance(body, dict) else None
                    if next_link and isinstance(next_link, str):
                        page_url = next_link
                        params = None  # nextLink already includes query params.
                    else:
                        page_url = None
                partial = page_url is not None
                items = results
                used_version = version
                break
            except GraphAPIError as exc:
                last_error = exc
                # Wrong api-version commonly yields 400/404 with api-version text; try next.
                if exc.status_code in (400, 404) and _looks_like_invalid_api_version(getattr(exc, "response_body", None)):
                    continue
                raise

        if used_version is None:
            if last_error:
                raise last_error
            raise GraphAPIError(
                "Unable to query Defender for Cloud recommendations (no compatible api-version).",
                status_code=None,
                request_id=None,
                response=None,
                code="arm_api_version",
                retry_after=None,
                failure_origin="dashboard_config_error",
                method="GET",
                url=url,
                path=f"/subscriptions/{sub_id}/providers/Microsoft.Security/assessments",
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
            "subscription_id": sub_id,
            "api_version": used_version,
            "count": len(items),
            "partial": partial,
            "value": items,
        }
