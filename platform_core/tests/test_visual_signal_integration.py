import json
import unittest
from pathlib import Path

from platform_core.signal_providers import VISION_U_EYE_PROVIDER, attach_signal


class TestVisualSignalIntegration(unittest.TestCase):
    def test_golden_payload(self) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        sample_path = repo_root / "contracts" / "examples" / "vision_u_eye.sample.json"
        payload = json.loads(sample_path.read_text(encoding="utf-8"))

        self.assertTrue(VISION_U_EYE_PROVIDER.validate(payload))

        snapshot = {"snapshot_id": "integration-test", "signals": {}}
        attach_signal(snapshot, VISION_U_EYE_PROVIDER, payload)

        # Non-negotiable: no field renaming or reshaping.
        self.assertEqual(snapshot["signals"]["visual"], payload)


if __name__ == "__main__":
    unittest.main()
