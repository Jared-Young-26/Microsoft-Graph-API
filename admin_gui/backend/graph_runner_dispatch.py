from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
import os
import time

from . import control_plane


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_int(value: Any, default: int) -> int:
    if value is None:
        return default
    try:
        return int(value)
    except Exception:
        return default


def _runner_mode() -> str:
    return str(os.environ.get("GAS_GRAPH_RUNNER_MODE") or "auto").strip().lower()


def _runner_agent_override() -> str | None:
    value = os.environ.get("GAS_GRAPH_RUNNER_AGENT_ID")
    value = str(value).strip() if value else ""
    return value or None


def _runner_timeout_seconds() -> int:
    return max(5, min(600, _parse_int(os.environ.get("GAS_GRAPH_RUNNER_TIMEOUT_SECONDS"), 45)))


def map_service_action_to_runner_action_id(service: str, action: str) -> str | None:
    """Map UI service/action to graph runner action_id."""
    if service == "entra" and action == "list_users":
        return "graph.list_users"
    if service == "entra" and action == "get_user":
        return "graph.get_user"
    if service == "exchange" and action == "list_mail_folders":
        return "graph.exchange.list_mail_folders"
    if service == "system" and action == "graph_check":
        return "graph.connection_test"
    return None


@dataclass
class GraphRunnerError(Exception):
    """Base error for graph runner dispatch failures."""

    message: str
    status_code: int = 502
    detail: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return self.message

    def to_payload(self, *, service: str, action: str) -> dict[str, Any]:
        return {
            "ok": False,
            "failure_source": "control_plane_graph_runner",
            "failure_outcome": "error",
            "error_class": "runner",
            "error": self.message,
            "detail": self.detail or None,
            "status_code": int(self.status_code or 502),
            "service": service,
            "action": action,
            "timestamp": _now_iso(),
        }


class GraphRunnerUnavailableError(GraphRunnerError):
    """Raised when no eligible runner is available."""

    def __init__(self, message: str, detail: dict[str, Any] | None = None):
        super().__init__(message=message, status_code=503, detail=detail or {})


class GraphRunnerTimeoutError(GraphRunnerError):
    """Raised when a job does not complete in time."""

    def __init__(self, message: str, detail: dict[str, Any] | None = None):
        super().__init__(message=message, status_code=504, detail=detail or {})


class GraphRunnerJobFailedError(GraphRunnerError):
    """Raised when a runner job fails."""

    def __init__(self, message: str, detail: dict[str, Any] | None = None):
        super().__init__(message=message, status_code=502, detail=detail or {})


def _agent_supports(agent: dict[str, Any], required_caps: list[str]) -> bool:
    caps = agent.get("capabilities") or []
    if not isinstance(caps, list):
        return False
    cap_set = {str(c) for c in caps if c}
    return all(str(req) in cap_set for req in required_caps)


def _pick_runner_agent(required_caps: list[str], *, db_path=None) -> dict[str, Any] | None:
    agents = control_plane.list_agents(status="online", db_path=db_path, limit=1000).get("items") or []
    candidates = [a for a in agents if isinstance(a, dict) and _agent_supports(a, required_caps)]
    if not candidates:
        return None
    candidates.sort(key=lambda a: str(a.get("last_seen") or a.get("updated_at") or a.get("created_at") or ""), reverse=True)
    return candidates[0]


def _resolve_runner_agent(required_caps: list[str], *, db_path=None) -> dict[str, Any]:
    override = _runner_agent_override()
    if override:
        agents = control_plane.list_agents(status=None, db_path=db_path, limit=2000).get("items") or []
        for agent in agents:
            if not isinstance(agent, dict):
                continue
            if str(agent.get("agent_id") or "") != override:
                continue
            if not _agent_supports(agent, required_caps):
                raise GraphRunnerUnavailableError(
                    "Runner agent does not satisfy required capabilities.",
                    detail={"agent_id": override, "required_capabilities": required_caps},
                )
            return agent
        raise GraphRunnerUnavailableError("Runner agent not found.", detail={"agent_id": override})

    agent = _pick_runner_agent(required_caps, db_path=db_path)
    if not agent:
        raise GraphRunnerUnavailableError(
            "No online agent advertises required Graph capabilities.",
            detail={"required_capabilities": required_caps},
        )
    return agent


def should_dispatch_via_runner(service: str, action: str) -> bool:
    """Return True when Graph runner should handle this service/action."""
    action_id = map_service_action_to_runner_action_id(service, action)
    if not action_id:
        return False
    mode = _runner_mode()
    if mode in ("off", "disabled", "local"):
        return False
    if mode in ("auto", "controlplane", "control_plane", "runner"):
        return True
    return True


def dispatch_runner_action(
    *,
    service: str,
    action: str,
    params: dict[str, Any],
    risk_level: str = "safe",
    requested_by: str | None = None,
    timeout_seconds: int | None = None,
    db_path=None,
) -> Any:
    """Dispatch an action to a graph runner agent and return the action result payload."""

    action_id = map_service_action_to_runner_action_id(service, action)
    if not action_id:
        raise GraphRunnerUnavailableError("No graph runner mapping for action.", detail={"service": service, "action": action})

    required_caps = ["graph.core"]
    agent = _resolve_runner_agent(required_caps, db_path=db_path)
    agent_id = str(agent.get("agent_id") or "")
    if not agent_id:
        raise GraphRunnerUnavailableError("Runner agent missing agent_id.", detail={"agent": agent})

    jid = control_plane.enqueue_job(
        agent_id=agent_id,
        action_id=action_id,
        params=params,
        risk_level=risk_level,
        requested_by=requested_by,
        db_path=db_path,
    ).get("job_id")
    if not jid:
        raise GraphRunnerError("Failed to enqueue runner job.", status_code=500, detail={"agent_id": agent_id, "action_id": action_id})

    timeout = int(timeout_seconds or _runner_timeout_seconds())
    start = time.monotonic()
    last_detail = None
    while time.monotonic() - start < timeout:
        detail = control_plane.get_job_detail(str(jid), db_path=db_path)
        last_detail = detail
        status = str(detail.get("status") or "").lower()
        if status in ("completed", "failed"):
            break
        time.sleep(0.25)

    if not last_detail:
        raise GraphRunnerTimeoutError("Runner job timed out.", detail={"job_id": jid, "timeout_seconds": timeout})

    status = str(last_detail.get("status") or "").lower()
    if status not in ("completed", "failed"):
        raise GraphRunnerTimeoutError(
            "Runner job timed out.",
            detail={"job_id": jid, "timeout_seconds": timeout, "status": status},
        )

    result = last_detail.get("result") if isinstance(last_detail.get("result"), dict) else None
    if status == "failed":
        stderr = result.get("stderr") if result else None
        error_payload = last_detail.get("error")
        raise GraphRunnerJobFailedError(
            "Runner job failed.",
            detail={
                "job_id": jid,
                "agent_id": agent_id,
                "action_id": action_id,
                "stderr": stderr,
                "error": error_payload,
                "result": result.get("result") if isinstance(result, dict) else None,
            },
        )

    if not result:
        raise GraphRunnerError("Runner job completed without result payload.", status_code=502, detail={"job_id": jid, "agent_id": agent_id, "action_id": action_id})

    return result.get("result")

