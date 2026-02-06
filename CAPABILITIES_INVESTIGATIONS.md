# Graph Admin Studio - Investigations (Explore -> Investigate -> Report) Ruthless Spec

## North Star
Investigations turn Graph Admin Studio from "a toolbox" into an operator cockpit.
They must eliminate copy/paste, preserve chain-of-custody evidence, and make troubleshooting feel like:

> Ask -> Probe -> Learn -> Correlate -> Act -> Prove

Exploration stays freeform.
Investigations add focus, memory, and evidence capture.
Reports become deliberate assembly from investigations.

---

## 0) Core Principles (Non-Negotiables)

### 0.1 Two Modes: Explore vs Investigate
- Explore Mode: stateless, ad-hoc, neutral sandbox.
- Investigation Mode: stateful, context-aware, evidence-first workflow.

The UI must make it obvious which mode the operator is in.

### 0.2 Zero copy/paste by design
- Any identifier discovered (UPN, device ID, drive ID, site ID, mailbox SMTP, etc.)
  must be promotable to context in one click.
- Any action form must auto-fill from active context when possible.

### 0.3 Timeline is the record of truth
- In Investigation Mode, every action run is a timeline event by default.
- Evidence is referenced, not embedded.
- Exports are audit-friendly (hashes, manifest).

### 0.4 Safe change workflow is integrated
- Caution/Dangerous actions must support:
  Plan -> (Dry-run) -> Execute -> Verify
- Typed confirmation for dangerous actions.
- Optional requirement: active incident/investigation ID for dangerous operations.

### 0.5 Local-first, privacy-first
- Everything runs on the admin host.
- No secrets/tokens stored in snapshots or exports.
- Screenshots/EVTX/REG evidence stored as evidence artifacts with retention controls and redaction metadata.

---

## 1) Investigation Data Model (Authoritative)

### 1.1 Investigation
Fields:
- investigation_id (UUID)
- title
- status (open | paused | resolved | archived)
- symptom_id (optional; links to symptom templates)
- created_at, updated_at
- tags[]
- owner (local operator identity)
- summary (editable markdown)
- root_cause_label (optional controlled vocabulary)
- resolution_label (fixed | not_fixed | unknown)
- time_window_start, time_window_end (optional)

### 1.2 Investigation Context (the "Context Bar")
A structured object stored per investigation:
- user: { upn, id }
- device: { name, managed_device_id, azure_ad_device_id, ip }
- mailbox: { smtp, object_id }
- onedrive: { drive_id, web_url }
- sharepoint: { site_id, site_url, list_id }
- teams: { team_id, channel_id }
- azure: { subscription_id, resource_group, resource_id }
- onprem: { dc_name, share_path, printer_name }
- notes: freeform key-value facts

Context can be partially populated. Every field is optional.

### 1.3 Investigation Timeline Events
Each timeline entry is immutable after creation (edits create a new revision entry).

Event fields:
- event_id (UUID)
- time (ISO)
- kind:
  - action_run
  - snapshot
  - evidence
  - note
  - inference
  - change
- action_id (if action_run)
- risk (safe/caution/dangerous)
- inputs_redacted
- outputs_ref (reference to stored result/snapshot/evidence)
- summary (short human readable)
- signals[] (optional)
- evidence_refs[] (optional)
- context_deltas (what context keys were updated by this event)

### 1.4 Evidence Artifacts
Evidence is stored separately and referenced by id:
- evidence_id
- kind (json | evtx | reg_export | hive | screenshot | bundle)
- sha256
- size
- created_at
- subject_refs[]
- redaction: { applied, methods[] }
- retention_policy

---

## 2) Core UX Surfaces

### 2.1 Investigation List
- Filter by status, tag, symptom, date range.
- Quick actions:
  - New Investigation
  - Create from Symptom Template
  - Export bundle
  - Archive

