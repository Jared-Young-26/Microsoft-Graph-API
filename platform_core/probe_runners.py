from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable, Dict, Optional
import getpass
import platform
import socket
import time

from .snapshot_models import ProbeResult
from .mock_providers import load_fixture

try:
    from microsoft import GraphAPIError
except Exception:  # pragma: no cover - optional import for non-graph contexts
    GraphAPIError = Exception


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _duration_ms(start: float) -> int:
    return int((time.monotonic() - start) * 1000)


def _severity_for(ok: bool, data: Any) -> str:
    if ok:
        if isinstance(data, dict):
            if data.get("missing") or data.get("partial") or data.get("errors"):
                return "warn"
        return "info"
    return "high"


def _classify_error_message(message: str) -> str:
    if not message:
        return "unknown"
    lowered = message.lower()
    if "module" in lowered and ("not found" in lowered or "missing" in lowered or "not recognized" in lowered):
        return "missing_module"
    if "access is denied" in lowered or "insufficient" in lowered or "permission" in lowered or "unauthorized" in lowered:
        return "missing_permission"
    if "token" in lowered or "authentication" in lowered or "aadsts" in lowered:
        return "auth"
    if "dns" in lowered or "resolve" in lowered or "nxdomain" in lowered or "name or service not known" in lowered:
        return "dns"
    if "throttle" in lowered or "too many requests" in lowered or "429" in lowered:
        return "throttling"
    if "timed out" in lowered or "timeout" in lowered or "connection refused" in lowered or "network" in lowered:
        return "network"
    return "unknown"


def _classify_graph_error(exc: Exception) -> str:
    if isinstance(exc, GraphAPIError):
        status = getattr(exc, "status_code", None)
        code = str(getattr(exc, "code", "") or "").lower()
        message = str(exc)
        if status == 401:
            return "auth"
        if status == 403:
            return "missing_permission"
        if status == 429:
            return "throttling"
        if status and status >= 500:
            return "network"
        if "authorization_requestdenied" in code:
            return "missing_permission"
        if "invalidauthenticationtoken" in code:
            return "auth"
        return _classify_error_message(message)
    return _classify_error_message(str(exc))


