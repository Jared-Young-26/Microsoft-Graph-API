from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json
import os
import time
import urllib.error
import urllib.request

from ..token_store import AgentTokenStore
from .interface import ActionDefinition, ActionResult
from .manifest import load_manifest_for_plugin


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_get_json(url: str, *, timeout: int = 10) -> tuple[int | None, Any | None, int | None]:
    started = time.time()
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"}, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8") if resp else ""
            elapsed_ms = int((time.time() - started) * 1000)
            try:
                return resp.status, json.loads(raw) if raw else None, elapsed_ms
            except Exception:
                return resp.status, {"raw": raw}, elapsed_ms
    except urllib.error.HTTPError as exc:
        elapsed_ms = int((time.time() - started) * 1000)
        return int(exc.code), None, elapsed_ms
    except Exception:
        elapsed_ms = int((time.time() - started) * 1000)
        return None, None, elapsed_ms


@dataclass
class RunnerCorePlugin:
    """Core runner utilities (connectivity, diagnostics)."""

    id: str = "runner_core"

    def capabilities(self) -> list[str]:
        return ["runner.connectivity_test"]

    def actions(self) -> list[ActionDefinition]:
        manifest_actions = load_manifest_for_plugin(self.id)
        if manifest_actions:
            return manifest_actions
        return [
            ActionDefinition(
                action_id="runner.connectivity_test",
                title="Connectivity test",
                description="Verify the runner can reach the control plane and upload artifacts.",
                required_capabilities=["runner.connectivity_test"],
                risk_level="safe",
            )
        ]

    def handle(self, action_id: str, params: dict | None) -> ActionResult:
        params = params or {}
        if action_id != "runner.connectivity_test":
            return ActionResult(ok=False, stderr=f"Unknown action_id: {action_id}", exit_code=2)

        store = AgentTokenStore()
        state_dir = store.state_dir
        evidence_dir = state_dir / "evidence"
        evidence_dir.mkdir(parents=True, exist_ok=True)

        control_plane_url = os.environ.get("CONTROL_PLANE_URL") or ""
        catalog_url = ""
        if control_plane_url:
            base = control_plane_url.rstrip("/")
            catalog_url = f"{base}/api/capabilities/catalog"

        status_code, catalog_data, elapsed_ms = (None, None, None)
        if catalog_url:
            status_code, catalog_data, elapsed_ms = _safe_get_json(catalog_url, timeout=10)

        report: dict[str, Any] = {
            "generated_at": _now_iso(),
            "state_dir": str(state_dir),
            "control_plane_url": control_plane_url or None,
            "capabilities_catalog": {
                "url": catalog_url or None,
                "status_code": status_code,
                "elapsed_ms": elapsed_ms,
                "ok": bool(status_code and 200 <= int(status_code) < 400),
            },
            "token_store": {
                "agent_id_path": str(store.agent_id_path),
                "token_path": str(store.token_path),
                "agent_id_present": bool(store.read_agent_id()),
                "token_present": bool(store.read_token()),
            },
        }

        out_path = evidence_dir / f"connectivity-{int(time.time())}.json"
        try:
            out_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
        except Exception as exc:
            return ActionResult(ok=False, stderr=str(exc), exit_code=1)

        # Return the report + an artifact; the agent runtime will attempt to upload it.
        # The job will fail if artifact upload fails, proving connectivity/auth issues.
        return ActionResult(
            ok=True,
            result={"report": report, "note": "Artifact upload performed by runtime after action completes."},
            artifacts=[out_path],
        )

