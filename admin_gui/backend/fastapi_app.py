from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import asyncio
import json
import os
import subprocess
try:
    import pty
except Exception:
    pty = None

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

app = FastAPI(title="Graph Admin Studio API")
ensure_snapshot_scheduler()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://127.0.0.1", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"] ,
    allow_headers=["*"] ,
)


class TaskRequest(BaseModel):
    service: str
    action: str
    params: dict | None = None
    target: dict | None = None


class ConfigUpdate(BaseModel):
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
    passphrase: str | None = None
    use_keychain: bool | None = False


class ConfigImportRequest(BaseModel):
    passphrase: str | None = None
    payload: dict | None = None


@app.get("/api/status")
def status():
    return STATE.status()


@app.get("/api/status/summary")
def status_summary():
    return _system_status_summary()


@app.get("/api/config")
def get_config():
    return STATE.get_config_public()


@app.post("/api/config")
def update_config(config: ConfigUpdate):
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


@app.get("/api/artifacts/{filename}")
def get_artifact(filename: str):
    path = ARTIFACTS_DIR / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="Artifact not found")
    return FileResponse(path, filename=path.name)


@app.post("/api/config/export")
def export_config(payload: ConfigExportRequest):
    data = payload.model_dump()
    try:
        blob = STATE.export_config_encrypted(passphrase=data.get("passphrase"), use_keychain=bool(data.get("use_keychain")))
        return {"ok": True, "data": blob}
    except Exception as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})


@app.post("/api/config/import")
def import_config(payload: ConfigImportRequest):
    data = payload.model_dump()
    try:
        blob = data.get("payload") or {}
        result = STATE.import_config_encrypted(blob, passphrase=data.get("passphrase"))
        return {"ok": True, "data": result}
    except Exception as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})


@app.post("/api/task")
def run_task(task: TaskRequest):
    try:
        data = dispatch_task(task.service, task.action, task.params, task.target)
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
        return JSONResponse(
            status_code=400,
            content={
                "ok": False,
                "error": str(exc),
                "status_code": exc.status_code,
                "request_id": exc.request_id,
                "detail": detail,
                "hint": hint,
                "rate_limit": rate_limit or None,
                "suggested_wait_seconds": suggested_wait,
            },
        )
    except PowerShellCommandError as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc), "detail": exc.output})
    except Exception as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})


@app.get("/api/topology/history")
def get_topology_history(limit: int | None = None):
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
    data = _list_action_snapshots(snapshot_type=type, target=target, prefix=prefix, action=action, limit=limit)
    return {"ok": True, "data": data}


@app.get("/api/snapshots/{snapshot_id}")
def get_snapshot(snapshot_id: str):
    data = _get_action_snapshot(snapshot_id)
    if not data:
        return JSONResponse(status_code=404, content={"ok": False, "error": "Snapshot not found"})
    return {"ok": True, "data": data}


@app.get("/api/snapshots/history")
def get_snapshot_history(canonical_id: str | None = None, limit: int | None = 20):
    data = _list_engine_snapshots(canonical_id=canonical_id, limit=limit or 20)
    return {"ok": True, "data": data}


@app.get("/api/snapshots/engine/{snapshot_id}")
def get_engine_snapshot(snapshot_id: str):
    data = _get_engine_snapshot(snapshot_id)
    if not data:
        return JSONResponse(status_code=404, content={"ok": False, "error": "Snapshot not found"})
    return {"ok": True, "data": data}


@app.get("/api/snapshots/entities")
def list_snapshot_entities(limit: int | None = 200):
    data = _list_snapshot_entities(limit=limit or 200)
    return {"ok": True, "data": data}


@app.get("/api/snapshots/engine/diff")
def diff_engine_snapshots(snapshot_a: str | None = None, snapshot_b: str | None = None, a: str | None = None, b: str | None = None):
    left = snapshot_a or a
    right = snapshot_b or b
    data = _diff_engine_snapshots(left, right)
    if not data:
        return JSONResponse(status_code=404, content={"ok": False, "error": "Snapshots not found"})
    return {"ok": True, "data": data}


@app.get("/api/snapshots/golden")
def list_golden_snapshots():
    data = _list_golden_snapshots()
    return {"ok": True, "data": data}


@app.post("/api/snapshots/golden")
def set_golden_snapshot(payload: dict):
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
    try:
        data = _clear_golden_snapshot(kind)
        return {"ok": True, "data": data}
    except Exception as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})


@app.get("/api/snapshots/golden/diff")
def diff_golden_snapshot(snapshot_id: str):
    try:
        data = _diff_golden_snapshot(snapshot_id)
        return {"ok": True, "data": data}
    except Exception as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})


