from dotenv import load_dotenv
from datetime import datetime, timezone
from contextvars import ContextVar
import os
import time
import msal
import requests
import random
import subprocess
import uuid
import threading
import json
import re
import base64
from collections import defaultdict
from contextlib import contextmanager

# Load environment variables from .env file
load_dotenv()
REQUIRED_ENV_VARS = ["TENANT_ID", "CLIENT_ID", "CLIENT_SECRET"]

SENSITIVE_KEYWORDS = (
    "password",
    "passphrase",
    "secret",
    "token",
    "credential",
    "private",
    "client_secret",
    "refresh_token",
    "access_token",
    "apikey",
    "api_key",
)


def _is_sensitive_key(key: str) -> bool:
    normalized = str(key or "").lower()
    if not normalized:
        return False
    if normalized.endswith("_key") or normalized.endswith("apikey"):
        return True
    return any(keyword in normalized for keyword in SENSITIVE_KEYWORDS)


def _redact_payload(value, depth: int = 0):
    if value is None or isinstance(value, (int, float, bool)):
        return value
    if isinstance(value, str):
        redacted = value
        for keyword in SENSITIVE_KEYWORDS:
            pattern = re.compile(rf"(?i)({re.escape(keyword)}\\s*[:=]\\s*)(\\S+)")
            redacted = pattern.sub(r"\\1[redacted]", redacted)
        return redacted
    if depth > 6:
        return "[truncated]"
    if isinstance(value, list):
        return [_redact_payload(item, depth + 1) for item in value]
    if isinstance(value, dict):
        sanitized = {}
        for key, val in value.items():
            if _is_sensitive_key(key):
                sanitized[key] = "[redacted]"
            else:
                sanitized[key] = _redact_payload(val, depth + 1)
        return sanitized
    return value


def is_powershell_envelope(value) -> bool:
    if not isinstance(value, dict):
        return False
    return all(key in value for key in ("ok", "data", "error", "meta"))


def unwrap_powershell_data(value):
    if is_powershell_envelope(value):
        return value.get("data")
    return value


_TRACE_CONTEXT: ContextVar[dict | None] = ContextVar("gas_trace_context", default=None)


def set_trace_context(context: dict | None):
    return _TRACE_CONTEXT.set(context)


def reset_trace_context(token):
    _TRACE_CONTEXT.reset(token)


def get_trace_context() -> dict | None:
    return _TRACE_CONTEXT.get()


def _redact_headers(headers: dict) -> dict:
    if not isinstance(headers, dict):
        return {}
    cleaned = {}
    for key, value in headers.items():
        key_str = str(key)
        lowered = key_str.lower()
        if lowered in ("authorization", "cookie", "set-cookie"):
            cleaned[key_str] = "[redacted]"
        else:
            cleaned[key_str] = str(value)
    return cleaned


def _route_group_from_path(path: str | None) -> str:
    """Return an endpoint-aware circuit-breaker group for a Graph path.

    The goal is to avoid overly broad grouping (e.g. treating `/users/*` as one bucket)
    for endpoints that are known to be flaky or have different backend dependencies
    (OneDrive/SharePoint). This grouping is used only for local retry/circuit guardrails.
    """

    if not path:
        return "root"
    clean = str(path).strip()
    if "graph.microsoft.com" in clean:
        idx = clean.find("/v1.0")
        if idx != -1:
            clean = clean[idx + len("/v1.0") :]
    clean = clean.split("?", 1)[0].strip()
    if not clean:
        return "root"
    if not clean.startswith("/"):
        clean = f"/{clean}"
    parts = [p for p in clean.split("/") if p]
    if not parts:
        return "root"

    # OneDrive resolve drive: /users/{id}/drive (or deeper under drive)
    if parts[0].lower() == "users" and len(parts) >= 3 and parts[2].lower() == "drive":
        return "onedrive.resolve_drive"

    # OneDrive drives API: /drives/{drive-id}/...
    if parts[0].lower() == "drives":
        return "onedrive.drives"

    # SharePoint sites API: /sites/...
    if parts[0].lower() == "sites":
        return "sharepoint.sites"

    return parts[0].lower()


def _service_from_route_group(route_group: str | None, trace_service: str | None) -> str | None:
    """Derive service key for concurrency/caps from the endpoint-aware route group.

    This prevents client-side amplification when the UI trace context is missing/mismatched.
    """

    group = (route_group or "").lower()
    if group.startswith("onedrive."):
        return "onedrive"
    if group.startswith("sharepoint."):
        return "sharepoint"
    if trace_service:
        return str(trace_service).lower()
    return None


# ---- Graph runtime guardrails (local-only, in-memory) -----------------------

_DEFAULT_MAX_ATTEMPTS = 6

_CIRCUIT_FAILURE_THRESHOLD = 5
_CIRCUIT_WINDOW_SECONDS = 30
_CIRCUIT_COOLDOWN_SECONDS = 90

_GLOBAL_MAX_INFLIGHT = 6
_SERVICE_MAX_INFLIGHT = {"onedrive": 2, "sharepoint": 2}

_GRAPH_GUARD_LOCK = threading.Lock()
_CIRCUIT_STATE: dict[str, dict] = {}
_INFLIGHT_TOTAL = 0
_INFLIGHT_BY_SERVICE: dict[str, int] = defaultdict(int)

_GLOBAL_SEMAPHORE = threading.BoundedSemaphore(_GLOBAL_MAX_INFLIGHT)
_SERVICE_SEMAPHORES = {svc: threading.BoundedSemaphore(limit) for svc, limit in _SERVICE_MAX_INFLIGHT.items()}


def _circuit_wait_seconds(route_group: str) -> int:
    now = time.time()
    with _GRAPH_GUARD_LOCK:
        entry = _CIRCUIT_STATE.get(route_group) or {}
        open_until = entry.get("open_until") or 0
    if open_until and open_until > now:
        return int(max(1, round(open_until - now)))
    return 0


