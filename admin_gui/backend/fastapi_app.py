from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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

from .core import STATE, dispatch_task
from microsoft import GraphAPIError, PowerShellCommandError

ROOT = Path(__file__).resolve().parents[1]

app = FastAPI(title="Graph Admin Studio API")

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


@app.get("/api/status")
def status():
    return STATE.status()


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


@app.post("/api/task")
def run_task(task: TaskRequest):
    try:
        data = dispatch_task(task.service, task.action, task.params)
        return {"ok": True, "data": data}
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
