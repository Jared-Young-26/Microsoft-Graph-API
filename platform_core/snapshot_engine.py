from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError as FutureTimeout
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional
import uuid

from .entity_resolution import EntityResolver
from .lens import assemble_lens
from .probe_registry import PROBE_REGISTRY
from .probe_runners import run_graph_probe, run_powershell_probe, run_local_probe
from .quality import compute_completeness
from .snapshot_models import Event, Snapshot, Subject, SubjectRef
from .snapshot_storage import SnapshotSqlStore
from .signal_rules import apply_signal_rules


PROFILE_ORDER = {"core": 0, "troubleshoot": 1, "deep": 2}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _profile_allows(profile: str, minimum: str) -> bool:
    return PROFILE_ORDER.get(profile, 0) >= PROFILE_ORDER.get(minimum, 0)


def _extract_kind(subject: Any) -> str:
    if isinstance(subject, Subject):
        return subject.kind
    if isinstance(subject, dict):
        return subject.get("kind") or subject.get("subject_kind") or subject.get("subject_type") or ""
    return ""


def _resolve_subject(resolver: EntityResolver, subject: Any) -> Subject:
    if isinstance(subject, Subject):
        resolver.store.upsert_entity(subject.canonical_id, subject.kind, display_name=subject.display_name)
        for alias in subject.aliases:
            resolver.store.add_alias(subject.canonical_id, alias.type, alias.value, alias.confidence)
        return subject
    if not isinstance(subject, dict):
        raise ValueError("Subject must be a Subject or dict.")
    kind = _extract_kind(subject)
    if not kind:
        raise ValueError("Subject kind is required.")
    canonical_id = subject.get("canonical_id")
    identifiers = subject.get("identifiers")
    aliases = subject.get("aliases") or []
    display_name = subject.get("display_name") or subject.get("name")

    if canonical_id:
        resolver.store.upsert_entity(canonical_id, kind, display_name=display_name)
        for alias in aliases:
            try:
                alias_type = alias.get("type") if isinstance(alias, dict) else None
                alias_value = alias.get("value") if isinstance(alias, dict) else None
                alias_confidence = alias.get("confidence") if isinstance(alias, dict) else None
            except Exception:
                alias_type = None
                alias_value = None
                alias_confidence = None
            if alias_type and alias_value:
                resolver.store.add_alias(canonical_id, alias_type, alias_value, alias_confidence)
        return Subject(
            subject_type=subject.get("subject_type") or ("node" if kind else "resource"),
            kind=kind,
            canonical_id=canonical_id,
            display_name=display_name,
            aliases=[],
        )

    if identifiers is None and aliases:
        identifiers = {}
        for alias in aliases:
            if isinstance(alias, dict):
                alias_type = alias.get("type")
                alias_value = alias.get("value")
                if alias_type and alias_value:
                    identifiers.setdefault(alias_type, []).append(alias_value)
    if identifiers is None:
        identifiers = {k: v for k, v in subject.items() if k not in ("kind", "subject_kind", "subject_type")}
        identifiers["display_name"] = display_name
    return resolver.resolve_subject(kind, identifiers)


