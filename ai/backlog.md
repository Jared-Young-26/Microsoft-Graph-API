# Backlog

This file contains candidate work items.

## Prioritization Labels

- P0 -> critical / blocking
- P1 -> high value
- P2 -> useful
- P3 -> later / exploratory

## Template

### [P1] Example Task Title
- Goal:
- Why it matters:
- In scope:
- Out of scope:
- Dependencies:
- Risks:
- Done when:

## Prioritized Items

### [P0] Add server-side operator auth/authorization for human mutation routes
- Goal: stop relying on Observe-vs-Act UI metadata as the only boundary for config changes, task execution, pairing-code minting, job enqueue, and other human-triggered mutations.
- Why it matters: the current backend exposes mutating human/operator routes without a server-side operator guard, which makes the local listener itself the only trust boundary.
- In scope:
  - `admin_gui/backend/flask_app.py`
  - `admin_gui/backend/fastapi_app.py`
  - any shared auth helper that keeps the two transports aligned
  - focused backend tests for the chosen operator trust model
- Out of scope:
  - frontend redesign
  - broad identity platform work
  - changing agent token semantics unless separation from human auth requires it
- Dependencies:
  - `ai/reviews/security_report.md`
  - current backend route inventory
- Risks:
  - choosing an auth model that works in one backend but not the other
  - accidentally gating agent routes or breaking the local operator workflow
- Done when:
  - unauthenticated human mutation requests are rejected under the chosen trust model
  - both backend entrypoints enforce the same operator guard
  - focused regression tests cover the new behavior

### [P0] Restrict Flask and FastAPI browser-serving paths to an explicit frontend asset allowlist
- Goal: stop direct GET access to `admin_gui/backend` local state and any other non-frontend files under `admin_gui/`.
- Why it matters: both backend entrypoints currently serve arbitrary files from the `admin_gui/` tree, while config, SQLite DBs, and audit logs live under `admin_gui/backend/`.
- In scope:
  - `admin_gui/backend/flask_app.py`
  - `admin_gui/backend/fastapi_app.py`
  - targeted tests for allowlisted assets and blocked backend/state paths
- Out of scope:
  - moving the runtime state out of `admin_gui/backend/`
  - redesigning the help/install flows
- Dependencies:
  - current frontend asset list in `admin_gui/index.html`
  - current help/install/static paths
- Risks:
  - blocking legitimate assets or deep links by mistake
  - leaving Flask and FastAPI with different allowlists
- Done when:
  - requests such as `/backend/config.json` and `/backend/control_plane.sqlite` are denied
  - `/`, `/help`, `/help/*`, `/investigations`, and `/workspaces` still render correctly
  - the allowed browser-served file set is explicit and test-covered

### [P1] Bring FastAPI frontend asset serving to parity with Flask
- Goal: make both backend entrypoints serve the same frontend boot assets with the same cache-busting/versioning contract.
- Why it matters: the frontend now depends on boot-critical JS staying aligned, and FastAPI still serves raw files while Flask rewrites `index.html` with a shared `?v=` token.
- In scope:
  - `admin_gui/backend/flask_app.py`
  - `admin_gui/backend/fastapi_app.py`
  - focused frontend-serving tests if needed
- Out of scope:
  - feature changes
  - API contract changes unrelated to asset delivery
- Dependencies:
  - the static-file allowlist work, if it changes how frontend assets are served
- Risks:
  - stale cached JS causing false boot failures
  - backend parity drift between Flask and FastAPI
- Done when:
  - FastAPI and Flask serve the same boot asset set
  - `portal_schema.js`, `service_shells.js`, and `app.js` are covered by the same explicit versioning path

### [P1] Add cross-file boot contract tests for `index.html`, `portal_schema.js`, and `service_shells.js`
- Goal: fail fast when script order, service-shell mount points, or workspace block prerequisites drift.
- Why it matters: the frontend depends on exact cross-file alignment, not just per-file unit correctness.
- In scope:
  - direct Node tests under `admin_gui/`
  - script order
  - service-shell placeholder coverage
  - required template/mount/workspace-block contracts
- Out of scope:
  - visual redesign
  - backend task behavior
- Dependencies:
  - accurate repo map and architecture doc
- Risks:
  - tests that are too brittle on benign markup changes
- Done when:
  - a drift in script order or required service-shell structure breaks validation immediately

### [P1] Split `admin_gui/app.js` by bounded responsibility without changing DOM or API contracts
- Goal: reduce the blast radius of changes to the current frontend runtime.
- Why it matters: safe edits are getting harder because boot logic, registries, routing, rendering, and local persistence all live in one file.
- In scope:
  - extract bounded modules such as boot/helpers/registries
  - preserve current selectors, IDs, data attributes, and request shapes
- Out of scope:
  - framework rewrite
  - UI redesign
  - backend behavior changes
- Dependencies:
  - boot contract tests
- Risks:
  - accidental boot-order regressions
  - breaking stable DOM hooks or workspace IDs
- Done when:
  - targeted slices are moved out of `app.js`
  - the page still boots identically
  - existing tests still pass

### [P1] Make helper utilities single-source-of-truth instead of drifting copies
- Goal: stop `json_inspector.js` and `help_parser.js` from diverging from the live logic embedded in `app.js`.
- Why it matters: the repo currently contains standalone helper modules plus inlined runtime implementations for the same concerns.
- In scope:
  - `admin_gui/json_inspector.js`
  - `admin_gui/help_parser.js`
  - the matching `app.js` call sites
  - focused tests
- Out of scope:
  - changing help-center UX
  - changing JSON inspector features
- Dependencies:
  - `app.js` modularization plan
- Risks:
  - subtle UI regressions if behavior is not preserved exactly
- Done when:
  - one implementation path is clearly authoritative
  - tests cover the adopted contract

### [P2] Codify repeated validation commands into a lightweight dev workflow
- Goal: make validation repeatable without making contributors guess which direct `node` and `pytest` commands to run.
- Why it matters: the repo has test files, but no single wrapper script or documented validation entrypoint.
- In scope:
  - direct validation command docs or a small wrapper
  - frontend Node checks
  - backend/platform/agent pytest subsets
- Out of scope:
  - CI redesign
  - broad dependency changes
- Dependencies:
  - agreement on the canonical minimal test set
- Risks:
  - wrapper scripts that hide which tests actually run
- Done when:
  - a normal implementation thread has an obvious, repo-native validation path

### [P2] Protect bespoke surfaces from accidental service-shell generalization
- Goal: add guardrails around the panels that are intentionally hand-authored.
- Why it matters: `remote_workflows`, `ssh`, `topology`, `reports`, `actionpacks`, `investigations`, `settings`, `controlplane`, `workspaces`, and `help` carry workflow-specific structure that the triplet shell cannot represent cleanly.
- In scope:
  - docs/tests/comments that make the bespoke boundary explicit
  - targeted checks for panels that must stay custom
- Out of scope:
  - converting bespoke panels into generated shells
- Dependencies:
  - accurate architecture notes
- Risks:
  - over-constraining harmless cleanup work
- Done when:
  - future threads can tell immediately which surfaces are safe to template and which are not
