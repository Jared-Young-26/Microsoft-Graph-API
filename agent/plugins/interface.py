from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol


@dataclass(frozen=True)
class ActionDefinition:
    """Action definition exposed to the control plane catalog."""

    action_id: str
    title: str
    description: str = ""
    required_capabilities: list[str] = field(default_factory=list)
    risk_level: str = "safe"
    params_schema: Any | None = None
    output_schema: Any | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "action_id": self.action_id,
            "title": self.title,
            "description": self.description,
            "required_capabilities": list(self.required_capabilities or []),
            "risk_level": self.risk_level,
            "params_schema": self.params_schema,
            "output_schema": self.output_schema,
        }


@dataclass
class ActionResult:
    """Normalized action execution result."""

    ok: bool
    result: Any | None = None
    stdout: str | None = None
    stderr: str | None = None
    exit_code: int | None = None
    artifacts: list[Path] = field(default_factory=list)


class AgentPlugin(Protocol):
    """Agent plugin interface."""

    id: str

    def capabilities(self) -> list[str]:
        """Return capabilities exposed by this plugin."""

    def actions(self) -> list[ActionDefinition]:
        """Return supported actions."""

    def handle(self, action_id: str, params: dict | None) -> ActionResult | dict:
        """Handle an action."""
