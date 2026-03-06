from pathlib import Path
from datetime import datetime, timezone
import hashlib
import io
import sqlite3
import secrets
import getpass
import os
import zipfile
from flask import Flask, Response, jsonify, request, send_from_directory

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
from exchange import send_message_as_user as exchange_send_message_as_user
from . import control_plane
from .graph_runner_dispatch import GraphRunnerError
from .artifact_retention import ensure_artifact_retention_reaper
from . import workflows_v2

ROOT = Path(__file__).resolve().parents[1]

# Disable Flask's built-in static route so SPA fallbacks can handle deep links.
app = Flask(__name__, static_folder=None)
# Prevent stale UI assets (app.js/styles.css) from being served out of the browser cache.
# This portal is local-first and changes frequently during development, so prefer correctness.
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
ensure_snapshot_scheduler()
ensure_onedrive_cache_warmup_scheduler()
control_plane.ensure_lease_reaper()
ensure_artifact_retention_reaper(ARTIFACTS_DIR)


@app.after_request
def _disable_caching(response):
    """Disable caching so UI changes show up immediately without hard refresh."""
    response.headers["Cache-Control"] = "no-store, max-age=0"
    response.headers["Pragma"] = "no-cache"
    return response


def _render_index_html() -> Response:
    """Render index.html with a cache-busting query string for UI assets.

    Some browsers can be stubborn about reusing cached local assets (especially
    during rapid iteration). Adding a simple version query string makes it
    unambiguous which build is loaded.
    """

    index_path = ROOT / "index.html"
    html = index_path.read_text(encoding="utf-8")
    try:
        version = int(
            max(
                (ROOT / "styles.css").stat().st_mtime,
                (ROOT / "app.js").stat().st_mtime,
                (ROOT / "triage.js").stat().st_mtime,
                (ROOT / "investigation_summary.js").stat().st_mtime,
                (ROOT / "next_steps.js").stat().st_mtime,
            )
        )
    except Exception:
        version = int(index_path.stat().st_mtime)
    qs = f"?v={version}"
    html = html.replace('href="styles.css"', f'href="styles.css{qs}"')
    html = html.replace('src="triage.js"', f'src="triage.js{qs}"')
    html = html.replace('src="investigation_summary.js"', f'src="investigation_summary.js{qs}"')
    html = html.replace('src="next_steps.js"', f'src="next_steps.js{qs}"')
    html = html.replace('src="app.js"', f'src="app.js{qs}"')
    return Response(html, mimetype="text/html")


@app.get("/api/status")
def status():
    """Run status."""
    return jsonify(STATE.status())


@app.get("/api/status/summary")
def status_summary():
    """Run status summary."""
    return jsonify(_system_status_summary())


@app.get("/api/config")
def get_config():
    """Get config."""
    return jsonify(STATE.get_config_public())


@app.post("/api/config")
def update_config():
    """Update config."""
    payload = request.get_json(silent=True) or {}
    reload_flag = payload.pop("reload", False)
    try:
        data = STATE.update_config(payload)
        if reload_flag:
            STATE.reload()
        return jsonify({"ok": True, "data": data})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.post("/api/config/reload")
def reload_config():
    """Run reload config."""
    STATE.reload()
    return jsonify({"ok": True, "data": STATE.get_config_public()})


def _agent_token_from_headers() -> str | None:
    """Extract agent token from request headers."""
    auth = request.headers.get("Authorization") or ""
    if isinstance(auth, str) and auth.lower().startswith("bearer "):
        return auth.split(" ", 1)[1].strip() or None
    token = request.headers.get("X-Agent-Token") or request.headers.get("x-agent-token")
    return str(token).strip() if token else None


def _require_agent_auth(agent_id: str, token: str | None) -> None:
    """Require valid agent auth."""
    if not token or not control_plane.authenticate_agent(agent_id, token):
        raise PermissionError("Unauthorized")


@app.post("/api/agents/register")
def register_agent():
    """Register agent."""
    payload = request.get_json(silent=True) or {}
    try:
        data = control_plane.register_agent(payload)
        return jsonify(data)
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.post("/api/pairing-codes")
def create_pairing_code():
    """Create a one-time pairing code (operator/UI)."""
    payload = request.get_json(silent=True) or {}
    try:
        data = control_plane.create_pairing_code(
            tenant_id=payload.get("tenant_id"),
            workspace_id=payload.get("workspace_id"),
            ttl_seconds=payload.get("ttl_seconds"),
        )
        return jsonify({"ok": True, "data": data})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.post("/api/agents/heartbeat")
