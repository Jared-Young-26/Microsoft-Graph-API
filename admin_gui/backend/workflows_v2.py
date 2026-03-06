from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
import os
import time

from . import control_plane


RISK_ORDER = {"safe": 0, "caution": 1, "danger": 2}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_risk(value: Any) -> str:
    risk = str(value or "safe").strip().lower()
    if risk in ("low", "read", "readonly", "read_only"):
        return "safe"
    if risk in ("medium", "warn", "warning"):
        return "caution"
    if risk in ("high", "dangerous"):
        return "danger"
    if risk not in ("safe", "caution", "danger"):
        return "safe"
    return risk


def _max_risk_level_env() -> str:
    value = os.environ.get("GAS_MAX_RISK_LEVEL") or os.environ.get("MAX_RISK_LEVEL") or "caution"
    return _normalize_risk(value)


def _step_timeout_seconds_env() -> int:
    try:
        value = int(os.environ.get("GAS_WORKFLOW_STEP_TIMEOUT_SECONDS") or 300)
    except Exception:
        value = 300
    return max(5, min(3600, value))


def _sleep_poll_seconds_env() -> float:
    try:
        value = float(os.environ.get("GAS_WORKFLOW_POLL_SECONDS") or 0.25)
    except Exception:
        value = 0.25
    return max(0.05, min(2.0, value))


def _cap_set(value: Any) -> set[str]:
    if value is None:
        return set()
    if isinstance(value, list):
        return {str(v) for v in value if v}
    if isinstance(value, dict):
        return {str(k) for k, enabled in value.items() if enabled}
    return set()


@dataclass(frozen=True)
class WorkflowValidationResult:
    ok: bool
    errors: list[dict[str, Any]]
    warnings: list[dict[str, Any]]
    normalized: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": bool(self.ok),
            "errors": self.errors,
            "warnings": self.warnings,
            "normalized": self.normalized,
        }


