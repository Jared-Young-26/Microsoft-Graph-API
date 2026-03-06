from pathlib import Path
from datetime import datetime, timezone
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request, Response, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Any
from dataclasses import dataclass, field
import asyncio
import hashlib
import io
import json
import os
import sqlite3
import subprocess
import secrets
import shutil
import getpass
import zipfile
try:
    import pty
except Exception:
    pty = None

from .core import (
    STATE,
    dispatch_task,
    record_graph_trace,
    list_graph_traces,
    graph_reliability_summary,
    _read_audit_log,
    get_action_source,
    _list_action_snapshots,
    _get_action_snapshot,
    _diff_action_snapshots,
    _list_engine_snapshots,
    _get_engine_snapshot,
    _list_snapshot_entities,
    _diff_engine_snapshots,
    _resolve_snapshot_subject,
    _list_snapshot_events,
    _list_symptom_templates,
    _get_symptom_template,
    _plan_symptom_tier0,
    _create_investigation,
    _list_investigations,
    _get_investigation,
    _update_investigation,
    _add_investigation_note,
    _add_investigation_event,
    _get_investigation_context,
    _update_investigation_context,
    _create_incident,
    _list_incidents,
    _get_incident,
    _update_incident,
    _link_incident_snapshot,
    _link_incident_event,
    _build_incident_graph,
    _build_incident_timeline,
    _get_incident_report,
    _update_incident_report,
    _render_incident_report,
    _list_golden_snapshots,
    _set_golden_snapshot,
    _clear_golden_snapshot,
    _diff_golden_snapshot,
    _extract_action_payload,
    _capture_snapshots,
    _finalize_draft_snapshot,
    _system_status_summary,
    _ingest_vision_u_eye_visual_signal,
    _list_vision_u_eye_visual_signals,
    _maybe_ingest_vision_u_eye_job_result,
    ensure_snapshot_scheduler,
    ensure_onedrive_cache_warmup_scheduler,
    ARTIFACTS_DIR,
)
from platform_core.interpreter import interpret_response
from platform_core.graph_error_transparency import build_graph_error_response
from microsoft import GraphAPIError, PowerShellCommandError, set_trace_context, reset_trace_context
from . import control_plane
from .graph_runner_dispatch import GraphRunnerError
from .artifact_retention import ensure_artifact_retention_reaper
from . import workflows_v2

ROOT = Path(__file__).resolve().parents[1]

app = FastAPI(title="Graph Admin Studio API")
ensure_snapshot_scheduler()
ensure_onedrive_cache_warmup_scheduler()
control_plane.ensure_lease_reaper()
ensure_artifact_retention_reaper(ARTIFACTS_DIR)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://127.0.0.1", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"] ,
    allow_headers=["*"] ,
)


class TaskRequest(BaseModel):
    """Task Request."""
    service: str
    action: str
    params: dict | None = None
    target: dict | None = None


class ConfigUpdate(BaseModel):
    """Config Update."""
    tenant_id: str | None = None
    client_id: str | None = None
    client_secret: str | None = None
    graph_user_id: str | None = None
    onedrive_drive_id: str | None = None
    spo_admin_url: str | None = None
    ps_user_principal_name: str | None = None
    ps_org: str | None = None
    ps_auth_mode: str | None = None
    azure_tenant_id: str | None = None
    azure_subscription_id: str | None = None
    use_keychain: bool | None = None
    config_lock: bool | None = None
    reload: bool | None = False


class ConfigExportRequest(BaseModel):
    """Config Export Request."""
    passphrase: str | None = None
    use_keychain: bool | None = False


class ConfigImportRequest(BaseModel):
    """Config Import Request."""
    passphrase: str | None = None
    payload: dict | None = None


class AgentRegisterRequest(BaseModel):
    """Agent registration request."""

    agent_id: str | None = None
    agent_token: str | None = None
    pairing_code: str | None = None
    rotate_token: bool | None = None
    tenant_id: str | None = None
    workspace_id: str | None = None
    name: str | None = None
    hostname: str | None = None
    os: str | None = None
    arch: str | None = None
    version: str | None = None
    capabilities: Any | None = None
    labels: Any | None = None
    status: str | None = None


class AgentHeartbeatRequest(BaseModel):
    """Agent heartbeat request."""

    agent_id: str
    agent_token: str | None = None
    status: str | None = None
    capabilities: Any | None = None
    labels: Any | None = None
    tenant_id: str | None = None
    workspace_id: str | None = None


class JobResultRequest(BaseModel):
    """Job result request."""

    job_id: str
    status: str | None = None
    result: Any | None = None
    stdout: str | None = None
    stderr: str | None = None
    exit_code: int | None = None
    artifacts: Any | None = None
    duration_ms: int | None = None
    error: Any | None = None


class JobEnqueueRequest(BaseModel):
    """Enqueue a control plane job (human/UI)."""

    agent_id: str
    action_id: str
    params: Any | None = None
    tenant_id: str | None = None
    workspace_id: str | None = None
    interactive_scope: bool | None = None


class PairingCodeCreateRequest(BaseModel):
    """Create a one-time pairing code for bootstrapping an agent."""

    tenant_id: str | None = None
    workspace_id: str | None = None
    ttl_seconds: int | None = None


class WorkflowValidateRequest(BaseModel):
    """Validate an Action Pack v2 workflow."""

    workflow: Any
    online_only: bool | None = None


class WorkflowCompileRequest(BaseModel):
    """Compile natural language text into an Action Pack v2 workflow (stub)."""

    text: str
    allowed_action_ids: list[str] | None = None
    agent_id: str | None = None
    max_risk_level: str | None = None
    interactive_scope: bool | None = None


class WorkflowRunRequest(BaseModel):
    """Run an Action Pack v2 workflow."""

    workflow: Any


class TerminalStartRequest(BaseModel):
    """Terminal start request."""

    interactive_scope: bool | None = None
    ttl_seconds: int | None = None


