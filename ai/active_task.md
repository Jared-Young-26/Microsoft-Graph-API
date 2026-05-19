# Active Task

## Title
Start bounded `admin_gui/app.js` modularization by extracting boot/preflight logic into `admin_gui/app_boot.js`

## Goal
Reduce `admin_gui/app.js` coupling and blast radius by moving the boot-contract loading/validation layer into one dedicated module while preserving all existing runtime behavior.

## Status
Prepared on 2026-03-11; refreshed by automation on 2026-03-12. Not started.

## Why This Task Now
- The cross-file boot contract safety net is complete and green, so the highest-value remaining `P1` is the first bounded `app.js` split.
- `admin_gui/app.js` remains the primary maintainability risk due to size and mixed responsibilities.
- The boot/preflight slice is lower ambiguity than broader extractions because its invariants are explicit and already test-covered.
- This thread fits one focused implementation pass without requiring new architecture decisions.

## In Scope
- Add `admin_gui/app_boot.js` to own:
  - portal schema load/minimal validation
  - service-shell API load/minimal validation
  - persistence security helper load/validation
  - boot-failure rendering helper used during preflight
- Keep `admin_gui/app.js` behavior intact by consuming the extracted boot API instead of duplicating preflight logic.
- Update shell boot wiring and contract tests for the new script/module boundary.
- Keep canonical validation green.

## Out of Scope
- broader `app.js` modularization beyond boot/preflight
- DOM, selector, workspace-block, or API contract changes
- backend feature changes unrelated to serving the new frontend asset
- frontend redesign or framework changes

## Invariants
- Preserve script boot order semantics and execution timing (no `DOMContentLoaded` behavior change).
- Preserve stable IDs, selectors, data attributes, and request shapes.
- Preserve `window.GraphAdminPortalSchema`, `window.GraphAdminServiceShells`, and persistence-security contract behavior.
- Keep Flask/FastAPI frontend shell serving parity.

## Deliverables
- New `admin_gui/app_boot.js` containing boot/preflight responsibilities currently at the top of `app.js`.
- `admin_gui/app.js` updated to consume extracted boot/preflight exports with no user-visible behavior change.
- Boot-asset serving and boot-contract tests updated to include the new asset and expected load order.
- `/ai` docs refreshed after implementation.

## Validation
- `node admin_gui/boot_contract.test.js`
- `npm run validate`

## Prerequisites
- Existing frontend/backend validation baseline remains green (`npm run validate`).
- No new architecture decision required before this extraction slice.

## Done
- Boot/preflight logic no longer lives directly in `admin_gui/app.js`.
- Boot contract tests and canonical validation remain green without weakening assertions.
- Shell-serving version-token logic covers the new frontend asset in both Flask and FastAPI paths.
