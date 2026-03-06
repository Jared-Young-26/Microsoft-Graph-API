from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
from datetime import datetime, timezone
import json
import os
import platform
import socket
import tempfile
import time
import zipfile

from .config import AgentConfig
from .control_plane_client import ControlPlaneClient
from .json_logger import JsonLogger
from .token_store import AgentTokenStore
from .plugins.registry import load_plugins
from .plugins.interface import ActionResult
from .redaction import redact


def _ms_since(start: float) -> int:
    return int((time.time() - start) * 1000)


def _build_zip_bundle(bundle_path: Path, paths: list[Path]) -> None:
    """Build a zip bundle containing the provided file paths."""
    with zipfile.ZipFile(bundle_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for item in paths:
            try:
                p = Path(item).expanduser()
                if not p.exists() or not p.is_file():
                    continue
                zf.write(p, arcname=p.name)
            except Exception:
                continue


def _artifact_type_for_path(path: Path) -> str:
    suffix = str(Path(path).suffix or "").lower()
    if suffix in (".zip",):
        return "zip"
    if suffix in (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"):
        return "image"
    if suffix in (".mp4", ".mov", ".avi", ".mkv", ".webm"):
        return "video"
    if suffix in (".json", ".jsonl", ".txt", ".log", ".csv"):
        return "text"
    return "file"


@dataclass
class AgentRuntime:
    """Agent runtime."""

    config: AgentConfig

    def __post_init__(self) -> None:
        self.store = AgentTokenStore()
        self.client = ControlPlaneClient(self.config.control_plane_url)
        os.environ.setdefault("CONTROL_PLANE_URL", self.config.control_plane_url)
        log_path_env = os.environ.get("GAS_AGENT_LOG_PATH") or None
        log_path = Path(log_path_env).expanduser() if log_path_env else (self.store.state_dir / "agent.log.jsonl")
        self.logger = JsonLogger("gas-agent", {"agent_name": self.config.agent_name}, sink_path=log_path)
        self.plugins = load_plugins()
        self.action_index: dict[str, Any] = {}
        for plugin in self.plugins:
            try:
                for action in plugin.actions() or []:
                    self.action_index[action.action_id] = plugin
            except Exception:
                continue

    def _capabilities_payload(self) -> dict[str, Any]:
        caps: set[str] = set()
        for plugin in self.plugins:
            try:
                caps.update(plugin.capabilities() or [])
            except Exception:
                continue
        if self.config.break_glass_enabled:
            caps.add("break_glass.enabled")
        return {"capabilities": sorted(caps)}

    def _state_path(self, name: str) -> Path:
        """Resolve a state file path under the agent state dir."""
        self.store.state_dir.mkdir(parents=True, exist_ok=True)
        return self.store.state_dir / name

    def _persist_job_record(self, record: dict[str, Any]) -> None:
        """Persist a redacted job record for later evidence bundling."""
        try:
            safe = redact(record)
            last_path = self._state_path("last_job_result.json")
            last_path.write_text(json.dumps(safe, indent=2, default=str), encoding="utf-8")
            log_path = self._state_path("job_results.jsonl")
            with log_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(safe, default=str) + "\n")
        except Exception:
            return

    def _bootstrap_token(self) -> str | None:
        stored = self.store.read_token()
        if stored:
            return stored
        if self.config.token:
            self.store.write_token(self.config.token)
            return self.config.token
        return None

    def _bootstrap_agent_id(self) -> str | None:
        return self.store.read_agent_id()

    def _register(self) -> tuple[str, str]:
        agent_id = self._bootstrap_agent_id()
        token = self._bootstrap_token()
        payload: dict[str, Any] = {
            "agent_id": agent_id,
            "agent_token": token,
            "pairing_code": self.config.pairing_code,
            "name": self.config.agent_name,
            "tenant_id": self.config.tenant_id,
            "workspace_id": self.config.workspace_id,
            "hostname": socket.gethostname(),
            "os": platform.system(),
            "arch": platform.machine(),
            "version": os.environ.get("GAS_AGENT_VERSION") or "0.0.0",
            "labels": self.config.labels,
            **self._capabilities_payload(),
        }
        # Never log token-bearing payload.
        data = self.client.register(payload)
        next_agent_id = str(data.get("agent_id") or "")
        next_token = str(data.get("agent_token") or "").strip() or None
        if not next_agent_id:
            raise RuntimeError("Invalid register response (missing agent_id)")
        if not next_token:
            # Server may not rotate token on re-register. Keep stored token.
            next_token = str(token or "").strip() or None
        if not next_token:
            raise RuntimeError("Invalid register response (missing agent_token)")
        self.store.write_agent_id(next_agent_id)
        self.store.write_token(next_token)
        self.logger.info("agent_registered", agent_id=next_agent_id, hostname=payload.get("hostname"))
        return next_agent_id, next_token

    def _heartbeat(self, agent_id: str, token: str) -> None:
        payload = {
            **self._capabilities_payload(),
            "labels": self.config.labels,
            "tenant_id": self.config.tenant_id,
            "workspace_id": self.config.workspace_id,
        }
        self.client.heartbeat(agent_id, token, payload)

    def register_only(self) -> str:
        """Register/pair and exit (does not start polling loop)."""
        agent_id, _token = self._register()
        return agent_id

    def _handle_action(self, action_id: str, params: dict | None) -> ActionResult:
        plugin = self.action_index.get(action_id)
        if not plugin:
            return ActionResult(ok=False, stderr=f"Unknown action_id: {action_id}", exit_code=2)
        result = plugin.handle(action_id, params or {})
        if isinstance(result, ActionResult):
            return result
        if isinstance(result, dict):
            ok = bool(result.get("ok", True))
            return ActionResult(
                ok=ok,
                result=result.get("result") if "result" in result else result,
                stdout=result.get("stdout"),
                stderr=result.get("stderr"),
                exit_code=result.get("exit_code"),
                artifacts=[Path(p) for p in (result.get("artifacts") or []) if p],
            )
        return ActionResult(ok=False, stderr="Plugin returned invalid result", exit_code=2)

    def _upload_artifacts(self, agent_id: str, token: str, job_id: str, paths: list[Path]) -> list[dict[str, Any]]:
        if not paths:
            return []
        # If the plugin produced a single file, upload it directly to preserve type (png/mp4/etc).
        if len(paths) == 1:
            try:
                direct = Path(paths[0]).expanduser()
                if direct.exists() and direct.is_file():
                    resp = self.client.upload_artifact(
                        agent_id,
                        token,
                        direct.name,
                        direct.read_bytes(),
                        job_id=job_id,
                        artifact_type=_artifact_type_for_path(direct),
                    )
                    data = (resp.get("data") or {}) if resp.get("ok") is True else (resp.get("data") or resp)
                    artifact_id = data.get("artifact_id")
                    if artifact_id:
                        return [
                            {
                                "artifact_id": artifact_id,
                                "filename": data.get("filename"),
                                "url": data.get("url"),
                                "sha256": data.get("sha256"),
                                "size_bytes": data.get("size_bytes"),
                            }
                        ]
            except Exception:
                pass

        with tempfile.TemporaryDirectory(prefix="gas-agent-") as tmpdir:
            bundle = Path(tmpdir) / f"{job_id}-artifacts.zip"
            _build_zip_bundle(bundle, paths)
            content = bundle.read_bytes()
            resp = self.client.upload_artifact(
                agent_id,
                token,
                bundle.name,
                content,
                job_id=job_id,
                artifact_type=_artifact_type_for_path(bundle),
            )
        if resp.get("ok") is True:
            data = resp.get("data") or {}
        else:
            data = resp.get("data") or resp
        artifact_id = data.get("artifact_id")
        if not artifact_id:
            return []
        return [
            {
                "artifact_id": artifact_id,
                "filename": data.get("filename"),
                "url": data.get("url"),
                "sha256": data.get("sha256"),
                "size_bytes": data.get("size_bytes"),
            }
        ]

    def _run_job(self, agent_id: str, token: str, job: dict[str, Any]) -> None:
        job_id = str(job.get("job_id") or "")
        action_id = str(job.get("action_id") or "")
        risk_level = str(job.get("risk_level") or "safe").lower().strip()
        params = job.get("params") if isinstance(job.get("params"), dict) else {}

        log = self.logger.with_fields(job_id=job_id, action_id=action_id)
        started = time.time()
        log.info("job_started", risk_level=risk_level)

        if risk_level == "danger" and not self.config.break_glass_enabled:
            duration_ms = _ms_since(started)
            error = {"error": "break_glass_required", "risk_level": risk_level}
            self.client.post_job_result(
                agent_id,
                token,
                {
                    "job_id": job_id,
                    "status": "failed",
                    "result": None,
                    "stdout": "",
                    "stderr": "Refused: BREAK_GLASS_ENABLED required for danger jobs.",
                    "exit_code": 3,
                    "duration_ms": duration_ms,
                    "error": error,
                },
            )
            log.warning("job_refused", status="failed", duration_ms=duration_ms)
            return

        status = "completed"
        stdout = ""
        stderr = ""
        exit_code = 0
        result_payload: Any = None
        error_payload: Any = None
        artifacts_payload: list[dict[str, Any]] = []

        try:
            action_result = self._handle_action(action_id, params)
            status = "completed" if action_result.ok else "failed"
            result_payload = action_result.result
            stdout = action_result.stdout or ""
            stderr = action_result.stderr or ""
            if action_result.exit_code is not None:
                exit_code = int(action_result.exit_code)
            else:
                exit_code = 0 if action_result.ok else 1
            if action_result.artifacts:
                artifacts_payload = self._upload_artifacts(agent_id, token, job_id, action_result.artifacts)
        except Exception as exc:
            status = "failed"
            exit_code = 1
            stderr = str(exc)
            error_payload = {"error": "exception", "type": exc.__class__.__name__, "message": str(exc)}
            log.error("job_exception", exception=exc.__class__.__name__)

        duration_ms = _ms_since(started)
        job_result_payload = {
            "job_id": job_id,
            "status": status,
            "result": result_payload,
            "stdout": stdout,
            "stderr": stderr,
            "exit_code": exit_code,
            "artifacts": artifacts_payload,
            "duration_ms": duration_ms,
            "error": error_payload,
        }
        self.client.post_job_result(
            agent_id,
            token,
            job_result_payload,
        )
        self._persist_job_record(
            {
                "ts": datetime.now(timezone.utc).isoformat(),
                "agent_id": agent_id,
                "job_id": job_id,
                "action_id": action_id,
                "status": status,
                "duration_ms": duration_ms,
                "exit_code": exit_code,
                "error": error_payload,
                "artifacts": artifacts_payload,
                "stdout_tail": stdout[-4000:] if stdout else "",
                "stderr_tail": stderr[-4000:] if stderr else "",
            }
        )
        log.info("job_finished", status=status, duration_ms=duration_ms, exit_code=exit_code)

    def run_forever(self) -> None:
        agent_id, token = self._register()
        self.logger.info(
            "agent_loop_started",
            agent_id=agent_id,
            poll_interval=self.config.poll_interval,
            break_glass_enabled=bool(self.config.break_glass_enabled),
        )
        while True:
            try:
                self._heartbeat(agent_id, token)
                if self.config.break_glass_enabled:
                    session_payload = self.client.next_terminal_session(agent_id, token)
                    if session_payload:
                        try:
                            import asyncio
                            from .terminal import TerminalSession, serve_terminal_session

                            session = TerminalSession.from_payload(session_payload, agent_id=agent_id)
                            log = self.logger.with_fields(session_id=session.session_id)
                            log.warning("terminal_session_started", expires_at=session.expires_at)
                            asyncio.run(
                                serve_terminal_session(
                                    control_plane_url=self.config.control_plane_url,
                                    agent_id=agent_id,
                                    token=token,
                                    session=session,
                                )
                            )
                            log.warning("terminal_session_finished")
                        except Exception as exc:
                            self.logger.error("terminal_session_error", agent_id=agent_id, error=str(exc))
                        continue
                job = self.client.next_job(agent_id, token, lease_seconds=900)
                if not job:
                    time.sleep(self.config.poll_interval)
                    continue
                self._run_job(agent_id, token, job)
            except PermissionError:
                self.logger.warning("agent_unauthorized", agent_id=agent_id)
                agent_id, token = self._register()
            except KeyboardInterrupt:
                self.logger.info("agent_stopped", agent_id=agent_id)
                return
            except Exception as exc:
                self.logger.error("agent_loop_error", agent_id=agent_id, error=str(exc))
                time.sleep(min(30, max(1, self.config.poll_interval)))
