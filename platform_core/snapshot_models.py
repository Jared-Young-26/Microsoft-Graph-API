from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field, model_serializer, model_validator

SCHEMA_VERSION = "v1"
SNAPSHOT_SCHEMA = f"gas.snapshot.{SCHEMA_VERSION}"
EVENT_SCHEMA = f"gas.event.{SCHEMA_VERSION}"
EVIDENCE_SCHEMA = f"gas.evidence.{SCHEMA_VERSION}"
PROBE_SCHEMA = f"gas.probe.{SCHEMA_VERSION}"
INCIDENT_SCHEMA = f"gas.incident.{SCHEMA_VERSION}"
REPORT_SCHEMA = f"gas.report.{SCHEMA_VERSION}"


class SchemaModel(BaseModel):
    """Schema Model."""
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str

    @model_validator(mode="before")
    @classmethod
    def _coerce_schema(cls, values):
        """Internal helper for coerce schema."""
        if isinstance(values, dict) and "schema" in values and "schema_id" not in values:
            values = dict(values)
            values["schema_id"] = values.pop("schema")
        return values

    @model_serializer(mode="wrap")
    def _serialize_schema(self, serializer):
        """Internal helper for serialize schema."""
        data = serializer(self)
        if "schema_id" in data:
            data["schema"] = data.pop("schema_id")
        return data


class Alias(BaseModel):
    """Alias."""
    model_config = ConfigDict(extra="allow")

    type: str
    value: str
    confidence: Optional[float] = None


class Subject(BaseModel):
    """Subject."""
    model_config = ConfigDict(extra="allow")

    subject_type: str
    kind: str
    canonical_id: str
    display_name: Optional[str] = None
    aliases: List[Alias] = Field(default_factory=list)


class SubjectRef(BaseModel):
    """Subject Ref."""
    model_config = ConfigDict(extra="allow")

    subject_type: str
    kind: str
    canonical_id: str
    display_name: Optional[str] = None


class ProbeResult(SchemaModel):
    """Probe Result."""
    schema_id: str = Field(PROBE_SCHEMA)
    probe: str
    ok: bool
    severity: str = "info"
    error_class: Optional[str] = None
    duration_ms: Optional[int] = None
    collected_at: str
    data: Any = None
    evidence_refs: List[str] = Field(default_factory=list)
    meta: Dict[str, Any] = Field(default_factory=dict)


class Snapshot(SchemaModel):
    """Snapshot."""
    schema_id: str = Field(SNAPSHOT_SCHEMA)
    snapshot_id: str
    captured_at: str
    profile: str
    scope: Dict[str, Any] = Field(default_factory=dict)
    subject: Subject
    lens: Dict[str, Any] = Field(default_factory=dict)
    relationships: List[Dict[str, Any]] = Field(default_factory=list)
    quality: Dict[str, Any] = Field(default_factory=dict)
    evidence_refs: List[str] = Field(default_factory=list)


class Event(SchemaModel):
    """Event."""
    schema_id: str = Field(EVENT_SCHEMA)
    event_id: str
    emitted_at: str
    snapshot_id: str
    subject_refs: List[SubjectRef] = Field(default_factory=list)
    meta: Dict[str, Any] = Field(default_factory=dict)


class Evidence(SchemaModel):
    """Evidence."""
    schema_id: str = Field(EVIDENCE_SCHEMA)
    evidence_id: str
    captured_at: str
    kind: str
    description: Optional[str] = None
    location: Optional[str] = None
    redaction: Dict[str, Any] = Field(default_factory=dict)
    meta: Dict[str, Any] = Field(default_factory=dict)


class IncidentSubject(BaseModel):
    """Incident Subject."""
    model_config = ConfigDict(extra="allow")

    canonical_id: str
    role: str
    kind: str


class Incident(SchemaModel):
    """Incident."""
    schema_id: str = Field(INCIDENT_SCHEMA)
    incident_id: str
    created_at: str
    symptom_id: Optional[str] = None
    status: str = "open"
    title: Optional[str] = None
    description: Optional[str] = None
    time_window_start: Optional[str] = None
    time_window_end: Optional[str] = None
    subjects: List[IncidentSubject] = Field(default_factory=list)


class IncidentReport(SchemaModel):
    """Incident Report."""
    schema_id: str = Field(REPORT_SCHEMA)
    incident_id: str
    title: str
    customer: Optional[str] = None
    reported_by: Optional[str] = None
    severity: Optional[str] = None
    status: str = "open"
    reported_at: Optional[str] = None
    resolved_at: Optional[str] = None
    summary_reported: Optional[str] = None
    summary_actual: Optional[str] = None
    root_cause: Optional[str] = None
    resolution: Optional[str] = None
    preventive_actions: Optional[str] = None
    validation: Optional[str] = None
    affected: Optional[str] = None
    impact_window: Dict[str, Optional[str]] = Field(default_factory=dict)
    timeline: List[Dict[str, Any]] = Field(default_factory=list)
    evidence_refs: List[Dict[str, Any]] = Field(default_factory=list)
    attachments: List[Dict[str, Any]] = Field(default_factory=list)
    template_id: Optional[str] = None