def _record_circuit_failure(
    route_group: str,
    status: int | None,
    *,
    request_id: str | None = None,
    timestamp_utc: str | None = None,
) -> None:
    if not route_group:
        return
    if not status or status < 500:
        return
    now = time.time()
    timestamp_utc = timestamp_utc or datetime.now(timezone.utc).isoformat()
    window_start = now - _CIRCUIT_WINDOW_SECONDS
    with _GRAPH_GUARD_LOCK:
        entry = _CIRCUIT_STATE.setdefault(
            route_group,
            {
                "failures": [],
                "open_until": 0,
                "opened_at": None,
                "opened_reason": None,
                "last_status": None,
                "last_upstream_request_id": None,
                "last_upstream_timestamp": None,
            },
        )
        failures = [ts for ts in entry.get("failures") or [] if ts >= window_start]
        failures.append(now)
        entry["failures"] = failures
        entry["last_status"] = int(status)
        if request_id:
            entry["last_upstream_request_id"] = str(request_id)
        entry["last_upstream_timestamp"] = str(timestamp_utc)
        if len(failures) >= _CIRCUIT_FAILURE_THRESHOLD:
            was_open = bool(entry.get("open_until") and float(entry.get("open_until") or 0) > now)
            entry["open_until"] = now + _CIRCUIT_COOLDOWN_SECONDS
            if not was_open:
                entry["opened_at"] = str(timestamp_utc)
                entry["opened_reason"] = "repeated_upstream_5xx"


def _circuit_snapshot() -> dict:
    now = time.time()
    snapshot: dict[str, dict] = {}
    with _GRAPH_GUARD_LOCK:
        for group, entry in _CIRCUIT_STATE.items():
            open_until = float(entry.get("open_until") or 0)
            remaining = max(0, int(round(open_until - now))) if open_until else 0
            failures = entry.get("failures") or []
            snapshot[group] = {
                "state": "open" if remaining > 0 else "closed",
                "remaining_seconds": remaining,
                "failure_count_window": len([ts for ts in failures if ts >= now - _CIRCUIT_WINDOW_SECONDS]),
                "last_status": entry.get("last_status"),
                "opened_at": entry.get("opened_at"),
                "opened_reason": entry.get("opened_reason"),
                "last_upstream_status": entry.get("last_status"),
                "last_upstream_request_id": entry.get("last_upstream_request_id"),
                "last_upstream_timestamp": entry.get("last_upstream_timestamp"),
            }
    return snapshot


@contextmanager
def _graph_concurrency_gate(service: str | None):
    global _INFLIGHT_TOTAL
    start = time.perf_counter()
    _GLOBAL_SEMAPHORE.acquire()
    svc_sem = None
    svc_key = str(service).lower() if service else None
    if svc_key in _SERVICE_SEMAPHORES:
        svc_sem = _SERVICE_SEMAPHORES[svc_key]
        svc_sem.acquire()
    queue_wait_ms = int(round((time.perf_counter() - start) * 1000))
    try:
        with _GRAPH_GUARD_LOCK:
            _INFLIGHT_TOTAL += 1
            if svc_key:
                _INFLIGHT_BY_SERVICE[svc_key] += 1
        yield queue_wait_ms
    finally:
        with _GRAPH_GUARD_LOCK:
            _INFLIGHT_TOTAL = max(0, _INFLIGHT_TOTAL - 1)
            if svc_key:
                _INFLIGHT_BY_SERVICE[svc_key] = max(0, _INFLIGHT_BY_SERVICE.get(svc_key, 0) - 1)
        if svc_sem is not None:
            svc_sem.release()
        _GLOBAL_SEMAPHORE.release()


def graph_runtime_state() -> dict:
    with _GRAPH_GUARD_LOCK:
        inflight_total = int(_INFLIGHT_TOTAL)
        inflight_by_service = dict(_INFLIGHT_BY_SERVICE)
    return {
        "circuit_breakers": _circuit_snapshot(),
        "concurrency": {
            "max_inflight": _GLOBAL_MAX_INFLIGHT,
            "max_inflight_by_service": dict(_SERVICE_MAX_INFLIGHT),
            "inflight_total": inflight_total,
            "inflight_by_service": inflight_by_service,
        },
    }