def _select_probes(subject_kind: str, profile: str, registry: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    selected = []
    for entry in registry:
        if subject_kind not in (entry.get("subject_kinds") or []):
            continue
        if not _profile_allows(profile, entry.get("profile_min", "core")):
            continue
        selected.append(entry)
    return selected


def _probe_runner(tool: str):
    if tool == "graph":
        return run_graph_probe
    if tool == "powershell":
        return run_powershell_probe
    if tool == "local":
        return run_local_probe
    return run_local_probe


def _infer_relationships(subject: Subject, lens: Dict[str, Any]) -> List[Dict[str, Any]]:
    relationships: List[Dict[str, Any]] = []
    if subject.kind == "user":
        groups = ((lens.get("authz") or {}).get("access") or {}).get("group_memberships") or []
        for group in groups:
            if not isinstance(group, dict):
                continue
            target = group.get("id") or group.get("displayName") or group.get("display_name")
            if not target:
                continue
            relationships.append(
                {
                    "type": "user_member_of_group",
                    "source": subject.canonical_id,
                    "target": target,
                    "target_name": group.get("displayName") or group.get("display_name"),
                }
            )
        licenses = ((lens.get("authz") or {}).get("access") or {}).get("licenses") or []
        for license_item in licenses:
            if not isinstance(license_item, dict):
                continue
            target = license_item.get("skuId") or license_item.get("skuPartNumber")
            if not target:
                continue
            relationships.append(
                {
                    "type": "user_has_license",
                    "source": subject.canonical_id,
                    "target": target,
                    "target_name": license_item.get("skuPartNumber"),
                }
            )
    if subject.kind == "dc":
        partners = ((lens.get("health") or {}).get("replication") or {}).get("partners") or []
        for partner in partners:
            if not isinstance(partner, dict):
                continue
            target = partner.get("partner") or partner.get("Partner")
            if not target:
                continue
            relationships.append(
                {
                    "type": "dc_replication_partner",
                    "source": subject.canonical_id,
                    "target": target,
                }
            )
    connectivity = (lens.get("connectivity") or {}).get("probes") or []
    for probe in connectivity:
        if not isinstance(probe, dict):
            continue
        ip = probe.get("ip") or probe.get("IPAddress") or probe.get("address")
        if ip:
            relationships.append(
                {"type": "device_resolves_to_ip", "source": subject.canonical_id, "target": ip}
            )
        ports = probe.get("ports") or probe.get("open_ports")
        if ports:
            relationships.append(
                {
                    "type": "device_reachable_on_ports",
                    "source": subject.canonical_id,
                    "target": ",".join(str(port) for port in ports),
                }
            )
    return relationships


def _emit_time_signals(
    store: SnapshotSqlStore,
    subject: Subject,
    lens: Dict[str, Any],
    context: Dict[str, Any],
) -> None:
    health = lens.get("health") or {}
    time_info = health.get("time") or {}
    thresholds = context.get("time_thresholds") or {}
    warn_ms = thresholds.get("warn_ms", 300)
    high_ms = thresholds.get("high_ms", 5000)
    offsets = []
    for key in ("offset_ms", "dc_offset_ms", "ntp_offset_ms"):
        value = time_info.get(key)
        try:
            if value is not None:
                offsets.append(float(value))
        except Exception:
            continue
    for offset in offsets:
        if abs(offset) >= high_ms:
            event_id = str(uuid.uuid4())
            emitted_at = _now_iso()
            store.add_event(
                event_id=event_id,
                time=emitted_at,
                kind="signal",
                source=context.get("source"),
                service="time",
                signal_name="time.skew_detected",
                canonical_ids=[subject.canonical_id],
                event={
                    "event_id": event_id,
                    "emitted_at": emitted_at,
                    "signal": "time.skew_detected",
                    "subject": {"canonical_id": subject.canonical_id, "kind": subject.kind},
                    "offset_ms": offset,
                    "threshold_ms": high_ms,
                },
            )
        elif abs(offset) >= warn_ms:
            event_id = str(uuid.uuid4())
            emitted_at = _now_iso()
            store.add_event(
                event_id=event_id,
                time=emitted_at,
                kind="signal",
                source=context.get("source"),
                service="time",
                signal_name="time.skew_warning",
                canonical_ids=[subject.canonical_id],
                event={
                    "event_id": event_id,
                    "emitted_at": emitted_at,
                    "signal": "time.skew_warning",
                    "subject": {"canonical_id": subject.canonical_id, "kind": subject.kind},
                    "offset_ms": offset,
                    "threshold_ms": warn_ms,
                },
            )


@dataclass
class SnapshotEngine:
    store: SnapshotSqlStore
    resolver: EntityResolver
    registry: Iterable[Dict[str, Any]] = tuple(PROBE_REGISTRY)

    def capture_snapshot(self, subject: Any, profile: str, context: Dict[str, Any]) -> Dict[str, Any]:
        resolved_subject = _resolve_subject(self.resolver, subject)
        subject_kind = resolved_subject.kind
        probes = _select_probes(subject_kind, profile, self.registry)
        probe_plan = context.get("probe_plan") or []
        if probe_plan:
            probes = [entry for entry in probes if entry.get("probe_id") in set(probe_plan)]

        max_workers = int(context.get("max_workers") or 6)
        probe_results: List[Any] = []
        futures = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for entry in probes:
                probe_id = entry.get("probe_id")
                tool = entry.get("tool")
                runner = _probe_runner(tool)
                options = dict(context.get("probe_options", {}).get(probe_id, {}))
                inputs = dict(entry.get("inputs") or {})
                default_overrides = (context.get("probe_defaults") or {}).get(probe_id, {})
                if isinstance(default_overrides, dict):
                    inputs.update(default_overrides)
                if inputs.get("include_optional_ports") and inputs.get("optional_ports"):
                    ports = list(inputs.get("ports") or [])
                    for port in inputs.get("optional_ports") or []:
                        if port not in ports:
                            ports.append(port)
                    inputs["ports"] = ports
                if "inputs" not in options:
                    options["inputs"] = inputs
                if "handler" not in options:
                    options["handler"] = (context.get("probe_handlers") or {}).get(probe_id)
                timeout_s = entry.get("timeout_s")
                future = executor.submit(runner, probe_id, resolved_subject, context, options)
                futures.append((future, timeout_s, probe_id))

            for future, timeout_s, probe_id in futures:
                try:
                    result = future.result(timeout=timeout_s or None)
                except FutureTimeout:
                    result = run_local_probe(
                        probe_id,
                        resolved_subject,
                        context,
                        {
                            "handler": lambda **_: None,
                            "evidence_refs": [],
                            "error": f"Probe timeout after {timeout_s}s",
                        },
                    )
                    result.ok = False
                    result.error_class = "network"
                    result.severity = "high"
                    result.data = {"missing": {"error": f"Probe timeout after {timeout_s}s"}}
                except Exception as exc:
                    result = run_local_probe(
                        probe_id,
                        resolved_subject,
                        context,
                        {
                            "handler": lambda **_: None,
                            "evidence_refs": [],
                            "error": str(exc),
                        },
                    )
                    result.ok = False
                    result.error_class = "unknown"
                    result.severity = "high"
                    result.data = {"missing": {"error": str(exc)}}
                probe_results.append(result)

        lens = assemble_lens(subject_kind, probe_results, registry=self.registry)
        relationships = _infer_relationships(resolved_subject, lens)

        previous_snapshot_id = self.store.get_latest_snapshot_id(resolved_subject.canonical_id)
        lens.setdefault("change", {})
        lens["change"]["previous_snapshot_id"] = previous_snapshot_id

        _emit_time_signals(self.store, resolved_subject, lens, context)
        apply_signal_rules(self.store, resolved_subject, lens, probe_results, context)

        required_probe_ids = [entry.get("probe_id") for entry in probes if entry.get("probe_id")]
        quality = compute_completeness(lens, probe_results, required_probe_ids, registry=self.registry)
        quality["completeness"] = quality.get("overall")

        snapshot_id = uuid.uuid4().hex
        captured_at = _now_iso()
        executed_probes = [entry.get("probe_id") for entry in probes if entry.get("probe_id")]
        symptom_id = context.get("symptom_id")
        symptom_tier = context.get("symptom_tier")
        symptom_trigger = context.get("symptom_trigger")

        snapshot = Snapshot(
            snapshot_id=snapshot_id,
            captured_at=captured_at,
            profile=profile,
            scope={"profile": profile, "subject_kind": subject_kind},
            subject=resolved_subject,
            lens=lens,
            relationships=relationships,
            quality=quality,
            evidence_refs=[],
        )

        probe_payloads = []
        for result in probe_results:
            if hasattr(result, "model_dump"):
                probe_payloads.append(result.model_dump(by_alias=True))
            elif isinstance(result, dict):
                probe_payloads.append(result)
            else:
                probe_payloads.append({"probe": getattr(result, "probe", "unknown")})

        snapshot_payload = snapshot.model_dump(by_alias=True)

        # Optional external signals (validated via contracts/*).
        from .signal_providers import VISION_U_EYE_PROVIDER, attach_signal

        signals = context.get("signals") if isinstance(context, dict) else None
        if isinstance(signals, dict):
            visual_payload = signals.get("visual")
            if isinstance(visual_payload, dict):
                try:
                    attach_signal(snapshot_payload, VISION_U_EYE_PROVIDER, visual_payload)
                    self.store.upsert_snapshot_signal(
                        snapshot_id=snapshot_id,
                        signal_name=VISION_U_EYE_PROVIDER.name,
                        provider_version=VISION_U_EYE_PROVIDER.version,
                        payload=visual_payload,
                    )
                except Exception:
                    pass
        snapshot_payload["probe_results"] = probe_payloads
        if symptom_id:
            snapshot_payload["symptom_id"] = symptom_id
        if symptom_tier:
            snapshot_payload["symptom_tier"] = symptom_tier
        if symptom_trigger:
            snapshot_payload["symptom_trigger"] = symptom_trigger
        snapshot_payload["executed_probes"] = executed_probes

        self.store.add_snapshot(
            snapshot_id,
            resolved_subject.canonical_id,
            resolved_subject.kind,
            profile,
            captured_at,
            snapshot_payload,
        )

        event_id = uuid.uuid4().hex
        event = Event(
            event_id=event_id,
            emitted_at=captured_at,
            snapshot_id=snapshot_id,
            subject_refs=[
                SubjectRef(
                    subject_type=resolved_subject.subject_type,
                    kind=resolved_subject.kind,
                    canonical_id=resolved_subject.canonical_id,
                    display_name=resolved_subject.display_name,
                )
            ],
            meta={
                "profile": profile,
                "subject_kind": subject_kind,
                "symptom_id": symptom_id,
                "symptom_tier": symptom_tier,
                "executed_probes": executed_probes,
            },
        )
        self.store.add_event(
            event_id,
            captured_at,
            "snapshot.captured",
            context.get("source"),
            context.get("service"),
            "snapshot_capture",
            [resolved_subject.canonical_id],
            event.model_dump(by_alias=True),
        )

        # Inference escalation: trigger troubleshoot snapshot on high severity/errors
        allow_escalation = bool(context.get("allow_inference_escalation", True))
        if allow_escalation and profile == "core":
            critical = False
            for result in probe_results:
                severity = getattr(result, "severity", None) if isinstance(result, object) else None
                error_class = getattr(result, "error_class", None) if isinstance(result, object) else None
                if isinstance(result, dict):
                    severity = result.get("severity")
                    error_class = result.get("error_class")
                # Escalate only for truly high-severity failures; coverage gaps (missing
                # modules/permissions) and transient upstream issues should not trigger
                # additional snapshots automatically.
                if severity == "high":
                    critical = True
                    break
            if critical:
                escalation_context = dict(context or {})
                escalation_context["allow_inference_escalation"] = False
                escalation_context["source"] = "inference"
                escalation_context["service"] = "snapshot"
                try:
                    escalation = self.capture_snapshot(resolved_subject, "troubleshoot", escalation_context)
                    self.store.add_event(
                        event_id=uuid.uuid4().hex,
                        time=_now_iso(),
                        kind="snapshot.escalation",
                        source="inference",
                        service="snapshot",
                        signal_name="snapshot_escalation",
                        canonical_ids=[resolved_subject.canonical_id],
                        event={"trigger": "severity", "snapshot_id": snapshot_id, "escalation": escalation},
                    )
                except Exception:
                    pass

        return {
            "snapshot_id": snapshot_id,
            "event_id": event_id,
            "canonical_id": resolved_subject.canonical_id,
            "profile": profile,
            "subject_kind": subject_kind,
            "probe_count": len(probe_results),
            "quality": quality,
            "probe_outcomes": [
                {
                    "probe": getattr(result, "probe", result.get("probe") if isinstance(result, dict) else None),
                    "ok": getattr(result, "ok", result.get("ok") if isinstance(result, dict) else None),
                    "severity": getattr(result, "severity", result.get("severity") if isinstance(result, dict) else None),
                    "error_class": getattr(result, "error_class", result.get("error_class") if isinstance(result, dict) else None),
                }
                for result in probe_results
            ],
        }
