from .frontend_allowlist import ROOT


VERSIONED_BOOT_ASSET_PATHS = (
    "styles.css",
    "portal_schema.js",
    "service_shells.js",
    "persistence_security.js",
    "triage.js",
    "investigation_summary.js",
    "next_steps.js",
    "app.js",
)


def render_index_html() -> str:
    """Render index.html with a shared cache-busting query string for boot assets."""

    index_path = ROOT / "index.html"
    html = index_path.read_text(encoding="utf-8")
    try:
        version = int(max((ROOT / asset_path).stat().st_mtime for asset_path in VERSIONED_BOOT_ASSET_PATHS))
    except Exception:
        version = int(index_path.stat().st_mtime)
    qs = f"?v={version}"
    for asset_path in VERSIONED_BOOT_ASSET_PATHS:
        attribute = "href" if asset_path.endswith(".css") else "src"
        html = html.replace(f'{attribute}="{asset_path}"', f'{attribute}="{asset_path}{qs}"')
    return html
