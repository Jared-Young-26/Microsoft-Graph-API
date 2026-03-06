import tempfile
import unittest
import os
from pathlib import Path
from unittest import mock


class TestControlPlaneMVI(unittest.TestCase):
    """Validate minimum viable control plane contracts (agents + jobs)."""

    def test_register_heartbeat_lease_and_result(self):
        """Register an agent, heartbeat, lease a job, and record results."""

        from admin_gui.backend import control_plane

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "control_plane.sqlite"

            reg = control_plane.register_agent(
                {
                    "name": "test-agent",
                    "hostname": "test-host",
                    "os": "linux",
                    "arch": "x86_64",
                    "version": "0.0.1",
                    "capabilities": ["demo.echo"],
                    "labels": {"env": "test"},
                },
                db_path=db_path,
            )
            self.assertTrue(reg.get("agent_id"))
            self.assertTrue(reg.get("agent_token"))
            agent_id = reg["agent_id"]
            token = reg["agent_token"]

            self.assertTrue(control_plane.authenticate_agent(agent_id, token, db_path=db_path))

            hb = control_plane.heartbeat_agent(
                agent_id,
                status="online",
                capabilities=["demo.echo", "demo.sleep"],
                labels={"env": "test", "role": "worker"},
                db_path=db_path,
            )
            self.assertEqual(hb.get("agent_id"), agent_id)
            self.assertEqual(hb.get("status"), "online")
            self.assertTrue(hb.get("last_seen"))

            agents = control_plane.list_agents(db_path=db_path)
            self.assertEqual(agents.get("count"), 1)
            self.assertEqual(agents["items"][0]["agent_id"], agent_id)

            jid = control_plane.enqueue_job(
                agent_id=agent_id,
                action_id="demo.echo",
                params={"message": "hello"},
                risk_level="safe",
                requested_by="test",
                db_path=db_path,
            )["job_id"]
            self.assertTrue(jid)

            leased = control_plane.lease_next_job(agent_id, lease_seconds=60, db_path=db_path)
            self.assertEqual(leased.get("job_id"), jid)
            self.assertEqual(leased.get("agent_id"), agent_id)
            self.assertEqual(leased.get("action_id"), "demo.echo")
            self.assertEqual((leased.get("params") or {}).get("message"), "hello")
            self.assertTrue(leased.get("lease_expires_at"))
            self.assertEqual(leased.get("status"), "running")

            no_more = control_plane.lease_next_job(agent_id, lease_seconds=60, db_path=db_path)
            self.assertIsNone(no_more)

            result = control_plane.record_job_result(
                agent_id,
                jid,
                status="completed",
                result={"ok": True},
                stdout="hello\n",
                stderr="",
                exit_code=0,
                artifacts=[{"name": "out.txt"}],
                duration_ms=12,
                db_path=db_path,
            )
            self.assertEqual(result.get("job_id"), jid)
            self.assertEqual(result.get("status"), "completed")
            self.assertTrue(result.get("finished_at"))

            detail = control_plane.get_job_detail(jid, db_path=db_path)
            self.assertEqual(detail.get("job_id"), jid)
            self.assertEqual(detail.get("status"), "completed")
            self.assertIsInstance(detail.get("result"), dict)
            self.assertEqual(detail["result"].get("exit_code"), 0)

    def test_enqueue_job_rejects_secret_material(self):
        """Control plane must not store secrets in job params."""

        from admin_gui.backend import control_plane

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "control_plane.sqlite"
            reg = control_plane.register_agent({"name": "test-agent"}, db_path=db_path)
            agent_id = reg["agent_id"]

            with self.assertRaises(ValueError):
                control_plane.enqueue_job(
                    agent_id=agent_id,
                    action_id="demo.echo",
                    params={"client_secret": "should-not-store"},
                    db_path=db_path,
                )

    def test_register_rotates_token(self):
        """Re-registering with token keeps agent_id; rotate only when requested."""

        from admin_gui.backend import control_plane

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "control_plane.sqlite"

            reg1 = control_plane.register_agent({"name": "test-agent"}, db_path=db_path)
            agent_id = reg1["agent_id"]
            token1 = reg1["agent_token"]

            reg2 = control_plane.register_agent({"agent_id": agent_id, "agent_token": token1, "name": "test-agent"}, db_path=db_path)
            self.assertEqual(reg2["agent_id"], agent_id)
            self.assertFalse(reg2.get("agent_token"))
            self.assertTrue(control_plane.authenticate_agent(agent_id, token1, db_path=db_path))

            reg3 = control_plane.register_agent(
                {"agent_id": agent_id, "agent_token": token1, "rotate_token": True, "name": "test-agent"},
                db_path=db_path,
            )
            token2 = reg3["agent_token"]

            self.assertEqual(reg3["agent_id"], agent_id)
            self.assertNotEqual(token1, token2)
            self.assertFalse(control_plane.authenticate_agent(agent_id, token1, db_path=db_path))
            self.assertTrue(control_plane.authenticate_agent(agent_id, token2, db_path=db_path))

    def test_reaper_requeues_expired_lease(self):
        """Reaper moves expired running jobs back to queued."""

        from admin_gui.backend import control_plane

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "control_plane.sqlite"

            reg = control_plane.register_agent({"name": "test-agent"}, db_path=db_path)
            agent_id = reg["agent_id"]

            jid = control_plane.enqueue_job(agent_id=agent_id, action_id="demo.sleep", params={"ms": 10}, db_path=db_path)["job_id"]
            leased = control_plane.lease_next_job(agent_id, lease_seconds=60, db_path=db_path)
            self.assertEqual(leased.get("job_id"), jid)

            with control_plane.open_db(db_path) as conn:
                conn.execute("BEGIN IMMEDIATE")
                conn.execute(
                    "UPDATE jobs SET lease_expires_at = ?, status = 'running' WHERE job_id = ?",
                    ("1970-01-01T00:00:00+00:00", jid),
                )
                conn.commit()

            requeued = control_plane.requeue_expired_leases(db_path=db_path)
            self.assertEqual(requeued, 1)

            jobs = control_plane.list_jobs(agent_id=agent_id, db_path=db_path)
            self.assertEqual(jobs.get("count"), 1)
            self.assertEqual(jobs["items"][0].get("status"), "queued")

    def test_register_requires_pairing_code_when_enabled(self):
        """When enabled, first-time agent registration must present a valid pairing code."""

        from admin_gui.backend import control_plane

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "control_plane.sqlite"

            with mock.patch.dict(os.environ, {"CONTROL_PLANE_REQUIRE_PAIRING_CODE": "true"}, clear=False):
                with self.assertRaises(PermissionError):
                    control_plane.register_agent({"name": "a"}, db_path=db_path)

                pairing = control_plane.create_pairing_code(tenant_id="t1", workspace_id="w1", ttl_seconds=600, db_path=db_path)
                code = pairing["pairing_code"]
                reg = control_plane.register_agent({"name": "a", "pairing_code": code}, db_path=db_path)
                self.assertTrue(reg.get("agent_id"))
                self.assertTrue(reg.get("agent_token"))

                agents = control_plane.list_agents(db_path=db_path)
                self.assertEqual(agents.get("count"), 1)
                self.assertEqual(agents["items"][0].get("tenant_id"), "t1")
                self.assertEqual(agents["items"][0].get("workspace_id"), "w1")

                with self.assertRaises(PermissionError):
                    control_plane.register_agent({"name": "b", "pairing_code": code}, db_path=db_path)

    def test_record_artifact_creates_row(self):
        """Artifact uploads should be recorded in the artifacts table."""

        from admin_gui.backend import control_plane

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "control_plane.sqlite"

            reg = control_plane.register_agent({"name": "agent"}, db_path=db_path)
            agent_id = reg["agent_id"]

            artifact_id = "a1"
            sha256 = "0" * 64
            control_plane.record_artifact(
                artifact_id=artifact_id,
                agent_id=agent_id,
                job_id=None,
                type="zip",
                filename="a1.zip",
                sha256=sha256,
                size_bytes=123,
                storage_path="a1.zip",
                db_path=db_path,
            )

            with control_plane.open_db(db_path) as conn:
                row = conn.execute(
                    "SELECT artifact_id, agent_id, sha256, size_bytes FROM artifacts WHERE artifact_id = ?",
                    (artifact_id,),
                ).fetchone()
            self.assertEqual(str(row["artifact_id"]), artifact_id)
            self.assertEqual(str(row["agent_id"]), agent_id)
            self.assertEqual(str(row["sha256"]), sha256)
            self.assertEqual(int(row["size_bytes"]), 123)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