class GraphAPIError(RuntimeError):
    def __init__(
        self,
        message,
        status_code=None,
        request_id=None,
        response=None,
        code=None,
        retry_after=None,
        *,
        failure_origin=None,
        method=None,
        url=None,
        path=None,
        params=None,
        request_headers=None,
        response_headers=None,
        response_body=None,
        attempts=None,
        duration_ms=None,
        ui_request_id=None,
        correlation_id=None,
        error_class=None,
        total_attempts=None,
        tenant_id=None,
        queue_wait_ms=None,
        circuit=None,
        failure_outcome=None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.request_id = request_id
        self.response = response
        self.code = code
        self.retry_after = retry_after
        self.failure_origin = failure_origin
        self.method = method
        self.url = url
        self.path = path
        self.params = params
        self.request_headers = request_headers
        self.response_headers = response_headers
        self.response_body = response_body
        self.attempts = attempts or []
        self.duration_ms = duration_ms
        self.ui_request_id = ui_request_id
        self.correlation_id = correlation_id
        self.error_class = error_class
        self.total_attempts = total_attempts
        self.tenant_id = tenant_id
        self.queue_wait_ms = queue_wait_ms
        self.circuit = circuit
        self.failure_outcome = failure_outcome


class GraphSession:
    def __init__(self, *, tenant_id=None, client_id=None, client_secret=None, debug=False):
        self._validate_env(tenant_id, client_id, client_secret)
        self.tenant_id = tenant_id or os.getenv("TENANT_ID")
        self.client_id = client_id or os.getenv("CLIENT_ID")
        self.client_secret = client_secret or os.getenv("CLIENT_SECRET")
        self.scope = ["https://graph.microsoft.com/.default"]
        authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        self.graph_base = "https://graph.microsoft.com/v1.0"
        self.app = msal.ConfidentialClientApplication(
            client_id=self.client_id,
            authority=authority,
            client_credential=self.client_secret,
        )
        self._thread_local = threading.local()
        self.token = None
        self.expires_at = 0
        self.debug = debug

    def _get_session(self) -> requests.Session:
        session = getattr(self._thread_local, "session", None)
        if session is None:
            session = requests.Session()
            setattr(self._thread_local, "session", session)
        return session

    def _reset_session(self) -> requests.Session:
        session = requests.Session()
        setattr(self._thread_local, "session", session)
        return session

    def get_runtime_state(self) -> dict:
        return graph_runtime_state()
    
    def token_expiry_human(self):
        if not self.expires_at:
            return "No token aquired"
        
        dt = datetime.fromtimestamp(self.expires_at, tz=timezone.utc)
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    
    def _validate_env(self, tenant_id, client_id, client_secret):
        missing = []
        if not (tenant_id or os.getenv("TENANT_ID")):
            missing.append("TENANT_ID")
        if not (client_id or os.getenv("CLIENT_ID")):
            missing.append("CLIENT_ID")
        if not (client_secret or os.getenv("CLIENT_SECRET")):
            missing.append("CLIENT_SECRET")
        if missing:
            raise RuntimeError(f"Missing Microsoft Configuration Variables: {missing}")
    
    def _request(self, method, url, **kwargs):
        max_attempts_supplied = "max_attempts" in kwargs
        max_budget_supplied = "max_budget_s" in kwargs or "retry_budget_seconds" in kwargs

        max_attempts = int(kwargs.pop("max_attempts", _DEFAULT_MAX_ATTEMPTS) or 1)
        max_budget_s = kwargs.pop("max_budget_s", None)
        retry_budget_seconds = kwargs.pop("retry_budget_seconds", None)
        if max_budget_s is None and retry_budget_seconds is not None:
            max_budget_s = retry_budget_seconds
        ignore_circuit_breaker = bool(kwargs.pop("ignore_circuit_breaker", False))
        extra_headers = kwargs.pop("headers", {}) or {}

        try:
            if max_budget_s is not None:
                max_budget_s = float(max_budget_s)
                if max_budget_s <= 0:
                    max_budget_s = None
        except Exception:
            max_budget_s = None

        params = kwargs.get("params") if isinstance(kwargs.get("params"), dict) else None
        safe_params = _redact_payload(params or {}) if params else {}
        safe_request_headers = _redact_headers(dict(extra_headers or {}))

        trace_ctx = get_trace_context() or {}
        ui_request_id = trace_ctx.get("ui_request_id")
        trace_service = trace_ctx.get("service")
        if ui_request_id and isinstance(extra_headers, dict):
            extra_headers = dict(extra_headers)
            extra_headers.setdefault("client-request-id", str(ui_request_id))
            extra_headers.setdefault("return-client-request-id", "true")
            safe_request_headers = _redact_headers(dict(extra_headers))

        attempts = []
        start_perf = time.perf_counter()
        started_at = datetime.now(timezone.utc).isoformat()
        path_only = url.replace(self.graph_base, "") if url.startswith(self.graph_base) else url
        route_group = _route_group_from_path(path_only)
        # Route-group specific defaults (only when caller didn't specify overrides).
        if not max_attempts_supplied:
            if route_group == "onedrive.resolve_drive":
                max_attempts = 4
            elif route_group == "sharepoint.sites":
                max_attempts = 4
        if not max_budget_supplied and max_budget_s is None:
            if route_group == "onedrive.resolve_drive":
                max_budget_s = 45
            elif route_group == "sharepoint.sites":
                max_budget_s = 60

        derived_service = _service_from_route_group(route_group, trace_service)
        service_for_trace = derived_service or trace_service
        last_response = None
        last_status = None
        last_request_id = None
        last_client_request_id = None
        last_response_headers = None
        last_response_body = None

        def _budget_exceeded() -> bool:
            if max_budget_s is None:
                return False
            return (time.perf_counter() - start_perf) >= max_budget_s

        def _raise_budget_exhausted() -> None:
            duration_ms = int(round((time.perf_counter() - start_perf) * 1000))
            circuit_state = _circuit_snapshot().get(route_group) or {}
            circuit_state = {**circuit_state, "route_group": route_group} if circuit_state else None

            error_class = "network"
            if last_status == 429:
                error_class = "throttling"
            elif last_status in (502, 503, 504):
                status_counts = {}
                for item in attempts:
                    if isinstance(item, dict) and item.get("status") is not None:
                        status_counts[int(item["status"])] = status_counts.get(int(item["status"]), 0) + 1
                persistent_503 = last_status == 503 and status_counts.get(503, 0) >= 3
                error_class = "transient_upstream_persistent" if persistent_503 else "transient_upstream"
            elif isinstance(last_status, int) and last_status >= 500:
                error_class = "unknown"

            failure_origin = "graph_upstream" if last_status is not None else "dashboard_http"
            trace = {
                "ui_request_id": ui_request_id,
                "tenant_id": self.tenant_id,
                "service": service_for_trace,
                "method": method,
                "url": url,
                "path": path_only,
                "params": safe_params,
                "request_headers": safe_request_headers,
                "started_at": started_at,
                "ended_at": datetime.now(timezone.utc).isoformat(),
                "duration_ms": duration_ms,
                "attempts": attempts,
                "queue_wait_ms": queue_wait_ms,
                "failure_origin": failure_origin,
                "failure_outcome": "retry_budget_exhausted",
                "raw_graph": {
                    "status": last_status,
                    "headers": _redact_headers(last_response_headers or {}),
                    "body": last_response_body,
                },
                "circuit": circuit_state,
                "error_class": error_class,
            }
            emit_trace(trace)
            raise GraphAPIError(
                "Graph retry budget exceeded.",
                status_code=last_status,
                request_id=last_request_id,
                response=last_response,
                code=None,
                retry_after=None,
                failure_origin=failure_origin,
                method=method,
                url=url,
                path=path_only,
                params=safe_params,
                request_headers=safe_request_headers,
                response_headers=_redact_headers(last_response_headers or {}) if last_response_headers else None,
                response_body=last_response_body,
                attempts=attempts,
                duration_ms=duration_ms,
                ui_request_id=ui_request_id,
                correlation_id=last_client_request_id or (str(ui_request_id) if ui_request_id else None),
                error_class=error_class,
                total_attempts=max_attempts,
                tenant_id=self.tenant_id,
                queue_wait_ms=queue_wait_ms,
                circuit=circuit_state,
                failure_outcome="retry_budget_exhausted",
            )

        def emit_trace(trace):
            hook = trace_ctx.get("trace_hook")
            if callable(hook):
                try:
                    hook(trace)
                except Exception:
                    pass

        with _graph_concurrency_gate(derived_service) as queue_wait_ms:
            # Fail-fast on a hot route group (Graph/SPO/OD 5xx storms) unless explicitly bypassed.
            if not ignore_circuit_breaker:
                circuit_wait = _circuit_wait_seconds(route_group)
                if circuit_wait > 0:
                    duration_ms = int(round((time.perf_counter() - start_perf) * 1000))
                    circuit_state = _circuit_snapshot().get(route_group) or {}
                    circuit_state = {
                        **circuit_state,
                        "route_group": route_group,
                        "remaining_seconds": circuit_wait,
                    }

                    trace = {
                        "ui_request_id": ui_request_id,
                        "tenant_id": self.tenant_id,
                        "service": service_for_trace,
                        "method": method,
                        "url": url,
                        "path": path_only,
                        "params": safe_params,
                        "request_headers": safe_request_headers,
                        "started_at": started_at,
                        "ended_at": datetime.now(timezone.utc).isoformat(),
                        "duration_ms": duration_ms,
                        "attempts": [],
                        "queue_wait_ms": queue_wait_ms,
                        "failure_origin": "dashboard_guardrail",
                        "failure_outcome": "circuit_open",
                        "error_class": "circuit_open",
                        "circuit": circuit_state,
                        # No upstream Graph response was received (fail-fast local guardrail).
                        "raw_graph": None,
                        "synthetic_status": 503,
                    }
                    emit_trace(trace)
                    raise GraphAPIError(
                        f"Circuit breaker open for route group '{route_group}'.",
                        status_code=503,
                        request_id=None,
                        response=None,
                        code=None,
                        retry_after=circuit_wait,
                        failure_origin="dashboard_guardrail",
                        method=method,
                        url=url,
                        path=path_only,
                        params=safe_params,
                        request_headers=safe_request_headers,
                        response_headers=None,
                        response_body=None,
                        attempts=[],
                        duration_ms=duration_ms,
                        ui_request_id=ui_request_id,
                        correlation_id=str(ui_request_id) if ui_request_id else None,
                        error_class="circuit_open",
                        total_attempts=max_attempts,
                        tenant_id=self.tenant_id,
                        queue_wait_ms=queue_wait_ms,
                        circuit=circuit_state,
                        failure_outcome="circuit_open",
                    )

            force_new_session = False
            for attempt in range(1, max_attempts + 1):
                if _budget_exceeded():
                    _raise_budget_exhausted()

                headers = {**self.get_headers(), **extra_headers}
                attempt_start = time.perf_counter()
                attempt_time = datetime.now(timezone.utc).isoformat()

                try:
                    session = self._reset_session() if force_new_session else self._get_session()
                    response = session.request(
                        method=method,
                        url=url,
                        headers=headers,
                        timeout=30,
                        **kwargs,
                    )
                except requests.RequestException as exc:
                    attempt_duration_ms = int(round((time.perf_counter() - attempt_start) * 1000))
                    entry = {
                        "attempt": attempt,
                        "time": attempt_time,
                        "status": None,
                        "wait_ms": None,
                        "new_connection_used": bool(force_new_session),
                        "duration_ms": attempt_duration_ms,
                        "error": str(exc),
                        "error_type": exc.__class__.__name__,
                    }
                    attempts.append(entry)
                    force_new_session = True
                    if _budget_exceeded():
                        _raise_budget_exhausted()

                    if attempt == max_attempts:
                        duration_ms = int(round((time.perf_counter() - start_perf) * 1000))
                        trace = {
                            "ui_request_id": ui_request_id,
                            "tenant_id": self.tenant_id,
                            "service": service_for_trace,
                            "method": method,
                            "url": url,
                            "path": path_only,
                            "params": safe_params,
                            "request_headers": safe_request_headers,
                            "started_at": started_at,
                            "ended_at": datetime.now(timezone.utc).isoformat(),
                            "duration_ms": duration_ms,
                            "attempts": attempts,
                            "queue_wait_ms": queue_wait_ms,
                            "failure_origin": "dashboard_http",
                            "failure_outcome": "retry_exhausted",
                            "error": str(exc),
                        }
                        emit_trace(trace)
                        raise GraphAPIError(
                            "Graph request failed before receiving a response.",
                            status_code=None,
                            request_id=None,
                            response=None,
                            code=None,
                            retry_after=None,
                            failure_origin="dashboard_http",
                            method=method,
                            url=url,
                            path=path_only,
                            params=safe_params,
                            request_headers=safe_request_headers,
                            response_headers=None,
                            response_body=None,
                            attempts=attempts,
                            duration_ms=duration_ms,
                            ui_request_id=ui_request_id,
                            correlation_id=str(ui_request_id) if ui_request_id else None,
                            error_class="network",
                            total_attempts=max_attempts,
                            tenant_id=self.tenant_id,
                            queue_wait_ms=queue_wait_ms,
                            failure_outcome="retry_exhausted",
                        ) from exc

                    sleep_time = min((2**attempt) + random.random(), 30)
                    if max_budget_s is not None:
                        elapsed = time.perf_counter() - start_perf
                        if elapsed + sleep_time > max_budget_s:
                            _raise_budget_exhausted()
                    entry["wait_ms"] = int(round(sleep_time * 1000))
                    time.sleep(sleep_time)
                    continue

                # We received an upstream response.
                retry_after = self._parse_retry_after(response.headers)
                raw_headers = dict(response.headers or {})
                try:
                    raw_body = response.text
                except Exception:
                    raw_body = None
                request_id = raw_headers.get("request-id")
                client_request_id = raw_headers.get("client-request-id")
                last_response = response
                last_status = response.status_code
                last_request_id = request_id
                last_client_request_id = client_request_id
                last_response_headers = raw_headers
                last_response_body = raw_body

                # Retryable statuses: throttle + transient upstream (Graph/SPO/OD).
                if response.status_code in (429, 500, 502, 503, 504):
                    entry = {
                        "attempt": attempt,
                        "time": attempt_time,
                        "status": response.status_code,
                        "wait_ms": None,
                        "new_connection_used": bool(force_new_session),
                        "duration_ms": int(round((time.perf_counter() - attempt_start) * 1000)),
                        "retry_after_seconds": retry_after,
                        "request_id": request_id,
                        "client_request_id": client_request_id,
                    }

                    if response.status_code >= 500 and not ignore_circuit_breaker:
                        _record_circuit_failure(
                            route_group,
                            response.status_code,
                            request_id=request_id,
                            timestamp_utc=attempt_time,
                        )

                    if attempt == max_attempts:
                        attempts.append(entry)

                        duration_ms = int(round((time.perf_counter() - start_perf) * 1000))
                        final_origin = "graph_upstream"
                        circuit_state = _circuit_snapshot().get(route_group) or {}
                        circuit_state = {**circuit_state, "route_group": route_group} if circuit_state else None
                        status_counts = {}
                        for item in attempts:
                            if isinstance(item, dict) and item.get("status") is not None:
                                status_counts[int(item["status"])] = status_counts.get(int(item["status"]), 0) + 1
                        persistent_503 = (
                            response.status_code == 503
                            and (
                                status_counts.get(503, 0) >= 3
                                or (
                                    isinstance(circuit_state, dict)
                                    and int(circuit_state.get("failure_count_window") or 0) >= _CIRCUIT_FAILURE_THRESHOLD
                                )
                            )
                        )

                        if response.status_code == 429:
                            error_class = "throttling"
                        elif response.status_code in (502, 503, 504):
                            error_class = "transient_upstream_persistent" if persistent_503 else "transient_upstream"
                        else:
                            error_class = "unknown"

                        trace = {
                            "ui_request_id": ui_request_id,
                            "tenant_id": self.tenant_id,
                            "service": service_for_trace,
                            "method": method,
                            "url": url,
                            "path": path_only,
                            "params": safe_params,
                            "request_headers": safe_request_headers,
                            "started_at": started_at,
                            "ended_at": datetime.now(timezone.utc).isoformat(),
                            "duration_ms": duration_ms,
                            "attempts": attempts,
                            "queue_wait_ms": queue_wait_ms,
                            "failure_origin": final_origin,
                            "failure_outcome": "retry_exhausted",
                            "raw_graph": {
                                "status": response.status_code,
                                "headers": _redact_headers(raw_headers),
                                "body": raw_body,
                            },
                            "circuit": circuit_state,
                            "error_class": error_class,
                        }
                        emit_trace(trace)
                        raise GraphAPIError(
                            f"Transient Graph Error {response.status_code}",
                            status_code=response.status_code,
                            request_id=request_id,
                            response=response,
                            code=None,
                            retry_after=retry_after,
                            failure_origin=final_origin,
                            method=method,
                            url=url,
                            path=path_only,
                            params=safe_params,
                            request_headers=safe_request_headers,
                            response_headers=_redact_headers(raw_headers),
                            response_body=raw_body,
                            attempts=attempts,
                            duration_ms=duration_ms,
                            ui_request_id=ui_request_id,
                            correlation_id=client_request_id or (str(ui_request_id) if ui_request_id else None),
                            error_class=error_class,
                            total_attempts=max_attempts,
                            tenant_id=self.tenant_id,
                            queue_wait_ms=queue_wait_ms,
                            circuit=circuit_state,
                            failure_outcome="retry_exhausted",
                        )

                    sleep_time = retry_after if retry_after is not None else min((2**attempt) + random.random(), 30)
                    if max_budget_s is not None:
                        elapsed = time.perf_counter() - start_perf
                        if elapsed + sleep_time > max_budget_s:
                            attempts.append(entry)
                            _raise_budget_exhausted()
                    entry["wait_ms"] = int(round(sleep_time * 1000))
                    attempts.append(entry)
                    if response.status_code >= 500:
                        force_new_session = True
                    time.sleep(sleep_time)
                    continue

                try:
                    response.raise_for_status()
                except requests.HTTPError as exc:
                    resp = exc.response
                    request_id = resp.headers.get("request-id") if resp else None
                    retry_after = self._parse_retry_after(resp.headers) if resp else None

                    raw_headers = dict(resp.headers or {}) if resp else {}
                    try:
                        raw_body = resp.text if resp else None
                    except Exception:
                        raw_body = None
                    last_response = resp
                    last_status = resp.status_code if resp is not None else None
                    last_request_id = request_id
                    last_client_request_id = raw_headers.get("client-request-id") if raw_headers else None
                    last_response_headers = raw_headers
                    last_response_body = raw_body

                    code = None
                    detail = None
                    if resp is not None:
                        try:
                            error_payload = resp.json().get("error", {})
                            code = error_payload.get("code")
                            detail = error_payload.get("message")
                        except Exception:
                            detail = raw_body.strip() if isinstance(raw_body, str) else None

                    message = f"Graph request failed ({resp.status_code if resp else 'unknown'})"
                    if code:
                        message = f"{message} [{code}]"
                    if detail:
                        message = f"{message}: {detail}"

                    duration_ms = int(round((time.perf_counter() - start_perf) * 1000))
                    client_request_id = raw_headers.get("client-request-id")
                    attempts.append(
                        {
                            "attempt": attempt,
                            "time": datetime.now(timezone.utc).isoformat(),
                            "status": resp.status_code if resp is not None else None,
                            "wait_ms": None,
                            "new_connection_used": bool(force_new_session),
                            "duration_ms": int(round((time.perf_counter() - attempt_start) * 1000)),
                            "retry_after_seconds": retry_after,
                            "request_id": request_id,
                            "client_request_id": client_request_id,
                        }
                    )

                    trace = {
                        "ui_request_id": ui_request_id,
                        "tenant_id": self.tenant_id,
                        "service": service_for_trace,
                        "method": method,
                        "url": url,
                        "path": path_only,
                        "params": safe_params,
                        "request_headers": safe_request_headers,
                        "started_at": started_at,
                        "ended_at": datetime.now(timezone.utc).isoformat(),
                        "duration_ms": duration_ms,
                        "attempts": attempts,
                        "queue_wait_ms": queue_wait_ms,
                        "failure_origin": "graph_upstream",
                        "raw_graph": {
                            "status": resp.status_code if resp is not None else None,
                            "headers": _redact_headers(raw_headers),
                            "body": raw_body,
                        },
                    }
                    emit_trace(trace)
                    raise GraphAPIError(
                        message,
                        status_code=resp.status_code if resp else None,
                        request_id=request_id,
                        response=resp,
                        code=code,
                        retry_after=retry_after,
                        failure_origin="graph_upstream",
                        method=method,
                        url=url,
                        path=path_only,
                        params=safe_params,
                        request_headers=safe_request_headers,
                        response_headers=_redact_headers(raw_headers),
                        response_body=raw_body,
                        attempts=attempts,
                        duration_ms=duration_ms,
                        ui_request_id=ui_request_id,
                        correlation_id=client_request_id or (str(ui_request_id) if ui_request_id else None),
                        error_class="missing_permission"
                        if (resp and resp.status_code == 403)
                        else "auth"
                        if (resp and resp.status_code == 401)
                        else "unknown",
                        total_attempts=max_attempts,
                        tenant_id=self.tenant_id,
                        queue_wait_ms=queue_wait_ms,
                    ) from exc

                duration_ms = int(round((time.perf_counter() - start_perf) * 1000))
                attempts.append(
                    {
                        "attempt": attempt,
                        "time": datetime.now(timezone.utc).isoformat(),
                        "status": response.status_code,
                        "wait_ms": None,
                        "new_connection_used": bool(force_new_session),
                        "duration_ms": int(round((time.perf_counter() - attempt_start) * 1000)),
                        "request_id": response.headers.get("request-id"),
                        "client_request_id": response.headers.get("client-request-id"),
                    }
                )
                trace = {
                    "ui_request_id": ui_request_id,
                    "tenant_id": self.tenant_id,
                    "service": service_for_trace,
                    "method": method,
                    "url": url,
                    "path": path_only,
                    "params": safe_params,
                    "request_headers": safe_request_headers,
                    "started_at": started_at,
                    "ended_at": datetime.now(timezone.utc).isoformat(),
                    "duration_ms": duration_ms,
                    "attempts": attempts,
                    "queue_wait_ms": queue_wait_ms,
                    "failure_origin": None,
                    "raw_graph": {
                        "status": response.status_code,
                        "headers": _redact_headers(dict(response.headers or {})),
                        "body": None,
                    },
                }
                emit_trace(trace)
                return response

    def _parse_retry_after(self, headers):
        if not headers:
            return None
        retry_after = headers.get("Retry-After")
        if retry_after:
            try:
                return int(retry_after)
            except (TypeError, ValueError):
                return None
        retry_after_ms = headers.get("x-ms-retry-after-ms")
        if retry_after_ms:
            try:
                return max(1, int(int(retry_after_ms) / 1000))
            except (TypeError, ValueError):
                return None
        return None

    def get_graph_token(self):
        result = self.app.acquire_token_for_client(scopes=self.scope)

        if "access_token" not in result:
            raise RuntimeError(f"Could not acquire Microsoft Graph token: {result}")
        
        self.token = result["access_token"]
        self.expires_at = time.time() + int(result["expires_in"])
        self._log(f"Token acquired. Expires at: {self.token_expiry_human()}")
        return self.token

    def get_headers(self):
        if not self.token or time.time() > self.expires_at - 60:
            self.get_graph_token()
        
        return {"Authorization": f"Bearer {self.token}"}
    
    def url(self, path):
        return f"{self.graph_base}/{path.lstrip('/')}"
    
    def get(self, url, **kwargs):
        full_url = url if url.startswith("http") else self.url(url)
        return self._request("GET", full_url, **kwargs)
    
    def post(self, url, **kwargs):
        full_url = url if url.startswith("http") else self.url(url)
        return self._request("POST", full_url, **kwargs)

    def put(self, url, **kwargs):
        full_url = url if url.startswith("http") else self.url(url)
        return self._request("PUT", full_url, **kwargs)
    
    def patch(self, url, **kwargs):
        full_url = url if url.startswith("http") else self.url(url)
        return self._request("PATCH", full_url, **kwargs)
    
    def delete(self, url, **kwargs):
        full_url = url if url.startswith("http") else self.url(url)
        return self._request("DELETE", full_url, **kwargs)
    
    def paged_get(
        self,
        url,
        *,
        params: dict | None = None,
        max_pages: int = 10,
        max_items: int = 500,
        return_meta: bool = False,
        retry_budget_seconds: int | float | None = None,
        max_attempts: int | None = None,
    ):
        """Fetch paginated Graph results with guardrails to avoid fan-out amplification.

        Backward compatible default: returns a list of items. When `return_meta=True`,
        returns a dict with `value` plus `partial` and `reason` fields.
        """

        results = []
        next_url = url
        page_count = 0
        partial = False
        reason = None
        start_perf = time.perf_counter()
        budget_s = None
        if retry_budget_seconds is not None:
            try:
                budget_s = float(retry_budget_seconds)
                if budget_s <= 0:
                    budget_s = None
            except Exception:
                budget_s = None

        while next_url:
            if max_pages is not None and page_count >= int(max_pages):
                partial = True
                reason = "max_pages"
                break
            if max_items is not None and len(results) >= int(max_items):
                partial = True
                reason = "max_items"
                break

            remaining_budget = None
            if budget_s is not None:
                elapsed = time.perf_counter() - start_perf
                remaining_budget = max(1.0, budget_s - elapsed)

            kwargs = {}
            if page_count == 0 and params:
                kwargs["params"] = params
            if remaining_budget is not None:
                kwargs["retry_budget_seconds"] = remaining_budget
            if max_attempts is not None:
                kwargs["max_attempts"] = int(max_attempts)

            response = self.get(next_url, **kwargs)
            data = response.json()
            page_items = data.get("value", []) or []
            if not isinstance(page_items, list):
                page_items = [page_items]
            remaining_slots = None
            if max_items is not None:
                remaining_slots = max(0, int(max_items) - len(results))
            if remaining_slots is not None and remaining_slots <= 0:
                partial = True
                reason = "max_items"
                break
            if remaining_slots is not None:
                results.extend(page_items[:remaining_slots])
            else:
                results.extend(page_items)

            page_count += 1
            next_url = data.get("@odata.nextLink")
            # NextLink already includes the original query parameters.
            params = None

            if max_items is not None and len(results) >= int(max_items):
                partial = True
                reason = "max_items"
                break

        if not return_meta:
            return results
        return {
            "value": results,
            "partial": partial,
            "reason": reason,
            "pages": page_count,
            "count": len(results),
        }
    
    def _log(self, msg):
        if self.debug:
            print(msg)


class ServiceClient:
    def __init__(self, graph_session):
        self.graph = graph_session

    def get(self, url, **kwargs):
        return self.graph.get(url, **kwargs)

    def post(self, url, **kwargs):
        return self.graph.post(url, **kwargs)

    def put(self, url, **kwargs):
        return self.graph.put(url, **kwargs)

    def patch(self, url, **kwargs):
        return self.graph.patch(url, **kwargs)

    def delete(self, url, **kwargs):
        return self.graph.delete(url, **kwargs)


class PowerShellCommandError(RuntimeError):
    def __init__(self, message, output=None):
        super().__init__(message)
        self.output = output


class PowerShellSession:
    def __init__(self, pwsh_path="pwsh"):
        self.pwsh_path = pwsh_path
        self.process = None
        self._lock = threading.Lock()

    def _start(self):
        if self.process and self.process.poll() is None:
            return
        try:
            self.process = subprocess.Popen(
                [self.pwsh_path, "-NoLogo", "-NoProfile", "-Command", "-"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
        except FileNotFoundError as e:
            raise RuntimeError("PowerShell (pwsh) not found. Install PowerShell 7 and ensure 'pwsh' is on PATH.") from e

    def _build_param_block(self, parameters):
        if not parameters:
            return "$__codex_params = @{}"
        payload = json.dumps(parameters)
        payload = payload.replace("'", "''")
        return (
            "$__codex_params = @{}; "
            f"try {{ $__codex_params = '{payload}' | ConvertFrom-Json -AsHashtable }} "
            "catch { $__codex_params = @{} }"
        )

    def _wrap_script(self, script, *, parameters=None, depth=8, capture_text=False, working_dir=None):
        token = f"__CODEX_PS_ENVELOPE__{uuid.uuid4().hex}"
        param_block = self._build_param_block(parameters)
        invoke_with_params = False
        if parameters:
            stripped = (script or "").strip()
            if stripped and all(ch not in stripped for ch in ["\n", ";", "|", "`", "{", "}"]) and " " not in stripped:
                invoke_with_params = True
        invoke_flag = "$true" if invoke_with_params else "$false"
        cmd_literal = script.replace("'", "''") if script else ""
        workdir_block = ""
        if working_dir:
            workdir_literal = working_dir.replace("'", "''")
            workdir_block = f"Push-Location '{workdir_literal}'"
        pop_block = "Pop-Location" if working_dir else ""
        capture_block = "| Out-String" if capture_text else ""
        return token, (
            "$ErrorActionPreference = 'Stop'\n"
            "$ProgressPreference = 'SilentlyContinue'\n"
            "$Error.Clear()\n"
            f"{param_block}\n"
            "foreach ($k in $__codex_params.Keys) { Set-Variable -Name $k -Value $__codex_params[$k] -Scope Local }\n"
            "$__codex_ok = $true\n"
            "$__codex_error = $null\n"
            "$__codex_data = $null\n"
            "$__codex_start = Get-Date\n"
            "try {\n"
            f"{workdir_block}\n"
            f"  if ({invoke_flag}) {{ $__codex_data = & '{cmd_literal}' @__codex_params {capture_block} }}\n"
            "  else {\n"
            f"    $__codex_data = & {{\n{script}\n    }} {capture_block}\n"
            "  }\n"
            "} catch {\n"
            "  $__codex_ok = $false\n"
            "  $__codex_error = $_\n"
            "} finally {\n"
            f"  {pop_block}\n"
            "}\n"
            "$__codex_end = Get-Date\n"
            "$__codex_errors = @()\n"
            "if ($Error.Count -gt 0) {\n"
            "  $__codex_errors = $Error | ForEach-Object {\n"
            "    [PSCustomObject]@{\n"
            "      message = $_.Exception.Message\n"
            "      type = $_.Exception.GetType().FullName\n"
            "      category = $_.CategoryInfo.Reason\n"
            "      fully_qualified_error_id = $_.FullyQualifiedErrorId\n"
            "    }\n"
            "  }\n"
            "}\n"
            "$__codex_error_info = $null\n"
            "if ($__codex_error) {\n"
            "  $__codex_error_info = [PSCustomObject]@{\n"
            "    message = $__codex_error.Exception.Message\n"
            "    type = $__codex_error.Exception.GetType().FullName\n"
            "    category = $__codex_error.CategoryInfo.Reason\n"
            "    fully_qualified_error_id = $__codex_error.FullyQualifiedErrorId\n"
            "    script_stack_trace = $__codex_error.ScriptStackTrace\n"
            "    details = ($__codex_error | Out-String).Trim()\n"
            "  }\n"
            "}\n"
            "$__codex_meta = [PSCustomObject]@{\n"
            "  started_at = $__codex_start.ToString('o')\n"
            "  ended_at = $__codex_end.ToString('o')\n"
            "  duration_ms = [math]::Round((($__codex_end) - $__codex_start).TotalMilliseconds, 2)\n"
            "  error_count = $Error.Count\n"
            "  non_terminating_errors = $__codex_errors\n"
            "}\n"
            "$__codex_payload = [PSCustomObject]@{\n"
            "  ok = $__codex_ok\n"
            "  data = $__codex_data\n"
            "  error = $__codex_error_info\n"
            "  meta = $__codex_meta\n"
            "}\n"
            f"Write-Output '{token}::BEGIN'\n"
            f"$__codex_payload | ConvertTo-Json -Depth {depth} -Compress\n"
            f"Write-Output '{token}::END'\n"
        )

    def _read_envelope(self, token):
        payload_lines = []
        started = False
        while True:
            line = self.process.stdout.readline()
            if line == "":
                break
            line_stripped = line.strip()
            if line_stripped == f"{token}::BEGIN":
                started = True
                payload_lines = []
                continue
            if line_stripped == f"{token}::END":
                break
            if started:
                payload_lines.append(line)
        return "".join(payload_lines).strip()

    def _execute_enveloped(self, script, *, parameters=None, depth=8, capture_text=False, working_dir=None):
        self._start()
        token, wrapped = self._wrap_script(
            script,
            parameters=parameters,
            depth=depth,
            capture_text=capture_text,
            working_dir=working_dir,
        )
        with self._lock:
            self.process.stdin.write(wrapped)
            self.process.stdin.flush()
            payload_text = self._read_envelope(token)
        if not payload_text:
            return {"ok": False, "data": None, "error": {"message": "No PowerShell output"}, "meta": {}}
        try:
            payload = json.loads(payload_text)
        except json.JSONDecodeError as exc:
            payload = {
                "ok": False,
                "data": payload_text,
                "error": {"message": f"Failed to parse PowerShell JSON: {exc}"},
                "meta": {},
            }
        if parameters:
            payload.setdefault("meta", {})
            payload["meta"]["parameters"] = _redact_payload(parameters)
        payload["data"] = _redact_payload(payload.get("data"))
        payload["error"] = _redact_payload(payload.get("error"))
        return payload

    def run(self, script, parameters=None, working_dir=None):
        return self._execute_enveloped(script, parameters=parameters, capture_text=True, working_dir=working_dir)

    def close(self):
        if not self.process or self.process.poll() is not None:
            return
        try:
            self.process.stdin.write("exit\n")
            self.process.stdin.flush()
            self.process.stdin.close()
            self.process.wait(timeout=5)
        except Exception:
            pass

    def run_json(self, script_or_command, parameters=None, depth=8, working_dir=None):
        return self._execute_enveloped(
            script_or_command,
            parameters=parameters,
            depth=depth,
            capture_text=False,
            working_dir=working_dir,
        )


class RemotePowerShellSession:
    def __init__(self, runner, prefer_pwsh=True):
        self.runner = runner
        self.prefer_pwsh = prefer_pwsh
        self._helper = PowerShellSession()

    def _encode_command(self, script: str) -> str:
        return base64.b64encode(script.encode("utf-16le")).decode("ascii")

    def _extract_envelope(self, output: str, token: str):
        begin_marker = f"{token}::BEGIN"
        end_marker = f"{token}::END"
        start = output.find(begin_marker)
        if start == -1:
            return None
        start += len(begin_marker)
        end = output.find(end_marker, start)
        if end == -1:
            return None
        return output[start:end].strip()

    def _run_encoded(self, shell: str, encoded_command: str, timeout: int):
        command = f"{shell} -NoProfile -NonInteractive -EncodedCommand {encoded_command}"
        return self.runner.run_command(command, timeout=timeout)

    def _execute(self, script, *, parameters=None, depth=8, capture_text=False, working_dir=None, timeout=60):
        token, wrapped = self._helper._wrap_script(
            script,
            parameters=parameters,
            depth=depth,
            capture_text=capture_text,
            working_dir=working_dir,
        )
        encoded = self._encode_command(wrapped)
        shells = ["pwsh", "powershell"] if self.prefer_pwsh else ["powershell", "pwsh"]
        last_result = None
        for shell in shells:
            result = self._run_encoded(shell, encoded, timeout)
            last_result = result
            stderr = (result.get("stderr") or "").lower()
            if result.get("returncode") in (127, 9009) or "not found" in stderr:
                continue
            payload_text = self._extract_envelope(result.get("stdout") or "", token)
            if payload_text:
                try:
                    payload = json.loads(payload_text)
                except json.JSONDecodeError as exc:
                    payload = {
                        "ok": False,
                        "data": payload_text,
                        "error": {"message": f"Failed to parse PowerShell JSON: {exc}"},
                        "meta": {},
                    }
                if parameters:
                    payload.setdefault("meta", {})
                    payload["meta"]["parameters"] = _redact_payload(parameters)
                payload.setdefault("meta", {})
                payload["meta"]["ssh"] = {
                    "host": result.get("host"),
                    "user": result.get("user"),
                    "port": result.get("port"),
                    "transport": result.get("transport"),
                    "duration_ms": result.get("duration_ms"),
                    "shell": shell,
                }
                payload["data"] = _redact_payload(payload.get("data"))
                payload["error"] = _redact_payload(payload.get("error"))
                return payload
        return {
            "ok": False,
            "data": None,
            "error": {
                "message": "Remote PowerShell execution failed.",
                "details": (last_result or {}).get("stderr") or (last_result or {}).get("stdout"),
            },
            "meta": {
                "ssh": {
                    "host": (last_result or {}).get("host"),
                    "user": (last_result or {}).get("user"),
                    "port": (last_result or {}).get("port"),
                    "transport": (last_result or {}).get("transport"),
                    "duration_ms": (last_result or {}).get("duration_ms"),
                }
            },
        }

    def run(self, script, parameters=None, working_dir=None, timeout=60):
        return self._execute(
            script,
            parameters=parameters,
            capture_text=True,
            working_dir=working_dir,
            timeout=timeout,
        )

    def run_json(self, script_or_command, parameters=None, depth=8, working_dir=None, timeout=60):
        return self._execute(
            script_or_command,
            parameters=parameters,
            depth=depth,
            capture_text=False,
            working_dir=working_dir,
            timeout=timeout,
        )


class PowerShellModuleClient:
    def __init__(self, session=None, pwsh_path="pwsh"):
        self.session = session or PowerShellSession(pwsh_path=pwsh_path)
        self.connected = False

    def _connect_script(self):
        return None

    def _disconnect_script(self):
        return None

    def connect(self):
        if self.connected:
            return True
        script = self._connect_script()
        if script:
            result = self.session.run(script)
            if isinstance(result, dict) and not result.get("ok", True):
                raise PowerShellCommandError("PowerShell connect failed.", output=result)
        self.connected = True
        return True

    def run(self, script, parameters=None, working_dir=None):
        self.connect()
        return self.session.run(script, parameters=parameters, working_dir=working_dir)

    def run_json(self, script, parameters=None, depth=8, working_dir=None):
        return self.session.run_json(script, parameters=parameters, depth=depth, working_dir=working_dir)

    def disconnect(self):
        script = self._disconnect_script()
        if script:
            try:
                result = self.session.run(script)
                if isinstance(result, dict) and not result.get("ok", True):
                    raise PowerShellCommandError("PowerShell disconnect failed.", output=result)
            except PowerShellCommandError:
                pass
        self.connected = False
        return True

    def close(self):
        self.disconnect()
        self.session.close()
