from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import hashlib
import json
import os
import platform
import secrets
import shutil
import subprocess
import time
import urllib.parse
import urllib.request
import zipfile

from ..token_store import AgentTokenStore
from .interface import ActionDefinition, ActionResult
from .manifest import load_manifest_for_plugin


def _now_utc_z() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _parse_int(value: Any, default: int) -> int:
    if value is None:
        return default
    try:
        return int(value)
    except Exception:
        return default


def _parse_bool(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in ("1", "true", "yes", "y", "on")


def _png_size(data: bytes) -> tuple[int | None, int | None]:
    # Minimal PNG parser (IHDR). Avoid non-stdlib deps.
    if not data or len(data) < 24:
        return None, None
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        return None, None
    if data[12:16] != b"IHDR":
        return None, None
    try:
        width = int.from_bytes(data[16:20], "big")
        height = int.from_bytes(data[20:24], "big")
        if width <= 0 or height <= 0:
            return None, None
        return width, height
    except Exception:
        return None, None


def _download_bytes(url: str, timeout_seconds: int = 30) -> bytes:
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
        return resp.read()


@dataclass
class VisionUEyeRunnerPlugin:
    """Vision-U-Eye runner plugin (screen capture + stub analysis)."""

    id: str = "vision_u_eye_runner"
    _store: AgentTokenStore = field(default_factory=AgentTokenStore, init=False, repr=False)
    _session_id: str = field(default="", init=False, repr=False)
    _sequence: int = field(default=0, init=False, repr=False)

    def __post_init__(self) -> None:
        self._session_id = self._load_or_create_session_id()
        self._sequence = self._load_sequence()

    def capabilities(self) -> list[str]:
        if not self._capture_supported():
            return []
        return ["observe.screen", "observe.snapshots"]

    def actions(self) -> list[ActionDefinition]:
        manifest_actions = load_manifest_for_plugin(self.id)
        if manifest_actions:
            return manifest_actions
        return [
            ActionDefinition(
                action_id="vision.capture_snapshot",
                title="Capture snapshot",
                description="Capture the current screen to an image artifact and emit a Vision-U-Eye signal payload.",
                required_capabilities=["observe.screen", "observe.snapshots"],
                risk_level="safe",
            ),
            ActionDefinition(
                action_id="vision.record_segment",
                title="Record segment",
                description="Record a short segment (v0: frame bundle zip) and return artifact + metadata.",
                required_capabilities=["observe.screen", "observe.snapshots"],
                risk_level="safe",
            ),
            ActionDefinition(
                action_id="vision.analyze_snapshot",
                title="Analyze snapshot",
                description="Analyze a snapshot (v0 stub) and return narration + labels + confidence.",
                required_capabilities=["observe.snapshots"],
                risk_level="safe",
            ),
            ActionDefinition(
                action_id="vision.stream_status",
                title="Stream status",
                description="Return sensor state (recording, fps, last capture time, queue depth).",
                required_capabilities=["observe.screen"],
                risk_level="safe",
            ),
        ]

    def handle(self, action_id: str, params: dict | None) -> ActionResult:
        params = params or {}
        if action_id == "vision.capture_snapshot":
            return self._capture_snapshot(params)
        if action_id == "vision.record_segment":
            return self._record_segment(params)
        if action_id == "vision.analyze_snapshot":
            return self._analyze_snapshot(params)
        if action_id == "vision.stream_status":
            return self._stream_status()
        return ActionResult(ok=False, stderr=f"Unknown action_id: {action_id}", exit_code=2)

    # ---- State ------------------------------------------------------------

    def _vision_dir(self) -> Path:
        path = self._store.state_dir / "vision_u_eye"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _state_path(self) -> Path:
        return self._vision_dir() / "state.json"

    def _session_path(self) -> Path:
        return self._vision_dir() / "session_id.txt"

    def _sequence_path(self) -> Path:
        return self._vision_dir() / "sequence.txt"

    def _load_or_create_session_id(self) -> str:
        path = self._session_path()
        try:
            existing = path.read_text(encoding="utf-8").strip()
            if existing:
                return existing
        except Exception:
            pass
        new = secrets.token_hex(16)
        try:
            path.write_text(new, encoding="utf-8")
        except Exception:
            pass
        return new

    def _load_sequence(self) -> int:
        path = self._sequence_path()
        try:
            text = path.read_text(encoding="utf-8").strip()
            value = int(text)
            return max(0, value)
        except Exception:
            return 0

    def _next_sequence(self) -> int:
        self._sequence = max(0, int(self._sequence or 0)) + 1
        try:
            self._sequence_path().write_text(str(self._sequence), encoding="utf-8")
        except Exception:
            pass
        return self._sequence

    def _read_state(self) -> dict[str, Any]:
        try:
            path = self._state_path()
            if not path.exists():
                return {}
            parsed = json.loads(path.read_text(encoding="utf-8"))
            return parsed if isinstance(parsed, dict) else {}
        except Exception:
            return {}

    def _write_state(self, updates: dict[str, Any]) -> None:
        current = self._read_state()
        current.update(updates or {})
        try:
            self._state_path().write_text(json.dumps(current, indent=2, default=str), encoding="utf-8")
        except Exception:
            pass

    # ---- Capture / analysis ----------------------------------------------

    def _capture_supported(self) -> bool:
        # Optional dependency path.
        try:
            import mss  # noqa: F401

            return True
        except Exception:
            pass

        system = platform.system().lower()
        if system == "darwin":
            return shutil.which("screencapture") is not None
        if system == "windows":
            return shutil.which("pwsh") is not None or shutil.which("powershell") is not None
        # Linux / other unix
        return shutil.which("gnome-screenshot") is not None or shutil.which("import") is not None

    def _capture_screen_png(self, dest: Path, *, timeout_seconds: int = 15) -> tuple[bool, str | None]:
        # Try mss first (when installed).
        try:
            from mss import mss

            with mss() as sct:
                sct.shot(output=str(dest))
            if dest.exists() and dest.stat().st_size > 0:
                return True, None
        except Exception:
            pass

        system = platform.system().lower()
        if system == "darwin" and shutil.which("screencapture"):
            try:
                subprocess.run(
                    ["screencapture", "-x", "-t", "png", str(dest)],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE,
                    timeout=timeout_seconds,
                )
                return dest.exists(), None
            except subprocess.CalledProcessError as exc:
                return False, (exc.stderr.decode("utf-8", errors="replace") if exc.stderr else str(exc))
            except Exception as exc:
                return False, str(exc)

        if system == "windows":
            exe = shutil.which("pwsh") or shutil.which("powershell")
            if not exe:
                return False, "PowerShell not available for screenshot capture."
            script = r"""
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$bounds = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
$bitmap = New-Object System.Drawing.Bitmap $bounds.Width, $bounds.Height
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
$graphics.CopyFromScreen($bounds.Location, [System.Drawing.Point]::Empty, $bounds.Size)
$bitmap.Save($args[0], [System.Drawing.Imaging.ImageFormat]::Png)
$graphics.Dispose()
$bitmap.Dispose()
"""
            try:
                subprocess.run(
                    [exe, "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-Command", script, str(dest)],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE,
                    timeout=timeout_seconds,
                )
                return dest.exists(), None
            except subprocess.CalledProcessError as exc:
                return False, (exc.stderr.decode("utf-8", errors="replace") if exc.stderr else str(exc))
            except Exception as exc:
                return False, str(exc)

        if shutil.which("gnome-screenshot"):
            try:
                subprocess.run(
                    ["gnome-screenshot", "-f", str(dest)],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE,
                    timeout=timeout_seconds,
                )
                return dest.exists(), None
            except Exception:
                pass

        if shutil.which("import"):
            try:
                subprocess.run(
                    ["import", "-window", "root", str(dest)],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE,
                    timeout=timeout_seconds,
                )
                return dest.exists(), None
            except subprocess.CalledProcessError as exc:
                return False, (exc.stderr.decode("utf-8", errors="replace") if exc.stderr else str(exc))
            except Exception as exc:
                return False, str(exc)

        return False, "No supported screenshot method found."

    def _build_visual_signal(
        self,
        *,
        endpoint_id: str,
        session_id: str,
        sequence: int,
        semantic_encoding: str,
        ui_method: str,
        correlation: dict[str, Any] | None = None,
        user_id: str | None = None,
    ) -> dict[str, Any]:
        observation_event_id = f"{session_id}.{int(sequence):08d}"
        return {
            "schema": "vision_u_eye.visual_signal.v1",
            "event_type": "perception",
            "event_id": secrets.token_hex(16),
            "endpoint_id": endpoint_id,
            "session_id": session_id,
            "user_id": user_id,
            "timestamp_utc": _now_utc_z(),
            "monotonic_timestamp": int(time.monotonic_ns()),
            "sequence": int(sequence),
            "episode_id": f"{session_id}.ep0001",
            "observation_event_id": observation_event_id,
            "perception": {
                "ui": {"method": ui_method, "elements": []},
                "ocr": {"available": False},
                "correlation": correlation or {},
                "semantic": {"method": "sha256", "encoding": semantic_encoding},
                "diff": {"changed": False, "fields_changed": [], "changes": {}},
            },
        }

    def _capture_snapshot(self, params: dict[str, Any]) -> ActionResult:
        if not self._capture_supported():
            return ActionResult(ok=False, stderr="Unsupported platform: screen capture unavailable.", exit_code=2)

        vision_dir = self._vision_dir()
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        filename = f"snapshot-{stamp}-{secrets.token_hex(6)}.png"
        path = vision_dir / filename

        ok, err = self._capture_screen_png(path)
        if not ok or not path.exists():
            return ActionResult(ok=False, stderr=err or "Capture failed.", exit_code=1)

        data = b""
        try:
            data = path.read_bytes()
        except Exception as exc:
            return ActionResult(ok=False, stderr=str(exc), exit_code=1)

        sha = _sha256_hex(data)
        width, height = _png_size(data)
        endpoint_id = str(params.get("endpoint_id") or self._store.read_agent_id() or platform.node() or "unknown").strip()
        session_id = str(params.get("session_id") or self._session_id).strip() or self._session_id
        user_id = os.environ.get("USERNAME") or os.environ.get("USER") or None
        sequence = self._next_sequence()

        snapshot_meta: dict[str, Any] = {
            "format": "png",
            "bytes": len(data),
            "sha256": sha,
            "width": width,
            "height": height,
            "captured_at_utc": _now_utc_z(),
        }
        analysis = {
            "engine": "stub",
            "narration": "Snapshot captured.",
            "labels": ["snapshot", "screen"],
            "confidence": 0.05,
            "width": width,
            "height": height,
            "sha256": sha,
        }

        correlation = {
            "agent": {
                "agent_id": self._store.read_agent_id(),
                "hostname": platform.node(),
                "os": platform.system(),
                "arch": platform.machine(),
            },
            "capture": snapshot_meta,
            "note": "Artifact attached via job_results.artifacts.",
        }
        visual_signal = self._build_visual_signal(
            endpoint_id=endpoint_id,
            session_id=session_id,
            sequence=sequence,
            semantic_encoding=sha,
            ui_method="capture_snapshot",
            correlation=correlation,
            user_id=user_id,
        )

        self._write_state(
            {
                "last_capture_at": snapshot_meta["captured_at_utc"],
                "last_capture_sha256": sha,
                "recording": False,
                "fps": 0,
            }
        )

        return ActionResult(ok=True, result={"snapshot": snapshot_meta, "analysis": analysis, "visual_signal": visual_signal}, artifacts=[path])

    def _record_segment(self, params: dict[str, Any]) -> ActionResult:
        if not self._capture_supported():
            return ActionResult(ok=False, stderr="Unsupported platform: screen capture unavailable.", exit_code=2)

        duration = _parse_int(params.get("duration_seconds") or params.get("duration") or params.get("seconds"), 5)
        duration = max(1, min(60, duration))
        fps = _parse_int(params.get("fps"), 1)
        fps = max(1, min(5, fps))
        total_frames = max(1, min(300, duration * fps))

        vision_dir = self._vision_dir()
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        zip_path = vision_dir / f"segment-{stamp}-{secrets.token_hex(6)}.zip"

        self._write_state({"recording": True, "fps": fps})
        frames: list[Path] = []
        started = time.monotonic()
        try:
            for idx in range(total_frames):
                frame_name = f"frame-{idx:04d}.png"
                frame_path = vision_dir / frame_name
                ok, err = self._capture_screen_png(frame_path)
                if not ok:
                    return ActionResult(ok=False, stderr=err or "Frame capture failed.", exit_code=1)
                frames.append(frame_path)
                # Sleep to target fps.
                target_next = (idx + 1) * (1.0 / float(fps))
                delay = target_next - (time.monotonic() - started)
                if delay > 0:
                    time.sleep(min(1.0, delay))
        finally:
            self._write_state({"recording": False, "fps": fps, "last_capture_at": _now_utc_z()})

        try:
            with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                manifest = {
                    "format": "frames_zip",
                    "duration_seconds": duration,
                    "fps": fps,
                    "frames": [p.name for p in frames],
                    "created_at_utc": _now_utc_z(),
                }
                zf.writestr("manifest.json", json.dumps(manifest, indent=2))
                for p in frames:
                    if p.exists():
                        zf.write(p, arcname=p.name)
        except Exception as exc:
            return ActionResult(ok=False, stderr=str(exc), exit_code=1)

        # Best-effort cleanup frame files after bundling.
        for p in frames:
            try:
                p.unlink()
            except Exception:
                pass

        result = {
            "segment": {"format": "frames_zip", "duration_seconds": duration, "fps": fps, "frames": total_frames},
        }
        return ActionResult(ok=True, result=result, artifacts=[zip_path])

    def _resolve_snapshot_bytes(self, params: dict[str, Any]) -> tuple[bytes | None, dict[str, Any]]:
        meta: dict[str, Any] = {}
        raw_path = params.get("path") or params.get("file") or None
        if raw_path:
            p = Path(str(raw_path)).expanduser()
            if p.exists() and p.is_file():
                data = p.read_bytes()
                meta["source"] = "path"
                meta["path"] = str(p)
                meta["filename"] = p.name
                return data, meta

        raw_url = params.get("url") or params.get("artifact_url") or params.get("snapshot_url") or None
        if raw_url:
            url = str(raw_url).strip()
            if url.startswith("/"):
                base = str(os.environ.get("CONTROL_PLANE_URL") or "").strip().rstrip("/")
                if base:
                    url = base + url
            data = _download_bytes(url)
            meta["source"] = "url"
            meta["url"] = url
            return data, meta

        return None, {"source": "none"}

    def _analyze_snapshot(self, params: dict[str, Any]) -> ActionResult:
        data, source_meta = self._resolve_snapshot_bytes(params)
        if not data:
            return ActionResult(ok=False, stderr="Missing snapshot bytes (provide path=... or artifact_url=...).", exit_code=2)

        sha = _sha256_hex(data)
        width, height = _png_size(data)
        labels = ["snapshot", "screen"]
        if width and height:
            labels.append("image")
        analysis = {
            "engine": "stub",
            "narration": f"Snapshot analyzed (stub). bytes={len(data)} sha256={sha}",
            "labels": labels,
            "confidence": 0.1,
            "width": width,
            "height": height,
            "sha256": sha,
            "source": source_meta,
        }

        endpoint_id = str(params.get("endpoint_id") or self._store.read_agent_id() or platform.node() or "unknown").strip()
        session_id = str(params.get("session_id") or self._session_id).strip() or self._session_id
        user_id = os.environ.get("USERNAME") or os.environ.get("USER") or None
        sequence = self._next_sequence()
        correlation = {
            "agent": {
                "agent_id": self._store.read_agent_id(),
                "hostname": platform.node(),
                "os": platform.system(),
                "arch": platform.machine(),
            },
            "analysis": analysis,
            "source": source_meta,
        }
        visual_signal = self._build_visual_signal(
            endpoint_id=endpoint_id,
            session_id=session_id,
            sequence=sequence,
            semantic_encoding=sha,
            ui_method="analyze_snapshot",
            correlation=correlation,
            user_id=user_id,
        )
        return ActionResult(ok=True, result={"analysis": analysis, "visual_signal": visual_signal})

    def _stream_status(self) -> ActionResult:
        state = self._read_state()
        payload = {
            "recording": bool(state.get("recording", False)),
            "fps": state.get("fps") or 0,
            "last_capture_at": state.get("last_capture_at"),
            "queue_depth": 0,
            "session_id": self._session_id,
        }
        return ActionResult(ok=True, result=payload)
