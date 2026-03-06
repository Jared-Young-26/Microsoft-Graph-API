from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import os


def _default_state_dir() -> Path:
    """Resolve default state directory (~/.gas)."""
    override = os.environ.get("GAS_HOME")
    if override:
        return Path(override).expanduser()
    try:
        return Path.home() / ".gas"
    except Exception:
        return Path(".gas").resolve()


def _write_secret(path: Path, value: str) -> None:
    """Write a secret value to disk with best-effort restrictive permissions."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.strip() + "\n", encoding="utf-8")
    try:
        os.chmod(path, 0o600)
    except Exception:
        return


def _read_secret(path: Path) -> str | None:
    """Read a secret value from disk."""
    try:
        value = path.read_text(encoding="utf-8").strip()
        return value or None
    except Exception:
        return None


@dataclass(frozen=True)
class AgentTokenStore:
    """Local agent token storage."""

    state_dir: Path = field(default_factory=_default_state_dir)

    @property
    def token_path(self) -> Path:
        return self.state_dir / "agent_token"

    @property
    def agent_id_path(self) -> Path:
        return self.state_dir / "agent_id"

    def read_token(self) -> str | None:
        return _read_secret(self.token_path)

    def write_token(self, token: str) -> None:
        _write_secret(self.token_path, token)

    def read_agent_id(self) -> str | None:
        return _read_secret(self.agent_id_path)

    def write_agent_id(self, agent_id: str) -> None:
        _write_secret(self.agent_id_path, agent_id)