def agent_heartbeat():
    """Agent heartbeat."""
    payload = request.get_json(silent=True) or {}
    agent_id = payload.get("agent_id")
    token = _agent_token_from_headers() or payload.get("agent_token")
    try:
        _require_agent_auth(str(agent_id), str(token) if token is not None else None)
        data = control_plane.heartbeat_agent(
            str(agent_id),
            status="online",
            capabilities=payload.get("capabilities"),
            labels=payload.get("labels"),
            tenant_id=payload.get("tenant_id"),
            workspace_id=payload.get("workspace_id"),
        )
        return jsonify(data)
    except KeyError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 404
    except PermissionError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 401
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.get("/api/agents")
def list_agents():
    """List agents."""
    try:
        status = request.args.get("status") or None
        query = request.args.get("query") or None
        tenant_id = request.args.get("tenant_id") or None
        workspace_id = request.args.get("workspace_id") or None
        limit = request.args.get("limit", type=int) or 200
        offset = request.args.get("offset", type=int) or 0
        data = control_plane.list_agents(
            status=status,
            query=query,
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            limit=limit,
            offset=offset,
        )
        return jsonify({"ok": True, "data": data})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.get("/api/capabilities/catalog")
def capabilities_catalog():
    """List known actions and required capabilities."""
    try:
        from agent.catalog import build_capabilities_catalog

        return jsonify({"ok": True, "data": build_capabilities_catalog()})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 500


@app.get("/install/agent.zip")
def download_agent_zip():
    """Download the agent code as a zip (v0 bootstrap helper)."""
    agent_root = (ROOT.parent / "agent").resolve()
    if not agent_root.exists():
        return jsonify({"ok": False, "error": "Agent folder not found"}), 404

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
    buf.seek(0)
    return Response(
        buf.getvalue(),
        mimetype="application/zip",
        headers={"Content-Disposition": 'attachment; filename="agent.zip"'},
    )


@app.get("/api/agents/<agent_id>/next-job")
def agent_next_job(agent_id):
    """Lease next queued job for agent."""
    lease_seconds = request.args.get("lease_seconds", type=int) or 900
    token = _agent_token_from_headers()
    try:
        _require_agent_auth(str(agent_id), token)
        job = control_plane.lease_next_job(str(agent_id), lease_seconds=lease_seconds)
        if not job:
            return Response(status=204)
        return jsonify(job)
    except PermissionError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 401
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.post("/api/agents/<agent_id>/job-result")
def agent_job_result(agent_id):
    """Record job result for agent."""
    payload = request.get_json(silent=True) or {}
    token = _agent_token_from_headers() or payload.get("agent_token")
    try:
        _require_agent_auth(str(agent_id), str(token) if token is not None else None)
        data = control_plane.record_job_result(
            str(agent_id),
            str(payload.get("job_id")),
            status=payload.get("status"),
            result=payload.get("result"),
            stdout=payload.get("stdout"),
            stderr=payload.get("stderr"),
            exit_code=payload.get("exit_code"),
            artifacts=payload.get("artifacts"),
            duration_ms=payload.get("duration_ms"),
            error=payload.get("error"),
        )
        _maybe_ingest_vision_u_eye_job_result(
            agent_id=str(agent_id),
            job_id=str(payload.get("job_id") or ""),
            action_id=str(data.get("action_id") or ""),
            status=str(data.get("status") or payload.get("status") or ""),
            result=payload.get("result"),
            artifacts=payload.get("artifacts"),
        )
        return jsonify({"ok": True, "data": data})
    except KeyError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 404
    except PermissionError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 401
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.post("/api/terminal/<agent_id>/start")
def start_terminal_session(agent_id):
    """Start a break-glass terminal session (human-only)."""
    if _agent_token_from_headers():
        return jsonify({"ok": False, "error": "Terminal endpoints reject job tokens"}), 403
    if request.headers.get("X-Job-Token") or request.headers.get("x-job-token"):
        return jsonify({"ok": False, "error": "Terminal endpoints reject job tokens"}), 403
    payload = request.get_json(silent=True) or {}
    if payload.get("interactive_scope") is not True:
        return jsonify({"ok": False, "error": "interactive_scope=true required"}), 403

    operator = getpass.getuser()
    allowlist = str(os.environ.get("GAS_TERMINAL_ALLOWED_OPERATORS") or "").strip()
    if allowlist:
        allowed = {part.strip() for part in allowlist.split(",") if part.strip()}
        if operator not in allowed and "*" not in allowed:
            return jsonify({"ok": False, "error": "Operator not allowed"}), 403
    remote = request.remote_addr or ""
    if remote and remote not in ("127.0.0.1", "::1"):
        return jsonify({"ok": False, "error": "Terminal start requires localhost"}), 403
    ttl = int(payload.get("ttl_seconds") or 900)
    try:
        session = control_plane.create_terminal_session(agent_id=str(agent_id), operator=operator, ttl_seconds=ttl)
        return jsonify({"ok": True, "data": {**session, "ws_path": f"/ws/terminal/{session['session_id']}"}})
    except KeyError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 404
    except PermissionError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 403
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 409
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.get("/api/terminal/<agent_id>/next-session")
def agent_next_terminal_session(agent_id):
    """Agent: lease next pending terminal session (outbound websocket follows)."""
    token = _agent_token_from_headers()
    try:
        _require_agent_auth(str(agent_id), token)
    except PermissionError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 401
    try:
        session = control_plane.lease_next_terminal_session(str(agent_id))
        if not session:
            return Response(status=204)
        return jsonify({"ok": True, "data": session})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.post("/api/jobs/enqueue")