def _agent_token_from_request(request: Request) -> str | None:
    """Extract agent token from request headers."""
    auth = request.headers.get("authorization") or ""
    if isinstance(auth, str) and auth.lower().startswith("bearer "):
        return auth.split(" ", 1)[1].strip() or None
    token = request.headers.get("x-agent-token") or request.headers.get("X-Agent-Token")
    return str(token).strip() if token else None


def _require_agent_auth(agent_id: str, token: str | None) -> None:
    """Require valid agent auth."""
    if not token or not control_plane.authenticate_agent(agent_id, token):
        raise HTTPException(status_code=401, detail="Unauthorized")


def _require_interactive_scope(payload: dict | None) -> None:
    if not isinstance(payload, dict) or payload.get("interactive_scope") is not True:
        raise HTTPException(status_code=403, detail="interactive_scope=true required")


def _reject_job_tokens(request: Request) -> None:
    # Terminal endpoints are human-only; job/agent tokens are rejected.
    token = _agent_token_from_request(request)
    if token:
        raise HTTPException(status_code=403, detail="Terminal endpoints reject job tokens")
    if request.headers.get("x-job-token") or request.headers.get("X-Job-Token"):
        raise HTTPException(status_code=403, detail="Terminal endpoints reject job tokens")


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed
    except Exception:
        return None


@dataclass
class _TerminalHub:
    session_id: str
    agent_id: str
    agent_ws: WebSocket | None = None
    operator_ws: set[WebSocket] = field(default_factory=set)
    pending_commands: list[dict[str, Any]] = field(default_factory=list)


_TERMINAL_HUBS: dict[str, _TerminalHub] = {}


def _terminal_hub(session_id: str, agent_id: str) -> _TerminalHub:
    hub = _TERMINAL_HUBS.get(session_id)
    if hub and hub.agent_id == agent_id:
        return hub
    hub = _TerminalHub(session_id=session_id, agent_id=agent_id)
    _TERMINAL_HUBS[session_id] = hub
    return hub


@app.post("/api/agents/register")
def register_agent(payload: AgentRegisterRequest):
    """Register agent."""
    try:
        return control_plane.register_agent(payload.model_dump())
    except Exception as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})


@app.post("/api/pairing-codes")
def create_pairing_code(payload: PairingCodeCreateRequest):
    """Create a one-time pairing code (operator/UI)."""
    try:
        data = control_plane.create_pairing_code(
            tenant_id=payload.tenant_id,
            workspace_id=payload.workspace_id,
            ttl_seconds=payload.ttl_seconds,
        )
        return {"ok": True, "data": data}
    except Exception as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})


@app.post("/api/agents/heartbeat")
def agent_heartbeat(payload: AgentHeartbeatRequest, request: Request):
    """Agent heartbeat."""
    token = _agent_token_from_request(request) or payload.agent_token
    _require_agent_auth(payload.agent_id, token)
    try:
        return control_plane.heartbeat_agent(
            payload.agent_id,
            status="online",
            capabilities=payload.capabilities,
            labels=payload.labels,
            tenant_id=payload.tenant_id,
            workspace_id=payload.workspace_id,
        )
    except KeyError as exc:
        return JSONResponse(status_code=404, content={"ok": False, "error": str(exc)})
    except Exception as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})


@app.get("/api/agents")
def list_agents(
    status: str | None = None,
    query: str | None = None,
    tenant_id: str | None = None,
    workspace_id: str | None = None,
    limit: int | None = 200,
    offset: int | None = 0,
):
    """List agents."""
    try:
        data = control_plane.list_agents(
            status=status,
            query=query,
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            limit=int(limit or 200),
            offset=int(offset or 0),
        )
        return {"ok": True, "data": data}
    except Exception as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})


@app.get("/api/capabilities/catalog")
def capabilities_catalog():
    """List known actions and required capabilities."""
    try:
        from agent.catalog import build_capabilities_catalog

        return {"ok": True, "data": build_capabilities_catalog()}
    except Exception as exc:
        return JSONResponse(status_code=500, content={"ok": False, "error": str(exc)})


@app.get("/install/agent.zip")
def download_agent_zip():
    """Download the agent code as a zip (v0 bootstrap helper)."""

    agent_root = (ROOT.parent / "agent").resolve()
    if not agent_root.exists():
        raise HTTPException(status_code=404, detail="Agent folder not found")

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in agent_root.rglob("*"):
            if path.is_dir():
                continue
            if "__pycache__" in path.parts:
                continue
            if path.suffix.lower() == ".pyc":
                continue
            if path.name == ".DS_Store":
                continue
            rel = path.relative_to(ROOT.parent)
            zf.write(path, arcname=str(rel).replace("\\", "/"))
    headers = {"Content-Disposition": 'attachment; filename="agent.zip"'}
    return Response(content=buf.getvalue(), media_type="application/zip", headers=headers)


@app.get("/api/agents/{agent_id}/next-job")
def agent_next_job(agent_id: str, request: Request, lease_seconds: int | None = None):
    """Lease next queued job for agent."""
    token = _agent_token_from_request(request)
    _require_agent_auth(agent_id, token)
    try:
        job = control_plane.lease_next_job(agent_id, lease_seconds=int(lease_seconds or 900))
        if not job:
            return Response(status_code=204)
        return job
    except Exception as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})


