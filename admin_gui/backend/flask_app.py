from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory

from .core import STATE, dispatch_task, _read_audit_log, get_action_source, _list_action_snapshots, _get_action_snapshot
from platform_core.interpreter import interpret_response
from microsoft import GraphAPIError, PowerShellCommandError

ROOT = Path(__file__).resolve().parents[1]

app = Flask(__name__, static_folder=str(ROOT), static_url_path="")


@app.get("/api/status")
def status():
    return jsonify(STATE.status())


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
        data = dispatch_task(service, action, params)
        normalized = None
        try:
            normalized = interpret_response(service, action, data, source=get_action_source(service, action))
        except Exception:
            normalized = None
        return jsonify({"ok": True, "data": data, "normalized": normalized})
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
    limit = request.args.get("limit", type=int) or 50
    data = _list_action_snapshots(snapshot_type=snapshot_type, target=target, prefix=prefix, limit=limit)
    return jsonify({"ok": True, "data": data})


@app.get("/api/snapshots/<snapshot_id>")
def get_snapshot(snapshot_id):
    data = _get_action_snapshot(snapshot_id)
    if not data:
        return jsonify({"ok": False, "error": "Snapshot not found"}), 404
    return jsonify({"ok": True, "data": data})


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


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8001, debug=True)