def enqueue_job():
    """Enqueue a control plane job (human/UI)."""
    payload = request.get_json(silent=True) or {}
    agent_id = str(payload.get("agent_id") or "").strip()
    action_id = str(payload.get("action_id") or "").strip()
    params = payload.get("params")
    tenant_id = payload.get("tenant_id")
    workspace_id = payload.get("workspace_id")
    interactive_scope = bool(payload.get("interactive_scope"))
    try:
        job = control_plane.enqueue_action_job(
            agent_id=agent_id,
            action_id=action_id,
            params=params,
            requested_by=getpass.getuser(),
            interactive_scope=interactive_scope,
            tenant_id=tenant_id,
            workspace_id=workspace_id,
        )
        return jsonify({"ok": True, "data": job})
    except KeyError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 404
    except PermissionError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 403
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.post("/api/actionpacks/v2/validate")
def validate_action_pack_v2():
    """Validate an Action Pack v2 workflow."""
    payload = request.get_json(silent=True) or {}
    try:
        workflow = payload.get("workflow")
        online_only = payload.get("online_only")
        result = workflows_v2.validate_workflow_v2(workflow, online_only=bool(online_only) if online_only is not None else True)
        return jsonify({"ok": True, "data": result.to_dict()})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.post("/api/actionpacks/v2/compile")
def compile_action_pack_v2():
    """Compile natural language text into an Action Pack v2 workflow (stub)."""
    payload = request.get_json(silent=True) or {}
    try:
        data = workflows_v2.compile_workflow_v2(
            payload.get("text") or "",
            allowed_action_ids=payload.get("allowed_action_ids"),
            agent_id=payload.get("agent_id"),
            max_risk_level=payload.get("max_risk_level"),
            interactive_scope=payload.get("interactive_scope"),
        )
        return jsonify({"ok": True, "data": data})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.post("/api/actionpacks/v2/run")
def run_action_pack_v2():
    """Run an Action Pack v2 workflow."""
    payload = request.get_json(silent=True) or {}
    try:
        data = workflows_v2.run_workflow_v2(payload.get("workflow"))
        return jsonify({"ok": True, "data": data})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.get("/api/jobs")
def list_jobs():
    """List jobs."""
    try:
        agent_id = request.args.get("agent_id") or None
        status = request.args.get("status") or None
        query = request.args.get("query") or None
        tenant_id = request.args.get("tenant_id") or None
        workspace_id = request.args.get("workspace_id") or None
        limit = request.args.get("limit", type=int) or 200
        offset = request.args.get("offset", type=int) or 0
        data = control_plane.list_jobs(
            agent_id=agent_id,
            status=status,
            query=query,
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            limit=limit,
            offset=offset,
        )
        return jsonify({"ok": True, "data": data})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.get("/api/jobs/<job_id>")
def get_job(job_id):
    """Get job detail."""
    try:
        data = control_plane.get_job_detail(str(job_id))
        return jsonify({"ok": True, "data": data})
    except KeyError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 404
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.get("/api/audit")
def get_audit():
    """Get audit."""
    params = {
        "service": request.args.get("service") or None,
        "action": request.args.get("action") or None,
        "ok": request.args.get("ok"),
        "user": request.args.get("user") or None,
        "since": request.args.get("since") or None,
        "until": request.args.get("until") or None,
        "query": request.args.get("query") or None,
        "limit": request.args.get("limit", type=int),
        "offset": request.args.get("offset", type=int),
    }
    data = _read_audit_log(**params)
    return jsonify({"ok": True, "data": data})


