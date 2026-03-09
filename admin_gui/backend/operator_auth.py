from __future__ import annotations

import hmac
import os
import re
from dataclasses import dataclass
from typing import Mapping


OPERATOR_TOKEN_ENV = "GAS_OPERATOR_TOKEN"
OPERATOR_TOKEN_HEADER = "X-Operator-Token"

PROTECTED_ROUTE = "protected"
AGENT_ROUTE = "agent"
EXEMPT_ROUTE = "exempt"

_MUTATING_METHODS = frozenset({"POST", "PUT", "DELETE", "PATCH"})
_AGENT_ROUTE_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("POST", re.compile(r"^/api/agents/register$")),
    ("POST", re.compile(r"^/api/agents/heartbeat$")),
    ("POST", re.compile(r"^/api/agents/[^/]+/job-result$")),
    ("POST", re.compile(r"^/api/artifacts/upload$")),
)
_EXEMPT_ROUTE_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("POST", re.compile(r"^/ingest/perception$")),
    ("POST", re.compile(r"^/api/signals/visual$")),
)


@dataclass(frozen=True)
class OperatorAuthError(Exception):
    status_code: int
    error_code: str
    message: str

    def to_payload(self) -> dict[str, object]:
        return {
            "ok": False,
            "error": self.message,
            "error_code": self.error_code,
        }


def _normalize_method(method: str | None) -> str:
    return str(method or "").strip().upper()


def _normalize_path(path: str | None) -> str:
    value = str(path or "").strip()
    if not value:
        return "/"
    return value.split("?", 1)[0]


def classify_operator_route(method: str | None, path: str | None) -> str:
    normalized_method = _normalize_method(method)
    normalized_path = _normalize_path(path)

    for allowed_method, pattern in _AGENT_ROUTE_PATTERNS:
        if normalized_method == allowed_method and pattern.match(normalized_path):
            return AGENT_ROUTE

    for allowed_method, pattern in _EXEMPT_ROUTE_PATTERNS:
        if normalized_method == allowed_method and pattern.match(normalized_path):
            return EXEMPT_ROUTE

    if normalized_method not in _MUTATING_METHODS:
        return EXEMPT_ROUTE

    if normalized_path.startswith("/api/"):
        return PROTECTED_ROUTE

    return EXEMPT_ROUTE


def operator_token_from_headers(headers: Mapping[str, str] | None) -> str | None:
    if headers is None:
        return None
    token = headers.get(OPERATOR_TOKEN_HEADER) or headers.get(OPERATOR_TOKEN_HEADER.lower())
    if token is None:
        return None
    value = str(token).strip()
    return value or None


def require_operator_auth(headers: Mapping[str, str] | None) -> None:
    expected = str(os.environ.get(OPERATOR_TOKEN_ENV) or "").strip()
    if not expected:
        raise OperatorAuthError(
            status_code=503,
            error_code="operator_token_not_configured",
            message=f"{OPERATOR_TOKEN_ENV} is not configured",
        )

    provided = operator_token_from_headers(headers)
    if not provided:
        raise OperatorAuthError(
            status_code=401,
            error_code="operator_token_required",
            message=f"{OPERATOR_TOKEN_HEADER} header required",
        )

    if not hmac.compare_digest(provided, expected):
        raise OperatorAuthError(
            status_code=401,
            error_code="operator_token_invalid",
            message="Invalid operator token",
        )


def enforce_operator_auth(method: str | None, path: str | None, headers: Mapping[str, str] | None) -> None:
    if classify_operator_route(method, path) == PROTECTED_ROUTE:
        require_operator_auth(headers)
