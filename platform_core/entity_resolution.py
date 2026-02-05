from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Tuple
import uuid

from .snapshot_models import Alias, Subject
from .snapshot_storage import SnapshotSqlStore


STRONG_IDS = {"entra_device_id", "ad_object_guid", "bios_uuid", "serial"}
MEDIUM_IDS = {"fqdn", "objectId", "sid"}
WEAK_IDS = {"hostname", "ip"}

CONFIDENCE_SCORE = {
    "strong": 0.95,
    "medium": 0.75,
    "weak": 0.55,
}

NODE_KINDS = {
    "device",
    "workstation",
    "server",
    "dc",
    "network_device",
    "admin_host",
    "dns_server",
    "dhcp_server",
    "file_server",
    "print_server",
}


def _normalize_alias_value(alias_type: str, value: str) -> str:
    """Normalize alias value."""
    if not value:
        return value
    lowered_types = {"fqdn", "hostname", "upn", "email", "mail", "ip", "dns"}
    if alias_type.lower() in lowered_types:
        return value.strip().lower()
    return value.strip()


def _confidence_for(alias_type: str) -> float:
    """Internal helper for confidence for."""
    if alias_type in STRONG_IDS:
        return CONFIDENCE_SCORE["strong"]
    if alias_type in MEDIUM_IDS:
        return CONFIDENCE_SCORE["medium"]
    if alias_type in WEAK_IDS:
        return CONFIDENCE_SCORE["weak"]
    return 0.4


def _subject_type_for(kind: str) -> str:
    """Internal helper for subject type for."""
    return "node" if kind in NODE_KINDS else "resource"


def _iter_identifiers(identifiers: Any) -> Iterable[Tuple[str, str]]:
    """Internal helper for iter identifiers."""
    if not identifiers:
        return []
    if isinstance(identifiers, dict):
        for key, value in identifiers.items():
            if value is None or value == "":
                continue
            if isinstance(value, (list, tuple)):
                for item in value:
                    if item is None or item == "":
                        continue
                    yield str(key), str(item)
            else:
                yield str(key), str(value)
        return []
    if isinstance(identifiers, (list, tuple)):
        for item in identifiers:
            if not item:
                continue
            if isinstance(item, dict):
                alias_type = item.get("type") or item.get("alias_type")
                alias_value = item.get("value") or item.get("alias_value")
                if alias_type and alias_value:
                    yield str(alias_type), str(alias_value)
            elif isinstance(item, (list, tuple)) and len(item) >= 2:
                yield str(item[0]), str(item[1])
        return []
    return []


@dataclass
class EntityResolver:
    """Entity Resolver."""
    store: SnapshotSqlStore

    def resolve_subject(self, kind: str, identifiers: Any) -> Subject:
        """Resolve subject."""
        aliases: List[Alias] = []
        candidates: Dict[str, float] = {}
        display_name = None

        if isinstance(identifiers, dict):
            display_name = identifiers.get("display_name") or identifiers.get("name")

        for alias_type, alias_value in _iter_identifiers(identifiers):
            if alias_type in ("display_name", "name"):
                if not display_name:
                    display_name = alias_value
                continue
            normalized_value = _normalize_alias_value(alias_type, alias_value)
            confidence = _confidence_for(alias_type)
            aliases.append(Alias(type=alias_type, value=normalized_value, confidence=confidence))
            existing = self.store.resolve_alias(alias_type, normalized_value)
            if existing:
                candidates[existing] = candidates.get(existing, 0.0) + confidence

        canonical_id = None
        if candidates:
            canonical_id = max(candidates.items(), key=lambda item: item[1])[0]

        if not canonical_id:
            if aliases:
                strongest = max(aliases, key=lambda entry: entry.confidence or 0.0)
                canonical_id = f"{kind}:{strongest.value}"
            else:
                canonical_id = f"{kind}:{uuid.uuid4().hex}"

        self.store.upsert_entity(canonical_id, kind, display_name=display_name)
        for alias in aliases:
            self.store.add_alias(canonical_id, alias.type, alias.value, alias.confidence)

        return Subject(
            subject_type=_subject_type_for(kind),
            kind=kind,
            canonical_id=canonical_id,
            display_name=display_name,
            aliases=aliases,
        )
