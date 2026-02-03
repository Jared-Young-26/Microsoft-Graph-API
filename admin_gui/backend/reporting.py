from __future__ import annotations

import os
import re
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List


try:
    from reportlab.lib.pagesizes import LETTER
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
except Exception:  # pragma: no cover - optional dependency
    LETTER = None
    getSampleStyleSheet = None
    SimpleDocTemplate = None
    Paragraph = None
    Spacer = None
    PageBreak = None


SECRET_PATTERN = re.compile(r"(?i)(password|secret|token|client_secret|access_key)[\\s:=]+\\S+")
EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}")
IP_PATTERN = re.compile(r"\\b(\\d{1,3}\\.){3}\\d{1,3}\\b")
DOMAIN_PATTERN = re.compile(r"\\b[a-zA-Z0-9-]{2,}\\.[a-zA-Z]{2,}\\b")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def redact_text(text: str, mode: str = "internal") -> str:
    if not text:
        return text
    redacted = SECRET_PATTERN.sub("[redacted]", text)
    if mode == "client":
        redacted = EMAIL_PATTERN.sub("[redacted-email]", redacted)
        redacted = IP_PATTERN.sub("[redacted-ip]", redacted)
        redacted = DOMAIN_PATTERN.sub("[redacted-domain]", redacted)
    return redacted


def redact_payload(payload: Any, mode: str = "internal", depth: int = 0) -> Any:
    if payload is None:
        return payload
    if depth > 6:
        return "[truncated]"
    if isinstance(payload, list):
        return [redact_payload(item, mode, depth + 1) for item in payload]
    if isinstance(payload, dict):
        sanitized = {}
        for key, value in payload.items():
            if SECRET_PATTERN.search(str(key)):
                sanitized[key] = "[redacted]"
            else:
                sanitized[key] = redact_payload(value, mode, depth + 1)
        return sanitized
    if isinstance(payload, str):
        return redact_text(payload, mode)
    return payload


