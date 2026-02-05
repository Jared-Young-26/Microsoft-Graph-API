from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

from .json_schema_validator import JsonSchemaValidationError, validate_schema


class SignalProvider:
    """Signal Provider."""
    name: str
    version: str

    def validate(self, payload: dict) -> bool:
        """Run validate."""
        raise NotImplementedError

    def normalize(self, payload: dict) -> dict:
        """Run normalize."""
        return payload


@lru_cache
def _vision_u_eye_schema() -> Dict[str, Any]:
    """Internal helper for vision u eye schema."""
    repo_root = Path(__file__).resolve().parents[1]
    schema_path = repo_root / "contracts" / "visual_signal.v1.json"
    return json.loads(schema_path.read_text(encoding="utf-8"))


@dataclass(frozen=True)
class VisionUEyeProvider(SignalProvider):
    """Vision U Eye Provider."""
    name: str = "visual"
    version: str = "1.0"
    namespace: str = "vision_u_eye.visual_signal"

    def validate(self, payload: dict) -> bool:
        """Run validate."""
        if not isinstance(payload, dict):
            return False
        try:
            validate_schema(_vision_u_eye_schema(), payload)
        except JsonSchemaValidationError:
            return False
        # Ensure deterministic JSON-serializable.
        try:
            json.dumps(payload, sort_keys=True)
        except Exception:
            return False
        return True

    def normalize(self, payload: dict) -> dict:
        """Run normalize."""
        return payload


VISION_U_EYE_PROVIDER = VisionUEyeProvider()


def attach_signal(snapshot: dict, provider: SignalProvider, payload: dict) -> dict:
    """Run attach signal."""
    if not provider.validate(payload):
        raise ValueError(f"Invalid payload for signal {provider.name} v{provider.version}")
    normalized = provider.normalize(payload)

    signals = snapshot.get("signals")
    if signals is None:
        signals = {}
        snapshot["signals"] = signals
    if not isinstance(signals, dict):
        raise ValueError("snapshot.signals must be an object when present")

    # Non-negotiable: never rename/reshape payload fields.
    signals[provider.name] = normalized
    return snapshot


attach_signal_to_snapshot = attach_signal
