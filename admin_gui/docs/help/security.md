# Security & Safety

## Least privilege guidance

Use only the permissions you need. Start with read-only scopes and add write scopes only when required.

## Where secrets are stored

- Secrets and tokens are stored **locally** in the environment config.
- Use keychain integration if available.
- Snapshots do **not** store secrets.

## Evidence bundle hygiene

Exports may contain sensitive identifiers:

- User IDs
- Group IDs
- Hostnames

Review exports before sharing.

## Operational guardrails

- Prefer **Preview plan** before Run pack
- Use Dry-run for first-time workflows
- Require second review for dangerous actions

> [!WARNING]
> Do not run destructive packs on production without previewing the plan and confirming inputs.
