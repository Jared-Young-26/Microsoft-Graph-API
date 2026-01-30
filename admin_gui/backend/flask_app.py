from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory

from .core import STATE, dispatch_task
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


@app.post("/api/task")
def run_task():
    payload = request.get_json(silent=True) or {}
    try:
        data = dispatch_task(payload.get("service"), payload.get("action"), payload.get("params"))
        return jsonify({"ok": True, "data": data})
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


@app.get("/")
def index():
    return send_from_directory(str(ROOT), "index.html")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8001, debug=True)
