# Decision Log

Append only when a durable design or workflow decision is made.

---

## Template

### YYYY-MM-DD — Decision title

**Context**
What problem or ambiguity existed?

**Decision**
What was chosen?

**Why**
Why was this preferable to the alternatives?

**Consequences**
What now becomes easier, harder, or constrained?

**Files affected**
List the major files, modules, or docs impacted.

### 2026-03-07 — Use AGENTS + durable memory + repo-local skills as the active Codex operating system

**Context**
The repo now contains a purpose-built Codex workflow kit (`AGENTS.md`, `/.agents/skills`, `.codex/config.toml`, and `/ai` templates/docs), while the old `/ai/prompts/*.md` files still exist as historical reference material.

**Decision**
Future Codex threads should use `AGENTS.md`, `/ai/*.md`, and `/.agents/skills/*` as the active operating system. The legacy `/ai/prompts/*.md` files remain reference-only and should not be pasted into new threads.

**Why**
This keeps repo context durable, reduces prompt churn between threads, and makes the source-of-truth order explicit when docs disagree.

**Consequences**
Doc-sync, handoff, and next-task prep become part of normal repo maintenance. Future threads should read `ai/constraints.md` and `ai/active_task.md` first instead of asking for restated context.

**Files affected**
`AGENTS.md`, `/.agents/skills/*`, `.codex/config.toml`, `/ai/*.md`, `/ai/prompts/*.md`

### 2026-03-07 — Use one explicit browser allowlist model across Flask and FastAPI file serving

**Context**
The current P0 hardening thread needs to close arbitrary browser file exposure in both backend entrypoints. Flask exposes browser files through its `/{path}` SPA fallback, while FastAPI exposes the same tree through both `/{path}` and `app.mount("/static", StaticFiles(directory=ROOT, html=True))`.

**Decision**
The implementation thread should define one explicit browser allowlist model that governs all browser file-serving surfaces. FastAPI's `/static` path should not remain a broad mount to `admin_gui/`; it must either be removed or narrowed so it cannot bypass the same allowlist enforced by the main fallback routes.

**Why**
Transport-specific heuristics would drift quickly and could leave FastAPI with a bypass even if the main catch-all route is fixed. One shared boundary keeps the trust model legible and testable.

**Consequences**
A small shared helper or mirrored constant is justified for the allowlist boundary. Focused regression tests need to probe both raw root paths and FastAPI `/static/...` paths. FastAPI cache-busting parity remains a separate follow-up once the file-serving boundary is explicit.

**Files affected**
`ai/active_task.md`, `ai/architecture.md`, `ai/repo_map.md`, `ai/task_breakdown.md`, `ai/plans/current_plan.md`, `ai/handoff.md`, `ai/status.md`, future `admin_gui/backend/flask_app.py`, future `admin_gui/backend/fastapi_app.py`
