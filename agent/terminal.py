from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
import json
import os
import platform
import secrets
import shutil
import subprocess
import time
import urllib.parse


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


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_int(value: Any, default: int) -> int:
    if value is None:
        return default
    try:
        return int(value)
    except Exception:
        return default


def _ws_base_url(http_base_url: str) -> str:
    parsed = urllib.parse.urlparse((http_base_url or "").strip())
    scheme = parsed.scheme.lower()
    if scheme == "https":
        ws_scheme = "wss"
    else:
        ws_scheme = "ws"
    return urllib.parse.urlunparse((ws_scheme, parsed.netloc, "", "", "", ""))


def build_terminal_ws_url(control_plane_url: str, session_id: str) -> str:
    base = _ws_base_url(control_plane_url).rstrip("/")
    sid = urllib.parse.quote(str(session_id or "").strip())
    return f"{base}/ws/terminal/{sid}"


def _chunk_text(text: str, *, max_chars: int = 16_000) -> list[str]:
    if not text:
        return []
    if max_chars <= 0:
        return [text]
    return [text[i : i + max_chars] for i in range(0, len(text), max_chars)]


def _command_runner_args(command: str) -> list[str]:
    system = platform.system().lower()
    if system == "windows":
        exe = shutil.which("pwsh") or shutil.which("powershell") or "powershell"
        return [exe, "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-Command", command]
    shell = os.environ.get("SHELL") or "/bin/sh"
    return [shell, "-lc", command]


def _run_command(command: str, *, timeout_seconds: int) -> dict[str, Any]:
    started = time.time()
    try:
        proc = subprocess.run(
            _command_runner_args(command),
            capture_output=True,
            text=True,
            timeout=max(1, int(timeout_seconds or 60)),
        )
        duration_ms = int((time.time() - started) * 1000)
        return {
            "ok": proc.returncode == 0,
            "stdout": proc.stdout or "",
            "stderr": proc.stderr or "",
            "exit_code": int(proc.returncode),
            "duration_ms": duration_ms,
        }
    except subprocess.TimeoutExpired as exc:
        duration_ms = int((time.time() - started) * 1000)
        out = ""
        err = ""
        try:
            out = (exc.stdout or "") if isinstance(exc.stdout, str) else ""
        except Exception:
            out = ""
        try:
            err = (exc.stderr or "") if isinstance(exc.stderr, str) else ""
        except Exception:
            err = ""
        return {
            "ok": False,
            "stdout": out,
            "stderr": (err + "\nTimed out").strip(),
            "exit_code": 124,
            "duration_ms": duration_ms,
            "error": {"error": "timeout"},
        }
    except Exception as exc:
        duration_ms = int((time.time() - started) * 1000)
        return {
            "ok": False,
            "stdout": "",
            "stderr": str(exc),
            "exit_code": 1,
            "duration_ms": duration_ms,
            "error": {"error": "exception", "type": exc.__class__.__name__, "message": str(exc)},
        }


@dataclass(frozen=True)
class TerminalSession:
    session_id: str
    agent_id: str
    expires_at: str | None = None

    @classmethod
    def from_payload(cls, payload: dict[str, Any], *, agent_id: str) -> "TerminalSession":
        sid = str(payload.get("session_id") or "").strip()
        if not sid:
            raise ValueError("terminal session missing session_id")
        return cls(session_id=sid, agent_id=str(agent_id), expires_at=str(payload.get("expires_at") or "") or None)


async def serve_terminal_session(
    *,
    control_plane_url: str,
    agent_id: str,
    token: str,
    session: TerminalSession,
) -> None:
    """Connect outbound to the control plane WebSocket and execute operator commands."""
    try:
        import websockets  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(f"websockets dependency missing: {exc}")

    ws_url = build_terminal_ws_url(control_plane_url, session.session_id)
    headers = [("Authorization", f"Bearer {token}")]

    command_timeout = _parse_int(os.environ.get("GAS_TERMINAL_COMMAND_TIMEOUT_SECONDS"), 120)
    command_timeout = max(1, min(3600, command_timeout))

    async with websockets.connect(ws_url, additional_headers=headers, max_size=8 * 1024 * 1024) as ws:
        await ws.send(json.dumps({"type": "hello", "role": "agent", "agent_id": agent_id, "timestamp": _now_iso()}))

        while True:
            # Respect expiry.
            expires = _parse_iso(session.expires_at) if session.expires_at else None
            if expires and expires <= datetime.now(timezone.utc):
                await ws.send(json.dumps({"type": "status", "status": "expired", "timestamp": _now_iso()}))
                return

            raw = await ws.recv()
            if raw is None:
                return
            try:
                msg = json.loads(raw) if isinstance(raw, str) else {}
            except Exception:
                msg = {}
            if not isinstance(msg, dict):
                continue
            msg_type = str(msg.get("type") or "").strip().lower()
            if msg_type in ("end", "close", "terminate"):
                await ws.send(json.dumps({"type": "status", "status": "closed", "timestamp": _now_iso()}))
                return
            if msg_type != "command":
                continue
            command = str(msg.get("command") or "").rstrip()
            if not command:
                continue
            cmd_id = str(msg.get("command_id") or secrets.token_hex(8))

            result = _run_command(command, timeout_seconds=command_timeout)
            for chunk in _chunk_text(result.get("stdout") or ""):
                await ws.send(json.dumps({"type": "output", "stream": "stdout", "command_id": cmd_id, "data": chunk}))
            for chunk in _chunk_text(result.get("stderr") or ""):
                await ws.send(json.dumps({"type": "output", "stream": "stderr", "command_id": cmd_id, "data": chunk}))
            await ws.send(
                json.dumps(
                    {
                        "type": "exit",
                        "command_id": cmd_id,
                        "exit_code": int(result.get("exit_code") or 0),
                        "ok": bool(result.get("ok")),
                        "duration_ms": int(result.get("duration_ms") or 0),
                        "timestamp": _now_iso(),
                    }
                )
            )
