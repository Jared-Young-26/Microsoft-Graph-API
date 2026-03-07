# Current Plan

## Active Objective
Harden the backend trust boundary in focused steps: close browser file exposure first, then add operator auth, then return to backend asset-delivery parity work from a safer baseline.

## Guardrails

- Keep the UI in vanilla HTML/CSS/JS.
- Preserve current route names, payload shapes, boot asset filenames, and deep-link URLs unless a documented security fix requires otherwise.
- Keep agent token auth and job flows stable.
- Preserve `/help`, `/investigations`, and `/workspaces` SPA fallback behavior.
- Do not expose `admin_gui/backend/` runtime state through browser-serving paths.
- Keep Flask and FastAPI behavior aligned wherever the hardening change applies.

## Sequence

1. Reconfirm the exact browser-served file set, supported deep links, and representative deny cases in both backend transports, including any `/static/*` browser dependency on FastAPI.
2. Replace raw `admin_gui/` file fallback and any equivalent FastAPI `/static` exposure with an explicit allowlist for frontend assets and help/install files.
3. Add focused backend regression tests for allowed assets/deep links and blocked backend-file access, including `/static/backend/...` deny probes on FastAPI.
4. Re-run a deep-link smoke check of the main SPA entrypoints and update `/ai` docs with the final allowlist assumptions.
5. Implement the smallest shared server-side operator guard that removes the current UI-only trust assumption.
6. Bring FastAPI boot-asset versioning to parity with Flask once the serving boundary is explicit.