@app.get("/api/snapshots/resolve")
def resolve_snapshot_subject(alias_type: str | None = None, alias_value: str | None = None):
    data = _resolve_snapshot_subject(alias_type, alias_value)
    if not data:
        return JSONResponse(status_code=404, content={"ok": False, "error": "No matching subject"})
    return {"ok": True, "data": data}


@app.get("/api/snapshots/events")
def list_snapshot_events(canonical_ids: str | None = None, limit: int | None = 50):
    ids = [cid for cid in (canonical_ids or "").split(",") if cid]
    data = _list_snapshot_events(canonical_ids=ids, limit=limit or 50)
    return {"ok": True, "data": data}


@app.get("/api/symptoms")
def list_symptoms():
    return {"ok": True, "data": _list_symptom_templates()}


@app.get("/api/symptoms/{symptom_id}")
def get_symptom(symptom_id: str):
    data = _get_symptom_template(symptom_id)
    if not data:
        return JSONResponse(status_code=404, content={"ok": False, "error": "Symptom template not found"})
    return {"ok": True, "data": data}


@app.get("/api/incidents")
def list_incidents(limit: int | None = 50):
    data = _list_incidents(limit=limit or 50)
    return {"ok": True, "data": data}


@app.post("/api/incidents")
def create_incident(payload: dict):
    try:
        data = _create_incident(payload)
        return {"ok": True, "data": data}
    except Exception as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})


@app.get("/api/incidents/{incident_id}")
def get_incident(incident_id: str):
    data = _get_incident(incident_id)
    if not data:
        return JSONResponse(status_code=404, content={"ok": False, "error": "Incident not found"})
    return {"ok": True, "data": data}


@app.put("/api/incidents/{incident_id}")
def update_incident(incident_id: str, payload: dict):
    try:
        data = _update_incident(incident_id, payload)
        return {"ok": True, "data": data}
    except Exception as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})


@app.post("/api/incidents/{incident_id}/snapshots")
def link_incident_snapshot(incident_id: str, payload: dict):
    try:
        data = _link_incident_snapshot(incident_id, payload.get("snapshot_id"))
        return {"ok": True, "data": data}
    except Exception as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})


@app.post("/api/incidents/{incident_id}/events")
def link_incident_event(incident_id: str, payload: dict):
    try:
        data = _link_incident_event(incident_id, payload.get("event_id"))
        return {"ok": True, "data": data}
    except Exception as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})


@app.get("/api/incidents/{incident_id}/graph")
def incident_graph(incident_id: str):
    try:
        data = _build_incident_graph(incident_id)
        return {"ok": True, "data": data}
    except Exception as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})


@app.get("/api/incidents/{incident_id}/timeline")
def incident_timeline(incident_id: str):
    try:
        data = _build_incident_timeline(incident_id)
        return {"ok": True, "data": data}
    except Exception as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})


@app.get("/api/incidents/{incident_id}/report")
def get_incident_report(incident_id: str):
    try:
        data = _get_incident_report(incident_id) or {}
        return {"ok": True, "data": data}
    except Exception as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})


@app.post("/api/incidents/{incident_id}/report")
def save_incident_report(incident_id: str, payload: dict):
    report = payload.get("report") if isinstance(payload, dict) else payload
    try:
        data = _update_incident_report(incident_id, report)
        return {"ok": True, "data": data}
    except Exception as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})


@app.post("/api/incidents/{incident_id}/report/render")
def render_incident_report(incident_id: str, payload: dict):
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
    try:
        data = _capture_snapshots(payload)
        return {"ok": True, "data": data}
    except Exception as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})


@app.post("/api/snapshots/finalize")
def finalize_snapshot(payload: dict):
    try:
        data = _finalize_draft_snapshot(payload)
        return {"ok": True, "data": data}
    except Exception as exc:
        return JSONResponse(status_code=400, content={"ok": False, "error": str(exc)})


@app.get("/api/snapshots/diff")
def diff_snapshots(snapshot_a: str | None = None, snapshot_b: str | None = None, a: str | None = None, b: str | None = None):
    left = snapshot_a or a
    right = snapshot_b or b
    data = _diff_action_snapshots(left, right)
    if not data:
        return JSONResponse(status_code=404, content={"ok": False, "error": "Snapshots not found"})
    return {"ok": True, "data": data}


@app.post("/api/topology/history")
def add_topology_history(payload: dict):
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
    return FileResponse(ROOT / "index.html")


app.mount("/", StaticFiles(directory=ROOT, html=True), name="static")


def _build_ssh_command(payload):
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


@app.websocket("/ws/ssh")
async def ssh_terminal(websocket: WebSocket):
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
            while True:
                data = await loop.run_in_executor(None, os.read, master_fd, 1024)
                if not data:
                    break
                await websocket.send_bytes(data)

        async def write_pty():
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
