from __future__ import annotations

from pathlib import Path
from typing import Any
import json

from .interface import ActionDefinition


def _normalize_risk(value: Any) -> str:
    risk = str(value or "safe").strip().lower()
    if risk in ("low", "read", "readonly", "read_only"):
        return "safe"
    if risk in ("medium", "warn", "warning"):
        return "caution"
    if risk in ("high", "dangerous"):
        return "danger"
    if risk not in ("safe", "caution", "danger"):
        return "safe"
    return risk


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    if isinstance(value, (set, tuple)):
        return [str(v).strip() for v in value if str(v).strip()]
    text = str(value).strip()
    if not text:
        return []
    # Allow comma-separated values for convenience.
    return [part.strip() for part in text.split(",") if part.strip()]


def load_action_manifest(path: Path, *, plugin_id: str) -> list[ActionDefinition]:
    """Load an action_manifest.json file for a plugin.

    Manifest shape (v0):
      - Either a dict with key "actions" (list), or a list of action objects.
      - Each action declares: action_id, title, description, risk, params_schema,
        required_capabilities, output_schema.
    """

    path = Path(path)
    if not path.exists():
        return []
    raw = json.loads(path.read_text(encoding="utf-8"))

    if isinstance(raw, dict):
        actions = raw.get("actions")
    else:
        actions = raw

    if not isinstance(actions, list):
        return []

    parsed: list[ActionDefinition] = []
    for entry in actions:
        if not isinstance(entry, dict):
            continue
        action_id = str(entry.get("action_id") or "").strip()
        title = str(entry.get("title") or "").strip()
        if not action_id or not title:
            continue
        description = str(entry.get("description") or "").strip()
        required_caps = _as_list(entry.get("required_capabilities") or entry.get("capabilities"))
        risk_level = _normalize_risk(entry.get("risk") or entry.get("risk_level"))
        params_schema = entry.get("params_schema")
        output_schema = entry.get("output_schema")
        parsed.append(
            ActionDefinition(
                action_id=action_id,
                title=title,
                description=description,
                required_capabilities=required_caps,
                risk_level=risk_level,
                params_schema=params_schema,
                output_schema=output_schema,
            )
        )
    return parsed


def manifest_path_for_plugin(plugin_id: str) -> Path:
    """Resolve the default manifest location for a built-in plugin."""
    return Path(__file__).resolve().parent / "manifests" / str(plugin_id) / "action_manifest.json"


def load_manifest_for_plugin(plugin_id: str) -> list[ActionDefinition]:
    """Load the built-in manifest for a plugin id (best-effort)."""
    return load_action_manifest(manifest_path_for_plugin(plugin_id), plugin_id=str(plugin_id))

