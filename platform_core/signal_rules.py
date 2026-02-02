from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Iterable
import uuid

from .snapshot_storage import SnapshotSqlStore
from .snapshot_models import Subject


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _emit(store: SnapshotSqlStore, subject: Subject, signal_name: str, payload: Dict[str, Any], context: Dict[str, Any]):
    event_id = uuid.uuid4().hex
    emitted_at = _now_iso()
    store.add_event(
        event_id=event_id,
        time=emitted_at,
        kind="signal",
        source=context.get("source"),
        service="snapshot",
        signal_name=signal_name,
        canonical_ids=[subject.canonical_id],
        event={
            "event_id": event_id,
            "emitted_at": emitted_at,
            "signal": signal_name,
            "subject": {"canonical_id": subject.canonical_id, "kind": subject.kind},
            **payload,
        },
    )


def apply_signal_rules(store: SnapshotSqlStore, subject: Subject, lens: Dict[str, Any], probe_results: Iterable[Any], context: Dict[str, Any]):
    connectivity = (lens.get("connectivity") or {}).get("probes") or []
    for probe in connectivity:
        if not isinstance(probe, dict):
            continue
        name = (probe.get("name") or probe.get("type") or "").lower()
        if name == "dns_resolve" and probe.get("ok") is False:
            _emit(store, subject, "dns.failure", {"target": probe.get("target"), "error": probe.get("error")}, context)
        if name == "port_probe" and probe.get("reachable") is False:
            _emit(store, subject, "port.blocked", {"target": probe.get("target"), "port": probe.get("port")}, context)

    eventlog = (lens.get("health") or {}).get("eventlog_summary") or {}
    levels = eventlog.get("levels") if isinstance(eventlog, dict) else None
    if isinstance(levels, dict):
        error_count = 0
        for key in ("Error", "Critical"):
            try:
                error_count += int(levels.get(key) or 0)
            except Exception:
                continue
        if error_count > 0:
            _emit(store, subject, "eventlog.errors_present", {"count": error_count}, context)

    registry_watchlist = (lens.get("config") or {}).get("registry_watchlist") or {}
    if isinstance(registry_watchlist, dict):
        items = registry_watchlist.get("items") or []
        errors = [item for item in items if isinstance(item, dict) and item.get("error")]
        if errors:
            _emit(
                store,
                subject,
                "registry.watchlist_error",
                {"count": len(errors), "watchlist_id": registry_watchlist.get("watchlist_id")},
                context,
            )