@app.post("/api/agents/{agent_id}/job-result")
def agent_job_result(agent_id: str, payload: JobResultRequest, request: Request):
    """Record job result for agent."""
    token = _agent_token_from_request(request)
    _require_agent_auth(agent_id, token)
    try:
        data = control_plane.record_job_result(
            agent_id,
            payload.job_id,
            status=payload.status,
            result=payload.result,
            stdout=payload.stdout,
            stderr=payload.stderr,
            exit_code=payload.exit_code,
            artifacts=payload.artifacts,
            duration_ms=payload.duration_ms,
            error=payload.error,
        )
        _maybe_ingest_vision_u_eye_job_result(
            agent_id=agent_id,
            job_id=payload.job_id,
            action_id=str(data.get("action_id") or ""),
            status=str(data.get("status") or payload.status or ""),
            result=payload.result,
            artifacts=payload.artifacts,
        )
        return {"ok": True, "data": data}
    except KeyError as exc:
        return JSONResponse(status_code=404, content={"ok": False, "error": str(exc)})
    except PermissionError as exc:
        return JSONResponse(status_code=403, content={"ok": False, "error": str(exc)})
    except Exception as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})


@app.post("/api/jobs/enqueue")
def enqueue_job(payload: JobEnqueueRequest):
    """Enqueue a control plane job (human/UI)."""
    try:
        job = control_plane.enqueue_action_job(
            agent_id=payload.agent_id,
            action_id=payload.action_id,
            params=payload.params,
            requested_by=getpass.getuser(),
            interactive_scope=bool(payload.interactive_scope),
            tenant_id=payload.tenant_id,
            workspace_id=payload.workspace_id,
        )
        return {"ok": True, "data": job}
    except KeyError as exc:
        return JSONResponse(status_code=404, content={"ok": False, "error": str(exc)})
    except PermissionError as exc:
        return JSONResponse(status_code=403, content={"ok": False, "error": str(exc)})
    except ValueError as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})
    except Exception as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})


@app.post("/api/actionpacks/v2/validate")
def validate_action_pack_v2(payload: WorkflowValidateRequest):
    """Validate an Action Pack v2 workflow."""
    try:
        result = workflows_v2.validate_workflow_v2(
            payload.workflow,
            online_only=bool(payload.online_only) if payload.online_only is not None else True,
        )
        return {"ok": True, "data": result.to_dict()}
    except Exception as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})


@app.post("/api/actionpacks/v2/compile")
def compile_action_pack_v2(payload: WorkflowCompileRequest):
    """Compile natural language text into an Action Pack v2 workflow (stub)."""
    try:
        data = workflows_v2.compile_workflow_v2(
            payload.text,
            allowed_action_ids=payload.allowed_action_ids,
            agent_id=payload.agent_id,
            max_risk_level=payload.max_risk_level,
            interactive_scope=payload.interactive_scope,
        )
        return {"ok": True, "data": data}
    except Exception as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})


@app.post("/api/actionpacks/v2/run")
def run_action_pack_v2(payload: WorkflowRunRequest):
    """Run an Action Pack v2 workflow."""
    try:
        data = workflows_v2.run_workflow_v2(payload.workflow)
        return {"ok": True, "data": data}
    except Exception as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})


@app.post("/api/terminal/{agent_id}/start")
def start_terminal_session(agent_id: str, payload: TerminalStartRequest, request: Request):
    """Start a break-glass terminal session (human-only)."""
    _reject_job_tokens(request)
    body = payload.model_dump() if payload else {}
    _require_interactive_scope(body)

    operator = getpass.getuser()
    allowlist = str(os.environ.get("GAS_TERMINAL_ALLOWED_OPERATORS") or "").strip()
    if allowlist:
        allowed = {part.strip() for part in allowlist.split(",") if part.strip()}
        if operator not in allowed and "*" not in allowed:
            return JSONResponse(status_code=403, content={"ok": False, "error": "Operator not allowed"})
    try:
        host = request.client.host if request.client else ""
    except Exception:
        host = ""
    if host and host not in ("127.0.0.1", "::1"):
        return JSONResponse(status_code=403, content={"ok": False, "error": "Terminal start requires localhost"})
    ttl = int(body.get("ttl_seconds") or 900)
    try:
        session = control_plane.create_terminal_session(agent_id=agent_id, operator=operator, ttl_seconds=ttl)
        return {
            "ok": True,
            "data": {
                **session,
                "ws_path": f"/ws/terminal/{session['session_id']}",
            },
        }
    except KeyError as exc:
        return JSONResponse(status_code=404, content={"ok": False, "error": str(exc)})
    except PermissionError as exc:
        return JSONResponse(status_code=403, content={"ok": False, "error": str(exc)})
    except ValueError as exc:
        return JSONResponse(status_code=409, content={"ok": False, "error": str(exc)})
    except Exception as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})


@app.get("/api/terminal/{agent_id}/next-session")
def agent_next_terminal_session(agent_id: str, request: Request):
    """Agent: lease next pending terminal session (outbound websocket follows)."""
    token = _agent_token_from_request(request)
    _require_agent_auth(agent_id, token)
    try:
        session = control_plane.lease_next_terminal_session(agent_id)
        if not session:
            return Response(status_code=204)
        return {"ok": True, "data": session}
    except Exception as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})


@app.get("/api/jobs")
def list_jobs(
    agent_id: str | None = None,
    status: str | None = None,
    query: str | None = None,
    tenant_id: str | None = None,
    workspace_id: str | None = None,
    limit: int | None = 200,
    offset: int | None = 0,
):
    """List jobs."""
    try:
        data = control_plane.list_jobs(
            agent_id=agent_id,
            status=status,
            query=query,
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            limit=int(limit or 200),
            offset=int(offset or 0),
        )
        return {"ok": True, "data": data}
    except Exception as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})


@app.get("/api/jobs/{job_id}")
def get_job(job_id: str):
    """Get job detail."""
    try:
        data = control_plane.get_job_detail(job_id)
        return {"ok": True, "data": data}
    except KeyError as exc:
        return JSONResponse(status_code=404, content={"ok": False, "error": str(exc)})
    except Exception as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})


@app.get("/api/status")
def status():
    """Run status."""
    return STATE.status()


@app.get("/api/status/summary")
def status_summary():
    """Run status summary."""
    return _system_status_summary()


@app.get("/api/config")
def get_config():
    """Get config."""
    return STATE.get_config_public()


