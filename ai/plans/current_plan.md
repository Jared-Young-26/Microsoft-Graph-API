# Current Plan

## Active Objective
Keep post-hardening work on focused, reviewable threads: maintain doc accuracy, preserve validation hygiene, and execute the highest-value remaining `P1`/`P2` implementation tasks.

## Guardrails

- Keep the UI in vanilla HTML/CSS/JS.
- Preserve current route names, payload shapes, boot asset filenames, and deep-link URLs unless a documented security fix requires otherwise.
- Keep agent token auth and job flows stable.
- Preserve `/help`, `/investigations`, and `/workspaces` SPA fallback behavior.
- Do not expose `admin_gui/backend/` runtime state through browser-serving paths.
- Keep Flask and FastAPI behavior aligned wherever the hardening change applies.

## Sequence

1. Completed 2026-03-07: replace raw `admin_gui/` file fallback and the equivalent FastAPI `/static` exposure with an explicit allowlist for frontend assets and help/install files.
2. Completed 2026-03-07: add focused backend regression tests for allowed assets/deep links and blocked backend-file access, including `/static/backend/...` deny probes.
3. Completed 2026-03-07: choose a shared header-based operator token model for human privileged routes, with agent-token and terminal-session flows kept separate.
4. Completed 2026-03-07: implement that operator guard in Flask and FastAPI, plus the minimum frontend changes needed to send the operator token from memory only.
5. Completed 2026-03-07: remove `client_secret` and secret-like Action Pack inputs from frontend persistence.
6. Completed 2026-03-07: bring FastAPI boot-asset versioning to parity with Flask through the shared `frontend_shell.py` helper.
7. Completed 2026-03-07: replace the `service_shells.js` help-item `innerHTML` path with structured DOM/text rendering without changing the current presentation.
8. Completed 2026-03-08: codify canonical validation entrypoints through `scripts/validate.sh` and `npm run validate` (`validate:frontend`, `validate:backend`).
9. Completed 2026-03-10; validated for landing on 2026-05-19: added `P1` cross-file boot contract tests for `index.html`, `portal_schema.js`, and `service_shells.js`, and kept the canonical validation path aligned through `scripts/validate.sh`.
10. Next: start the bounded `admin_gui/app.js` split with the stronger boot regression coverage in place.
