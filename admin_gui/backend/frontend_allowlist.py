from dataclasses import dataclass
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]

SPA_SHELL_PATHS = frozenset({
    "",
    "index.html",
    "help",
    "investigations",
    "workspaces",
})

BOOT_ASSET_PATHS = frozenset({
    "styles.css",
    "portal_schema.js",
    "service_shells.js",
    "persistence_security.js",
    "triage.js",
    "investigation_summary.js",
    "next_steps.js",
    "app.js",
})

HELP_MANIFEST_PATH = "docs/help/help_manifest.json"
HELP_DOCS_PREFIX = "docs/help/"
INSTALL_SCRIPT_PATH = "install/windows.ps1"


@dataclass(frozen=True)
class BrowserPathDecision:
    kind: str
    relative_path: str | None = None


def _normalize_browser_path(path: str | None) -> str | None:
    raw = str(path or "").split("?", 1)[0].split("#", 1)[0].replace("\\", "/").strip("/")
    if not raw:
        return ""
    normalized = PurePosixPath(raw)
    if normalized.is_absolute():
        return None
    if any(part in ("", ".", "..") for part in normalized.parts):
        return None
    return normalized.as_posix()


def classify_browser_path(path: str | None) -> BrowserPathDecision:
    normalized = _normalize_browser_path(path)
    if normalized is None:
        return BrowserPathDecision("deny")
    if normalized in SPA_SHELL_PATHS or normalized.startswith("help/"):
        return BrowserPathDecision("index")
    if normalized == "static" or normalized.startswith("static/"):
        return BrowserPathDecision("deny")
    if normalized in BOOT_ASSET_PATHS:
        return BrowserPathDecision("file", normalized)
    if normalized == HELP_MANIFEST_PATH:
        return BrowserPathDecision("file", normalized)
    if normalized.startswith(HELP_DOCS_PREFIX) and normalized.endswith(".md"):
        return BrowserPathDecision("file", normalized)
    if normalized == INSTALL_SCRIPT_PATH:
        return BrowserPathDecision("file", normalized)
    return BrowserPathDecision("deny")


def resolve_browser_file(path: str | None) -> Path | None:
    decision = classify_browser_path(path)
    if decision.kind != "file" or not decision.relative_path:
        return None
    candidate = ROOT / decision.relative_path
    if not candidate.is_file():
        return None
    return candidate
