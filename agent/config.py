from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import json
import os
import socket


def _parse_bool(value: str | None) -> bool:
    """Internal helper for parse bool."""
    if value is None:
        return False
    return str(value).strip().lower() in ("1", "true", "yes", "y", "on")


def _parse_int(value: str | None, default: int) -> int:
    """Internal helper for parse int."""
    if value is None:
        return default
    try:
        return int(str(value).strip())
    except Exception:
        return default


def _parse_labels(value: str | None) -> dict[str, str]:
    """Parse LABELS from env."""
    if not value:
        return {}
    raw = str(value).strip()
    if not raw:
        return {}
    if raw.startswith("{"):
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                return {str(k): str(v) for k, v in parsed.items() if k is not None and v is not None}
        except Exception:
            return {}
    out: dict[str, str] = {}
    parts = [part.strip() for part in raw.split(",") if part.strip()]
    for part in parts:
        if "=" not in part:
            continue
        key, val = part.split("=", 1)
        key = key.strip()
        val = val.strip()
        if not key:
            continue
        out[key] = val
    return out


def _normalize_url(url: str) -> str:
    """Normalize base URL."""
    normalized = (url or "").strip()
    while normalized.endswith("/"):
        normalized = normalized[:-1]
    return normalized


@dataclass(frozen=True)
class AgentConfig:
    """Agent runtime configuration."""

    control_plane_url: str
    agent_name: str
    tenant_id: str | None
    workspace_id: str | None
    labels: dict[str, str]
    token: str | None
    pairing_code: str | None
    poll_interval: int
    break_glass_enabled: bool


def _load_config_file(path: str | None) -> dict[str, Any]:
    """Load JSON config file."""
    if not path:
        return {}
    cfg_path = Path(path).expanduser()
    if not cfg_path.exists():
        return {}
    try:
        parsed = json.loads(cfg_path.read_text(encoding="utf-8"))
        return parsed if isinstance(parsed, dict) else {}
    except Exception:
        return {}


def load_agent_config(config_path: str | None = None) -> AgentConfig:
    """Load agent config from env + file."""
    file_cfg = _load_config_file(config_path)
    env_url = os.environ.get("CONTROL_PLANE_URL")
    env_name = os.environ.get("AGENT_NAME")
    env_tenant = os.environ.get("GAS_TENANT_ID")
    env_workspace = os.environ.get("GAS_WORKSPACE_ID")
    env_labels = os.environ.get("LABELS")
    env_token = os.environ.get("TOKEN")
    env_pairing_code = os.environ.get("GAS_PAIRING_CODE") or os.environ.get("PAIRING_CODE")
    env_poll = os.environ.get("POLL_INTERVAL")
    env_break_glass = os.environ.get("BREAK_GLASS_ENABLED")

    control_plane_url = _normalize_url(
        str(env_url or file_cfg.get("control_plane_url") or "http://127.0.0.1:8000")
    )
    agent_name = str(env_name or file_cfg.get("agent_name") or socket.gethostname() or "gas-agent")
    tenant_id = str(env_tenant or file_cfg.get("tenant_id") or "").strip() or None
    workspace_id = str(env_workspace or file_cfg.get("workspace_id") or "").strip() or None

    labels_file = file_cfg.get("labels")
    labels: dict[str, str] = {}
    if isinstance(labels_file, dict):
        labels = {str(k): str(v) for k, v in labels_file.items() if k is not None and v is not None}
    labels_env = _parse_labels(env_labels)
    labels.update(labels_env)

    file_token = file_cfg.get("token")
    token = str(env_token).strip() if env_token else str(file_token).strip() if file_token else None
    file_pairing_code = file_cfg.get("pairing_code")
    pairing_code = (
        str(env_pairing_code).strip()
        if env_pairing_code
        else str(file_pairing_code).strip()
        if file_pairing_code
        else None
    )
    poll_interval = _parse_int(str(env_poll) if env_poll is not None else None, int(file_cfg.get("poll_interval") or 5))
    poll_interval = max(1, min(3600, poll_interval))
    break_glass_enabled = (
        _parse_bool(env_break_glass) if env_break_glass is not None else bool(file_cfg.get("break_glass_enabled", False))
    )

    return AgentConfig(
        control_plane_url=control_plane_url,
        agent_name=agent_name,
        tenant_id=tenant_id,
        workspace_id=workspace_id,
        labels=labels,
        token=token,
        pairing_code=pairing_code,
        poll_interval=poll_interval,
        break_glass_enabled=break_glass_enabled,
    )
