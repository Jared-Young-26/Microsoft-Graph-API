# Handoff

## Objective
Prepare a resume-ready successor thread for the highest-value next task: close arbitrary browser file exposure by restricting Flask and FastAPI to an explicit frontend asset allowlist.

## Current Status
The active task, task breakdown, status, and current plan now all point at one thread-sized P0: static-file allowlisting in `admin_gui/backend/flask_app.py` and `admin_gui/backend/fastapi_app.py`. No product code was changed in this prep thread.

## Confirmed Facts
- Both backend entrypoints currently resolve arbitrary existing paths under `admin_gui/`.
- FastAPI also mounts `/static` to the full `admin_gui/` tree, so it currently has two browser file-serving surfaces over the same files.
- Local runtime state still lives under `admin_gui/backend/`, so raw browser path serving can expose config, SQLite DBs, logs, and source files.
- The next thread must preserve boot-critical asset names/order plus `/`, `/help`, `/help/*`, `/investigations`, and `/workspaces`.
- Operator auth is still a separate P0, but its trust model is not yet settled.
- FastAPI cache-busting parity with Flask is still pending and is intentionally sequenced after the allowlist thread.

## Ruled-Out Theories / Dead Ends
- Do not bundle operator auth into the next allowlist thread; that broadens scope and introduces an unresolved design choice.
- Do not move runtime state out of `admin_gui/backend/` as part of this pass; protect it in place.
- Do not treat this as a frontend refactor or boot-order cleanup thread.

## Files Changed Or Most Likely Involved
- Changed in this prep thread:
  - `ai/active_task.md`
  - `ai/task_breakdown.md`
  - `ai/status.md`
  - `ai/plans/current_plan.md`
  - `ai/handoff.md`
- Most likely involved next:
  - `admin_gui/backend/flask_app.py`
  - `admin_gui/backend/fastapi_app.py`
  - focused backend tests for allow/deny serving behavior
  - `admin_gui/index.html`
  - `admin_gui/docs/help/`
  - `admin_gui/install/windows.ps1`

## Validation Performed
- Doc consistency pass only: re-read `ai/active_task.md`, `ai/task_breakdown.md`, `ai/status.md`, `ai/plans/current_plan.md`, and `ai/handoff.md` after editing to confirm they agree on scope and sequencing.
- No product-code tests or runtime checks were run in this handoff/prep thread.

## Remaining Risks Or Unknowns
- The exact allowlist must be derived from the live browser surface; inventing extra public files would weaken the fix.
- If the implementation only patches the FastAPI catch-all route and leaves `/static` mounted to `ROOT`, the exposure remains.
- The final deny behavior and status codes for blocked paths still need to be chosen and test-covered.
- Operator auth remains unresolved after this thread and should follow immediately once file exposure is closed.

## Exact Next Step
Start an implementation thread in Worktree mode, read `ai/constraints.md`, `ai/active_task.md`, `ai/architecture.md`, `ai/repo_map.md`, `ai/reviews/security_report.md`, and this handoff, then enumerate the allowed browser asset/deep-link set from the live frontend and implement the same allowlist plus focused allow/deny tests in Flask, the FastAPI catch-all, and the FastAPI `/static` surface.

## Resume-Ready
Yes. The task is narrowed, the docs are aligned, and the next thread can start implementation directly without re-triaging scope.
