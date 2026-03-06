import io
import json
import os
import platform
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock


class TestAgentChassis(unittest.TestCase):
    def test_config_env_overrides_file(self):
        from agent.config import load_agent_config

        with tempfile.TemporaryDirectory() as tmpdir:
            cfg_path = Path(tmpdir) / "config.json"
            cfg_path.write_text(
                json.dumps(
                    {
                        "control_plane_url": "http://file.example",
                        "agent_name": "from-file",
                        "tenant_id": "t-file",
                        "workspace_id": "w-file",
                        "labels": {"env": "file"},
                        "pairing_code": "FILE-CODE",
                        "poll_interval": 10,
                        "break_glass_enabled": False,
                    }
                ),
                encoding="utf-8",
            )
            env = {
                "CONTROL_PLANE_URL": "http://env.example/",
                "AGENT_NAME": "from-env",
                "GAS_TENANT_ID": "t-env",
                "GAS_WORKSPACE_ID": "w-env",
                "LABELS": "env=prod,role=worker",
                "POLL_INTERVAL": "3",
                "BREAK_GLASS_ENABLED": "true",
                "GAS_PAIRING_CODE": "ENV-CODE",
            }
            with mock.patch.dict(os.environ, env, clear=False):
                cfg = load_agent_config(str(cfg_path))
            self.assertEqual(cfg.control_plane_url, "http://env.example")
            self.assertEqual(cfg.agent_name, "from-env")
            self.assertEqual(cfg.tenant_id, "t-env")
            self.assertEqual(cfg.workspace_id, "w-env")
            self.assertEqual(cfg.pairing_code, "ENV-CODE")
            self.assertEqual(cfg.poll_interval, 3)
            self.assertTrue(cfg.break_glass_enabled)
            self.assertEqual(cfg.labels.get("env"), "prod")
            self.assertEqual(cfg.labels.get("role"), "worker")

    def test_token_store_uses_gas_home(self):
        from agent.token_store import AgentTokenStore

        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch.dict(os.environ, {"GAS_HOME": tmpdir}, clear=False):
                store = AgentTokenStore()
                store.write_agent_id("a1")
                store.write_token("t1")
                self.assertEqual(store.read_agent_id(), "a1")
                self.assertEqual(store.read_token(), "t1")

    def test_logger_redacts_token(self):
        from agent.json_logger import JsonLogger

        buf = io.StringIO()
        with redirect_stdout(buf):
            logger = JsonLogger("test", {"token": "super-secret"})
            logger.info("hello", nested={"agent_token": "abc"})
        line = buf.getvalue().strip().splitlines()[-1]
        payload = json.loads(line)
        self.assertEqual(payload.get("token"), "[redacted]")
        self.assertEqual((payload.get("nested") or {}).get("agent_token"), "[redacted]")

    def test_catalog_contains_demo_actions(self):
        from agent.catalog import build_capabilities_catalog

        catalog = build_capabilities_catalog()
        actions = catalog.get("actions") or []
        action_ids = {item.get("action_id") for item in actions}
        self.assertIn("runner.connectivity_test", action_ids)
        self.assertIn("demo.echo", action_ids)
        self.assertIn("demo.sleep", action_ids)
        self.assertIn("demo.sysinfo", action_ids)

    def test_catalog_contains_windows_powershell_actions(self):
        from agent.catalog import build_capabilities_catalog

        catalog = build_capabilities_catalog()
        actions = catalog.get("actions") or []
        action_ids = {item.get("action_id") for item in actions}
        self.assertIn("powershell.whoami_all", action_ids)
        self.assertIn("powershell.module_inventory", action_ids)
        self.assertIn("powershell.health_check", action_ids)
        self.assertIn("query.eventlog", action_ids)
        self.assertIn("query.registry", action_ids)
        self.assertIn("query.files", action_ids)
        self.assertIn("query.processes", action_ids)
        self.assertIn("query.network_probe", action_ids)
        self.assertIn("evidence.bundle_zip", action_ids)

        caps = set(catalog.get("capabilities") or [])
        self.assertIn("powershell.core", caps)
        self.assertIn("query.eventlog", caps)
        self.assertIn("query.registry", caps)
        self.assertIn("query.files", caps)
        self.assertIn("query.processes", caps)
        self.assertIn("query.network_probe", caps)

    def test_catalog_contains_graph_runner_actions(self):
        from agent.catalog import build_capabilities_catalog

        catalog = build_capabilities_catalog()
        actions = catalog.get("actions") or []
        action_ids = {item.get("action_id") for item in actions}
        self.assertIn("graph.connection_test", action_ids)
        self.assertIn("graph.list_users", action_ids)
        self.assertIn("graph.get_user", action_ids)
        self.assertIn("graph.exchange.list_mail_folders", action_ids)

        caps = set(catalog.get("capabilities") or [])
        self.assertIn("graph.core", caps)

    def test_catalog_contains_vision_u_eye_actions(self):
        from agent.catalog import build_capabilities_catalog

        catalog = build_capabilities_catalog()
        actions = catalog.get("actions") or []
        action_ids = {item.get("action_id") for item in actions}
        self.assertIn("vision.capture_snapshot", action_ids)
        self.assertIn("vision.record_segment", action_ids)
        self.assertIn("vision.analyze_snapshot", action_ids)
        self.assertIn("vision.stream_status", action_ids)

        caps = set(catalog.get("capabilities") or [])
        self.assertIn("observe.screen", caps)
        self.assertIn("observe.snapshots", caps)

    def test_windows_powershell_plugin_unsupported_on_non_windows(self):
        if platform.system().lower() == "windows":
            self.skipTest("This test asserts non-Windows behavior.")

        from agent.plugins.windows_powershell_runner import WindowsPowerShellRunnerPlugin

        plugin = WindowsPowerShellRunnerPlugin()
        result = plugin.handle("powershell.whoami_all", {})
        self.assertFalse(result.ok)
        self.assertEqual(result.exit_code, 2)
        self.assertIn("Unsupported platform", result.stderr or "")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