@app.post("/api/artifacts/upload")
def upload_artifact():
    """Upload artifact (agent-authenticated)."""
    agent_id = request.form.get("agent_id") or ""
    job_id = request.form.get("job_id") or None
    artifact_type = request.form.get("type") or None
    token = _agent_token_from_headers()
    try:
        _require_agent_auth(str(agent_id), token)
    except PermissionError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 401
    file = request.files.get("file")
    if not file:
        return jsonify({"ok": False, "error": "Missing file"}), 400
    artifact_id = secrets.token_hex(16)
    suffix = Path(file.filename or "").suffix if file.filename else ""
    if not suffix or len(suffix) > 12:
        suffix = ".zip"
    stored_filename = f"{artifact_id}{suffix}"
    dest = Path(ARTIFACTS_DIR) / stored_filename
    sha = hashlib.sha256()
    size_bytes = 0
    try:
        with dest.open("wb") as handle:
            while True:
                chunk = file.stream.read(1024 * 1024)
                if not chunk:
                    break
                handle.write(chunk)
                sha.update(chunk)
                size_bytes += len(chunk)
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400
    sha256 = sha.hexdigest()
    try:
        control_plane.record_artifact(
            artifact_id=artifact_id,
            agent_id=str(agent_id),
            job_id=str(job_id).strip() if job_id else None,
            type=str(artifact_type).strip() if artifact_type else (file.mimetype or None),
            filename=stored_filename,
            sha256=sha256,
            size_bytes=size_bytes,
            storage_path=stored_filename,
        )
    except Exception as exc:
        try:
            if dest.exists():
                dest.unlink()
        except Exception:
            pass
        return jsonify({"ok": False, "error": "artifact_record_failed", "detail": str(exc)}), 500
    return jsonify(
        {
            "ok": True,
            "data": {
                "artifact_id": artifact_id,
                "filename": stored_filename,
                "sha256": sha256,
                "size_bytes": size_bytes,
                "url": f"/api/artifacts/{stored_filename}",
            },
        }
    )


