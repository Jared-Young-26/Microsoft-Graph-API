from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from microsoft import GraphAPIError


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _redact_headers(headers: Dict[str, Any] | None) -> Dict[str, str]:
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


def _try_parse_json(text: str | None) -> Any:
    if not text:
        return None
    try:
        return json.loads(text)
    except Exception:
        return None


def _classify_error_class(status: Optional[int], code: str | None) -> str | None:
    if status == 401:
        return "auth"
    if status == 403 or (code in ("Authorization_RequestDenied", "InsufficientPrivileges")):
        return "missing_permission"
    if status == 429:
        return "throttling"
    if status == 503 and code == "circuit_open":
        return "circuit_open"
    if status in (502, 503, 504):
        return "transient_upstream"
    if status and status >= 500:
        return "unknown"
    return None


def _has_upstream_artifacts(
    *,
    exc: GraphAPIError,
    raw_headers: Dict[str, Any] | None,
    raw_body_text: str | None,
) -> bool:
    """Heuristic: did we actually receive an upstream Graph response?"""

    if getattr(exc, "response", None) is not None:
        return True
    if getattr(exc, "request_id", None):
        return True
    if isinstance(raw_headers, dict):
        lowered = {str(k).lower(): v for k, v in raw_headers.items()}
        if lowered.get("request-id") or lowered.get("client-request-id"):
            return True
    if raw_body_text is not None:
        return True
    return False


def _classify_failure_source(
    *,
    exc: GraphAPIError,
    raw_headers: Dict[str, Any] | None,
    raw_body_text: str | None,
    raw_body_json: Any,
    json_parse_failed: bool,
) -> str:
    """Classify *where* the failure originated (upstream vs dashboard)."""

    # Parse errors are dashboard-side even if Graph returned something.
    if json_parse_failed:
        return "dashboard_parse_error"

    # Authoritative rule: if we received any upstream artifacts, the source is Graph.
    if _has_upstream_artifacts(exc=exc, raw_headers=raw_headers, raw_body_text=raw_body_text):
        return "graph_upstream"

    # Explicit dashboard-side source (legacy field: failure_origin).
    if getattr(exc, "failure_origin", None):
        return str(exc.failure_origin)

    # Transport errors: no upstream response available.
    if exc.response is None and exc.status_code is None:
        return "dashboard_http"

    # Synthetic 5xx (e.g., circuit breaker open) without any upstream artifacts.
    return "dashboard_retry_policy"


def _classify_failure_outcome(
    *,
    failure_source: str,
    error_class: str | None,
    status: Optional[int],
    attempts: list,
    total_attempts: Optional[int],
    message: str,
) -> str:
    """Classify *how* the request ended (success, retry exhausted, circuit open, etc.)."""

    if error_class == "circuit_open":
        return "circuit_open"
    if failure_source == "dashboard_http":
        lowered = (message or "").lower()
        if "timed out" in lowered or "timeout" in lowered:
            return "timeout"
        return "retry_exhausted"
    if total_attempts and total_attempts > 1 and len(attempts) >= total_attempts:
        return "retry_exhausted"
    if status is not None:
        return "retry_exhausted"
    return "retry_exhausted"


