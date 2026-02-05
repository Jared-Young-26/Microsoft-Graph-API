from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Tuple
from urllib.parse import quote
from urllib.parse import urlparse
import time
import re

from microsoft import GraphAPIError

from .graph_error_transparency import build_graph_error_response
from .snapshot_storage import SnapshotSqlStore


def _now() -> datetime:
    """Internal helper for now."""
    return datetime.now(timezone.utc)


def _now_iso() -> str:
    """Internal helper for now iso."""
    return _now().isoformat()


def _is_probably_upn(value: str) -> bool:
    """Return True if probably upn."""
    text = str(value or "").strip()
    return "@" in text and " " not in text


def _cache_keys(user_upn_or_id: str) -> Tuple[Optional[str], Optional[str]]:
    """Internal helper for cache keys."""
    value = str(user_upn_or_id or "").strip()
    if not value:
        return None, None
    if _is_probably_upn(value):
        return value.strip().lower(), None
    return None, value


def _encode_personal_token(value: str) -> str:
    """SharePoint personal site tokens: replace non-alphanumeric with underscore and collapse repeats."""

    text = str(value or "").strip().lower()
    if not text:
        return ""
    text = re.sub(r"[^a-z0-9]", "_", text)
    text = re.sub(r"_+", "_", text)
    return text.strip("_")


def _personal_site_segment_from_upn(upn: str) -> str | None:
    """Internal helper for personal site segment from upn."""
    upn = str(upn or "").strip()
    if not _is_probably_upn(upn):
        return None
    local, domain = upn.split("@", 1)
    local_token = _encode_personal_token(local)
    domain_token = _encode_personal_token(domain)
    if not local_token or not domain_token:
        return None
    return f"personal/{local_token}_{domain_token}"


def _derive_personal_host(spo_admin_url: str | None) -> str | None:
    """Internal helper for derive personal host."""
    if not spo_admin_url:
        return None
    raw = str(spo_admin_url).strip()
    if not raw:
        return None
    try:
        parsed = urlparse(raw if "://" in raw else f"https://{raw}")
        host = parsed.netloc or ""
    except Exception:
        host = raw
    host = host.strip().lower()
    if not host:
        return None
    # Typical: <tenant>-admin.sharepoint.com -> <tenant>-my.sharepoint.com
    if "-admin." in host:
        return host.replace("-admin.", "-my.", 1)
    # Already a -my host.
    if "-my." in host:
        return host
    # Fallback: <tenant>.sharepoint.com -> <tenant>-my.sharepoint.com
    if host.endswith(".sharepoint.com"):
        tenant = host.split(".", 1)[0]
        if tenant:
            return f"{tenant}-my.sharepoint.com"
    return None


@dataclass(frozen=True)
class DriveIdResolution:
    """Drive Id Resolution."""
    drive_id: str
    web_url: Optional[str] = None
    drive_type: Optional[str] = None
    cached: bool = False
    cache_fallback: bool = False
    cached_stale: bool = False
    last_verified_at: Optional[str] = None
    expires_at: Optional[str] = None
    warning: Optional[str] = None
    circuit: Optional[Dict[str, Any]] = None
    live_error: Optional[Dict[str, Any]] = None
    source: str = "primary"

    def to_payload(self) -> Dict[str, Any]:
        """Run to payload."""
        return {
            "id": self.drive_id,
            "drive_id": self.drive_id,
            "webUrl": self.web_url,
            "driveType": self.drive_type,
            "cached": self.cached,
            "cache_fallback": self.cache_fallback,
            "cached_stale": self.cached_stale,
            "last_verified_at": self.last_verified_at,
            "expires_at": self.expires_at,
            "warning": self.warning,
            "circuit": self.circuit,
            "live_error": self.live_error,
            "source": self.source,
        }


