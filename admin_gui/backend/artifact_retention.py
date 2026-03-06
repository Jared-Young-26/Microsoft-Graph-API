from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import os
import threading
import time


def _parse_int(value: Any, default: int) -> int:
    if value is None:
        return default
    try:
        return int(str(value).strip())
    except Exception:
        return default


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def prune_artifacts_dir(
    artifacts_dir: Path,
    *,
    max_age_days: int | None,
    max_total_bytes: int | None,
) -> dict[str, Any]:
    """Prune artifacts by age and total size.

    Age pruning runs first, then size pruning (oldest-first) until under limit.
    """

    artifacts_dir = Path(artifacts_dir)
    if not artifacts_dir.exists() or not artifacts_dir.is_dir():
        return {"ok": True, "removed": 0, "reason": "missing_dir"}

    max_age_days = int(max_age_days) if max_age_days is not None else None
    max_total_bytes = int(max_total_bytes) if max_total_bytes is not None else None
    if max_age_days is not None and max_age_days <= 0:
        max_age_days = None
    if max_total_bytes is not None and max_total_bytes <= 0:
        max_total_bytes = None
    if max_age_days is None and max_total_bytes is None:
        return {"ok": True, "removed": 0, "reason": "disabled"}

    now = time.time()
    cutoff = now - (max_age_days * 86400) if max_age_days is not None else None

    entries: list[dict[str, Any]] = []
    total_before = 0
    for path in artifacts_dir.iterdir():
        try:
            if not path.is_file():
                continue
            stat = path.stat()
            size = int(stat.st_size)
            mtime = float(stat.st_mtime)
            entries.append({"path": path, "size": size, "mtime": mtime})
            total_before += size
        except Exception:
            continue

    removed = 0
    removed_bytes = 0

    if cutoff is not None:
        for item in sorted(entries, key=lambda x: x["mtime"]):
            if item["mtime"] >= cutoff:
                continue
            try:
                Path(item["path"]).unlink()
                removed += 1
                removed_bytes += int(item["size"])
                item["deleted"] = True
            except Exception:
                continue

    remaining = [item for item in entries if not item.get("deleted")]
    total_after_age = sum(int(item["size"]) for item in remaining)

    if max_total_bytes is not None and total_after_age > max_total_bytes:
        remaining.sort(key=lambda x: x["mtime"])
        total = total_after_age
        for item in remaining:
            if total <= max_total_bytes:
                break
            try:
                Path(item["path"]).unlink()
                removed += 1
                removed_bytes += int(item["size"])
                total -= int(item["size"])
            except Exception:
                continue

    return {
        "ok": True,
        "removed": removed,
        "removed_bytes": removed_bytes,
        "total_before_bytes": total_before,
        "total_after_bytes": max(0, total_before - removed_bytes),
        "timestamp": _now_iso(),
        "config": {"max_age_days": max_age_days, "max_total_bytes": max_total_bytes},
    }


def _env_max_age_days() -> int | None:
    value = os.environ.get("GAS_ARTIFACT_RETENTION_MAX_AGE_DAYS")
    if value is None:
        value = os.environ.get("ARTIFACT_RETENTION_MAX_AGE_DAYS")
    return _parse_int(value, 30) if value is not None else 30


def _env_max_total_bytes() -> int | None:
    value = os.environ.get("GAS_ARTIFACT_RETENTION_MAX_BYTES")
    if value is None:
        value = os.environ.get("ARTIFACT_RETENTION_MAX_BYTES")
    default_bytes = 5 * 1024 * 1024 * 1024  # 5 GiB
    return _parse_int(value, default_bytes) if value is not None else default_bytes


def _env_interval_seconds() -> int:
    value = os.environ.get("GAS_ARTIFACT_RETENTION_INTERVAL_SECONDS")
    if value is None:
        value = os.environ.get("ARTIFACT_RETENTION_INTERVAL_SECONDS")
    return max(30, min(24 * 3600, _parse_int(value, 600)))


@dataclass
class ArtifactRetentionReaper:
    """Background artifact retention job."""

    artifacts_dir: Path
    interval_seconds: int = 600
    max_age_days: int | None = 30
    max_total_bytes: int | None = 5 * 1024 * 1024 * 1024
    _thread: threading.Thread | None = field(default=None, init=False)
    _stop: threading.Event = field(default_factory=threading.Event, init=False)
    last_run: dict[str, Any] | None = field(default=None, init=False)

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()

    def _run(self) -> None:
        while not self._stop.is_set():
            try:
                self.last_run = prune_artifacts_dir(
                    self.artifacts_dir,
                    max_age_days=self.max_age_days,
                    max_total_bytes=self.max_total_bytes,
                )
            except Exception:
                self.last_run = {"ok": False, "error": "prune_failed", "timestamp": _now_iso()}
            self._stop.wait(timeout=int(self.interval_seconds or 600))


REAPER: ArtifactRetentionReaper | None = None
_STARTED = False


def ensure_artifact_retention_reaper(artifacts_dir: Path) -> ArtifactRetentionReaper | None:
    """Ensure the artifact retention reaper is running."""

    global REAPER
    global _STARTED
    if _STARTED:
        return REAPER
    try:
        REAPER = ArtifactRetentionReaper(
            artifacts_dir=Path(artifacts_dir),
            interval_seconds=_env_interval_seconds(),
            max_age_days=_env_max_age_days(),
            max_total_bytes=_env_max_total_bytes(),
        )
        REAPER.start()
        _STARTED = True
        return REAPER
    except Exception:
        return None