def build_graph_error_response(
    exc: GraphAPIError,
    *,
    service: str | None = None,
    action: str | None = None,
) -> Dict[str, Any]:
    status = exc.status_code
    raw_headers: Dict[str, Any] = {}
    raw_body_text: str | None = None
    raw_body_json: Any = None
    json_parse_failed = False

    if exc.response is not None:
        try:
            raw_headers = dict(exc.response.headers or {})
        except Exception:
            raw_headers = {}
        try:
            raw_body_text = exc.response.text
        except Exception:
            raw_body_text = None
        raw_body_json = _try_parse_json(raw_body_text)
        if raw_body_text and raw_body_json is None:
            # If Graph claims JSON but parsing fails, call it out.
            content_type = str(raw_headers.get("Content-Type") or "").lower()
            if "application/json" in content_type:
                json_parse_failed = True
    else:
        # Some dashboard-origin errors (circuit breaker / retry policy) may not have a Response object,
        # but still carry headers/body in the exception.
        try:
            raw_headers = dict(getattr(exc, "response_headers", None) or {})
        except Exception:
            raw_headers = {}
        raw_body_text = getattr(exc, "response_body", None)
        raw_body_json = _try_parse_json(raw_body_text)

    error_code = exc.code
    if not error_code and isinstance(raw_body_json, dict):
        error_code = (raw_body_json.get("error") or {}).get("code")

    attempts = getattr(exc, "attempts", None) or []
    circuit = getattr(exc, "circuit", None)

    error_class = getattr(exc, "error_class", None) or _classify_error_class(status, error_code)
    # Promote transient upstream codes into a specific class when we can.
    if error_class in (None, "unknown") and status in (502, 503, 504):
        error_class = "transient_upstream"
    if status == 503 and error_class == "transient_upstream":
        # Mark persistent when we see repeated 503s or the circuit window is already hot.
        try:
            repeats = sum(1 for item in attempts if isinstance(item, dict) and item.get("status") == 503)
        except Exception:
            repeats = 0
        hot = False
        if isinstance(circuit, dict):
            try:
                hot = int(circuit.get("failure_count_window") or 0) >= 5
            except Exception:
                hot = False
        if repeats >= 3 or hot:
            error_class = "transient_upstream_persistent"

    failure_source = _classify_failure_source(
        exc=exc,
        raw_headers=raw_headers,
        raw_body_text=raw_body_text,
        raw_body_json=raw_body_json,
        json_parse_failed=json_parse_failed,
    )
    explicit_outcome = getattr(exc, "failure_outcome", None)
    if isinstance(explicit_outcome, str) and explicit_outcome.strip():
        failure_outcome = explicit_outcome.strip()
    else:
        failure_outcome = _classify_failure_outcome(
            failure_source=failure_source,
            error_class=error_class,
            status=status,
            attempts=attempts,
            total_attempts=getattr(exc, "total_attempts", None),
            message=str(exc),
        )

    retry_after = exc.retry_after
    if retry_after is None and isinstance(raw_headers, dict):
        retry_after_val = raw_headers.get("Retry-After")
        if retry_after_val:
            try:
                retry_after = int(retry_after_val)
            except Exception:
                retry_after = None
        retry_after_ms = raw_headers.get("x-ms-retry-after-ms")
        if retry_after is None and retry_after_ms:
            try:
                retry_after = max(1, int(int(retry_after_ms) / 1000))
            except Exception:
                retry_after = None

    diagnostics = {
        "ags": raw_headers.get("x-ms-ags-diagnostic"),
        "date": raw_headers.get("Date"),
    }

    rate_limit_headers = {}
    for key in (
        "Retry-After",
        "x-ms-retry-after-ms",
        "RateLimit-Remaining",
        "RateLimit-Reset",
        "RateLimit-Limit",
        "x-ms-throttle-limit",
        "x-ms-usage",
    ):
        if key in raw_headers:
            rate_limit_headers[key] = raw_headers.get(key)
    if retry_after is not None:
        rate_limit_headers["retry_after_seconds"] = retry_after

    # Enrich attempts with wait_s for UI readability and compute upstream/wait breakdowns.
    enriched_attempts = []
    wait_time_ms = 0
    upstream_time_ms = 0
    for item in attempts:
        if not isinstance(item, dict):
            continue
        wait_ms = item.get("wait_ms")
        if isinstance(wait_ms, (int, float)):
            wait_time_ms += int(wait_ms)
        dur_ms = item.get("duration_ms")
        if isinstance(dur_ms, (int, float)):
            upstream_time_ms += int(dur_ms)
        enriched = dict(item)
        if wait_ms is not None:
            try:
                enriched["wait_s"] = round(float(wait_ms) / 1000.0, 3)
            except Exception:
                enriched["wait_s"] = None
        enriched_attempts.append(enriched)

    honored_retry_after = any(
        isinstance(item, dict) and item.get("retry_after_seconds") not in (None, "", 0)
        for item in attempts
    )

    # If Retry-After isn't present, suggest the most recent backoff wait.
    if retry_after is None:
        last_wait_ms = None
        for item in reversed(enriched_attempts):
            if isinstance(item, dict) and item.get("wait_ms"):
                last_wait_ms = item.get("wait_ms")
                break
        if last_wait_ms:
            try:
                retry_after = max(1, int(round(float(last_wait_ms) / 1000.0)))
            except Exception:
                retry_after = None
        elif enriched_attempts:
            # Backoff schedule (approx): 2^attempt capped at 30s.
            try:
                retry_after = min(2 ** len(enriched_attempts), 30)
            except Exception:
                retry_after = None

    retry_timeline = {
        "attempt_number": len(enriched_attempts) if enriched_attempts else None,
        "total_attempts": getattr(exc, "total_attempts", None),
        "attempts": enriched_attempts,
    }

    raw_graph = None
    if status is not None or raw_headers or raw_body_text is not None:
        raw_graph = {
            "status": status,
            "headers": _redact_headers(raw_headers),
            "body": raw_body_text,
            "body_json": raw_body_json,
        }
    # Guardrail failures (e.g., circuit breaker open) should not look like upstream Graph responses.
    # Only include raw_graph when upstream artifacts were actually received.
    if (
        failure_source != "graph_upstream"
        and error_class == "circuit_open"
        and getattr(exc, "response", None) is None
        and not raw_headers
        and raw_body_text is None
    ):
        raw_graph = None

    # Keep legacy fields for existing UI logic.
    detail = raw_body_json if raw_body_json is not None else raw_body_text

    # Route group (circuit / retry diagnostics).
    route_group = None
    if isinstance(circuit, dict):
        route_group = circuit.get("route_group")
    if not route_group:
        path_candidate = getattr(exc, "path", None) or getattr(exc, "url", None)
        if path_candidate:
            try:
                from microsoft import _route_group_from_path  # type: ignore

                route_group = _route_group_from_path(path_candidate)
            except Exception:
                route_group = None

    request_context = {
        "method": getattr(exc, "method", None),
        "url": getattr(exc, "url", None),
        "path": getattr(exc, "path", None),
        "params": getattr(exc, "params", None),
        "tenant_id": getattr(exc, "tenant_id", None),
        "service": service,
        "action": action,
        "attempt_count": len(enriched_attempts) if enriched_attempts else None,
        "duration_ms": getattr(exc, "duration_ms", None),
        "queue_wait_ms": getattr(exc, "queue_wait_ms", None),
        "failure_source": failure_source,
        "failure_outcome": failure_outcome,
        "route_group": route_group,
    }

    synthetic_status = None
    if failure_source != "graph_upstream" and error_class == "circuit_open":
        synthetic_status = status or 503

    return {
        "ok": False,
        # Split attribution: source vs outcome. Keep legacy failure_origin as alias for source.
        "failure_source": failure_source,
        "failure_outcome": failure_outcome,
        "failure_origin": failure_source,
        "error_class": error_class,
        "error": str(exc),  # operator-friendly summary (never overwrites raw Graph fields)
        "normalized": {
            "error_summary": str(exc),
            "error_class": error_class,
        },
        "status_code": status,
        "synthetic_status": synthetic_status,
        "request_id": exc.request_id,
        "correlation_id": getattr(exc, "correlation_id", None),
        "ui_request_id": getattr(exc, "ui_request_id", None),
        "service": service,
        "action": action,
        "tenant_id": getattr(exc, "tenant_id", None),
        "timestamp": _now_iso(),
        "duration_ms": getattr(exc, "duration_ms", None),
        "upstream_time_ms": upstream_time_ms or None,
        "wait_time_ms": wait_time_ms or None,
        "method": getattr(exc, "method", None),
        "url": getattr(exc, "url", None),
        "path": getattr(exc, "path", None),
        "params": getattr(exc, "params", None),
        "queue_wait_ms": getattr(exc, "queue_wait_ms", None),
        "route_group": route_group,
        "circuit": circuit,
        "request": request_context,
        "raw_graph": raw_graph,
        "detail": detail,
        "diagnostics": diagnostics,
        "rate_limit": rate_limit_headers or None,
        "suggested_wait_seconds": retry_after,
        "retry_policy": {
            "max_attempts": getattr(exc, "total_attempts", None),
            "base_delay_s": 2,
            "max_delay_s": 30,
            "jitter": "uniform_0_1",
            "honored_retry_after": honored_retry_after,
        },
        "retry": retry_timeline,
    }


def build_support_bundle_from_error(error_payload: Dict[str, Any]) -> Dict[str, Any]:
    """Create a Microsoft-support-friendly bundle from a normalized error payload."""
    raw_graph = error_payload.get("raw_graph") or {}
    diagnostics = error_payload.get("diagnostics") or {}
    rate = error_payload.get("rate_limit") or {}
    selected_headers = {}
    for key in ("Retry-After", "x-ms-ags-diagnostic", "request-id", "client-request-id", "Date"):
        val = None
        if isinstance(raw_graph.get("headers"), dict):
            val = raw_graph["headers"].get(key) or raw_graph["headers"].get(key.lower())
        if val is None and isinstance(rate, dict):
            val = rate.get(key)
        if val is None and key == "Date":
            val = diagnostics.get("date")
        if val is not None:
            selected_headers[key] = val
    return {
        "method": error_payload.get("method"),
        "path": error_payload.get("path"),
        "timestamp": error_payload.get("timestamp"),
        "status_code": error_payload.get("status_code"),
        "request_id": error_payload.get("request_id"),
        "correlation_id": error_payload.get("correlation_id"),
        "ui_request_id": error_payload.get("ui_request_id"),
        "headers": selected_headers,
        "raw_body": raw_graph.get("body"),
    }
