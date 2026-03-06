from __future__ import annotations

from typing import Any
from datetime import datetime, timezone

from .plugins.registry import load_plugins


def build_capabilities_catalog() -> dict[str, Any]:
    """Build an action+capability catalog from installed plugins."""
    plugins = load_plugins()
    capabilities: set[str] = set()
    actions: list[dict[str, Any]] = []
    for plugin in plugins:
        try:
            for action in plugin.actions() or []:
                payload = {**action.to_dict(), "plugin_id": plugin.id}
                actions.append(payload)
                for cap in payload.get("required_capabilities") or []:
                    if cap:
                        capabilities.add(str(cap))
        except Exception:
            continue
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "capabilities": sorted(capabilities),
        "actions": sorted(actions, key=lambda item: str(item.get("action_id") or "")),
    }
