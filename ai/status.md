# Project Status

## Current milestone
Boot-contract safety net is complete and verified; the next prepared workstream is the first bounded `admin_gui/app.js` extraction slice (boot/preflight layer).

## Current active workstream
Prepared (not started): extract boot/preflight logic from `admin_gui/app.js` into `admin_gui/app_boot.js` while preserving script-order and runtime contracts.

## Recently completed
- 2026-05-19 19:45 EDT: installed `requirements.txt` into the `python3` environment used by `scripts/validate.sh`; `npm run validate` now passes with `failures=0 skipped=0`, including the 24-test backend hardening subset.
- 2026-05-19 EDT: landed the boot-contract safety-net stack in reviewable commits. `node admin_gui/boot_contract.test.js` passed, and `npm run validate` passed with `failures=0 skipped=1`; backend validation skipped because this environment is missing `flask`.
- 2026-03-12 20:02 EDT: nightly repo triage reran `npm run validate`; canonical validation remained green (`failures=0`, `skipped=0`), confirmed `admin_gui/app_boot.js` is still absent (prepared extraction not started), and found no new backlog-worthy risk.
- 2026-03-12 09:01 EDT: `prepare-next-task` reran and reconfirmed the highest-value next thread is the bounded boot/preflight extraction into `admin_gui/app_boot.js`; refreshed `/ai/active_task.md`, `/ai/task_breakdown.md`, and `/ai/status.md`.
- 2026-03-11 20:01 EDT: nightly repo triage reran `npm run validate`; canonical validation remained green (`failures=0`, `skipped=0`).
- 2026-03-11: `prepare-next-task` selected the next concrete thread as the first bounded `app.js` extraction slice (`app_boot.js`) and synced `/ai/active_task.md`, `/ai/task_breakdown.md`, and `/ai/status.md`.
- 2026-03-10: added `admin_gui/boot_contract.test.js` to guard `index.html` script order, required service-shell templates/mounts, schema-to-DOM alignment, and rendered service-shell validity; wired it into `npm run validate`.
- 2026-03-10 20:02 EDT: nightly repo triage reran `npm run validate` and reconfirmed canonical validation stays green (`failures=0`, `skipped=0`).
- 2026-03-08: added canonical validation entrypoints via `scripts/validate.sh` and `npm run validate` (`validate:frontend` / `validate:backend`), documented in `README.md`.
- 2026-03-07: operator-auth boundary, frontend allowlist, cache-busting parity, and persistence-security hardening threads all landed with focused regression coverage.

## Current blockers
- No repo-state blocker is known.
- Playwright remains unavailable in this workspace (`PLAYWRIGHT_MISSING`), but the next prepared task does not require browser automation.

## Next recommended tasks
- Implement the prepared boot/preflight extraction thread (`admin_gui/app_boot.js`) and keep `boot_contract.test.js` plus `npm run validate` green.
- After this first slice lands, choose the next bounded `app.js` extraction target (for example registry/state helpers) before attempting broader file splits.
- Re-evaluate whether `json_inspector.js` / `help_parser.js` single-source-of-truth cleanup should follow immediately or after one more `app.js` slice.

## Docs that may need refresh
- `ai/handoff.md` after the extraction thread completes or pauses.
- `ai/architecture.md` and `ai/repo_map.md` once the new boot module is actually added.

## Notes
- `ai/risk_register.md` currently lists known risks (`RISK-001` to `RISK-005`) as mitigated.
- The next primary maintainability risk remains `admin_gui/app.js` size/coupling.