@app.post("/api/config")
def update_config(config: ConfigUpdate):
    """Update config."""
    payload = config.model_dump()
    reload_flag = payload.pop("reload", False)
    try:
        data = STATE.update_config(payload)
        if reload_flag:
            STATE.reload()
        return {"ok": True, "data": data}
    except Exception as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})


@app.post("/api/config/reload")
def reload_config():
    """Run reload config."""
    STATE.reload()
    return {"ok": True, "data": STATE.get_config_public()}


@app.get("/api/audit")
def get_audit(
    service: str | None = None,
    action: str | None = None,
    ok: str | None = None,
    user: str | None = None,
    since: str | None = None,
    until: str | None = None,
    query: str | None = None,
    limit: int | None = 200,
    offset: int | None = 0,
):
    """Get audit."""
    data = _read_audit_log(
        service=service,
        action=action,
        ok=ok,
        user=user,
        since=since,
        until=until,
        query=query,
        limit=limit,
        offset=offset,
    )
    return {"ok": True, "data": data}


@app.post("/api/artifacts/upload")
async def upload_artifact(
    request: Request,
    agent_id: str = Form(...),
    job_id: str | None = Form(None),
    type: str | None = Form(None),
    file: UploadFile = File(...),
):
    """Upload artifact (agent-authenticated)."""
    token = _agent_token_from_request(request)
    _require_agent_auth(agent_id, token)
    artifact_id = secrets.token_hex(16)
    suffix = ""
    try:
        suffix = Path(file.filename or "").suffix
    except Exception:
        suffix = ""
    if not suffix or len(suffix) > 12:
        suffix = ".zip"
    stored_filename = f"{artifact_id}{suffix}"
    dest = ARTIFACTS_DIR / stored_filename
    sha = hashlib.sha256()
    size_bytes = 0
    try:
        with dest.open("wb") as handle:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                handle.write(chunk)
                sha.update(chunk)
                size_bytes += len(chunk)
    except Exception as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})
    sha256 = sha.hexdigest()
    try:
        control_plane.record_artifact(
            artifact_id=artifact_id,
            agent_id=agent_id,
            job_id=str(job_id).strip() if job_id else None,
            type=str(type).strip() if type else (file.content_type or None),
            filename=stored_filename,
            sha256=sha256,
            size_bytes=size_bytes,
            storage_path=stored_filename,
        )
    except Exception as exc:
        try:
            dest.unlink(missing_ok=True)  # type: ignore[arg-type]
        except TypeError:
            try:
                if dest.exists():
                    dest.unlink()
            except Exception:
                pass
        except Exception:
            pass
        return JSONResponse(status_code=500, content={"ok": False, "error": "artifact_record_failed", "detail": str(exc)})
    return {
        "ok": True,
        "data": {
            "artifact_id": artifact_id,
            "filename": stored_filename,
            "sha256": sha256,
            "size_bytes": size_bytes,
            "url": f"/api/artifacts/{stored_filename}",
        },
    }


@app.get("/api/artifacts/{filename}")
def get_artifact(filename: str):
    """Get artifact."""
    path = ARTIFACTS_DIR / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="Artifact not found")
    return FileResponse(path, filename=path.name)


@app.post("/api/config/export")
def export_config(payload: ConfigExportRequest):
    """Export config."""
    data = payload.model_dump()
    try:
        blob = STATE.export_config_encrypted(passphrase=data.get("passphrase"), use_keychain=bool(data.get("use_keychain")))
        return {"ok": True, "data": blob}
    except Exception as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})


@app.post("/api/config/import")
def import_config(payload: ConfigImportRequest):
    """Import config."""
    data = payload.model_dump()
    try:
        blob = data.get("payload") or {}
        result = STATE.import_config_encrypted(blob, passphrase=data.get("passphrase"))
        return {"ok": True, "data": result}
    except Exception as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})


@app.post("/api/task")
def run_task(task: TaskRequest):
    """Run task."""
    params = dict(task.params or {})
    ui_request_id = None
    if "_ui_request_id" in params:
        ui_request_id = str(params.pop("_ui_request_id"))
    token = set_trace_context(
        {
            "ui_request_id": ui_request_id,
            "service": task.service,
            "action": task.action,
            "trace_hook": record_graph_trace,
        }
    )
    try:
        data = dispatch_task(task.service, task.action, params, task.target)
        normalized = None
        try:
            normalized_payload = _extract_action_payload(data)
            normalized = interpret_response(
                task.service,
                task.action,
                normalized_payload,
                source=get_action_source(task.service, task.action),
            )
        except Exception:
            normalized = None
        return {"ok": True, "data": data, "normalized": normalized, "target": task.target}
    except GraphAPIError as exc:
        response = build_graph_error_response(exc, service=task.service, action=task.action)
        hint = None
        if response.get("error_class") == "missing_permission":
            hint = "App permission missing or admin consent not granted. Add the permission in Entra and grant admin consent."
        response["hint"] = hint
        status_code = exc.status_code
        if status_code is None:
            status_code = response.get("status_code")
        if status_code is None:
            failure_source = response.get("failure_source") or response.get("failure_origin")
            failure_outcome = response.get("failure_outcome")
            if failure_source == "dashboard_config_error":
                status_code = 400
            elif failure_source == "dashboard_http":
                status_code = 504 if failure_outcome == "timeout" else 502
            elif failure_source == "dashboard_parse_error":
                status_code = 502
            elif failure_source in ("dashboard_guardrail", "dashboard_retry_policy") and failure_outcome == "circuit_open":
                status_code = 503
            else:
                status_code = 502
        return JSONResponse(status_code=status_code, content=response)
    except GraphRunnerError as exc:
        return JSONResponse(
            status_code=int(exc.status_code or 502),
            content=exc.to_payload(service=task.service, action=task.action),
        )
    except sqlite3.Error as exc:
        # Surface SQLite/schema issues as a 500 so operators don't confuse them with Graph failures.
        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "failure_source": "dashboard_internal_error",
                "failure_outcome": "error",
                "error_class": "db_schema",
                "error": "Cache schema out of date; migration required.",
                "detail": {"message": str(exc)},
                "status_code": 500,
                "service": task.service,
                "action": task.action,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )
    except PowerShellCommandError as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc), "detail": exc.output})
    except Exception as exc:
        message = str(exc)
        lowered = message.lower()
        if isinstance(exc, ValueError):
            return JSONResponse(status_code=400, content={"ok": False, "error": message, "status_code": 400})
        if "missing microsoft configuration variables" in lowered or "missing graph" in lowered:
            return JSONResponse(
                status_code=400,
                content={
                    "ok": False,
                    "failure_source": "dashboard_config_error",
                    "failure_outcome": "retry_exhausted",
                    "failure_origin": "dashboard_config_error",
                    "error_class": "dashboard_config_error",
                    "error": message,
                    "status_code": 400,
                    "service": task.service,
                    "action": task.action,
                },
            )
        if "graph request handler not configured" in lowered:
            return JSONResponse(
                status_code=400,
                content={
                    "ok": False,
                    "failure_source": "dashboard_config_error",
                    "failure_outcome": "retry_exhausted",
                    "failure_origin": "dashboard_config_error",
                    "error_class": "dashboard_config_error",
                    "error": message,
                    "status_code": 400,
                    "service": task.service,
                    "action": task.action,
                },
            )
        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "failure_source": "dashboard_internal_error",
                "failure_outcome": "error",
                "error_class": "dashboard_internal_error",
                "error": message,
                "detail": {"type": exc.__class__.__name__},
                "status_code": 500,
                "service": task.service,
                "action": task.action,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )
    finally:
        if token is not None:
            reset_trace_context(token)


