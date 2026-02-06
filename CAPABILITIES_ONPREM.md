# CAPABILITIES_ONPREM.md
## Graph Admin Studio — On-Prem / Hybrid Module (Ruthless Spec)

### North Star
On-prem tools must answer:
- Is the domain healthy?
- Why can’t users authenticate?
- Why can’t they print/access shares?

---

## 1) Requirements
- PowerShell 7
- RSAT
- Domain-joined host (or delegated creds)

---

## 2) Context Keys
- context.dc_name
- context.user
- context.computer
- context.gpo_id
- context.share_path

---

## 3) Capability Map

### 3.1 AD / DC Health
Inspect:
- onprem.list_domain_controllers
- onprem.fsmo_roles
- onprem.replication_summary
- onprem.dcdiag_summary
- onprem.time_sync_status

---

### 3.2 Users & Computers
Inspect:
- onprem.get_user
- onprem.get_computer
Change:
- onprem.reset_password (Dangerous)
- onprem.unlock_account (Caution)

---

### 3.3 GPO
Inspect:
- onprem.gpo_inventory
- onprem.gpo_links_by_ou
- onprem.gpo_diff

---

### 3.4 Printers & SMB
Inspect:
- onprem.list_printers
- onprem.printer_gpo_mapping
- onprem.list_shares
- onprem.smb_sessions

---

### 3.5 Evidence
- onprem.export_evtx
- onprem.export_registry
- onprem.snapshot_bundle

---

## 4) Testing
- Commands run on DC/member server
- Outputs normalized and exportable

