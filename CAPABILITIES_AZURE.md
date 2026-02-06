# CAPABILITIES_AZURE.md
## Graph Admin Studio — Azure Module (Ruthless Spec)

### North Star
Azure must answer:
- What resources exist?
- What changed?
- Is security posture degrading?

---

## 1) Permissions
ARM REST:
- Reader (minimum)
- Security Reader (Defender)

PowerShell:
- Az.Accounts
- Az.Resources
- Az.Compute
- Az.Network

---

## 2) Context Keys
- context.subscription_id
- context.resource_group
- context.resource_id

---

## 3) Capability Map

### 3.1 Inventory (ARM REST)
Discover:
- azure.arm_list_subscriptions
- azure.arm_list_resource_groups
- azure.arm_list_vms
- azure.arm_list_vnets
- azure.arm_list_nsgs

---

### 3.2 Defender for Cloud
Inspect:
- defender.secure_score_summary
- defender.recommendations_list
- defender.alerts_list (if enabled)

Evidence:
- azure.security_posture_bundle

---

## 4) Testing
- ARM tokens acquired correctly
- Inventory bounded and cached

