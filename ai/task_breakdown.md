# Task Breakdown

## Objective
Execute one bounded first slice of `admin_gui/app.js` modularization by extracting boot/preflight logic into `admin_gui/app_boot.js` while preserving behavior and contracts.

## Prepared
- Originally prepared: 2026-03-11
- Automation refresh: 2026-03-12

## Why This Slice
- It directly targets the largest remaining maintainability risk (`app.js` size/coupling).
- It has explicit guardrails from `admin_gui/boot_contract.test.js`.
- It is small enough for one focused thread and unblocks later bounded extractions.

## Scope For This Thread
- `admin_gui/app_boot.js` (new): extracted boot/preflight functions and minimal validators.
- `admin_gui/app.js`: replace inline boot/preflight code with usage of extracted API.
- `admin_gui/index.html`: include `app_boot.js` in the boot sequence.
- `admin_gui/backend/frontend_shell.py`: add `app_boot.js` to shared version-token rewrite list.
- `admin_gui/boot_contract.test.js`: assert the updated script order contract.

## Out of Scope
- Any extraction beyond boot/preflight responsibilities.
- Refactoring business logic, action handlers, or rendering flows.
- Backend/API behavior changes beyond frontend asset serving parity.

## Execution Plan
1. Isolate current top-of-file boot/preflight functions in `admin_gui/app.js` and define the minimal public API for extraction.
2. Create `admin_gui/app_boot.js` with the extracted logic and stable global exposure pattern compatible with existing non-module script loading.
3. Update `admin_gui/index.html` and `admin_gui/backend/frontend_shell.py` so both transports serve/version the new asset consistently.
4. Update `admin_gui/app.js` to consume the extracted boot API and remove duplicated inline preflight logic.
5. Update `admin_gui/boot_contract.test.js` expected script order and rerun targeted + canonical validation.
6. Refresh `/ai` docs after implementation lands.

## Validation Plan
- Targeted: `node admin_gui/boot_contract.test.js`
- Canonical: `npm run validate`

## Risks To Watch
- Boot-order drift between `index.html`, `boot_contract.test.js`, and `frontend_shell.py`.
- Accidentally changing boot failure messaging/timing.
- Introducing a global-name mismatch between `app_boot.js` and `app.js`.

## Done Criteria
- Preflight logic is extracted into `admin_gui/app_boot.js` and consumed by `app.js`.
- Boot script contract assertions pass with the new explicit order.
- `npm run validate` remains green without reducing coverage.
- No selector, API, or auth-flow behavior changes are introduced.