def validate_workflow_v2(workflow: Any, *, db_path=None, online_only: bool = True) -> WorkflowValidationResult:
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    if not isinstance(workflow, dict):
        return WorkflowValidationResult(
            ok=False,
            errors=[{"error": "invalid_workflow", "message": "workflow must be a JSON object"}],
            warnings=[],
            normalized={},
        )

    steps = workflow.get("steps")
    if not isinstance(steps, list) or not steps:
        errors.append({"error": "invalid_steps", "message": "workflow.steps must be a non-empty list"})
        steps = []

    max_risk_level = _normalize_risk(workflow.get("max_risk_level") or _max_risk_level_env())
    interactive_scope = bool(workflow.get("interactive_scope"))
    stop_on_failure_default = bool(workflow.get("stop_on_failure", True))
    workflow_agent_id = str(workflow.get("agent_id") or "").strip() or None
    tenant_id = str(workflow.get("tenant_id") or "").strip() or None
    workspace_id = str(workflow.get("workspace_id") or "").strip() or None

    allowed_action_ids = workflow.get("allowed_action_ids")
    allowlist = None
    if isinstance(allowed_action_ids, list) and allowed_action_ids:
        allowlist = {str(a).strip() for a in allowed_action_ids if str(a).strip()}

    agents = control_plane.list_agents(db_path=db_path, limit=5000).get("items") or []
    agent_by_id: dict[str, dict[str, Any]] = {}
    for agent in agents:
        if not isinstance(agent, dict):
            continue
        aid = str(agent.get("agent_id") or "").strip()
        if not aid:
            continue
        status = str(agent.get("status") or "").strip().lower()
        agent_by_id[aid] = {
            "agent": agent,
            "caps": _cap_set(agent.get("capabilities")),
            "status": status,
        }

    normalized_steps: list[dict[str, Any]] = []
    for idx, step in enumerate(steps):
        if not isinstance(step, dict):
            errors.append({"error": "invalid_step", "step_index": idx, "message": "step must be an object"})
            continue

        action_id = str(step.get("action_id") or "").strip()
        if not action_id:
            errors.append({"error": "missing_action_id", "step_index": idx, "message": "step.action_id is required"})
            continue

        if allowlist is not None and action_id not in allowlist:
            errors.append(
                {
                    "error": "action_not_allowlisted",
                    "step_index": idx,
                    "action_id": action_id,
                    "message": "step.action_id is not in allowed_action_ids",
                }
            )
            continue

        if action_id.startswith("terminal.") or action_id.startswith("break_glass."):
            errors.append(
                {
                    "error": "terminal_disallowed",
                    "step_index": idx,
                    "action_id": action_id,
                    "message": "terminal actions are not permitted in workflows",
                }
            )
            continue

        try:
            spec = control_plane.get_action_spec(action_id)
        except KeyError:
            errors.append({"error": "unknown_action_id", "step_index": idx, "action_id": action_id})
            continue
        except Exception as exc:
            errors.append({"error": "catalog_unavailable", "step_index": idx, "message": str(exc)})
            continue

        risk_level = _normalize_risk(spec.get("risk_level"))
        if RISK_ORDER.get(risk_level, 0) > RISK_ORDER.get(max_risk_level, 1):
            errors.append(
                {
                    "error": "risk_disallowed",
                    "step_index": idx,
                    "action_id": action_id,
                    "risk_level": risk_level,
                    "max_risk_level": max_risk_level,
                }
            )
            continue

        if risk_level == "danger" and not interactive_scope:
            errors.append(
                {
                    "error": "interactive_scope_required",
                    "step_index": idx,
                    "action_id": action_id,
                    "message": "interactive_scope=true required for danger actions",
                }
            )
            continue

        required_caps = spec.get("required_capabilities") or []
        required_caps = [str(cap).strip() for cap in required_caps if str(cap).strip()]

        step_agent_id = str(step.get("agent_id") or workflow_agent_id or "").strip() or None
        if step_agent_id:
            agent_entry = agent_by_id.get(step_agent_id)
            if not agent_entry:
                errors.append(
                    {
                        "error": "unknown_agent_id",
                        "step_index": idx,
                        "agent_id": step_agent_id,
                        "action_id": action_id,
                    }
                )
                continue
            if online_only and agent_entry["status"] != "online":
                warnings.append(
                    {
                        "warning": "agent_not_online",
                        "step_index": idx,
                        "agent_id": step_agent_id,
                        "status": agent_entry["status"],
                    }
                )
            caps = agent_entry["caps"]
            missing = [cap for cap in required_caps if cap not in caps]
            if missing:
                errors.append(
                    {
                        "error": "missing_required_capabilities",
                        "step_index": idx,
                        "agent_id": step_agent_id,
                        "action_id": action_id,
                        "missing": missing,
                    }
                )
                continue
        else:
            # Ensure at least one agent supports the required capabilities.
            eligible = []
            for aid, entry in agent_by_id.items():
                if online_only and entry["status"] != "online":
                    continue
                caps = entry["caps"]
                if all(cap in caps for cap in required_caps):
                    eligible.append(aid)
            if not eligible:
                errors.append(
                    {
                        "error": "no_eligible_agent",
                        "step_index": idx,
                        "action_id": action_id,
                        "required_capabilities": required_caps,
                    }
                )
                continue

        normalized_steps.append(
            {
                "step_id": str(step.get("step_id") or f"step-{idx+1}"),
                "action_id": action_id,
                "params": step.get("params") if isinstance(step.get("params"), dict) else {},
                "condition": step.get("condition") or "always",
                "stop_on_failure": bool(step.get("stop_on_failure", stop_on_failure_default)),
                "agent_id": step_agent_id,
                "risk_level": risk_level,
                "required_capabilities": required_caps,
            }
        )

    normalized = {
        "name": str(workflow.get("name") or "workflow"),
        "agent_id": workflow_agent_id,
        "tenant_id": tenant_id,
        "workspace_id": workspace_id,
        "max_risk_level": max_risk_level,
        "interactive_scope": interactive_scope,
        "stop_on_failure": stop_on_failure_default,
        "steps": normalized_steps,
    }
    return WorkflowValidationResult(ok=not errors, errors=errors, warnings=warnings, normalized=normalized)


