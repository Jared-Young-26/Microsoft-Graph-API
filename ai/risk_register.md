# Risk Register

Tracks known technical and security risks in the project.

Fields:
- ID
- Risk description
- Severity (P0–P3)
- Area
- Status
- Mitigation
- Owner
- Last reviewed

## RISK-001
Description: Static file exposure through Flask and FastAPI routes.
Severity: P0
Area: admin_gui backend
Status: In progress
Mitigation: Implement explicit allowlist for browser-served files.
Owner: implementation thread
Last reviewed: 2026-03-07

## RISK-002
Description: Operator authentication model undefined for admin interface.
Severity: P0
Area: authentication
Status: Open
Mitigation: Design operator authentication flow.
Owner: architecture thread
Last reviewed: 2026-03-07

## RISK-003
Description: Inconsistent cache-busting between Flask and FastAPI asset routes.
Severity: P2
Area: frontend asset delivery
Status: Open
Mitigation: Align cache strategy after auth model defined.
Owner: backlog
Last reviewed: 2026-03-07