@app.post("/ingest/perception")
def ingest_vision_u_eye_perception(payload: dict):
    """Ingest vision u eye perception."""
    try:
        data = _ingest_vision_u_eye_visual_signal(payload)
        return data
    except Exception as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})


@app.post("/api/signals/visual")
def ingest_visual_signal_api(payload: dict):
    """Ingest visual signal api."""
    try:
        data = _ingest_vision_u_eye_visual_signal(payload)
        return data
    except Exception as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})


@app.get("/api/signals/visual")
def list_visual_signals_api(
    endpoint_id: str | None = None,
    session_id: str | None = None,
    canonical_id: str | None = None,
    since: str | None = None,
    until: str | None = None,
    limit: int = 50,
):
    """List visual signals api."""
    try:
        data = _list_vision_u_eye_visual_signals(
            endpoint_id=endpoint_id,
            session_id=session_id,
            canonical_id=canonical_id,
            since=since,
            until=until,
            limit=limit,
        )
        return {"ok": True, "data": data}
    except Exception as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})


@app.get("/api/debug/traces")
def debug_traces(
    limit: int = 50,
    ui_request_id: str | None = None,
    request_id: str | None = None,
):
    """Run debug traces."""
    try:
        data = list_graph_traces(limit=limit, ui_request_id=ui_request_id, request_id=request_id)
        return {"ok": True, "data": data}
    except Exception as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})


@app.get("/api/debug/traces/{ui_request_id}")
def debug_traces_by_ui(ui_request_id: str, limit: int = 200):
    """Run debug traces by ui."""
    try:
        data = list_graph_traces(limit=limit, ui_request_id=ui_request_id, request_id=None)
        return {"ok": True, "data": data}
    except Exception as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})


@app.get("/api/debug/traces/by-graph-request/{request_id}")
def debug_traces_by_graph_request(request_id: str, limit: int = 200):
    """Run debug traces by graph request."""
    try:
        data = list_graph_traces(limit=limit, ui_request_id=None, request_id=request_id)
        return {"ok": True, "data": data}
    except Exception as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})


@app.get("/api/debug/graph-reliability")
def debug_graph_reliability():
    """Run debug graph reliability."""
    try:
        data = graph_reliability_summary()
        return {"ok": True, "data": data}
    except Exception as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})


@app.get("/api/topology/history")
def get_topology_history(limit: int | None = None):
    """Get topology history."""
    try:
        data = STATE.get_topology_history(limit=limit)
        return {"ok": True, "data": data}
    except Exception as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})


@app.get("/api/snapshots")
def list_snapshots(
    type: str | None = None,
    target: str | None = None,
    prefix: str | None = None,
    action: str | None = None,
    limit: int | None = 50,
):
    """List snapshots."""
    data = _list_action_snapshots(snapshot_type=type, target=target, prefix=prefix, action=action, limit=limit)
    return {"ok": True, "data": data}


@app.get("/api/snapshots/{snapshot_id}")
def get_snapshot(snapshot_id: str):
    """Get snapshot."""
    data = _get_action_snapshot(snapshot_id)
    if not data:
        return JSONResponse(status_code=404, content={"ok": False, "error": "Snapshot not found"})
    return {"ok": True, "data": data}


@app.get("/api/snapshots/history")
def get_snapshot_history(canonical_id: str | None = None, limit: int | None = 20):
    """Get snapshot history."""
    data = _list_engine_snapshots(canonical_id=canonical_id, limit=limit or 20)
    return {"ok": True, "data": data}


@app.get("/api/snapshots/engine/{snapshot_id}")
def get_engine_snapshot(snapshot_id: str):
    """Get engine snapshot."""
    data = _get_engine_snapshot(snapshot_id)
    if not data:
        return JSONResponse(status_code=404, content={"ok": False, "error": "Snapshot not found"})
    return {"ok": True, "data": data}


@app.get("/api/snapshots/entities")
def list_snapshot_entities(limit: int | None = 200):
    """List snapshot entities."""
    data = _list_snapshot_entities(limit=limit or 200)
    return {"ok": True, "data": data}


