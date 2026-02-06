# CAPABILITIES_DEFENDER.md
## Graph Admin Studio — Defender Module (Ruthless Spec)

### North Star
Defender must correlate:
- device risk
- identity risk
- security posture

---

## 1) Permissions
ARM REST:
- Security Reader

Graph (if licensed):
- SecurityEvents.Read.All

---

## 2) Context Keys
- context.device_id
- context.alert_id
- context.recommendation_id

---

## 3) Capability Map

### 3.1 Secure Score
Inspect:
- defender.secure_score_summary

### 3.2 Recommendations
Inspect:
- defender.recommendations_list

### 3.3 Alerts
Inspect:
- defender.alerts_list (bounded)

Evidence:
- defender.security_evidence_bundle

---

## 4) Testing
- Score and recs return for tenant