class ReportRenderer:
    def __init__(self, report: Dict[str, Any]):
        self.report = report or {}

    def _summary_bullets(self) -> List[str]:
        summary = []
        reported = self.report.get("summary_reported")
        actual = self.report.get("summary_actual")
        root = self.report.get("root_cause")
        resolution = self.report.get("resolution")
        if reported:
            summary.append(f"Reported issue: {reported}")
        if actual:
            summary.append(f"Actual finding: {actual}")
        if root:
            summary.append(f"Root cause: {root}")
        if resolution:
            summary.append(f"Resolution: {resolution}")
        return summary[:6]

    def _change_recovery_block(self) -> List[str]:
        evidence = self.report.get("evidence_refs") or []
        has_diff = any(ref.get("type") == "diff" for ref in evidence)
        has_revert = any(
            ref.get("type") == "action_pack_run"
            and ("revert" in (ref.get("label") or "").lower() or "rollback" in (ref.get("label") or "").lower())
            for ref in evidence
        )
        if not (has_diff and has_revert):
            return []
        return [
            "## Configuration Change & Recovery",
            "A configuration change was identified via snapshot diffing and subsequently reverted.",
            "Evidence in this report documents the change, the rollback action, and validation steps.",
            "",
        ]

    def _timeline_lines(self) -> List[str]:
        lines = []
        for entry in self.report.get("timeline") or []:
            ts = entry.get("timestamp") or ""
            label = entry.get("label") or entry.get("summary") or "Timeline entry"
            lines.append(f"- {ts} — {label}".strip())
        return lines

    def _evidence_lines(self) -> List[str]:
        lines = []
        for ref in self.report.get("evidence_refs") or []:
            label = ref.get("label") or ref.get("id") or ref.get("type")
            summary = ref.get("summary") or ""
            lines.append(f"- {label} {f'({summary})' if summary else ''}".strip())
        return lines

    def render_markdown(self, redaction: str = "internal") -> str:
        report = redact_payload(self.report, redaction)
        title = report.get("title") or "Incident report"
        incident_id = report.get("incident_id") or ""
        status = report.get("status") or "open"
        severity = report.get("severity") or ""
        reported_at = report.get("reported_at") or ""
        resolved_at = report.get("resolved_at") or ""
        customer = report.get("customer") or ""
        reported_by = report.get("reported_by") or ""
        impact_start = report.get("impact_window", {}).get("start") or ""
        impact_end = report.get("impact_window", {}).get("end") or ""

        lines = [
            f"# {title}",
            f"**Incident ID:** {incident_id}",
            f"**Status:** {status}",
            f"**Severity:** {severity}",
            f"**Client:** {customer}",
            f"**Reported by:** {reported_by}",
            f"**Reported at:** {reported_at}",
            f"**Resolved at:** {resolved_at}",
            f"**Impact window:** {impact_start} → {impact_end}",
            "",
            "## Executive Summary",
        ]
        bullets = self._summary_bullets()
        if not bullets:
            lines.append("- Summary pending.")
        else:
            lines.extend([f"- {item}" for item in bullets])

        lines.extend(
            [
                "",
                "## Reported Issue",
                report.get("summary_reported") or "Not provided.",
                "",
                "## Actual Findings",
                report.get("summary_actual") or "Not provided.",
                "",
                "## Root Cause Analysis",
                report.get("root_cause") or "Not provided.",
                "",
                "## Resolution Steps",
                report.get("resolution") or "Not provided.",
                "",
                "## Verification Performed",
                report.get("validation") or "Not provided.",
                "",
                "## Preventive Actions",
                report.get("preventive_actions") or "None noted.",
                "",
                "## Affected Users / Devices / Services",
                report.get("affected") or "Not provided.",
                "",
            ]
        )

        lines.extend(self._change_recovery_block())

        lines.append("## Timeline")
        timeline_lines = self._timeline_lines()
        lines.extend(timeline_lines if timeline_lines else ["- Timeline pending."])
        lines.append("")
        lines.append("## Evidence Appendix")
        evidence_lines = self._evidence_lines()
        lines.extend(evidence_lines if evidence_lines else ["- Evidence not attached."])
        attachments = report.get("attachments") or []
        if attachments:
            lines.append("")
            lines.append("## Attachments")
            for item in attachments:
                label = item.get("label") or item.get("name") or item.get("id") or "Attachment"
                lines.append(f"- {label}")
        lines.append("")
        lines.append(f"_Generated: {_now_iso()}_")
        return "\n".join(lines)

    def render_text(self, redaction: str = "internal") -> str:
        markdown = self.render_markdown(redaction)
        text = re.sub(r"[#*_`]", "", markdown)
        return text

    def render_pdf(self, redaction: str = "internal", artifact_dir: str | None = None) -> Dict[str, Any]:
        if SimpleDocTemplate is None:
            raise RuntimeError("PDF rendering requires reportlab.")
        artifact_dir = str(artifact_dir or ".")
        filename = f"incident-report-{self.report.get('incident_id') or uuid.uuid4().hex}.pdf"
        path = os.path.join(artifact_dir, filename)
        doc = SimpleDocTemplate(path, pagesize=LETTER)
        styles = getSampleStyleSheet()
        story = []
        markdown = self.render_markdown(redaction)
        for line in markdown.split("\n"):
            if line.startswith("# "):
                story.append(Paragraph(line.replace("# ", ""), styles["Title"]))
            elif line.startswith("## "):
                story.append(Spacer(1, 8))
                story.append(Paragraph(line.replace("## ", ""), styles["Heading2"]))
            elif line.startswith("- "):
                story.append(Paragraph(line, styles["Normal"]))
            elif line.startswith("_Generated"):
                story.append(Spacer(1, 12))
                story.append(Paragraph(line.replace("_", ""), styles["Italic"]))
            elif line.strip() == "":
                story.append(Spacer(1, 8))
            else:
                story.append(Paragraph(line, styles["Normal"]))
        doc.build(story)
        return {"name": filename, "path": path, "generated_at": _now_iso()}
