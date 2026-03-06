from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json
import os
import sys
import time

from .redaction import redact


def _now_iso() -> str:
    """Internal helper for now iso."""
    return datetime.now(timezone.utc).isoformat()


@dataclass
class JsonLogger:
    """Structured JSON logger."""

    name: str
    base_fields: dict[str, Any] = field(default_factory=dict)
    sink_path: Path | None = None
    max_bytes: int | None = None
    backup_count: int | None = None
    _last_rotate_check: float = field(default=0.0, init=False, repr=False)

    def with_fields(self, **fields: Any) -> "JsonLogger":
        merged = dict(self.base_fields)
        merged.update(fields)
        return JsonLogger(
            self.name,
            merged,
            self.sink_path,
            max_bytes=self.max_bytes,
            backup_count=self.backup_count,
        )

    def __post_init__(self) -> None:
        if self.max_bytes is None:
            try:
                self.max_bytes = int(os.environ.get("GAS_LOG_MAX_BYTES") or 5_000_000)
            except Exception:
                self.max_bytes = 5_000_000
        if self.backup_count is None:
            try:
                self.backup_count = int(os.environ.get("GAS_LOG_BACKUP_COUNT") or 5)
            except Exception:
                self.backup_count = 5
        if self.max_bytes < 0:
            self.max_bytes = 0
        if self.backup_count < 0:
            self.backup_count = 0

    def _rotate_if_needed(self) -> None:
        if not self.sink_path:
            return
        if not self.max_bytes or self.max_bytes <= 0:
            return
        now = time.time()
        if (now - float(self._last_rotate_check or 0.0)) < 1.0:
            return
        self._last_rotate_check = now
        path = self.sink_path
        try:
            size = path.stat().st_size
        except Exception:
            return
        if size < int(self.max_bytes):
            return
        backups = int(self.backup_count or 0)
        if backups <= 0:
            try:
                path.unlink(missing_ok=True)  # type: ignore[arg-type]
            except TypeError:
                try:
                    if path.exists():
                        path.unlink()
                except Exception:
                    pass
            except Exception:
                pass
            return

        def rot_name(idx: int) -> Path:
            return path.with_name(path.name + f".{idx}")

        try:
            last = rot_name(backups)
            if last.exists():
                last.unlink()
        except Exception:
            pass

        for idx in range(backups - 1, 0, -1):
            src = rot_name(idx)
            dst = rot_name(idx + 1)
            try:
                if src.exists():
                    src.replace(dst)
            except Exception:
                continue

        try:
            if path.exists():
                path.replace(rot_name(1))
        except Exception:
            return

    def _emit(self, level: str, message: str, **fields: Any) -> None:
        payload = {
            "ts": _now_iso(),
            "level": level,
            "logger": self.name,
            "msg": message,
            **self.base_fields,
            **fields,
        }
        safe = redact(payload)
        line = json.dumps(safe, default=str)
        sys.stdout.write(line + "\n")
        sys.stdout.flush()
        if self.sink_path:
            try:
                self.sink_path.parent.mkdir(parents=True, exist_ok=True)
                self._rotate_if_needed()
                with self.sink_path.open("a", encoding="utf-8") as handle:
                    handle.write(line + "\n")
            except Exception:
                return

    def info(self, message: str, **fields: Any) -> None:
        self._emit("info", message, **fields)

    def warning(self, message: str, **fields: Any) -> None:
        self._emit("warning", message, **fields)

    def error(self, message: str, **fields: Any) -> None:
        self._emit("error", message, **fields)