@app.get("/api/snapshots/engine/diff")
def diff_engine_snapshots(snapshot_a: str | None = None, snapshot_b: str | None = None, a: str | None = None, b: str | None = None):
    """Diff engine snapshots."""
    left = snapshot_a or a
    right = snapshot_b or b
    data = _diff_engine_snapshots(left, right)
    if not data:
        return JSONResponse(status_code=404, content={"ok": False, "error": "Snapshots not found"})
    return {"ok": True, "data": data}


@app.get("/api/snapshots/golden")
def list_golden_snapshots():
    """List golden snapshots."""
    data = _list_golden_snapshots()
    return {"ok": True, "data": data}


@app.post("/api/snapshots/golden")
def set_golden_snapshot(payload: dict):
    """Set golden snapshot."""
    try:
        kind = payload.get("kind")
        snapshot_id = payload.get("snapshot_id")
        label = payload.get("label")
        data = _set_golden_snapshot(kind, snapshot_id, label)
        return {"ok": True, "data": data}
    except Exception as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})


@app.delete("/api/snapshots/golden/{kind}")
def clear_golden_snapshot(kind: str):
    """Run clear golden snapshot."""
    try:
        data = _clear_golden_snapshot(kind)
        return {"ok": True, "data": data}
    except Exception as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})


@app.get("/api/snapshots/golden/diff")
def diff_golden_snapshot(snapshot_id: str):
    """Diff golden snapshot."""
    try:
        data = _diff_golden_snapshot(snapshot_id)
        return {"ok": True, "data": data}
    except Exception as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})


@app.get("/api/snapshots/resolve")
def resolve_snapshot_subject(alias_type: str | None = None, alias_value: str | None = None):
    """Resolve snapshot subject."""
    data = _resolve_snapshot_subject(alias_type, alias_value)
    if not data:
        return JSONResponse(status_code=404, content={"ok": False, "error": "No matching subject"})
    return {"ok": True, "data": data}


@app.get("/api/snapshots/events")
def list_snapshot_events(canonical_ids: str | None = None, limit: int | None = 50):
    """List snapshot events."""
    ids = [cid for cid in (canonical_ids or "").split(",") if cid]
    data = _list_snapshot_events(canonical_ids=ids, limit=limit or 50)
    return {"ok": True, "data": data}


@app.get("/api/symptoms")
def list_symptoms():
    """List symptoms."""
    return {"ok": True, "data": _list_symptom_templates()}


@app.get("/api/symptoms/{symptom_id}")
def get_symptom(symptom_id: str):
    """Get symptom."""
    data = _get_symptom_template(symptom_id)
    if not data:
        return JSONResponse(status_code=404, content={"ok": False, "error": "Symptom template not found"})
    return {"ok": True, "data": data}


@app.post("/api/symptoms/plan")
def plan_symptom(payload: dict):
    """Build a Tier-0 snapshot plan for a symptom template."""
    try:
        data = _plan_symptom_tier0(payload)
        return {"ok": True, "data": data}
    except Exception as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})


@app.get("/api/investigations")
def list_investigations(limit: int | None = 50):
    """List investigations."""
    data = _list_investigations(limit=limit or 50)
    return {"ok": True, "data": data}


@app.post("/api/investigations")
def create_investigation(payload: dict):
    """Create investigation."""
    try:
        data = _create_investigation(payload)
        return {"ok": True, "data": data}
    except Exception as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})


@app.get("/api/investigations/{investigation_id}")
def get_investigation(investigation_id: str):
    """Get investigation."""
    data = _get_investigation(investigation_id)
    if not data:
        return JSONResponse(status_code=404, content={"ok": False, "error": "Investigation not found"})
    return {"ok": True, "data": data}


@app.put("/api/investigations/{investigation_id}")
def update_investigation(investigation_id: str, payload: dict):
    """Update investigation (title/status/tags/notes)."""
    try:
        data = _update_investigation(investigation_id, payload)
        return {"ok": True, "data": data}
    except Exception as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})


@app.post("/api/investigations/{investigation_id}/notes")
def add_investigation_note(investigation_id: str, payload: dict):
    """Add investigation note."""
    try:
        data = _add_investigation_note(investigation_id, payload)
        return {"ok": True, "data": data}
    except Exception as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})


@app.post("/api/investigations/{investigation_id}/events")
def add_investigation_event(investigation_id: str, payload: dict):
    """Add investigation event."""
    try:
        data = _add_investigation_event(investigation_id, payload)
        return {"ok": True, "data": data}
    except Exception as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})


@app.get("/api/investigations/{investigation_id}/context")
def get_investigation_context(investigation_id: str):
    """Get investigation context."""
    try:
        data = _get_investigation_context(investigation_id)
        return {"ok": True, "data": data}
    except Exception as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})


@app.put("/api/investigations/{investigation_id}/context")
def update_investigation_context(investigation_id: str, payload: dict):
    """Update investigation context."""
    try:
        data = _update_investigation_context(investigation_id, payload)
        return {"ok": True, "data": data}
    except Exception as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})


@app.get("/api/incidents")
def list_incidents(limit: int | None = 50):
    """List incidents."""
    data = _list_incidents(limit=limit or 50)
    return {"ok": True, "data": data}


@app.post("/api/incidents")
def create_incident(payload: dict):
    """Create incident."""
    try:
        data = _create_incident(payload)
        return {"ok": True, "data": data}
    except Exception as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})


@app.get("/api/incidents/{incident_id}")
def get_incident(incident_id: str):
    """Get incident."""
    data = _get_incident(incident_id)
    if not data:
        return JSONResponse(status_code=404, content={"ok": False, "error": "Incident not found"})
    return {"ok": True, "data": data}


@app.put("/api/incidents/{incident_id}")
def update_incident(incident_id: str, payload: dict):
    """Update incident."""
    try:
        data = _update_incident(incident_id, payload)
        return {"ok": True, "data": data}
    except Exception as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})