def compile_workflow_v2(
    text: str,
    *,
    allowed_action_ids: list[str] | None = None,
    agent_id: str | None = None,
    max_risk_level: str | None = None,
    interactive_scope: bool | None = None,
    db_path=None,
) -> dict[str, Any]:
    """Stub compiler: deterministic keyword mapping to allowlisted actions."""

    phrase = str(text or "").strip()
    lowered = phrase.lower()

    allowlist = None
    if allowed_action_ids:
        allowlist = {str(a).strip() for a in allowed_action_ids if str(a).strip()}

    max_risk = _normalize_risk(max_risk_level or _max_risk_level_env())
    interactive = bool(interactive_scope)

    keyword_map = [
        ("whoami", "powershell.whoami_all"),
        ("module inventory", "powershell.module_inventory"),
        ("health check", "powershell.health_check"),
        ("event log", "query.eventlog"),
        ("registry", "query.registry"),
        ("process", "query.processes"),
        ("network probe", "query.network_probe"),
        ("list users", "graph.list_users"),
        ("get user", "graph.get_user"),
        ("connection test", "graph.connection_test"),
        ("mail folders", "graph.exchange.list_mail_folders"),
        ("capture snapshot", "vision.capture_snapshot"),
        ("record segment", "vision.record_segment"),
        ("analyze snapshot", "vision.analyze_snapshot"),
    ]

    chosen: list[str] = []
    for keyword, action_id in keyword_map:
        if keyword in lowered and action_id not in chosen:
            chosen.append(action_id)
    if not chosen:
        # Fallback: do not guess. Return an empty workflow with guidance.
        chosen = []

    steps: list[dict[str, Any]] = []
    for idx, action_id in enumerate(chosen[:12]):
        if allowlist is not None and action_id not in allowlist:
            continue
        try:
            spec = control_plane.get_action_spec(action_id)
        except Exception:
            continue

        risk_level = _normalize_risk(spec.get("risk_level"))
        if RISK_ORDER.get(risk_level, 0) > RISK_ORDER.get(max_risk, 1):
            continue

        params: dict[str, Any] = {}
        schema = spec.get("params_schema") if isinstance(spec, dict) else None
        if isinstance(schema, dict) and isinstance(schema.get("properties"), dict):
            # Seed defaults / required placeholders.
            required = schema.get("required") if isinstance(schema.get("required"), list) else []
            for prop_key, prop_schema in schema["properties"].items():
                if not isinstance(prop_schema, dict):
                    continue
                if "default" in prop_schema:
                    params[prop_key] = prop_schema.get("default")
            for req in required:
                rk = str(req)
                if rk in params:
                    continue
                # Use a simple placeholder; callers can edit.
                params[rk] = f"<{rk}>"

        # Small quality-of-life defaults for some common actions.
        if action_id == "query.eventlog":
            params.setdefault("log_names", ["System"])
        if action_id == "query.registry":
            params.setdefault("hive", "HKLM")
            params.setdefault("path", "SOFTWARE")
        if action_id == "query.files":
            params.setdefault("allowed_roots", ["C:\\\\"])

        steps.append(
            {
                "step_id": f"step-{idx+1}",
                "action_id": action_id,
                "params": params,
                "condition": "always",
                "stop_on_failure": True,
            }
        )

    workflow = {
        "name": "Compiled action pack (v2)",
        "agent_id": str(agent_id).strip() if agent_id else None,
        "max_risk_level": max_risk,
        "interactive_scope": interactive,
        "stop_on_failure": True,
        "allowed_action_ids": sorted(list(allowlist)) if allowlist is not None else None,
        "steps": steps,
        "notes": [
            "This is a deterministic stub compiler (no LLM).",
            "Edit params before running. Only allowlisted actions are emitted.",
        ],
    }
    # Remove null-ish fields for cleanliness.
    workflow = {k: v for k, v in workflow.items() if v is not None}

    validation = validate_workflow_v2(workflow, db_path=db_path)
    return {
        "ok": bool(validation.ok),
        "workflow": workflow,
        "validation": validation.to_dict(),
        "compiled_at": _now_iso(),
    }


def _should_run_condition(condition: Any, *, previous_ok: bool | None) -> bool:
    if condition is None:
        return True
    if isinstance(condition, str):
        c = condition.strip().lower()
    elif isinstance(condition, dict):
        c = str(condition.get("type") or "").strip().lower()
    else:
        c = str(condition).strip().lower()
    if c in ("", "always"):
        return True
    if c in ("if_previous_ok", "prev_ok"):
        return bool(previous_ok)
    if c in ("if_previous_failed", "prev_failed"):
        return previous_ok is False
    return True


