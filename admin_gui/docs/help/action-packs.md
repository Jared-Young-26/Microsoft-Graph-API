# Action Packs (Deep Dive)

Action packs are **sequential workflows** composed of multiple steps. Each step maps to a Graph or PowerShell action.

## How packs run

1. Inputs are collected in the runner.
2. Inputs are merged with step defaults.
3. Steps run **sequentially** (not parallel).
4. Failure prompts you to **continue or stop**.

## Preview plan

Preview plan shows the exact steps and parameters that would run.

## Dry-run vs Run pack

- **Preview plan**: shows the step list with resolved parameters.
- **Dry-run**: skips non-safe steps.
- **Run pack**: executes all included steps.

## Safety behavior

If a step fails:

- You are prompted to continue or stop
- The pack records the failure in history
- A bundle can be exported after completion

## Editing and cloning

- **Edit steps** opens the builder pre-filled
- **Save as copy** clones a pack
- **Version history** allows rollback

## Deleting and restoring

- Delete moves a pack to **Trash** (soft delete)
- Restore from Deleted packs
- Permanently delete when needed

## Scopes

- **Global**: visible across tenants
- **Current tenant**: scoped to the active tenant

## Offboard user workflow

Steps:

1. User audit snapshot
2. Disable on-prem account
3. Remove licenses
4. Remove group memberships

> [!TIP]
> Always run Preview plan first for complex packs.