### 2.2 Investigation Workspace (Focused View)
Three-column cockpit layout:
- Left: Timeline (chronological; filter by kind/risk)
- Center: Output viewer (Raw/Pretty/Explain/Table) + "Attach" controls
- Right: Context Bar + "Facts" + "Suggested next actions"

### 2.3 Explore Mode (Neutral View)
- Task runners and tools remain available without forcing investigation creation.
- "Start investigation from this result" button creates a new investigation prefilled with detected context.

### 2.4 Reports (Assembly)
Reports are created from investigations:
- Select investigation(s)
- Select timeline entries/evidence to include
- Auto-generate narrative + allow edits
- Export

Reports do NOT share the same page as live execution/queues.

---

## 3) Auto-Capture & Context Binding

### 3.1 Auto-capture rules (Investigation Mode)
- Default: every action_run is captured as a timeline event.
- Captured items include:
  - action_id
  - redacted inputs
  - output reference
  - duration
  - failure_source/outcome if any

### 3.2 Context extraction (Promote-to-context)
After an action run:
- Parse output for known identifiers:
  - UPN/email
  - Entra object IDs
  - managedDeviceId / azureADDeviceId
  - driveId
  - siteId / siteUrl
  - mailbox SMTP
  - subscriptionId / resourceId
  - UNC paths, printer shares
- Present "Promote" buttons where applicable.
- Auto-promote safe obvious context changes (configurable).

### 3.3 Autofill action forms
Every action input schema may specify context_key.

When action form opens:
- If context_key is present -> prefill automatically.
- Allow override; show "prefilled" badge.

---

## 4) Investigation-Driven Automation

### 4.1 Symptom templates integration
When creating an investigation from a symptom:
- Run Tier-0 triage actions automatically.
- Update context as identifiers are discovered.
- Generate initial timeline entries.

### 4.2 Next Best Action (rules-based)
Based on signals in recent events:
- Recommend next probes/actions/packs.
- Provide one-click "Run next step" that uses current context.

### 4.3 Safe change integration
For Caution/Dangerous actions:
- Require plan + typed confirm.
- Auto-capture pre/post snapshots.
- Append verify event with diff summary.

---

## 5) Outputs & Exports

### 5.1 Investigation Bundle Export (ticket-ready)
ZIP includes:
- investigation metadata (JSON)
- timeline events (JSONL)
- selected outputs (JSON)
- snapshots (JSON)
- evidence manifest with hashes
- optional markdown summary (editable)
- retention/redaction notes

### 5.2 Chain-of-custody
Evidence files include:
- sha256 hash
- created_at
- tool version
- actor (local user)
- export timestamp

---

## 6) Replace/Deprecate Existing UI Elements (when ready)

### 6.1 Draft Snapshots
- Draft snapshots should be replaced by:
  - Investigation timeline pinning
  - "Attach last output" action
- Draft snapshot pages should be removed or marked legacy.

### 6.2 Reports page
- Reports should be an assembly surface, not a long scroll of unrelated tiles.
- Report queue and presets may remain but must be separated from live investigation workspace.

---

## 7) Implementation Order (Chunked Plan)
1) Investigation storage + CRUD + basic workspace shell
2) Timeline manual notes + attach last output
3) Auto-capture action runs + evidence refs
4) Context bar + promote-to-context
5) Autofill from context
6) Symptom template -> investigation bootstrapping
7) Suggested next actions
8) Export investigation bundle
9) Deprecate draft snapshots

---

## 8) Acceptance Criteria (Operator Reality Check)
Investigations are "done" when:
- You can run a real troubleshooting session without copying IDs manually.
- Every action you run in Investigation Mode is recorded automatically.
- You can reconstruct "what happened" from the timeline + evidence bundle.
- Reports can be generated from investigations without re-running actions.
- Explore Mode still works as a neutral sandbox.

---

## 9) Codex Execution Instructions
- Implement 1-2 features per chunk.
- Each chunk must include:
  - backend endpoints + storage
  - UI wiring
  - minimal tests
- Do not refactor unrelated modules while implementing investigations.

