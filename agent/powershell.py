from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import json
import os
import platform
import shutil
import subprocess
import tempfile


DEFAULT_TIMEOUT_SECONDS = 60


def _is_windows() -> bool:
    return platform.system().lower() == "windows"


def _which(executable: str) -> str | None:
    try:
        return shutil.which(executable)
    except Exception:
        return None


def _pick_powershell_executable() -> str | None:
    # Prefer PowerShell 7+ if available.
    if _which("pwsh"):
        return "pwsh"
    if _is_windows() and _which("powershell"):
        return "powershell"
    return None


def _safe_json_loads(value: str) -> Any:
    try:
        return json.loads(value)
    except Exception:
        # Try to recover if extra output preceded JSON.
        idx = value.rfind("{")
        if idx > 0:
            try:
                return json.loads(value[idx:])
            except Exception:
                return None
        return None


@dataclass(frozen=True)
class PowerShellResult:
    ok: bool
    data: Any | None
    error: str | None
    stdout: str
    stderr: str
    exit_code: int


class PowerShellRunner:
    """Run PowerShell scripts safely with JSON input/output."""

    def __init__(self, executable: str | None = None):
        self.executable = executable or _pick_powershell_executable()

    def is_available(self) -> bool:
        return bool(self.executable)

    def executable_path(self) -> str | None:
        if not self.executable:
            return None
        return _which(self.executable)

    def run_json(self, script_body: str, params: dict[str, Any] | None = None, timeout_seconds: int | None = None) -> PowerShellResult:
        """Run a script body with JSON params via stdin, returning parsed JSON payload."""
        if not self.executable:
            return PowerShellResult(
                ok=False,
                data=None,
                error="powershell_not_found",
                stdout="",
                stderr="PowerShell executable not found (pwsh/powershell).",
                exit_code=127,
            )

        timeout = int(timeout_seconds or DEFAULT_TIMEOUT_SECONDS)
        payload = json.dumps(params or {}, default=str)

        wrapper = f"""
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
$VerbosePreference = 'SilentlyContinue'
$InformationPreference = 'SilentlyContinue'
$DebugPreference = 'SilentlyContinue'
$WarningPreference = 'SilentlyContinue'

$raw = [Console]::In.ReadToEnd()
$params = @{{}}
if ($raw) {{
  try {{ $params = $raw | ConvertFrom-Json -ErrorAction Stop }} catch {{ $params = @{{}} }}
}}

try {{
  {script_body}
  $payload = @{{ ok = $true; data = $out; error = $null }}
}} catch {{
  $msg = $_.Exception.Message
  $payload = @{{ ok = $false; data = $null; error = $msg }}
}}

$payload | ConvertTo-Json -Depth 10 -Compress
"""

        with tempfile.TemporaryDirectory(prefix="gas-agent-ps-") as tmpdir:
            script_path = Path(tmpdir) / "runner.ps1"
            script_path.write_text(wrapper, encoding="utf-8")
            cmd = [self.executable, "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File", str(script_path)]
            try:
                proc = subprocess.run(
                    cmd,
                    input=payload.encode("utf-8"),
                    capture_output=True,
                    timeout=timeout,
                    check=False,
                )
                stdout = (proc.stdout or b"").decode("utf-8", errors="replace").strip()
                stderr = (proc.stderr or b"").decode("utf-8", errors="replace").strip()
                parsed = _safe_json_loads(stdout) if stdout else None
                if isinstance(parsed, dict):
                    ok = bool(parsed.get("ok", False))
                    return PowerShellResult(
                        ok=ok,
                        data=parsed.get("data"),
                        error=str(parsed.get("error")) if parsed.get("error") else None,
                        stdout=stdout,
                        stderr=stderr,
                        exit_code=int(proc.returncode),
                    )
                return PowerShellResult(
                    ok=False,
                    data=None,
                    error="invalid_json_output",
                    stdout=stdout,
                    stderr=stderr,
                    exit_code=int(proc.returncode),
                )
            except subprocess.TimeoutExpired:
                return PowerShellResult(
                    ok=False,
                    data=None,
                    error="timeout",
                    stdout="",
                    stderr=f"PowerShell timed out after {timeout}s.",
                    exit_code=124,
                )