def _pick_agent_for_caps(required_caps: list[str], *, db_path=None) -> str:
    # Prefer most recently seen online agent that satisfies required caps.
    agents = control_plane.list_agents(status="online", db_path=db_path, limit=5000).get("items") or []
    candidates = []
    for agent in agents:
        if not isinstance(agent, dict):
            continue
        caps = _cap_set(agent.get("capabilities"))
        if all(cap in caps for cap in required_caps):
            candidates.append(agent)
    if not candidates:
        raise RuntimeError("No eligible agent available for required capabilities.")
    candidates.sort(key=lambda a: str(a.get("last_seen") or a.get("updated_at") or a.get("created_at") or ""), reverse=True)
    agent_id = str(candidates[0].get("agent_id") or "").strip()
    if not agent_id:
        raise RuntimeError("Eligible agent missing agent_id.")
    return agent_id


def run_workflow_v2(workflow: Any, *, db_path=None) -> dict[str, Any]:
    """Run a workflow by dispatching jobs sequentially and polling completion."""

    validation = validate_workflow_v2(workflow, db_path=db_path, online_only=True)
    if not validation.ok:
        return {"ok": False, "error": "validation_failed", "validation": validation.to_dict()}

    normalized = validation.normalized
    steps = normalized.get("steps") if isinstance(normalized.get("steps"), list) else []

    step_timeout = _step_timeout_seconds_env()
    poll_seconds = _sleep_poll_seconds_env()

    run_started = _now_iso()
    previous_ok: bool | None = None
    run_steps: list[dict[str, Any]] = []
    overall_ok = True

    for step in steps:
        condition = step.get("condition")
        should_run = _should_run_condition(condition, previous_ok=previous_ok)
        if not should_run:
            run_steps.append({**step, "status": "skipped"})
            continue

        action_id = str(step.get("action_id") or "")
        required_caps = step.get("required_capabilities") or []
        required_caps = [str(cap).strip() for cap in required_caps if str(cap).strip()]
        agent_id = str(step.get("agent_id") or "").strip() or _pick_agent_for_caps(required_caps, db_path=db_path)

        params = step.get("params") if isinstance(step.get("params"), dict) else {}
        try:
            job = control_plane.enqueue_action_job(
                agent_id=agent_id,
                action_id=action_id,
                params=params,
                requested_by=None,
                interactive_scope=bool(normalized.get("interactive_scope")),
                tenant_id=normalized.get("tenant_id"),
                workspace_id=normalized.get("workspace_id"),
                db_path=db_path,
            )
        except Exception as exc:
            run_steps.append({**step, "agent_id": agent_id, "status": "enqueue_failed", "error": str(exc)})
            overall_ok = False
            previous_ok = False
            if bool(step.get("stop_on_failure", True)):
                break
            continue

        job_id = str(job.get("job_id") or "")
        started = time.monotonic()
        last_detail = None
        while time.monotonic() - started < step_timeout:
            try:
                detail = control_plane.get_job_detail(job_id, db_path=db_path)
                last_detail = detail
            except Exception:
                detail = None
            if isinstance(detail, dict):
                status = str(detail.get("status") or "").lower()
                if status in ("completed", "failed"):
                    break
            time.sleep(poll_seconds)

        if not isinstance(last_detail, dict):
            run_steps.append({**step, "agent_id": agent_id, "job_id": job_id, "status": "unknown"})
            overall_ok = False
            previous_ok = False
            if bool(step.get("stop_on_failure", True)):
                break
            continue

        status = str(last_detail.get("status") or "").lower()
        ok = status == "completed"
        previous_ok = ok
        overall_ok = overall_ok and ok
        run_steps.append(
            {
                **step,
                "agent_id": agent_id,
                "job_id": job_id,
                "status": status,
                "job": last_detail,
            }
        )
        if not ok and bool(step.get("stop_on_failure", True)):
            break

    return {
        "ok": bool(overall_ok),
        "started_at": run_started,
        "finished_at": _now_iso(),
        "workflow": normalized,
        "steps": run_steps,
    }
