from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple, Union
import re


@dataclass
class JsonSchemaValidationError(ValueError):
    path: str
    message: str

    def __str__(self) -> str:  # pragma: no cover - trivial
        prefix = self.path or "/"
        return f"{prefix}: {self.message}"


def _type_name(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return type(value).__name__


def _as_list(value: Any) -> List[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _join(path: str, key: str) -> str:
    if not path:
        return f"/{key}"
    return f"{path}/{key}"


def _validate_type(schema_type: Any, value: Any) -> bool:
    allowed = _as_list(schema_type)
    if not allowed:
        return True
    for item in allowed:
        if item == "null" and value is None:
            return True
        if item == "object" and isinstance(value, dict):
            return True
        if item == "array" and isinstance(value, list):
            return True
        if item == "string" and isinstance(value, str):
            return True
        if item == "boolean" and isinstance(value, bool):
            return True
        if item == "integer" and isinstance(value, int) and not isinstance(value, bool):
            return True
        if item == "number" and isinstance(value, (int, float)) and not isinstance(value, bool):
            return True
    return False


def validate_schema(schema: Dict[str, Any], payload: Any) -> None:
    """Validate a payload against a limited subset of JSON Schema Draft 2020-12.

    Supported keywords: type, required, properties, additionalProperties, items, const,
    minimum, minLength, pattern.
    """

    def walk(node_schema: Dict[str, Any], value: Any, path: str) -> None:
        # Type
        if "type" in node_schema and not _validate_type(node_schema.get("type"), value):
            raise JsonSchemaValidationError(
                path=path,
                message=f"Expected {node_schema.get('type')}, got {_type_name(value)}",
            )

        # Const
        if "const" in node_schema and value != node_schema.get("const"):
            raise JsonSchemaValidationError(path=path, message=f"Expected const {node_schema.get('const')!r}")

        # Numbers
        if isinstance(value, int) and not isinstance(value, bool):
            minimum = node_schema.get("minimum")
            if minimum is not None and value < int(minimum):
                raise JsonSchemaValidationError(path=path, message=f"Expected >= {minimum}")

        # Strings
        if isinstance(value, str):
            min_len = node_schema.get("minLength")
            if min_len is not None and len(value) < int(min_len):
                raise JsonSchemaValidationError(path=path, message=f"Expected minLength {min_len}")
            pattern = node_schema.get("pattern")
            if pattern:
                try:
                    if re.match(pattern, value) is None:
                        raise JsonSchemaValidationError(path=path, message="String does not match pattern")
                except re.error:
                    # If a pattern is invalid, treat that as schema error rather than payload error.
                    raise JsonSchemaValidationError(path=path, message="Invalid schema pattern") from None

        # Objects
        if isinstance(value, dict):
            required = node_schema.get("required") or []
            for key in required:
                if key not in value:
                    raise JsonSchemaValidationError(path=path, message=f"Missing required property '{key}'")
            props: Dict[str, Any] = node_schema.get("properties") or {}
            additional = node_schema.get("additionalProperties", True)
            for key, child in value.items():
                if key in props:
                    child_schema = props.get(key) or {}
                    if isinstance(child_schema, dict):
                        walk(child_schema, child, _join(path, key))
                else:
                    if additional is False:
                        raise JsonSchemaValidationError(path=_join(path, key), message="Additional property not allowed")
                    if isinstance(additional, dict):
                        walk(additional, child, _join(path, key))
            return

        # Arrays
        if isinstance(value, list):
            items_schema = node_schema.get("items")
            if isinstance(items_schema, dict):
                for idx, item in enumerate(value):
                    walk(items_schema, item, _join(path, str(idx)))
            return

    if not isinstance(schema, dict):
        raise JsonSchemaValidationError(path="", message="Schema must be an object")
    walk(schema, payload, "")

