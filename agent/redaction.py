from __future__ import annotations

from typing import Any


SENSITIVE_KEY_FRAGMENTS = ("token", "secret", "password", "apikey", "api_key", "private_key", "credential")


def redact(value: Any) -> Any:
    """Redact secrets from nested structures."""
    if isinstance(value, dict):
        out = {}
        for key, val in value.items():
            key_str = str(key)
            if any(fragment in key_str.lower() for fragment in SENSITIVE_KEY_FRAGMENTS):
                out[key_str] = "[redacted]"
            else:
                out[key_str] = redact(val)
        return out
    if isinstance(value, list):
        return [redact(item) for item in value]
    return value

