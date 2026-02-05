from pathlib import Path
from datetime import datetime, timezone
import sqlite3
from flask import Flask, jsonify, request, send_from_directory

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
    ensure_snapshot_scheduler,
    ensure_onedrive_cache_warmup_scheduler,
    ARTIFACTS_DIR,
)
from platform_core.interpreter import interpret_response
from platform_core.graph_error_transparency import build_graph_error_response
from microsoft import GraphAPIError, PowerShellCommandError, set_trace_context, reset_trace_context

ROOT = Path(__file__).resolve().parents[1]

# Disable Flask's built-in static route so SPA fallbacks can handle deep links.
app = Flask(__name__, static_folder=None)
ensure_snapshot_scheduler()
ensure_onedrive_cache_warmup_scheduler()


@app.get("/api/status")
def status():
    return jsonify(STATE.status())


@app.get("/api/status/summary")
def status_summary():
    return jsonify(_system_status_summary())


@app.get("/api/config")
def get_config():
    return jsonify(STATE.get_config_public())


@app.post("/api/config")
def update_config():
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
    STATE.reload()
    return jsonify({"ok": True, "data": STATE.get_config_public()})


@app.get("/api/audit")
def get_audit():
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


@app.get("/api/artifacts/<path:filename>")
def get_artifact(filename):
    try:
        return send_from_directory(ARTIFACTS_DIR, filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify({"ok": False, "error": "Artifact not found"}), 404


@app.post("/api/config/export")
def export_config():
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
    payload = request.get_json(silent=True) or {}
    service = payload.get("service")
    action = payload.get("action")
    params = payload.get("params") or {}
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
        return jsonify({"ok": False, "error": str(exc), "detail": exc.output}), 400
    except Exception as exc:
        message = str(exc)
        lowered = message.lower()
        # Treat validation / parameter issues as client errors.
        if isinstance(exc, ValueError):
            return jsonify({"ok": False, "error": message, "status_code": 400}), 400
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


@app.post("/ingest/perception")
def ingest_vision_u_eye_perception():
    payload = request.get_json(silent=True) or {}
    try:
        data = _ingest_vision_u_eye_visual_signal(payload)
        return jsonify(data)
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.get("/api/debug/traces")
def debug_traces():
    limit = request.args.get("limit", type=int) or 50
    ui_request_id = request.args.get("ui_request_id") or None
    request_id = request.args.get("request_id") or None
    return jsonify({"ok": True, "data": list_graph_traces(limit=limit, ui_request_id=ui_request_id, request_id=request_id)})


@app.get("/api/debug/traces/<ui_request_id>")
def debug_traces_by_ui(ui_request_id):
    limit = request.args.get("limit", type=int) or 200
    return jsonify({"ok": True, "data": list_graph_traces(limit=limit, ui_request_id=ui_request_id)})


@app.get("/api/debug/traces/by-graph-request/<request_id>")
def debug_traces_by_graph_request(request_id):
    limit = request.args.get("limit", type=int) or 200
    return jsonify({"ok": True, "data": list_graph_traces(limit=limit, request_id=request_id)})


@app.get("/api/debug/graph-reliability")
def graph_reliability():
    return jsonify({"ok": True, "data": graph_reliability_summary()})


@app.post("/api/signals/visual")
def ingest_visual_signal_api():
    payload = request.get_json(silent=True) or {}
    try:
        data = _ingest_vision_u_eye_visual_signal(payload)
        return jsonify(data)
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.get("/api/signals/visual")
def list_visual_signals_api():
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
    limit = request.args.get("limit", type=int)
    try:
        data = STATE.get_topology_history(limit=limit)
        return jsonify({"ok": True, "data": data})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.get("/api/snapshots")
def list_snapshots():
    snapshot_type = request.args.get("type") or None
    target = request.args.get("target") or None
    prefix = request.args.get("prefix") or None
    action = request.args.get("action") or None
    limit = request.args.get("limit", type=int) or 50
    data = _list_action_snapshots(snapshot_type=snapshot_type, target=target, prefix=prefix, action=action, limit=limit)
    return jsonify({"ok": True, "data": data})


@app.get("/api/snapshots/diff")
def diff_snapshots():
    snapshot_a = request.args.get("a") or request.args.get("snapshot_a")
    snapshot_b = request.args.get("b") or request.args.get("snapshot_b")
    data = _diff_action_snapshots(snapshot_a, snapshot_b)
    if not data:
        return jsonify({"ok": False, "error": "Snapshots not found"}), 404
    return jsonify({"ok": True, "data": data})


@app.get("/api/snapshots/<snapshot_id>")
def get_snapshot(snapshot_id):
    data = _get_action_snapshot(snapshot_id)
    if not data:
        return jsonify({"ok": False, "error": "Snapshot not found"}), 404
    return jsonify({"ok": True, "data": data})


@app.get("/api/snapshots/history")
def get_snapshot_history():
    canonical_id = request.args.get("canonical_id") or None
    limit = request.args.get("limit", type=int) or 20
    data = _list_engine_snapshots(canonical_id=canonical_id, limit=limit)
    return jsonify({"ok": True, "data": data})


@app.get("/api/snapshots/engine/<snapshot_id>")
def get_engine_snapshot(snapshot_id):
    data = _get_engine_snapshot(snapshot_id)
    if not data:
        return jsonify({"ok": False, "error": "Snapshot not found"}), 404
    return jsonify({"ok": True, "data": data})


@app.get("/api/snapshots/entities")
def list_snapshot_entities():
    limit = request.args.get("limit", type=int) or 200
    data = _list_snapshot_entities(limit=limit)
    return jsonify({"ok": True, "data": data})


@app.get("/api/snapshots/engine/diff")
def diff_engine_snapshots():
    snapshot_a = request.args.get("a") or request.args.get("snapshot_a")
    snapshot_b = request.args.get("b") or request.args.get("snapshot_b")
    data = _diff_engine_snapshots(snapshot_a, snapshot_b)
    if not data:
        return jsonify({"ok": False, "error": "Snapshots not found"}), 404
    return jsonify({"ok": True, "data": data})


@app.get("/api/snapshots/golden")
def list_golden_snapshots():
    data = _list_golden_snapshots()
    return jsonify({"ok": True, "data": data})


@app.post("/api/snapshots/golden")
def set_golden_snapshot():
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
    try:
        data = _clear_golden_snapshot(kind)
        return jsonify({"ok": True, "data": data})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.get("/api/snapshots/golden/diff")
def diff_golden_snapshot():
    snapshot_id = request.args.get("snapshot_id")
    try:
        data = _diff_golden_snapshot(snapshot_id)
        return jsonify({"ok": True, "data": data})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.get("/api/snapshots/resolve")
def resolve_snapshot_subject():
    alias_type = request.args.get("alias_type") or None
    alias_value = request.args.get("alias_value") or None
    data = _resolve_snapshot_subject(alias_type, alias_value)
    if not data:
        return jsonify({"ok": False, "error": "No matching subject"}), 404
    return jsonify({"ok": True, "data": data})


@app.get("/api/snapshots/events")
def list_snapshot_events():
    canonical_ids = request.args.get("canonical_ids") or ""
    ids = [cid for cid in canonical_ids.split(",") if cid]
    limit = request.args.get("limit", type=int) or 50
    data = _list_snapshot_events(canonical_ids=ids, limit=limit)
    return jsonify({"ok": True, "data": data})


@app.get("/api/symptoms")
def list_symptoms():
    return jsonify({"ok": True, "data": _list_symptom_templates()})


@app.get("/api/symptoms/<symptom_id>")
def get_symptom(symptom_id):
    data = _get_symptom_template(symptom_id)
    if not data:
        return jsonify({"ok": False, "error": "Symptom template not found"}), 404
    return jsonify({"ok": True, "data": data})


@app.get("/api/incidents")
def list_incidents():
    limit = request.args.get("limit", type=int) or 50
    data = _list_incidents(limit=limit)
    return jsonify({"ok": True, "data": data})


@app.post("/api/incidents")
def create_incident():
    payload = request.get_json(silent=True) or {}
    try:
        data = _create_incident(payload)
        return jsonify({"ok": True, "data": data})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.get("/api/incidents/<incident_id>")
def get_incident(incident_id):
    data = _get_incident(incident_id)
    if not data:
        return jsonify({"ok": False, "error": "Incident not found"}), 404
    return jsonify({"ok": True, "data": data})


@app.put("/api/incidents/<incident_id>")
def update_incident(incident_id):
    payload = request.get_json(silent=True) or {}
    try:
        data = _update_incident(incident_id, payload)
        return jsonify({"ok": True, "data": data})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.post("/api/incidents/<incident_id>/snapshots")
def link_incident_snapshot(incident_id):
    payload = request.get_json(silent=True) or {}
    snapshot_id = payload.get("snapshot_id")
    try:
        data = _link_incident_snapshot(incident_id, snapshot_id)
        return jsonify({"ok": True, "data": data})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.post("/api/incidents/<incident_id>/events")
def link_incident_event(incident_id):
    payload = request.get_json(silent=True) or {}
    event_id = payload.get("event_id")
    try:
        data = _link_incident_event(incident_id, event_id)
        return jsonify({"ok": True, "data": data})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.get("/api/incidents/<incident_id>/graph")
def incident_graph(incident_id):
    try:
        data = _build_incident_graph(incident_id)
        return jsonify({"ok": True, "data": data})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.get("/api/incidents/<incident_id>/timeline")
def incident_timeline(incident_id):
    try:
        data = _build_incident_timeline(incident_id)
        return jsonify({"ok": True, "data": data})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.get("/api/incidents/<incident_id>/report")
def get_incident_report(incident_id):
    try:
        data = _get_incident_report(incident_id) or {}
        return jsonify({"ok": True, "data": data})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.post("/api/incidents/<incident_id>/report")
def save_incident_report(incident_id):
    payload = request.get_json(silent=True) or {}
    report = payload.get("report") or payload
    try:
        data = _update_incident_report(incident_id, report)
        return jsonify({"ok": True, "data": data})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.post("/api/incidents/<incident_id>/report/render")
def render_incident_report(incident_id):
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
    payload = request.get_json(silent=True) or {}
    try:
        data = _capture_snapshots(payload)
        return jsonify({"ok": True, "data": data})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.post("/api/snapshots/finalize")
def finalize_snapshot():
    payload = request.get_json(silent=True) or {}
    try:
        data = _finalize_draft_snapshot(payload)
        return jsonify({"ok": True, "data": data})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.post("/api/topology/history")
def add_topology_history():
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
    return send_from_directory(str(ROOT), "index.html")


@app.get("/help")
@app.get("/help/<path:_path>")
def help_page(_path=None):
    return send_from_directory(str(ROOT), "index.html")


@app.get("/<path:path>")
def spa_fallback(path):
    if path.startswith("api/"):
        return jsonify({"ok": False, "error": "Not found"}), 404
    candidate = ROOT / path
    if candidate.exists() and candidate.is_file():
        return send_from_directory(str(ROOT), path)
    return send_from_directory(str(ROOT), "index.html")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8001, debug=True)
