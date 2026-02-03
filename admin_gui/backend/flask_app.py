from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory

from .core import (
    STATE,
    dispatch_task,
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
    ensure_snapshot_scheduler,
    ARTIFACTS_DIR,
)
from platform_core.interpreter import interpret_response
from microsoft import GraphAPIError, PowerShellCommandError

ROOT = Path(__file__).resolve().parents[1]

app = Flask(__name__, static_folder=str(ROOT), static_url_path="")
ensure_snapshot_scheduler()


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
    try:
        service = payload.get("service")
        action = payload.get("action")
        params = payload.get("params")
        target = payload.get("target")
        data = dispatch_task(service, action, params, target)
        normalized = None
        try:
            normalized_payload = _extract_action_payload(data)
            normalized = interpret_response(service, action, normalized_payload, source=get_action_source(service, action))
        except Exception:
            normalized = None
        return jsonify({"ok": True, "data": data, "normalized": normalized, "target": target})
    except GraphAPIError as exc:
        detail = ""
        rate_limit = {}
        suggested_wait = None
        if exc.response is not None:
            try:
                detail = exc.response.json()
            except Exception:
                detail = exc.response.text
            headers = exc.response.headers or {}
            header_keys = [
                "Retry-After",
                "x-ms-retry-after-ms",
                "RateLimit-Remaining",
                "RateLimit-Reset",
                "RateLimit-Limit",
                "x-ms-throttle-limit",
                "x-ms-usage",
            ]
            for key in header_keys:
                if key in headers:
                    rate_limit[key] = headers.get(key)
            retry_after = exc.retry_after
            if retry_after is None:
                retry_after_header = headers.get("Retry-After")
                if retry_after_header:
                    try:
                        retry_after = int(retry_after_header)
                    except ValueError:
                        retry_after = None
            retry_after_ms = headers.get("x-ms-retry-after-ms")
            if retry_after is None and retry_after_ms:
                try:
                    retry_after = max(1, int(int(retry_after_ms) / 1000))
                except ValueError:
                    retry_after = None
            suggested_wait = retry_after
        hint = None
        if exc.code in ("Authorization_RequestDenied", "InsufficientPrivileges"):
            hint = "App permission missing or admin consent not granted. Add the permission in Entra and grant admin consent."
        if isinstance(detail, dict):
            err_code = detail.get("error", {}).get("code") if detail.get("error") else None
            if err_code in ("Authorization_RequestDenied", "InsufficientPrivileges"):
                hint = "App permission missing or admin consent not granted. Add the permission in Entra and grant admin consent."
        return jsonify({
            "ok": False,
            "error": str(exc),
            "status_code": exc.status_code,
            "request_id": exc.request_id,
            "detail": detail,
            "hint": hint,
            "rate_limit": rate_limit or None,
            "suggested_wait_seconds": suggested_wait,
        }), 400
    except PowerShellCommandError as exc:
        return jsonify({"ok": False, "error": str(exc), "detail": exc.output}), 400
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


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8001, debug=True)