def resolve_onedrive_drive_id(
    *,
    store: SnapshotSqlStore,
    graph: Any,
    tenant_id: str,
    user_upn_or_id: str,
    force_live: bool = False,
    ignore_circuit_breaker: bool = False,
    spo_admin_url: str | None = None,
    ttl_days: int = 14,
    stale_window_days: int = 30,
    max_attempts: int = 4,
    max_budget_s: int = 45,
    pending_max_attempts: int = 10,
) -> Dict[str, Any]:
    """Resolve a user's OneDrive driveId with cache-first behavior.

    - Uses cache when valid (unless force_live).
    - On transient Graph 5xx, falls back to cached value when available.
    - Canonical resolution for UPN inputs: UPN -> Entra user object id -> drive.
    - If SharePoint/OneDrive is degraded and no cache is available, returns status="pending"
      and enqueues a background retry (instead of failing the action).
    """

    if not tenant_id:
        raise ValueError("tenant_id is required for drive id caching.")
    if not user_upn_or_id or not str(user_upn_or_id).strip():
        raise ValueError("user_upn_or_id is required.")

    user_upn, user_object_id = _cache_keys(user_upn_or_id)

    cached = None
    if not force_live:
        cached = store.get_onedrive_drive_cache(
            tenant_id=tenant_id,
            user_upn=user_upn,
            user_object_id=user_object_id,
            allow_expired=False,
            stale_window_days=stale_window_days,
        )
        if cached and cached.get("drive_id"):
            # If a pending retry exists for this identifier, a valid cache hit makes it obsolete.
            try:
                store.clear_onedrive_drive_pending(
                    tenant_id=tenant_id,
                    user_upn=str(user_upn or user_object_id or user_upn_or_id),
                )
            except Exception:
                pass
            return DriveIdResolution(
                drive_id=str(cached.get("drive_id")),
                web_url=cached.get("web_url"),
                drive_type=cached.get("drive_type"),
                cached=True,
                cache_fallback=False,
                cached_stale=False,
                last_verified_at=cached.get("last_verified_at"),
                expires_at=cached.get("expires_at"),
                source="cache",
            ).to_payload()

    # Keep a stale entry around for 5xx storms.
    stale = store.get_onedrive_drive_cache(
        tenant_id=tenant_id,
        user_upn=user_upn,
        user_object_id=user_object_id,
        allow_expired=True,
        stale_window_days=stale_window_days,
    )

    # If a background retry is queued, don't amplify by re-running live resolution from UI calls.
    # Scheduler/worker paths should use force_live=True to bypass this short-circuit.
    if not force_live:
        pending_key = str(user_upn or user_object_id or user_upn_or_id).strip().lower()
        pending_row = store.get_onedrive_drive_pending(tenant_id=tenant_id, user_upn=pending_key)
        if isinstance(pending_row, dict) and pending_row:
            # If we have a stale cache entry, prefer returning it (operators can keep working)
            # while the background queue continues trying to refresh.
            if stale and stale.get("drive_id"):
                return DriveIdResolution(
                    drive_id=str(stale.get("drive_id")),
                    web_url=stale.get("web_url"),
                    drive_type=stale.get("drive_type"),
                    cached=True,
                    cache_fallback=True,
                    cached_stale=bool(stale.get("expired")),
                    last_verified_at=stale.get("last_verified_at"),
                    expires_at=stale.get("expires_at"),
                    warning="Using stale cached drive_id while a background refresh is queued.",
                    source="cache",
                ).to_payload()

            pending_row = dict(pending_row)
            pending_row.setdefault("max_attempts", int(pending_max_attempts or 10))
            next_run_at = pending_row.get("next_run_at")
            next_retry_seconds = None
            if isinstance(next_run_at, str) and next_run_at.strip():
                try:
                    parsed = datetime.fromisoformat(next_run_at.replace("Z", "+00:00"))
                    if parsed.tzinfo is None:
                        parsed = parsed.replace(tzinfo=timezone.utc)
                    next_retry_seconds = max(0, int((parsed - _now()).total_seconds()))
                except Exception:
                    next_retry_seconds = None

            paused = bool(pending_row.get("paused"))
            attempts = pending_row.get("attempts")
            if paused:
                if isinstance(next_retry_seconds, int) and next_retry_seconds > 0:
                    warning = (
                        f"Drive ID resolution paused after {attempts} attempts; next retry in {next_retry_seconds}s."
                        if isinstance(attempts, int)
                        else f"Drive ID resolution paused; next retry in {next_retry_seconds}s."
                    )
                else:
                    warning = (
                        f"Drive ID resolution paused after {attempts} attempts; retry scheduled."
                        if isinstance(attempts, int)
                        else "Drive ID resolution paused; retry scheduled."
                    )
            elif isinstance(next_retry_seconds, int) and next_retry_seconds <= 0:
                warning = "Drive ID resolution queued; retry is due and will run on the next scheduler tick."
            else:
                warning = "Drive ID resolution already queued; background retry pending."

            return {
                "id": None,
                "drive_id": None,
                "webUrl": None,
                "driveType": None,
                "cached": False,
                "cache_fallback": False,
                "cached_stale": False,
                "status": "pending",
                "pending": pending_row,
                "next_retry_seconds": next_retry_seconds,
                "warning": warning,
                "source": "pending",
            }

    def _suggest_pending_delay_seconds(exc: GraphAPIError) -> int:
        """Internal helper for suggest pending delay seconds."""
        circuit = getattr(exc, "circuit", None)
        if isinstance(circuit, dict):
            remaining = circuit.get("remaining_seconds") or circuit.get("remainingSeconds")
            if isinstance(remaining, (int, float)) and remaining > 0:
                try:
                    return max(30, int(remaining))
                except Exception:
                    pass
        retry_after = getattr(exc, "retry_after", None)
        if isinstance(retry_after, (int, float)):
            try:
                return max(30, int(retry_after))
            except Exception:
                pass
        attempts = getattr(exc, "attempts", None) or []
        for item in reversed(attempts):
            if not isinstance(item, dict):
                continue
            wait_ms = item.get("wait_ms")
            if isinstance(wait_ms, (int, float)) and wait_ms > 0:
                try:
                    return max(30, int(round(float(wait_ms) / 1000.0)))
                except Exception:
                    continue
        # Default retry delay for background queue: 2 minutes (avoids minute-by-minute amplification).
        return 120

    def _enqueue_pending(identifier: str, exc: GraphAPIError) -> Dict[str, Any]:
        """Internal helper for enqueue pending."""
        identifier = str(identifier or "").strip().lower()
        if not identifier:
            return {"enqueued": False, "error": "missing_identifier"}
        delay_s = _suggest_pending_delay_seconds(exc)
        return store.enqueue_onedrive_drive_pending(
            tenant_id=tenant_id,
            user_upn=identifier,
            delay_seconds=delay_s,
            last_error=str(exc),
            last_error_class=getattr(exc, "error_class", None),
            max_attempts=pending_max_attempts,
        )

    def _build_pending_payload(identifier: str, exc: GraphAPIError) -> Dict[str, Any]:
        """Build pending payload."""
        pending = _enqueue_pending(identifier, exc)
        if isinstance(pending, dict):
            pending.setdefault("max_attempts", int(pending_max_attempts or 10))
        next_run_at = pending.get("next_run_at") if isinstance(pending, dict) else None
        next_retry_seconds = None
        if isinstance(next_run_at, str) and next_run_at:
            try:
                parsed = datetime.fromisoformat(next_run_at.replace("Z", "+00:00"))
                if parsed.tzinfo is None:
                    parsed = parsed.replace(tzinfo=timezone.utc)
                next_retry_seconds = max(0, int((parsed - _now()).total_seconds()))
            except Exception:
                next_retry_seconds = None
        return {
            "id": None,
            "drive_id": None,
            "webUrl": None,
            "driveType": None,
            "cached": False,
            "cache_fallback": False,
            "cached_stale": False,
            "status": "pending",
            "pending": pending,
            "next_retry_seconds": next_retry_seconds,
            "warning": "Drive ID resolution queued; Graph/SharePoint appears degraded. Try again shortly.",
            "circuit": getattr(exc, "circuit", None),
            "live_error": build_graph_error_response(exc, service="onedrive", action="get_user_drive_id"),
            "source": "pending",
        }

    def _fetch_user_object_id(*, upn: str, budget_s: int) -> Tuple[str, str]:
        """Internal helper for fetch user object id."""
        safe_upn = quote(str(upn), safe="")
        response = graph.get(
            f"/users/{safe_upn}",
            params={"$select": "id,userPrincipalName"},
            max_attempts=min(3, int(max_attempts or 3)),
            max_budget_s=budget_s,
            ignore_circuit_breaker=bool(ignore_circuit_breaker),
        )
        data = response.json() if response is not None else {}
        obj_id = data.get("id")
        resolved = data.get("userPrincipalName") or upn
        if not obj_id:
            raise RuntimeError("Graph returned a user payload without an id.")
        return str(obj_id), str(resolved).strip().lower()

    def _fetch_drive(*, object_id: str, budget_s: int) -> Dict[str, Any]:
        """Internal helper for fetch drive."""
        safe_id = quote(str(object_id), safe="")
        response = graph.get(
            f"/users/{safe_id}/drive",
            params={"$select": "id,webUrl,driveType"},
            max_attempts=max_attempts,
            max_budget_s=budget_s,
            ignore_circuit_breaker=bool(ignore_circuit_breaker),
        )
        data = response.json() if response is not None else {}
        return {
            "id": data.get("id"),
            "webUrl": data.get("webUrl"),
            "driveType": data.get("driveType"),
        }

    budget = max(1, int(max_budget_s or 45))
    start = time.monotonic()
    resolution_source = "primary"
    resolved_upn = user_upn

    # Step A (UPN inputs): resolve Entra user object id. Keep this fast; the drive call is the expensive step.
    if user_upn and not user_object_id:
        try:
            step_a_budget = min(20, max(5, budget // 3))
            user_object_id, resolved_upn = _fetch_user_object_id(upn=user_upn, budget_s=step_a_budget)
        except GraphAPIError as exc:
            # If we have a cached/stale drive id, use it; otherwise bubble up.
            if stale and stale.get("drive_id"):
                return DriveIdResolution(
                    drive_id=str(stale.get("drive_id")),
                    web_url=stale.get("web_url"),
                    drive_type=stale.get("drive_type"),
                    cached=True,
                    cache_fallback=True,
                    cached_stale=bool(stale.get("expired")),
                    last_verified_at=stale.get("last_verified_at"),
                    expires_at=stale.get("expires_at"),
                    warning="Using cached drive_id; user lookup failed.",
                    circuit=getattr(exc, "circuit", None),
                    live_error=build_graph_error_response(exc, service="onedrive", action="get_user_drive_id"),
                    source="cache",
                ).to_payload()
            raise

    if not user_object_id:
        raise RuntimeError("Unable to resolve user object id for drive resolution.")

    # Step B: resolve drive by user object id.
    try:
        elapsed = time.monotonic() - start
        remaining = max(1, budget - int(elapsed))
        live = _fetch_drive(object_id=user_object_id, budget_s=remaining)
    except GraphAPIError as exc:
        status = getattr(exc, "status_code", None)
        if status == 404:
            exc.error_class = "onedrive_not_provisioned"
            raise
        if getattr(exc, "error_class", None) == "circuit_open" or status in (502, 503, 504):
            if stale and stale.get("drive_id"):
                if force_live:
                    # When explicitly forcing live (scheduler or operator), keep the pending queue scheduled so we
                    # eventually refresh when upstream recovers.
                    try:
                        identifier = str(resolved_upn or user_upn or user_upn_or_id).strip().lower()
                        _enqueue_pending(identifier, exc)
                    except Exception:
                        pass
                return DriveIdResolution(
                    drive_id=str(stale.get("drive_id")),
                    web_url=stale.get("web_url"),
                    drive_type=stale.get("drive_type"),
                    cached=True,
                    cache_fallback=True,
                    cached_stale=bool(stale.get("expired")),
                    last_verified_at=stale.get("last_verified_at"),
                    expires_at=stale.get("expires_at"),
                    warning="Using cached drive_id; upstream degraded.",
                    circuit=getattr(exc, "circuit", None),
                    live_error=build_graph_error_response(exc, service="onedrive", action="get_user_drive_id"),
                    source="cache",
                ).to_payload()
            # No cache to fall back to: enqueue and return pending instead of failing.
            identifier = resolved_upn or user_upn or user_upn_or_id
            return _build_pending_payload(str(identifier), exc)

        # Non-transient failures: still allow stale cache fallback.
        if stale and stale.get("drive_id"):
            return DriveIdResolution(
                drive_id=str(stale.get("drive_id")),
                web_url=stale.get("web_url"),
                drive_type=stale.get("drive_type"),
                cached=True,
                cache_fallback=True,
                cached_stale=bool(stale.get("expired")),
                last_verified_at=stale.get("last_verified_at"),
                expires_at=stale.get("expires_at"),
                warning="Using cached drive_id; live lookup failed.",
                circuit=getattr(exc, "circuit", None),
                live_error=build_graph_error_response(exc, service="onedrive", action="get_user_drive_id"),
                source="cache",
            ).to_payload()
        raise

    drive_id = live.get("id")
    web_url = live.get("webUrl")
    drive_type = live.get("driveType")
    if not drive_id:
        raise RuntimeError("Graph returned a drive payload without an id.")

    # For object-id inputs, try to resolve the UPN so the cache can be keyed by (tenant_id, user_upn).
    if not resolved_upn and user_object_id:
        try:
            safe_user_id = quote(str(user_object_id), safe="")
            resp = graph.get(
                f"/users/{safe_user_id}",
                params={"$select": "userPrincipalName"},
                max_attempts=min(2, int(max_attempts or 2)),
                max_budget_s=max(3, min(8, budget)),
                ignore_circuit_breaker=bool(ignore_circuit_breaker),
            )
            payload = resp.json() if resp is not None else {}
            resolved_upn = payload.get("userPrincipalName")
            if resolved_upn:
                resolved_upn = str(resolved_upn).strip().lower()
        except Exception:
            # Cache insert will be skipped if no UPN is available.
            pass

    now_iso = _now_iso()
    expires_at = (_now() + timedelta(days=max(1, int(ttl_days or 14)))).isoformat()
    store.upsert_onedrive_drive_cache(
        tenant_id=tenant_id,
        user_upn=resolved_upn,
        user_object_id=user_object_id,
        drive_id=str(drive_id),
        web_url=web_url,
        drive_type=drive_type,
        last_verified_at=now_iso,
        expires_at=expires_at,
        source=resolution_source,
    )
    try:
        identifier = resolved_upn or user_upn or user_upn_or_id
        store.clear_onedrive_drive_pending(tenant_id=tenant_id, user_upn=str(identifier))
    except Exception:
        pass
    return DriveIdResolution(
        drive_id=str(drive_id),
        web_url=web_url,
        drive_type=drive_type,
        cached=False,
        cache_fallback=False,
        cached_stale=False,
        last_verified_at=now_iso,
        expires_at=expires_at,
        source=resolution_source,
    ).to_payload()