def _build_meta(source: str, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    meta = {
        "source": source,
        "host": socket.gethostname(),
        "user": getpass.getuser(),
    }
    if extra:
        meta.update(extra)
    return meta


def _resolve_handler(
    probe_id: str,
    context: Dict[str, Any],
    options: Dict[str, Any],
    tool: str,
) -> Optional[Callable[..., Any]]:
    handler = options.get("handler")
    if callable(handler):
        return handler
    handlers = context.get("probe_handlers") or {}
    if isinstance(handlers, dict) and probe_id in handlers:
        return handlers.get(probe_id)
    tool_handlers = context.get(f"{tool}_handlers") or {}
    if isinstance(tool_handlers, dict) and probe_id in tool_handlers:
        return tool_handlers.get(probe_id)
    return None


def run_graph_probe(probe_id: str, subject: Any, context: Dict[str, Any], options: Optional[Dict[str, Any]] = None) -> ProbeResult:
    options = options or {}
    start = time.monotonic()
    collected_at = _now_iso()
    graph = context.get("graph")
    handler = _resolve_handler(probe_id, context, options, "graph")

    if context.get("mock_mode"):
        fixture = load_fixture(probe_id)
        if fixture is not None:
            return ProbeResult(
                probe=probe_id,
                ok=True,
                severity="info",
                error_class=None,
                duration_ms=_duration_ms(start),
                collected_at=collected_at,
                data=fixture,
                evidence_refs=options.get("evidence_refs") or [],
                meta=_build_meta("mock", {"fixture": probe_id}),
            )
        return ProbeResult(
            probe=probe_id,
            ok=False,
            severity="warn",
            error_class="missing_module",
            duration_ms=_duration_ms(start),
            collected_at=collected_at,
            data={"missing": {"fixture": probe_id}},
            evidence_refs=options.get("evidence_refs") or [],
            meta=_build_meta("mock", {"error": "Missing fixture"}),
        )

    try:
        if handler:
            data = handler(subject=subject, context=context, options=options)
        else:
            request = options.get("request") or {}
            method = (request.get("method") or "GET").lower()
            url = request.get("url") or request.get("path")
            if not graph or not url:
                raise RuntimeError("Graph request handler not configured.")
            params = request.get("params")
            json_body = request.get("json") or request.get("body")
            headers = request.get("headers") or {}
            if request.get("paged"):
                data = graph.paged_get(url)
            else:
                response = getattr(graph, method)(url, params=params, json=json_body, headers=headers)
                if response.status_code == 204:
                    data = None
                else:
                    data = response.json()
        ok = True
        error_class = None
        error_message = None
    except Exception as exc:
        ok = False
        error_message = str(exc)
        error_class = _classify_graph_error(exc)
        data = {"missing": {"error": error_message}}

    severity = _severity_for(ok, data)
    return ProbeResult(
        probe=probe_id,
        ok=ok,
        severity=severity,
        error_class=error_class,
        duration_ms=_duration_ms(start),
        collected_at=collected_at,
        data=data,
        evidence_refs=options.get("evidence_refs") or [],
        meta=_build_meta("graph", {"error": error_message} if error_message else None),
    )


def run_powershell_probe(probe_id: str, subject: Any, context: Dict[str, Any], options: Optional[Dict[str, Any]] = None) -> ProbeResult:
    options = options or {}
    start = time.monotonic()
    collected_at = _now_iso()
    session = context.get("powershell")
    handler = _resolve_handler(probe_id, context, options, "powershell")

    if context.get("mock_mode"):
        fixture = load_fixture(probe_id)
        if fixture is not None:
            return ProbeResult(
                probe=probe_id,
                ok=True,
                severity="info",
                error_class=None,
                duration_ms=_duration_ms(start),
                collected_at=collected_at,
                data=fixture,
                evidence_refs=options.get("evidence_refs") or [],
                meta=_build_meta("mock", {"fixture": probe_id}),
            )
        return ProbeResult(
            probe=probe_id,
            ok=False,
            severity="warn",
            error_class="missing_module",
            duration_ms=_duration_ms(start),
            collected_at=collected_at,
            data={"missing": {"fixture": probe_id}},
            evidence_refs=options.get("evidence_refs") or [],
            meta=_build_meta("mock", {"error": "Missing fixture"}),
        )

    try:
        if handler:
            result = handler(subject=subject, context=context, options=options)
        else:
            script = options.get("script") or options.get("command") or options.get("script_or_command")
            if not session or not script:
                raise RuntimeError("PowerShell probe handler not configured.")
            params = options.get("parameters") or options.get("params")
            depth = options.get("depth", 8)
            working_dir = options.get("working_dir")
            result = session.run_json(script, parameters=params, depth=depth, working_dir=working_dir)
        if isinstance(result, dict) and result.get("ok") is False:
            ok = False
            error_message = str(result.get("error", {}).get("message") or result.get("error") or "PowerShell probe failed.")
            error_class = _classify_error_message(error_message)
            data = result.get("data") or {"missing": {"error": error_message}}
        else:
            ok = True
            error_message = None
            error_class = None
            data = result.get("data") if isinstance(result, dict) else result
    except Exception as exc:
        ok = False
        error_message = str(exc)
        error_class = _classify_error_message(error_message)
        data = {"missing": {"error": error_message}}

    severity = _severity_for(ok, data)
    return ProbeResult(
        probe=probe_id,
        ok=ok,
        severity=severity,
        error_class=error_class,
        duration_ms=_duration_ms(start),
        collected_at=collected_at,
        data=data,
        evidence_refs=options.get("evidence_refs") or [],
        meta=_build_meta("powershell", {"error": error_message} if error_message else None),
    )


def run_local_probe(probe_id: str, subject: Any, context: Dict[str, Any], options: Optional[Dict[str, Any]] = None) -> ProbeResult:
    options = options or {}
    start = time.monotonic()
    collected_at = _now_iso()
    handler = _resolve_handler(probe_id, context, options, "local")

    if context.get("mock_mode"):
        fixture = load_fixture(probe_id)
        if fixture is not None:
            return ProbeResult(
                probe=probe_id,
                ok=True,
                severity="info",
                error_class=None,
                duration_ms=_duration_ms(start),
                collected_at=collected_at,
                data=fixture,
                evidence_refs=options.get("evidence_refs") or [],
                meta=_build_meta("mock", {"fixture": probe_id}),
            )

    try:
        if handler:
            data = handler(subject=subject, context=context, options=options)
        else:
            data = {
                "hostname": socket.gethostname(),
                "platform": platform.platform(),
                "python": platform.python_version(),
            }
        ok = True
        error_message = None
        error_class = None
    except Exception as exc:
        ok = False
        error_message = str(exc)
        error_class = _classify_error_message(error_message)
        data = {"missing": {"error": error_message}}

    severity = _severity_for(ok, data)
    return ProbeResult(
        probe=probe_id,
        ok=ok,
        severity=severity,
        error_class=error_class,
        duration_ms=_duration_ms(start),
        collected_at=collected_at,
        data=data,
        evidence_refs=options.get("evidence_refs") or [],
        meta=_build_meta("local", {"error": error_message} if error_message else None),
    )
