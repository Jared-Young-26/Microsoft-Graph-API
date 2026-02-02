from __future__ import annotations

from pathlib import Path
import json

FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures"


def load_fixture(probe_id: str):
    if not probe_id:
        return None
    filename = f"{probe_id}.json"
    path = FIXTURE_DIR / filename
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except Exception:
        return None
