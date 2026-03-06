from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional
import json
import mimetypes
import urllib.error
import urllib.parse
import urllib.request


def _join(base_url: str, path: str) -> str:
    base = (base_url or "").rstrip("/")
    if not path.startswith("/"):
        path = "/" + path
    return base + path


def _request_json(url: str, method: str, payload: dict | None = None, headers: dict[str, str] | None = None, timeout: int = 30):
    data = None
    req_headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if headers:
        req_headers.update(headers)
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=req_headers, method=method.upper())
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8") if resp else ""
            if not raw:
                return resp.status, None
            try:
                return resp.status, json.loads(raw)
            except Exception:
                return resp.status, {"raw": raw}
    except urllib.error.HTTPError as exc:
        raw = ""
        try:
            raw = exc.read().decode("utf-8")  # type: ignore[attr-defined]
        except Exception:
            raw = ""
        try:
            parsed = json.loads(raw) if raw else None
        except Exception:
            parsed = {"raw": raw} if raw else None
        return int(exc.code), parsed


def _request_bytes(url: str, method: str, body: bytes, headers: dict[str, str] | None = None, timeout: int = 60):
    req_headers = {"Accept": "application/json"}
    if headers:
        req_headers.update(headers)
    req = urllib.request.Request(url, data=body, headers=req_headers, method=method.upper())
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.status, resp.read()


@dataclass
class ControlPlaneClient:
    """HTTP client for the control plane."""

    base_url: str
    timeout_seconds: int = 30

    def register(self, payload: dict[str, Any]) -> dict[str, Any]:
        status, data = _request_json(
            _join(self.base_url, "/api/agents/register"),
            "POST",
            payload,
            timeout=self.timeout_seconds,
        )
        if status >= 400:
            raise RuntimeError(f"register failed (status={status})")
        return data or {}

    def heartbeat(self, agent_id: str, token: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        headers = {"Authorization": f"Bearer {token}"}
        body = {"agent_id": agent_id, **(payload or {})}
        status, data = _request_json(
            _join(self.base_url, "/api/agents/heartbeat"),
            "POST",
            body,
            headers=headers,
            timeout=self.timeout_seconds,
        )
        if status == 401:
            raise PermissionError("unauthorized")
        if status >= 400:
            raise RuntimeError(f"heartbeat failed (status={status})")
        return data or {}

    def next_job(self, agent_id: str, token: str, lease_seconds: int = 900) -> Optional[dict[str, Any]]:
        headers = {"Authorization": f"Bearer {token}"}
        url = _join(self.base_url, f"/api/agents/{urllib.parse.quote(agent_id)}/next-job")
        url = url + "?" + urllib.parse.urlencode({"lease_seconds": str(int(lease_seconds))})
        status, data = _request_json(url, "GET", payload=None, headers=headers, timeout=self.timeout_seconds)
        if status == 204:
            return None
        if status == 401:
            raise PermissionError("unauthorized")
        if status >= 400:
            raise RuntimeError(f"next-job failed (status={status})")
        return data or None

    def next_terminal_session(self, agent_id: str, token: str) -> Optional[dict[str, Any]]:
        headers = {"Authorization": f"Bearer {token}"}
        url = _join(self.base_url, f"/api/terminal/{urllib.parse.quote(agent_id)}/next-session")
        status, data = _request_json(url, "GET", payload=None, headers=headers, timeout=self.timeout_seconds)
        if status == 204:
            return None
        if status == 401:
            raise PermissionError("unauthorized")
        if status >= 400:
            raise RuntimeError(f"next-terminal-session failed (status={status})")
        if isinstance(data, dict) and data.get("ok") is True and isinstance(data.get("data"), dict):
            return data.get("data")
        return data if isinstance(data, dict) else None

    def post_job_result(self, agent_id: str, token: str, payload: dict[str, Any]) -> dict[str, Any]:
        headers = {"Authorization": f"Bearer {token}"}
        url = _join(self.base_url, f"/api/agents/{urllib.parse.quote(agent_id)}/job-result")
        status, data = _request_json(url, "POST", payload, headers=headers, timeout=self.timeout_seconds)
        if status == 401:
            raise PermissionError("unauthorized")
        if status >= 400:
            raise RuntimeError(f"job-result failed (status={status})")
        return data or {}

    def upload_artifact(
        self,
        agent_id: str,
        token: str,
        filename: str,
        content: bytes,
        *,
        content_type: str | None = None,
        job_id: str | None = None,
        artifact_type: str | None = None,
    ) -> dict[str, Any]:
        if not content_type:
            guessed, _ = mimetypes.guess_type(filename or "")
            content_type = guessed or "application/octet-stream"
        boundary = "----gas-agent-boundary"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": f"multipart/form-data; boundary={boundary}"}

        safe_name = filename or "artifact.zip"
        parts: list[bytes] = []
        parts.append(f"--{boundary}\r\n".encode("utf-8"))
        parts.append(b'Content-Disposition: form-data; name="agent_id"\r\n\r\n')
        parts.append(agent_id.encode("utf-8"))
        parts.append(b"\r\n")

        if job_id:
            parts.append(f"--{boundary}\r\n".encode("utf-8"))
            parts.append(b'Content-Disposition: form-data; name="job_id"\r\n\r\n')
            parts.append(str(job_id).encode("utf-8"))
            parts.append(b"\r\n")

        if artifact_type:
            parts.append(f"--{boundary}\r\n".encode("utf-8"))
            parts.append(b'Content-Disposition: form-data; name="type"\r\n\r\n')
            parts.append(str(artifact_type).encode("utf-8"))
            parts.append(b"\r\n")

        parts.append(f"--{boundary}\r\n".encode("utf-8"))
        parts.append(
            f'Content-Disposition: form-data; name="file"; filename="{safe_name}"\r\n'.encode("utf-8")
        )
        parts.append(f"Content-Type: {content_type}\r\n\r\n".encode("utf-8"))
        parts.append(content)
        parts.append(b"\r\n")
        parts.append(f"--{boundary}--\r\n".encode("utf-8"))
        body = b"".join(parts)

        url = _join(self.base_url, "/api/artifacts/upload")
        status, raw = _request_bytes(url, "POST", body, headers=headers, timeout=max(60, self.timeout_seconds))
        if status == 401:
            raise PermissionError("unauthorized")
        if status >= 400:
            raise RuntimeError(f"artifact upload failed (status={status})")
        try:
            return json.loads(raw.decode("utf-8")) if raw else {}
        except Exception:
            return {"raw": raw.decode("utf-8", errors="replace")}
