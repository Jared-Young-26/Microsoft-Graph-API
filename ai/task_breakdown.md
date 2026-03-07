# Task Breakdown

This file is the implementation task list for the current static-file allowlist thread.

## Objective

Replace the current arbitrary-file SPA/static fallback and FastAPI `/static` mount with an explicit, test-covered browser asset allowlist in both backend transports, without breaking the portal shell, supported deep links, or required help/install downloads.

## Scope

- Keep the vanilla HTML/CSS/JS frontend intact.
- Preserve current route names, payload shapes, boot asset names, deep-link URLs, and agent APIs.
- Keep Flask and FastAPI aligned on which browser paths are allowed, including any explicit static mount behavior.
- Treat `admin_gui/backend/` runtime state, config, DBs, logs, and non-frontend source files as denied by default.
- Do not solve operator auth in this thread unless a tiny shared helper overlap is unavoidable and documented separately.

## Explicit Deferrals

- Leave operator auth/authorization to its own follow-up architecture and implementation threads; the trust model is still unresolved.
- Leave FastAPI boot-asset cache-busting parity to a later thread once the file-serving boundary is explicit.
- Do not expand this thread into state relocation, frontend cleanup, or broader backend redesign.

## Implementation Sequence

1. Freeze the current browser-facing surface before editing.
   - Enumerate boot-critical assets referenced by `admin_gui/index.html`.
   - Enumerate browser entrypoints and support files that must remain reachable: `/`, `/help`, `/help/*`, `/investigations`, `/workspaces`, root boot assets, help docs/manifest, and install helpers.
   - Enumerate representative deny cases such as `backend/config.json`, `backend/control_plane.sqlite`, `backend/*.jsonl`, backend Python modules, and stray source files that are not meant to be browser assets.
   - Confirm whether any live browser path still depends on `/static/*`; if not, treat that mount as a pure exposure surface to remove or narrow.

2. Define one explicit allowlist model both transports can share.
   - Prefer a shared helper or clearly mirrored constant if that keeps Flask and FastAPI behavior identical.
   - Keep SPA deep-link routing explicit instead of falling through to arbitrary file-existence checks.
   - Model the boundary in path classes: SPA shell routes, allowlisted root assets, allowlisted help/install files, and denied backend/state/source paths.

3. Update Flask browser-serving behavior.
   - Allow the SPA shell plus allowlisted static/help/install assets only.
   - Return a deny response for backend/state/source paths instead of serving files directly.

4. Update FastAPI browser-serving behavior to the same allowlist.
   - Keep API routes and the SSH WebSocket path untouched.
   - Preserve current HTML-shell and deep-link behavior even if raw-file serving changes.
   - Remove or narrow the `/static` mount so it cannot bypass the same allowlist.

5. Add focused regression tests.
   - Cover allowed responses for representative assets and deep links.
   - Cover denied responses for backend state/config/db/log/source paths in both transports, including FastAPI `/static/backend/...` probes.
   - Keep the tests tight enough that benign markup changes do not create churn.

6. Validate with the smallest effective set.
   - Run the targeted backend tests added or updated for Flask and FastAPI static serving.
   - Smoke-check `/`, `/help`, `/investigations`, and `/workspaces` on one backend runtime if automated deep-link coverage remains partial.

7. Stop when the file-exposure boundary is closed in both transports.
   - Do not leave one backend still serving raw paths under `admin_gui/`.
   - Do not leave FastAPI's `/static` mount bypassing the new boundary.
   - Hand off operator auth and FastAPI cache-busting parity as separate follow-up work.

## Completion Criteria

- Both Flask and FastAPI serve only the explicit browser asset/deep-link set.
- Direct requests to representative backend config/db/log/source paths are denied, including FastAPI `/static/backend/...` paths.
- The main SPA shell plus `/help`, `/help/*`, `/investigations`, and `/workspaces` still load.
- Focused backend tests covering allow and deny behavior pass.