@app.get("/api/artifacts/<path:filename>")
def get_artifact(filename):
    """Get artifact."""
    try:
        return send_from_directory(ARTIFACTS_DIR, filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify({"ok": False, "error": "Artifact not found"}), 404


@app.post("/api/config/export")
def export_config():
    """Export config."""
    payload = request.get_json(silent=True) or {}
    passphrase = payload.get("passphrase") or None
    use_keychain = bool(payload.get("use_keychain"))
    try:
        data = STATE.export_config_encrypted(passphrase=passphrase, use_keychain=use_keychain)
        return jsonify({"ok": True, "data": data})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.post("/api/config/import")
def import_config():
    """Import config."""
    payload = request.get_json(silent=True) or {}
    passphrase = payload.get("passphrase") or None
    blob = payload.get("payload") or payload.get("data")
    try:
        data = STATE.import_config_encrypted(blob, passphrase=passphrase)
        return jsonify({"ok": True, "data": data})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.post("/api/task")
def run_task():
    """Run task."""
    payload = request.get_json(silent=True) or {}
    service = payload.get("service")
    action = payload.get("action")
    params = payload.get("params") or {}
    # Guard against malformed requests so we don't throw 500s from internal routing code.
    if not isinstance(service, str) or not service.strip() or not isinstance(action, str) or not action.strip():
        return (
            jsonify(
                {
                    "ok": False,
                    "failure_source": "dashboard_request_validation",
                    "failure_outcome": "error",
                    "error_class": "validation",
                    "error": "Missing required fields: service and action",
                    "status_code": 400,
                    "service": service,
                    "action": action,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            ),
            400,
        )
    ui_request_id = None
    if isinstance(params, dict) and "_ui_request_id" in params:
        ui_request_id = str(params.pop("_ui_request_id"))
    target = payload.get("target")
    token = set_trace_context(
        {
            "ui_request_id": ui_request_id,
            "service": service,
            "action": action,
            "trace_hook": record_graph_trace,
        }
    )
    try:
        data = dispatch_task(service, action, params, target)
        normalized = None
        try:
            normalized_payload = _extract_action_payload(data)
            normalized = interpret_response(service, action, normalized_payload, source=get_action_source(service, action))
        except Exception:
            normalized = None
        return jsonify({"ok": True, "data": data, "normalized": normalized, "target": target})
    except GraphAPIError as exc:
        response = build_graph_error_response(exc, service=service, action=action)
        hint = None
        if response.get("error_class") == "missing_permission":
            hint = "App permission missing or admin consent not granted. Add the permission in Entra and grant admin consent."
        response["hint"] = hint
        # Use an operator-meaningful HTTP status (avoid returning 400 for upstream/network failures).
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
        return jsonify(response), status_code
    except GraphRunnerError as exc:
        return jsonify(exc.to_payload(service=service, action=action)), int(exc.status_code or 502)
    except sqlite3.Error as exc:
        # Surface SQLite/schema issues as a 500 so operators don't confuse them with Graph failures.
        return (
            jsonify(
                {
                    "ok": False,
                    "failure_source": "dashboard_internal_error",
                    "failure_outcome": "error",
                    "error_class": "db_schema",
                    "error": "Cache schema out of date; migration required.",
                    "detail": {"message": str(exc)},
                    "status_code": 500,
                    "service": service,
                    "action": action,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            ),
            500,
        )
    except PowerShellCommandError as exc:
        return (
            jsonify(
                {
                    "ok": False,
                    "failure_source": "powershell",
                    "failure_outcome": "failed",
                    "error_class": "powershell_error",
                    "error": str(exc),
                    "detail": exc.output,
                    "status_code": 400,
                    "service": service,
                    "action": action,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            ),
            400,
        )
    except Exception as exc:
        message = str(exc)
        lowered = message.lower()
        # Treat validation / parameter issues as client errors.
        if isinstance(exc, ValueError):
            return (
                jsonify(
                    {
                        "ok": False,
                        "failure_source": "dashboard_request_validation",
                        "failure_outcome": "error",
                        "error_class": "validation",
                        "error": message,
                        "status_code": 400,
                        "service": service,
                        "action": action,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                ),
                400,
            )
        if "missing microsoft configuration variables" in lowered or "missing graph" in lowered:
            return (
                jsonify(
                    {
                        "ok": False,
                        "failure_source": "dashboard_config_error",
                        "failure_outcome": "retry_exhausted",
                        "failure_origin": "dashboard_config_error",
                        "error_class": "dashboard_config_error",
                        "error": message,
                        "status_code": 400,
                        "service": service,
                        "action": action,
                        "timestamp": None,
                    }
                ),
                400,
            )
        if "graph request handler not configured" in lowered:
            return (
                jsonify(
                    {
                        "ok": False,
                        "failure_source": "dashboard_config_error",
                        "failure_outcome": "retry_exhausted",
                        "failure_origin": "dashboard_config_error",
                        "error_class": "dashboard_config_error",
                        "error": message,
                        "status_code": 400,
                        "service": service,
                        "action": action,
                    }
                ),
                400,
            )
        # Anything else is an internal error. Return JSON (not an HTML debug page) so the UI can render it.
        return (
            jsonify(
                {
                    "ok": False,
                    "failure_source": "dashboard_internal_error",
                    "failure_outcome": "error",
                    "error_class": "dashboard_internal_error",
                    "error": message,
                    "detail": {"type": exc.__class__.__name__},
                    "status_code": 500,
                    "service": service,
                    "action": action,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            ),
            500,
        )
    finally:
        if token is not None:
            reset_trace_context(token)


def _csv_to_list(value):
    """Convert a CSV string (or list) into a clean list of strings."""
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return [str(v).strip() for v in value if str(v).strip()]
    raw = str(value).strip()
    if not raw:
        return []
    return [part.strip() for part in raw.split(",") if part.strip()]


@app.post("/api/exchange/send-mail")
def exchange_send_mail():
    """Send mail as a specific mailbox (Graph app-only)."""
    payload = request.get_json(silent=True) or {}
    ui_request_id = None
    if "_ui_request_id" in payload:
        ui_request_id = str(payload.pop("_ui_request_id"))

    token = set_trace_context(
        {
            "ui_request_id": ui_request_id,
            "service": "exchange",
            "action": "send_mail",
            "trace_hook": record_graph_trace,
        }
    )
    try:
        sender = payload.get("sender") or payload.get("from") or payload.get("mailbox") or ""
        to_recipients = _csv_to_list(payload.get("to_recipients") or payload.get("to") or payload.get("recipients"))
        cc_recipients = _csv_to_list(payload.get("cc_recipients") or payload.get("cc"))
        subject = payload.get("subject") or ""
        body_html = payload.get("body_html") or payload.get("body") or ""
        save_to_sent_items = bool(payload.get("save_to_sent_items") or payload.get("saveToSentItems") or False)

        sent = exchange_send_message_as_user(
            STATE.get_graph(),
            sender=str(sender),
            to_recipients=to_recipients,
            subject=str(subject),
            body_html=str(body_html),
            cc_recipients=cc_recipients or None,
            save_to_sent_items=save_to_sent_items,
        )
        return jsonify({"ok": True, "data": {"sent": bool(sent)}})
    except GraphAPIError as exc:
        response = build_graph_error_response(exc, service="exchange", action="send_mail")
        status_code = exc.status_code or response.get("status_code") or 502
        return jsonify(response), status_code
    except ValueError as exc:
        return jsonify({"ok": False, "error_class": "validation", "error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"ok": False, "error_class": "dashboard_internal_error", "error": str(exc)}), 500
    finally:
        if token is not None:
            reset_trace_context(token)


@app.post("/ingest/perception")
def ingest_vision_u_eye_perception():
    """Ingest vision u eye perception."""
    payload = request.get_json(silent=True) or {}
    try:
        data = _ingest_vision_u_eye_visual_signal(payload)
        return jsonify(data)
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.get("/api/debug/traces")
def debug_traces():
    """Run debug traces."""
    limit = request.args.get("limit", type=int) or 50
    ui_request_id = request.args.get("ui_request_id") or None
    request_id = request.args.get("request_id") or None
    return jsonify({"ok": True, "data": list_graph_traces(limit=limit, ui_request_id=ui_request_id, request_id=request_id)})


@app.get("/api/debug/traces/<ui_request_id>")
def debug_traces_by_ui(ui_request_id):
    """Run debug traces by ui."""
    limit = request.args.get("limit", type=int) or 200
    return jsonify({"ok": True, "data": list_graph_traces(limit=limit, ui_request_id=ui_request_id)})


@app.get("/api/debug/traces/by-graph-request/<request_id>")
def debug_traces_by_graph_request(request_id):
    """Run debug traces by graph request."""
    limit = request.args.get("limit", type=int) or 200
    return jsonify({"ok": True, "data": list_graph_traces(limit=limit, request_id=request_id)})


@app.get("/api/debug/graph-reliability")
def graph_reliability():
    """Run graph reliability."""
    return jsonify({"ok": True, "data": graph_reliability_summary()})


@app.post("/api/signals/visual")
def ingest_visual_signal_api():
    """Ingest visual signal api."""
    payload = request.get_json(silent=True) or {}
    try:
        data = _ingest_vision_u_eye_visual_signal(payload)
        return jsonify(data)
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.get("/api/signals/visual")
def list_visual_signals_api():
    """List visual signals api."""
    endpoint_id = request.args.get("endpoint_id") or None
    session_id = request.args.get("session_id") or None
    canonical_id = request.args.get("canonical_id") or None
    since = request.args.get("since") or None
    until = request.args.get("until") or None
    limit = request.args.get("limit", type=int) or 50
    try:
        data = _list_vision_u_eye_visual_signals(
            endpoint_id=endpoint_id,
            session_id=session_id,
            canonical_id=canonical_id,
            since=since,
            until=until,
            limit=limit,
        )
        return jsonify({"ok": True, "data": data})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.get("/api/topology/history")
def get_topology_history():
    """Get topology history."""
    limit = request.args.get("limit", type=int)
    try:
        data = STATE.get_topology_history(limit=limit)
        return jsonify({"ok": True, "data": data})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.get("/api/snapshots")
def list_snapshots():
    """List snapshots."""
    snapshot_type = request.args.get("type") or None
    target = request.args.get("target") or None
    prefix = request.args.get("prefix") or None
    action = request.args.get("action") or None
    limit = request.args.get("limit", type=int) or 50
    data = _list_action_snapshots(snapshot_type=snapshot_type, target=target, prefix=prefix, action=action, limit=limit)
    return jsonify({"ok": True, "data": data})


@app.get("/api/snapshots/diff")
def diff_snapshots():
    """Diff snapshots."""
    snapshot_a = request.args.get("a") or request.args.get("snapshot_a")
    snapshot_b = request.args.get("b") or request.args.get("snapshot_b")
    data = _diff_action_snapshots(snapshot_a, snapshot_b)
    if not data:
        return jsonify({"ok": False, "error": "Snapshots not found"}), 404
    return jsonify({"ok": True, "data": data})


@app.get("/api/snapshots/<snapshot_id>")
def get_snapshot(snapshot_id):
    """Get snapshot."""
    data = _get_action_snapshot(snapshot_id)
    if not data:
        return jsonify({"ok": False, "error": "Snapshot not found"}), 404
    return jsonify({"ok": True, "data": data})


@app.get("/api/snapshots/history")
def get_snapshot_history():
    """Get snapshot history."""
    canonical_id = request.args.get("canonical_id") or None
    limit = request.args.get("limit", type=int) or 20
    data = _list_engine_snapshots(canonical_id=canonical_id, limit=limit)
    return jsonify({"ok": True, "data": data})


@app.get("/api/snapshots/engine/<snapshot_id>")
def get_engine_snapshot(snapshot_id):
    """Get engine snapshot."""
    data = _get_engine_snapshot(snapshot_id)
    if not data:
        return jsonify({"ok": False, "error": "Snapshot not found"}), 404
    return jsonify({"ok": True, "data": data})


@app.get("/api/snapshots/entities")
def list_snapshot_entities():
    """List snapshot entities."""
    limit = request.args.get("limit", type=int) or 200
    data = _list_snapshot_entities(limit=limit)
    return jsonify({"ok": True, "data": data})


@app.get("/api/snapshots/engine/diff")
def diff_engine_snapshots():
    """Diff engine snapshots."""
    snapshot_a = request.args.get("a") or request.args.get("snapshot_a")
    snapshot_b = request.args.get("b") or request.args.get("snapshot_b")
    data = _diff_engine_snapshots(snapshot_a, snapshot_b)
    if not data:
        return jsonify({"ok": False, "error": "Snapshots not found"}), 404
    return jsonify({"ok": True, "data": data})


@app.get("/api/snapshots/golden")
def list_golden_snapshots():
    """List golden snapshots."""
    data = _list_golden_snapshots()
    return jsonify({"ok": True, "data": data})


@app.post("/api/snapshots/golden")
def set_golden_snapshot():
    """Set golden snapshot."""
    payload = request.get_json(silent=True) or {}
    try:
        kind = payload.get("kind")
        snapshot_id = payload.get("snapshot_id")
        label = payload.get("label")
        data = _set_golden_snapshot(kind, snapshot_id, label)
        return jsonify({"ok": True, "data": data})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.delete("/api/snapshots/golden/<kind>")
def clear_golden_snapshot(kind):
    """Run clear golden snapshot."""
    try:
        data = _clear_golden_snapshot(kind)
        return jsonify({"ok": True, "data": data})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.get("/api/snapshots/golden/diff")
def diff_golden_snapshot():
    """Diff golden snapshot."""
    snapshot_id = request.args.get("snapshot_id")
    try:
        data = _diff_golden_snapshot(snapshot_id)
        return jsonify({"ok": True, "data": data})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.get("/api/snapshots/resolve")
def resolve_snapshot_subject():
    """Resolve snapshot subject."""
    alias_type = request.args.get("alias_type") or None
    alias_value = request.args.get("alias_value") or None
    data = _resolve_snapshot_subject(alias_type, alias_value)
    if not data:
        return jsonify({"ok": False, "error": "No matching subject"}), 404
    return jsonify({"ok": True, "data": data})


@app.get("/api/snapshots/events")
def list_snapshot_events():
    """List snapshot events."""
    canonical_ids = request.args.get("canonical_ids") or ""
    ids = [cid for cid in canonical_ids.split(",") if cid]
    limit = request.args.get("limit", type=int) or 50
    data = _list_snapshot_events(canonical_ids=ids, limit=limit)
    return jsonify({"ok": True, "data": data})


@app.get("/api/symptoms")
def list_symptoms():
    """List symptoms."""
    return jsonify({"ok": True, "data": _list_symptom_templates()})


@app.get("/api/symptoms/<symptom_id>")
def get_symptom(symptom_id):
    """Get symptom."""
    data = _get_symptom_template(symptom_id)
    if not data:
        return jsonify({"ok": False, "error": "Symptom template not found"}), 404
    return jsonify({"ok": True, "data": data})


@app.post("/api/symptoms/plan")
def plan_symptom():
    """Build a Tier-0 snapshot plan for a symptom template."""
    payload = request.get_json(silent=True) or {}
    try:
        data = _plan_symptom_tier0(payload)
        return jsonify({"ok": True, "data": data})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.get("/api/investigations")
def list_investigations():
    """List investigations."""
    limit = request.args.get("limit", type=int) or 50
    data = _list_investigations(limit=limit)
    return jsonify({"ok": True, "data": data})


@app.post("/api/investigations")
def create_investigation():
    """Create investigation."""
    payload = request.get_json(silent=True) or {}
    try:
        data = _create_investigation(payload)
        return jsonify({"ok": True, "data": data})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.get("/api/investigations/<investigation_id>")
def get_investigation(investigation_id):
    """Get investigation."""
    data = _get_investigation(investigation_id)
    if not data:
        return jsonify({"ok": False, "error": "Investigation not found"}), 404
    return jsonify({"ok": True, "data": data})


@app.put("/api/investigations/<investigation_id>")
def update_investigation(investigation_id):
    """Update investigation (title/status/tags/notes)."""
    payload = request.get_json(silent=True) or {}
    try:
        data = _update_investigation(investigation_id, payload)
        return jsonify({"ok": True, "data": data})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.post("/api/investigations/<investigation_id>/notes")
def add_investigation_note(investigation_id):
    """Add investigation note."""
    payload = request.get_json(silent=True) or {}
    try:
        data = _add_investigation_note(investigation_id, payload)
        return jsonify({"ok": True, "data": data})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.post("/api/investigations/<investigation_id>/events")
def add_investigation_event(investigation_id):
    """Add investigation event."""
    payload = request.get_json(silent=True) or {}
    try:
        data = _add_investigation_event(investigation_id, payload)
        return jsonify({"ok": True, "data": data})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.get("/api/investigations/<investigation_id>/context")
def get_investigation_context(investigation_id):
    """Get investigation context."""
    try:
        data = _get_investigation_context(investigation_id)
        return jsonify({"ok": True, "data": data})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.put("/api/investigations/<investigation_id>/context")
def update_investigation_context(investigation_id):
    """Update investigation context."""
    payload = request.get_json(silent=True) or {}
    try:
        data = _update_investigation_context(investigation_id, payload)
        return jsonify({"ok": True, "data": data})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.get("/api/incidents")
def list_incidents():
    """List incidents."""
    limit = request.args.get("limit", type=int) or 50
    data = _list_incidents(limit=limit)
    return jsonify({"ok": True, "data": data})


@app.post("/api/incidents")
def create_incident():
    """Create incident."""
    payload = request.get_json(silent=True) or {}
    try:
        data = _create_incident(payload)
        return jsonify({"ok": True, "data": data})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.get("/api/incidents/<incident_id>")
def get_incident(incident_id):
    """Get incident."""
    data = _get_incident(incident_id)
    if not data:
        return jsonify({"ok": False, "error": "Incident not found"}), 404
    return jsonify({"ok": True, "data": data})


@app.put("/api/incidents/<incident_id>")
def update_incident(incident_id):
    """Update incident."""
    payload = request.get_json(silent=True) or {}
    try:
        data = _update_incident(incident_id, payload)
        return jsonify({"ok": True, "data": data})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.post("/api/incidents/<incident_id>/snapshots")
def link_incident_snapshot(incident_id):
    """Run link incident snapshot."""
    payload = request.get_json(silent=True) or {}
    snapshot_id = payload.get("snapshot_id")
    try:
        data = _link_incident_snapshot(incident_id, snapshot_id)
        return jsonify({"ok": True, "data": data})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.post("/api/incidents/<incident_id>/events")
def link_incident_event(incident_id):
    """Run link incident event."""
    payload = request.get_json(silent=True) or {}
    event_id = payload.get("event_id")
    try:
        data = _link_incident_event(incident_id, event_id)
        return jsonify({"ok": True, "data": data})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.get("/api/incidents/<incident_id>/graph")
def incident_graph(incident_id):
    """Run incident graph."""
    try:
        data = _build_incident_graph(incident_id)
        return jsonify({"ok": True, "data": data})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.get("/api/incidents/<incident_id>/timeline")
def incident_timeline(incident_id):
    """Run incident timeline."""
    try:
        data = _build_incident_timeline(incident_id)
        return jsonify({"ok": True, "data": data})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.get("/api/incidents/<incident_id>/report")
def get_incident_report(incident_id):
    """Get incident report."""
    try:
        data = _get_incident_report(incident_id) or {}
        return jsonify({"ok": True, "data": data})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.post("/api/incidents/<incident_id>/report")
def save_incident_report(incident_id):
    """Run save incident report."""
    payload = request.get_json(silent=True) or {}
    report = payload.get("report") or payload
    try:
        data = _update_incident_report(incident_id, report)
        return jsonify({"ok": True, "data": data})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.post("/api/incidents/<incident_id>/report/render")
def render_incident_report(incident_id):
    """Render incident report."""
    payload = request.get_json(silent=True) or {}
    fmt = payload.get("format") or "markdown"
    redaction = payload.get("redaction") or "internal"
    report = payload.get("report")
    try:
        data = _render_incident_report(incident_id, fmt, redaction, report=report)
        return jsonify({"ok": True, "data": data})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.post("/api/snapshots/capture")
def capture_snapshot():
    """Capture snapshot."""
    payload = request.get_json(silent=True) or {}
    try:
        data = _capture_snapshots(payload)
        return jsonify({"ok": True, "data": data})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.post("/api/snapshots/finalize")
def finalize_snapshot():
    """Finalize snapshot."""
    payload = request.get_json(silent=True) or {}
    try:
        data = _finalize_draft_snapshot(payload)
        return jsonify({"ok": True, "data": data})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.post("/api/topology/history")
def add_topology_history():
    """Add topology history."""
    payload = request.get_json(silent=True) or {}
    limit = payload.get("limit")
    snapshot = payload.get("snapshot") or payload.get("data") or payload
    try:
        data = STATE.append_topology_history(snapshot, limit=limit)
        return jsonify({"ok": True, "data": data})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.get("/")
def index():
    """Run index."""
    return _render_index_html()


@app.get("/help")
@app.get("/help/<path:_path>")
def help_page(_path=None):
    """Run help page."""
    return _render_index_html()


@app.get("/<path:path>")
def spa_fallback(path):
    """Run spa fallback."""
    if path.startswith("api/"):
        return jsonify({"ok": False, "error": "Not found"}), 404
    candidate = ROOT / path
    if candidate.exists() and candidate.is_file():
        # Always return the file (no conditional 304 responses) so UI updates are
        # immediately visible during local development.
        try:
            return send_from_directory(str(ROOT), path, conditional=False, max_age=0)
        except TypeError:
            # Flask <2.2 uses cache_timeout instead of max_age.
            return send_from_directory(str(ROOT), path, conditional=False, cache_timeout=0)
    return _render_index_html()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8001, debug=True)
