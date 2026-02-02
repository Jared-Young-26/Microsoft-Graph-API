from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional
import json
import uuid


@dataclass
class SnapshotStore:
    path: Path

    def _ensure_parent(self) -> None:
        if not self.path.parent.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)

    def put(
        self,
        snapshot_type: str,
        target_id: str,
        payload: Any,
        meta: Optional[Dict[str, Any]] = None,
        source: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        self._ensure_parent()
        entry = {
            "id": uuid.uuid4().hex,
            "type": snapshot_type,
            "target": target_id,
            "collected_at": datetime.now(timezone.utc).isoformat(),
            "source": source or {},
            "payload": payload,
            "meta": meta or {},
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, default=str) + "\n")
        return entry

    def list(self, snapshot_type: str, target_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        entries: List[Dict[str, Any]] = []
        if not self.path.exists():
            return entries
        target_key = str(target_id).lower()
        try:
            with self.path.open("r", encoding="utf-8") as handle:
                for line in handle:
                    try:
                        record = json.loads(line)
                    except Exception:
                        continue
                    if record.get("type") != snapshot_type:
                        continue
                    if str(record.get("target") or "").lower() != target_key:
                        continue
                    entries.append(record)
        except Exception:
            return []
        entries.sort(key=lambda item: item.get("collected_at") or "", reverse=True)
        if limit and limit > 0:
            return entries[:limit]
        return entries

    def get(self, snapshot_id: str) -> Optional[Dict[str, Any]]:
        if not self.path.exists():
            return None
        try:
            with self.path.open("r", encoding="utf-8") as handle:
                for line in handle:
                    try:
                        record = json.loads(line)
                    except Exception:
                        continue
                    if record.get("id") == snapshot_id:
                        return record
        except Exception:
            return None
        return None
