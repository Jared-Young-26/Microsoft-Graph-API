from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

from .probe_registry import PROBE_REGISTRY
from .snapshot_models import ProbeResult


def _extract_probe_id(result: Any) -> Optional[str]:
    """Internal helper for extract probe id."""
    if isinstance(result, ProbeResult):
        return result.probe
    if isinstance(result, dict):
        return result.get("probe")
    return None


def _extract_probe_ok(result: Any) -> bool:
    """Internal helper for extract probe ok."""
    if isinstance(result, ProbeResult):
        return bool(result.ok)
    if isinstance(result, dict):
        return bool(result.get("ok"))
    return False


def _extract_probe_data(result: Any) -> Any:
    """Internal helper for extract probe data."""
    if isinstance(result, ProbeResult):
        return result.data
    if isinstance(result, dict):
        return result.get("data")
    return None


def _extract_probe_error_class(result: Any) -> Optional[str]:
    """Internal helper for extract probe error class."""
    if isinstance(result, ProbeResult):
        return result.error_class
    if isinstance(result, dict):
        return result.get("error_class")
    return None


def _extract_probe_meta(result: Any) -> Dict[str, Any]:
    """Internal helper for extract probe meta."""
    if isinstance(result, ProbeResult):
        return result.meta or {}
    if isinstance(result, dict):
        return result.get("meta") or {}
    return {}


def _has_partial_data(data: Any) -> bool:
    """Return True if partial data."""
    if not isinstance(data, dict):
        return False
    for key in ("missing", "partial", "errors", "warnings"):
        value = data.get(key)
        if value:
            return True
    return False


def _section_from_outputs(outputs: Iterable[str]) -> Optional[str]:
    """Internal helper for section from outputs."""
    for path in outputs or []:
        if not path:
            continue
        parts = path.split(".")
        if parts and parts[0] == "lens":
            parts = parts[1:]
        if parts:
            return parts[0]
    return None


def _build_section_requirements(required_probes, registry_map: Dict[str, Dict[str, Any]]) -> Dict[str, List[str]]:
    """Build section requirements."""
    if isinstance(required_probes, dict):
        return {section: list(probes or []) for section, probes in required_probes.items()}
    if isinstance(required_probes, (list, tuple, set)):
        by_section: Dict[str, List[str]] = {}
        for probe_id in required_probes:
            entry = registry_map.get(probe_id) or {}
            section = _section_from_outputs(entry.get("outputs_to") or []) or "unknown"
            by_section.setdefault(section, []).append(probe_id)
        return by_section
    return {}


def compute_completeness(
    lens: Dict[str, Any],
    probe_results: Iterable[Any],
    required_probes: Any,
    registry: Optional[Iterable[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Compute completeness."""
    registry_items = list(registry or PROBE_REGISTRY)
    registry_map = {entry.get("probe_id"): entry for entry in registry_items if entry.get("probe_id")}
    required_by_section = _build_section_requirements(required_probes, registry_map)

    results_map: Dict[str, Any] = {}
    for result in probe_results or []:
        probe_id = _extract_probe_id(result)
        if probe_id:
            results_map[probe_id] = result

    sections = set(required_by_section.keys())
    if isinstance(lens, dict):
        sections |= set(lens.keys())

    section_scores: Dict[str, float] = {}
    missing_by_section: Dict[str, List[str]] = {}
    warnings: List[Dict[str, Any]] = []
    gaps: List[Dict[str, Any]] = []

    for section in sorted(sections):
        required = required_by_section.get(section, [])
        if not required:
            section_scores[section] = 1.0
            continue
        total = len(required)
        satisfied = 0
        missing = []
        for probe_id in required:
            result = results_map.get(probe_id)
            if result and _extract_probe_ok(result):
                satisfied += 1
                data = _extract_probe_data(result)
                if _has_partial_data(data):
                    warnings.append(
                        {
                            "probe": probe_id,
                            "section": section,
                            "issue": "partial",
                            "details": data.get("missing") if isinstance(data, dict) else None,
                        }
                    )
            else:
                missing.append(probe_id)
        missing_by_section[section] = missing
        section_scores[section] = satisfied / total if total else 1.0

    for probe_id, result in results_map.items():
        if _extract_probe_ok(result):
            continue
        error_class = _extract_probe_error_class(result) or "unknown"
        meta = _extract_probe_meta(result)
        entry = {
            "probe": probe_id,
            "error_class": error_class,
            "message": meta.get("error") or meta.get("message"),
        }
        if error_class in ("missing_module", "missing_permission"):
            gaps.append(entry)
        else:
            warnings.append({**entry, "issue": "failure"})

    overall = 1.0
    if section_scores:
        overall = sum(section_scores.values()) / len(section_scores)

    return {
        "sections": section_scores,
        "overall": overall,
        "missing_probes": missing_by_section,
        "gaps": gaps,
        "warnings": warnings,
    }
