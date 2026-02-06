# CAPABILITIES_POWERPLATFORM.md
## Graph Admin Studio — Power Platform Module (Ruthless Spec)

### North Star
Power Platform must surface **governance risk**:
- rogue flows
- risky connectors
- environment sprawl

---

## 1) Permissions
Power Platform Admin API:
- Environment.Read.All
- Flow.Read.All

---

## 2) Context Keys
- context.environment_id
- context.flow_id

---

## 3) Capability Map

### 3.1 Environments
Discover:
- powerplatform.list_environments

---

### 3.2 Flows
Inspect:
- powerplatform.list_flows
- powerplatform.get_flow_details

Audit:
- powerplatform.flow_risk_summary

---

## 4) Testing
- Environments list bounded
- Flow inventory normalized

