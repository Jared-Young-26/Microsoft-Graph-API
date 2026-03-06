import tempfile
import unittest
from pathlib import Path


class TestWorkflowsV2(unittest.TestCase):
    def test_validate_rejects_unknown_action_id(self):
        from admin_gui.backend import workflows_v2

        result = workflows_v2.validate_workflow_v2({"name": "t", "steps": [{"action_id": "nope.nope", "params": {}}]})
        self.assertFalse(result.ok)
        self.assertTrue(any(err.get("error") == "unknown_action_id" for err in result.errors))

    def test_validate_rejects_missing_required_capabilities(self):
        from admin_gui.backend import control_plane, workflows_v2

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "control_plane.sqlite"
            reg = control_plane.register_agent({"name": "agent", "capabilities": ["demo.echo"]}, db_path=db_path)
            agent_id = reg["agent_id"]

            workflow = {"name": "t", "agent_id": agent_id, "steps": [{"action_id": "demo.sleep", "params": {"ms": 1}}]}
            result = workflows_v2.validate_workflow_v2(workflow, db_path=db_path)
            self.assertFalse(result.ok)
            self.assertTrue(any(err.get("error") == "missing_required_capabilities" for err in result.errors))

    def test_validate_rejects_disallowed_risk_level(self):
        from admin_gui.backend import control_plane, workflows_v2

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "control_plane.sqlite"
            reg = control_plane.register_agent({"name": "agent", "capabilities": ["powershell.core"]}, db_path=db_path)
            agent_id = reg["agent_id"]

            workflow = {
                "name": "t",
                "agent_id": agent_id,
                "max_risk_level": "safe",
                "steps": [{"action_id": "powershell.health_check", "params": {}}],
            }
            result = workflows_v2.validate_workflow_v2(workflow, db_path=db_path)
            self.assertFalse(result.ok)
            self.assertTrue(any(err.get("error") == "risk_disallowed" for err in result.errors))

    def test_enqueue_action_job_validates_capabilities(self):
        from admin_gui.backend import control_plane

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "control_plane.sqlite"
            reg = control_plane.register_agent({"name": "agent", "capabilities": ["demo.echo"]}, db_path=db_path)
            agent_id = reg["agent_id"]

            with self.assertRaises(PermissionError):
                control_plane.enqueue_action_job(
                    agent_id=agent_id,
                    action_id="demo.sleep",
                    params={"ms": 1},
                    db_path=db_path,
                )


if __name__ == "__main__":  # pragma: no cover
    unittest.main()

