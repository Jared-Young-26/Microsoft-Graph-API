from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from microsoft import GraphAPIError

from .graph_error_transparency import build_graph_error_response
from .snapshot_storage import SnapshotSqlStore


def _now() -> datetime:
    """Internal helper for now."""
    return datetime.now(timezone.utc)


def _now_iso() -> str:
    """Internal helper for now iso."""
    return _now().isoformat()


@dataclass(frozen=True)
class SharePointSitesResult:
    """Share Point Sites Result."""
    value: list
    cached: bool = False
    cache_fallback: bool = False
    cached_stale: bool = False
    last_verified_at: Optional[str] = None
    expires_at: Optional[str] = None
    warning: Optional[str] = None
    circuit: Optional[Dict[str, Any]] = None
    partial: bool = False
    reason: Optional[str] = None
    live_error: Optional[Dict[str, Any]] = None

    def to_payload(self) -> Dict[str, Any]:
        """Run to payload."""
        return {
            "value": list(self.value or []),
            "cached": self.cached,
            "cache_fallback": self.cache_fallback,
            "cached_stale": self.cached_stale,
            "last_verified_at": self.last_verified_at,
            "expires_at": self.expires_at,
            "warning": self.warning,
            "circuit": self.circuit,
            "partial": self.partial,
            "reason": self.reason,
            "live_error": self.live_error,
        }


def list_sharepoint_sites_cached(
    *,
    store: SnapshotSqlStore,
    graph: Any,
    tenant_id: str,
    search_term: str = "*",
    force_live: bool = False,
    ttl_seconds: int = 7200,
    max_pages: int = 10,
    max_items: int = 500,
    max_budget_s: int = 60,
    max_attempts: int = 4,
) -> Dict[str, Any]:
    """List SharePoint sites with paging limits + cache to reduce 503 amplification."""

    tenant_id = str(tenant_id or "").strip()
    if not tenant_id:
        raise ValueError("tenant_id is required for SharePoint site caching.")

    term = str(search_term or "*").strip() or "*"

    cached = None
    if not force_live:
        cached = store.get_sharepoint_sites_cache(tenant_id=tenant_id, search_term=term, allow_expired=False)
        if cached and isinstance(cached.get("sites"), list):
            return SharePointSitesResult(
                value=cached["sites"],
                cached=True,
                cache_fallback=False,
                cached_stale=False,
                last_verified_at=cached.get("last_verified_at"),
                expires_at=cached.get("expires_at"),
            ).to_payload()

    stale = store.get_sharepoint_sites_cache(tenant_id=tenant_id, search_term=term, allow_expired=True)

    try:
        paged = graph.paged_get(
            "/sites",
            params={"search": term},
            max_pages=max_pages,
            max_items=max_items,
            return_meta=True,
            retry_budget_seconds=max_budget_s,
            max_attempts=max_attempts,
        )
    except GraphAPIError as exc:
        if stale and isinstance(stale.get("sites"), list) and stale.get("sites"):
            warning = "Using cached sites; upstream degraded."
            if getattr(exc, "error_class", None) == "circuit_open":
                warning = "Using cached sites; upstream degraded and circuit breaker is open."
            return SharePointSitesResult(
                value=stale["sites"],
                cached=True,
                cache_fallback=True,
                cached_stale=True,
                last_verified_at=stale.get("last_verified_at"),
                expires_at=stale.get("expires_at"),
                warning=warning,
                circuit=getattr(exc, "circuit", None),
                live_error=build_graph_error_response(exc, service="sharepoint", action="list_sites"),
            ).to_payload()
        raise

    sites = []
    if isinstance(paged, dict):
        sites = paged.get("value") or []
    elif isinstance(paged, list):
        sites = paged
    if not isinstance(sites, list):
        sites = [sites]

    now_iso = _now_iso()
    expires_at = (_now() + timedelta(seconds=max(60, int(ttl_seconds or 7200)))).isoformat()
    store.upsert_sharepoint_sites_cache(
        tenant_id=tenant_id,
        search_term=term,
        sites=sites,
        last_verified_at=now_iso,
        expires_at=expires_at,
    )

    partial = bool(isinstance(paged, dict) and paged.get("partial"))
    reason = paged.get("reason") if isinstance(paged, dict) else None

    return SharePointSitesResult(
        value=sites,
        cached=False,
        cache_fallback=False,
        last_verified_at=now_iso,
        expires_at=expires_at,
        partial=partial,
        reason=str(reason) if reason else None,
    ).to_payload()