@app.post("/api/incidents/{incident_id}/snapshots")
def link_incident_snapshot(incident_id: str, payload: dict):
    """Run link incident snapshot."""
    try:
        data = _link_incident_snapshot(incident_id, payload.get("snapshot_id"))
        return {"ok": True, "data": data}
    except Exception as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})


@app.post("/api/incidents/{incident_id}/events")
def link_incident_event(incident_id: str, payload: dict):
    """Run link incident event."""
    try:
        data = _link_incident_event(incident_id, payload.get("event_id"))
        return {"ok": True, "data": data}
    except Exception as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})


@app.get("/api/incidents/{incident_id}/graph")
def incident_graph(incident_id: str):
    """Run incident graph."""
    try:
        data = _build_incident_graph(incident_id)
        return {"ok": True, "data": data}
    except Exception as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})


@app.get("/api/incidents/{incident_id}/timeline")
def incident_timeline(incident_id: str):
    """Run incident timeline."""
    try:
        data = _build_incident_timeline(incident_id)
        return {"ok": True, "data": data}
    except Exception as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})


@app.get("/api/incidents/{incident_id}/report")
def get_incident_report(incident_id: str):
    """Get incident report."""
    try:
        data = _get_incident_report(incident_id) or {}
        return {"ok": True, "data": data}
    except Exception as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})


@app.post("/api/incidents/{incident_id}/report")
def save_incident_report(incident_id: str, payload: dict):
    """Run save incident report."""
    report = payload.get("report") if isinstance(payload, dict) else payload
    try:
        data = _update_incident_report(incident_id, report)
        return {"ok": True, "data": data}
    except Exception as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})


@app.post("/api/incidents/{incident_id}/report/render")
def render_incident_report(incident_id: str, payload: dict):
    """Render incident report."""
    fmt = payload.get("format") or "markdown"
    redaction = payload.get("redaction") or "internal"
    report = payload.get("report")
    try:
        data = _render_incident_report(incident_id, fmt, redaction, report=report)
        return {"ok": True, "data": data}
    except Exception as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})


@app.post("/api/snapshots/capture")
def capture_snapshot(payload: dict):
    """Capture snapshot."""
    try:
        data = _capture_snapshots(payload)
        return {"ok": True, "data": data}
    except Exception as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})


@app.post("/api/snapshots/finalize")
def finalize_snapshot(payload: dict):
    """Finalize snapshot."""
    try:
        data = _finalize_draft_snapshot(payload)
        return {"ok": True, "data": data}
    except Exception as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})


@app.get("/api/snapshots/diff")
def diff_snapshots(snapshot_a: str | None = None, snapshot_b: str | None = None, a: str | None = None, b: str | None = None):
    """Diff snapshots."""
    left = snapshot_a or a
    right = snapshot_b or b
    data = _diff_action_snapshots(left, right)
    if not data:
        return JSONResponse(status_code=404, content={"ok": False, "error": "Snapshots not found"})
    return {"ok": True, "data": data}


@app.post("/api/topology/history")
def add_topology_history(payload: dict):
    """Add topology history."""
    snapshot = payload.get("snapshot") or payload.get("data") or payload
    limit = payload.get("limit")
    try:
        data = STATE.append_topology_history(snapshot, limit=limit)
        return {"ok": True, "data": data}
    except Exception as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})


@app.get("/help")
@app.get("/help/{path:path}")
def help_page(path: str = ""):
    """Run help page."""
    return FileResponse(ROOT / "index.html")


@app.get("/{path:path}")
def spa_fallback(path: str):
    """Run spa fallback."""
    if path.startswith("api/"):
        raise HTTPException(status_code=404, detail="Not found")
    candidate = ROOT / path
    if candidate.exists() and candidate.is_file():
        return FileResponse(candidate)
    return FileResponse(ROOT / "index.html")


app.mount("/static", StaticFiles(directory=ROOT, html=True), name="static")


def _build_ssh_command(payload):
    """Build ssh command."""
    host = payload.get("host")
    if not host:
        raise RuntimeError("Host is required.")
    user = payload.get("user")
    port = int(payload.get("port") or 22)
    key_path = payload.get("key_path")
    strict_host_key = payload.get("strict_host_key", True)
    target = f"{user}@{host}" if user else host
    cmd = ["ssh", "-tt", "-p", str(port)]
    if strict_host_key:
        cmd += ["-o", "StrictHostKeyChecking=accept-new"]
    else:
        cmd += ["-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null"]
    if key_path:
        cmd += ["-i", key_path]
    cmd += [target]
    return cmd


