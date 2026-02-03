# Core Concepts

## Task Runner

The Task Runner executes a single action against a service:

- **Sequential execution** per action.
- **Cancel** stops the current request.
- Outputs are always structured JSON first.

### Output formats

- **Raw**: the JSON response
- **Pretty**: structured cards
- **Table**: rows/columns
- **Explain**: failure triage and recommendations
- **Graph**: topology or relationship visualization (when available)

## Output Viewer

Use the Output panel to:

- Search results
- Export incident bundles
- Save snapshots
- Inspect “Idle” status when nothing has run

## Snapshots

Snapshots capture a **state** of a subject (user, device, server, resource) at a point in time.

### Capture

- Use **Snapshot Capture** in Act
- Or auto-capture from Incident Intake or Action Packs

### Compare

- Compare two snapshots to see changes
- Use Diff + Triage view to prioritize impact

## Baselines

Golden baselines capture known-good state.

- Create from any snapshot
- Compare current vs golden
- Useful for “what changed since last week?”

## Incidents

Incidents combine:

- Intake (user/device/symptom)
- Snapshots
- Event timeline
- Evidence bundles

## Audit Log

Every action, update, or snapshot can be recorded:

- Who ran it
- When it ran
- What changed

Use this for accountability and ticket updates.
