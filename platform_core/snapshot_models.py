from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field, model_serializer, model_validator

SCHEMA_VERSION = "v1"
SNAPSHOT_SCHEMA = f"gas.snapshot.{SCHEMA_VERSION}"
EVENT_SCHEMA = f"gas.event.{SCHEMA_VERSION}"
EVIDENCE_SCHEMA = f"gas.evidence.{SCHEMA_VERSION}"
PROBE_SCHEMA = f"gas.probe.{SCHEMA_VERSION}"
INCIDENT_SCHEMA = f"gas.incident.{SCHEMA_VERSION}"


class SchemaModel(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str

    @model_validator(mode="before")
    @classmethod
    def _coerce_schema(cls, values):
        if isinstance(values, dict) and "schema" in values and "schema_id" not in values:
            values = dict(values)
            values["schema_id"] = values.pop("schema")
        return values

    @model_serializer(mode="wrap")
    def _serialize_schema(self, serializer):
        data = serializer(self)
        if "schema_id" in data:
            data["schema"] = data.pop("schema_id")
        return data


class Alias(BaseModel):
    model_config = ConfigDict(extra="allow")

    type: str
    value: str
    confidence: Optional[float] = None


class Subject(BaseModel):
    model_config = ConfigDict(extra="allow")

    subject_type: str
    kind: str
    canonical_id: str
    display_name: Optional[str] = None
    aliases: List[Alias] = Field(default_factory=list)


class SubjectRef(BaseModel):
    model_config = ConfigDict(extra="allow")

    subject_type: str
    kind: str
    canonical_id: str
    display_name: Optional[str] = None


class ProbeResult(SchemaModel):
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
    schema_id: str = Field(EVENT_SCHEMA)
    event_id: str
    emitted_at: str
    snapshot_id: str
    subject_refs: List[SubjectRef] = Field(default_factory=list)
    meta: Dict[str, Any] = Field(default_factory=dict)


class Evidence(SchemaModel):
    schema_id: str = Field(EVIDENCE_SCHEMA)
    evidence_id: str
    captured_at: str
    kind: str
    description: Optional[str] = None
    location: Optional[str] = None
    redaction: Dict[str, Any] = Field(default_factory=dict)
    meta: Dict[str, Any] = Field(default_factory=dict)


class IncidentSubject(BaseModel):
    model_config = ConfigDict(extra="allow")

    canonical_id: str
    role: str
    kind: str


class Incident(SchemaModel):
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