@app.websocket("/ws/terminal/{session_id}")
async def break_glass_terminal(websocket: WebSocket, session_id: str):
    """Break-glass terminal session relay (operator <-> agent)."""

    auth = websocket.headers.get("authorization") or ""
    role = "operator"
    token = None
    if isinstance(auth, str) and auth.lower().startswith("bearer "):
        role = "agent"
        token = auth.split(" ", 1)[1].strip() or None

    if role == "operator":
        if str(websocket.query_params.get("interactive_scope") or "").strip().lower() != "true":
            await websocket.close(code=1008)
            return

    try:
        session = control_plane.get_terminal_session(session_id)
    except Exception:
        await websocket.close(code=1008)
        return

    expires_at = _parse_iso(session.get("expires_at"))
    if expires_at and expires_at <= datetime.now(timezone.utc):
        try:
            control_plane.set_terminal_session_status(session_id, "expired")
        except Exception:
            pass
        await websocket.close(code=1000)
        return

    agent_id = str(session.get("agent_id") or "")
    if not agent_id:
        await websocket.close(code=1008)
        return

    if role == "agent":
        if not token or not control_plane.authenticate_agent(agent_id, token):
            await websocket.close(code=1008)
            return

    await websocket.accept()
    hub = _terminal_hub(session_id, agent_id)

    async def audit(kind: str, payload: Any | None = None) -> None:
        try:
            control_plane.append_terminal_audit(session_id, kind=kind, payload=payload)
        except Exception:
            return

    async def broadcast(payload: dict[str, Any]) -> None:
        dead: list[WebSocket] = []
        for op in list(hub.operator_ws):
            try:
                await op.send_json(payload)
            except Exception:
                dead.append(op)
        for op in dead:
            try:
                hub.operator_ws.discard(op)
            except Exception:
                pass

    async def send_to_agent(payload: dict[str, Any]) -> bool:
        if not hub.agent_ws:
            return False
        try:
            await hub.agent_ws.send_json(payload)
            return True
        except Exception:
            hub.agent_ws = None
            return False

    await websocket.send_json({"type": "hello", "role": role, "session": session})

    if role == "agent":
        hub.agent_ws = websocket
        try:
            control_plane.set_terminal_session_status(session_id, "active")
        except Exception:
            pass
        await audit("agent_connected", {"agent_id": agent_id})
        # Flush any queued commands.
        pending = list(hub.pending_commands)
        hub.pending_commands = []
        for cmd in pending:
            await send_to_agent(cmd)
        await broadcast({"type": "agent_status", "status": "connected"})
    else:
        hub.operator_ws.add(websocket)
        await audit("operator_connected", {"agent_id": agent_id})
        if hub.agent_ws:
            await websocket.send_json({"type": "agent_status", "status": "connected"})
        else:
            await websocket.send_json({"type": "agent_status", "status": "disconnected"})

    try:
        while True:
            text = await websocket.receive_text()
            if not text:
                continue
            try:
                msg = json.loads(text)
            except Exception:
                msg = {"type": "command", "command": text}

            if not isinstance(msg, dict):
                continue

            msg_type = str(msg.get("type") or "").strip().lower()
            if role == "operator":
                if msg_type in ("end", "close", "terminate"):
                    try:
                        control_plane.set_terminal_session_status(session_id, "closed")
                    except Exception:
                        pass
                    await audit("session_closed", {"by": "operator"})
                    await send_to_agent({"type": "end"})
                    await broadcast({"type": "session", "status": "closed"})
                    await websocket.close(code=1000)
                    return

                if msg_type not in ("command", ""):
                    continue
                command = msg.get("command") if msg.get("command") is not None else msg.get("data")
                command_text = str(command or "").rstrip()
                if not command_text:
                    continue
                cmd_id = str(msg.get("command_id") or secrets.token_hex(8))
                envelope = {"type": "command", "command_id": cmd_id, "command": command_text}
                await audit("command", {"command_id": cmd_id, "command": command_text})
                if not await send_to_agent(envelope):
                    hub.pending_commands.append(envelope)
                    hub.pending_commands = hub.pending_commands[-50:]
                    await websocket.send_json({"type": "queued", "command_id": cmd_id})
                continue

            # Agent -> operator messages.
            if msg_type in ("output", "exit", "error", "hello", "status"):
                await audit(msg_type, msg)
                await broadcast(msg)
                continue
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        try:
            if role == "operator":
                hub.operator_ws.discard(websocket)
                await audit("operator_disconnected", {"agent_id": agent_id})
            else:
                if hub.agent_ws == websocket:
                    hub.agent_ws = None
                await audit("agent_disconnected", {"agent_id": agent_id})
                await broadcast({"type": "agent_status", "status": "disconnected"})
        except Exception:
            pass


@app.websocket("/ws/ssh")
async def ssh_terminal(websocket: WebSocket):
    """Run ssh terminal."""
    await websocket.accept()
    master_fd = None
    proc = None
    try:
        if pty is None:
            raise RuntimeError("PTY not available on this host. SSH terminal requires a Unix-like environment.")
        init = await websocket.receive_text()
        payload = json.loads(init)
        cmd = _build_ssh_command(payload)
        master_fd, slave_fd = pty.openpty()
        proc = subprocess.Popen(cmd, stdin=slave_fd, stdout=slave_fd, stderr=slave_fd)
        os.close(slave_fd)

        loop = asyncio.get_running_loop()

        async def read_pty():
            """Run read pty."""
            while True:
                data = await loop.run_in_executor(None, os.read, master_fd, 1024)
                if not data:
                    break
                await websocket.send_bytes(data)

        async def write_pty():
            """Run write pty."""
            while True:
                msg = await websocket.receive()
                if msg.get("type") == "websocket.disconnect":
                    break
                if msg.get("bytes") is not None:
                    os.write(master_fd, msg["bytes"])
                elif msg.get("text") is not None:
                    os.write(master_fd, msg["text"].encode())

        reader = asyncio.create_task(read_pty())
        writer = asyncio.create_task(write_pty())
        done, pending = await asyncio.wait({reader, writer}, return_when=asyncio.FIRST_COMPLETED)
        for task in pending:
            task.cancel()
    except WebSocketDisconnect:
        pass
    except Exception as exc:
        try:
            await websocket.send_text(f"SSH error: {exc}")
        except Exception:
            pass
    finally:
        try:
            if proc and proc.poll() is None:
                proc.terminate()
        except Exception:
            pass
        if master_fd is not None:
            try:
                os.close(master_fd)
            except Exception:
                pass


@app.get("/api/signals/visual/{endpoint_id}/{episode_id}")
def visual_signal_timeline(endpoint_id: str, episode_id: str, limit: int | None = 200):
    """Run visual signal timeline."""
    try:
        events = STATE.snapshot_store.list_signal_timeline(
            signal_name="visual",
            endpoint_id=endpoint_id,
            episode_id=episode_id,
            limit=int(limit or 200),
        )
        return {"ok": True, "data": {"endpoint_id": endpoint_id, "episode_id": episode_id, "events": events}}
    except Exception as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})
