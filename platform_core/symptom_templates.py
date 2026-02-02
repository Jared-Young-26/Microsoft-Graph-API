from __future__ import annotations

from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class SymptomTemplate(BaseModel):
    model_config = ConfigDict(extra="allow")

    symptom_id: str
    display_name: str
    category: str
    intent_labels: List[str] = Field(default_factory=list)
    default_subject_roles: List[str] = Field(default_factory=list)
    derived_subject_rules: List[Dict[str, object]] = Field(default_factory=list)
    probe_plan: Dict[str, List[str]] = Field(default_factory=dict)
    expected_root_causes: List[str] = Field(default_factory=list)
    snapshot_profiles: Dict[str, str] = Field(default_factory=dict)


SYMPTOM_TEMPLATES: Dict[str, SymptomTemplate] = {
    "auth.login_failure": SymptomTemplate(
        symptom_id="auth.login_failure",
        display_name="Login failure",
        category="auth",
        intent_labels=["signin", "mfa", "token", "authentication"],
        default_subject_roles=["actor.user", "actor.device", "dependency.dc", "dependency.dns"],
        derived_subject_rules=[
            {"role": "dependency.dc", "source": "catalog", "key": "domain_controllers"},
            {"role": "dependency.dns", "source": "catalog", "key": "dns_servers"},
        ],
        probe_plan={
            "tier0": [
                "identity.user_core",
                "authz.user_groups_core",
                "authz.user_licenses_core",
                "authz.signin_summary_24h",
                "authz.ca_block_summary_24h",
                "connectivity.probe_dns_resolve_device",
                "connectivity.probe_ping_device",
            ],
            "tier1": [
                "identity.dc_record",
                "health.dcdiag_quick",
                "health.replication_summary",
                "health.replication_partners",
                "health.time_sync",
                "connectivity.port_probe_dc",
            ],
            "tier2": [],
        },
        expected_root_causes=["conditional_access", "account_disabled", "dns_failure", "replication_lag"],
        snapshot_profiles={"tier0": "core", "tier1": "troubleshoot", "tier2": "deep"},
    ),
    "resource.file_access_denied": SymptomTemplate(
        symptom_id="resource.file_access_denied",
        display_name="File access denied",
        category="resource",
        intent_labels=["file", "share", "smb", "access denied"],
        default_subject_roles=["actor.user", "actor.device", "dependency.file_server", "dependency.dns", "dependency.dc"],
        derived_subject_rules=[
            {"role": "dependency.file_server", "source": "catalog", "key": "file_servers"},
            {"role": "dependency.dns", "source": "catalog", "key": "dns_servers"},
            {"role": "dependency.dc", "source": "catalog", "key": "domain_controllers"},
        ],
        probe_plan={
            "tier0": [
                "identity.user_core",
                "authz.user_groups_core",
                "authz.user_licenses_core",
                "connectivity.probe_dns_resolve_device",
                "connectivity.probe_ping_device",
                "connectivity.probe_ports_device",
                "connectivity.port_probe_file_server",
                "health.smb_sessions_summary",
            ],
            "tier1": [
                "health.smb_openfiles_summary",
                "resource.share_reachability",
            ],
            "tier2": [],
        },
        expected_root_causes=["missing_acl", "smb_auth_failure", "dns_failure", "network_block"],
        snapshot_profiles={"tier0": "core", "tier1": "troubleshoot", "tier2": "deep"},
    ),
    "resource.print_failure": SymptomTemplate(
        symptom_id="resource.print_failure",
        display_name="Printing failure",
        category="resource",
        intent_labels=["print", "printer", "spooler", "queue"],
        default_subject_roles=["actor.user", "actor.device", "dependency.print_server", "dependency.dc"],
        derived_subject_rules=[
            {"role": "dependency.print_server", "source": "catalog", "key": "print_servers"},
            {"role": "dependency.dc", "source": "catalog", "key": "domain_controllers"},
        ],
        probe_plan={
            "tier0": [
                "resource.printers_summary",
                "resource.print_queue_summary",
                "health.print_spooler_status",
                "resource.gpo_mapping_summary",
                "connectivity.probe_ping_device",
            ],
            "tier1": [
                "identity.dc_record",
                "health.dcdiag_quick",
                "connectivity.port_probe_dc",
            ],
            "tier2": [],
        },
        expected_root_causes=["spooler_down", "printer_offline", "gpo_conflict", "driver_issue"],
        snapshot_profiles={"tier0": "core", "tier1": "troubleshoot", "tier2": "deep"},
    ),
    "cloud.storage_sync_failure": SymptomTemplate(
        symptom_id="cloud.storage_sync_failure",
        display_name="Cloud storage sync failure",
        category="cloud",
        intent_labels=["onedrive", "sharepoint", "sync", "storage"],
        default_subject_roles=["actor.user", "actor.device", "dependency.dns"],
        derived_subject_rules=[
            {"role": "dependency.dns", "source": "catalog", "key": "dns_servers"},
        ],
        probe_plan={
            "tier0": [
                "identity.user_core",
                "authz.user_licenses_core",
                "authz.signin_summary_24h",
                "authz.ca_block_summary_24h",
                "connectivity.dns_resolve_external",
                "connectivity.port_probe_external",
            ],
            "tier1": [
                "connectivity.probe_ping_device",
                "connectivity.probe_ports_device",
            ],
            "tier2": [],
        },
        expected_root_causes=["license_missing", "conditional_access", "network_block"],
        snapshot_profiles={"tier0": "core", "tier1": "troubleshoot", "tier2": "deep"},
    ),
    "device.performance_issue": SymptomTemplate(
        symptom_id="device.performance_issue",
        display_name="Device performance issue",
        category="device",
        intent_labels=["slow", "cpu", "memory", "performance"],
        default_subject_roles=["actor.device"],
        derived_subject_rules=[],
        probe_plan={
            "tier0": [
                "connectivity.probe_ping_device",
                "connectivity.probe_ports_device",
            ],
            "tier1": [],
            "tier2": [],
        },
        expected_root_causes=["resource_exhaustion", "network_latency"],
        snapshot_profiles={"tier0": "core", "tier1": "troubleshoot", "tier2": "deep"},
    ),
    "auth.account_lockout": SymptomTemplate(
        symptom_id="auth.account_lockout",
        display_name="Account lockout",
        category="auth",
        intent_labels=["lockout", "password", "auth"],
        default_subject_roles=["actor.user", "dependency.dc", "dependency.dns"],
        derived_subject_rules=[
            {"role": "dependency.dc", "source": "catalog", "key": "domain_controllers"},
            {"role": "dependency.dns", "source": "catalog", "key": "dns_servers"},
        ],
        probe_plan={
            "tier0": [
                "identity.user_core",
                "authz.signin_summary_24h",
                "authz.ca_block_summary_24h",
            ],
            "tier1": [
                "health.dcdiag_quick",
                "health.replication_summary",
                "health.time_sync",
            ],
            "tier2": [],
        },
        expected_root_causes=["bad_password", "stale_creds", "replication_lag"],
        snapshot_profiles={"tier0": "core", "tier1": "troubleshoot", "tier2": "deep"},
    ),
}


def list_symptom_templates() -> List[Dict[str, object]]:
    return [template.model_dump() for template in SYMPTOM_TEMPLATES.values()]


def get_symptom_template(symptom_id: str) -> Optional[Dict[str, object]]:
    if not symptom_id:
        return None
    template = SYMPTOM_TEMPLATES.get(symptom_id)
    return template.model_dump() if template else None
