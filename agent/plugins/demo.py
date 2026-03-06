from __future__ import annotations

from pathlib import Path
from typing import Any
import platform
import time

from .interface import ActionDefinition, ActionResult
from .manifest import load_manifest_for_plugin


class DemoPlugin:
    """Built-in demo plugin (safe)."""

    id = "demo"

    def capabilities(self) -> list[str]:
        return ["demo.echo", "demo.sleep", "demo.sysinfo"]

    def actions(self) -> list[ActionDefinition]:
        manifest_actions = load_manifest_for_plugin(self.id)
        if manifest_actions:
            return manifest_actions
        return [
            ActionDefinition(
                action_id="demo.echo",
                title="Echo",
                description="Returns params as result (for wiring tests).",
                required_capabilities=["demo.echo"],
                risk_level="safe",
            ),
            ActionDefinition(
                action_id="demo.sleep",
                title="Sleep",
                description="Sleeps for N milliseconds (for lease/timeout testing).",
                required_capabilities=["demo.sleep"],
                risk_level="safe",
            ),
            ActionDefinition(
                action_id="demo.sysinfo",
                title="System info",
                description="Returns basic platform information.",
                required_capabilities=["demo.sysinfo"],
                risk_level="safe",
            ),
        ]

    def handle(self, action_id: str, params: dict | None) -> ActionResult:
        params = params or {}
        if action_id == "demo.echo":
            return ActionResult(ok=True, result={"echo": params})
        if action_id == "demo.sleep":
            ms = params.get("ms") or params.get("milliseconds") or 0
            try:
                delay = max(0.0, float(ms) / 1000.0)
            except Exception:
                delay = 0.0
            time.sleep(min(60.0, delay))
            return ActionResult(ok=True, result={"slept_ms": int(delay * 1000)})
        if action_id == "demo.sysinfo":
            data: dict[str, Any] = {
                "platform": platform.platform(),
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "python_version": platform.python_version(),
            }
            return ActionResult(ok=True, result=data)
        return ActionResult(ok=False, stderr=f"Unknown action_id: {action_id}", exit_code=2)
