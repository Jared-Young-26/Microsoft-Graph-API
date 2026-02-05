import json
from pathlib import Path
import unittest

from platform_core.signal_providers import VisionUEyeProvider, attach_signal_to_snapshot


class VisionUEyeContractTests(unittest.TestCase):
    """Vision U Eye Contract Tests."""
    def test_sample_payload_validates_and_embeds_without_rename(self):
        """Run test sample payload validates and embeds without rename."""
        root = Path(__file__).resolve().parents[2]
        sample_path = root / "contracts" / "examples" / "vision_u_eye.sample.json"
        self.assertTrue(sample_path.exists(), "Missing contract sample file")
        payload = json.loads(sample_path.read_text(encoding="utf-8"))

        provider = VisionUEyeProvider()
        # Must validate against the authoritative contract.
        self.assertTrue(provider.validate(payload))

        normalized = provider.normalize(payload)
        # No field renaming / reshaping.
        self.assertEqual(normalized, payload)

        snapshot = {"snapshot_id": "integration-test", "signals": {}}
        attach_signal_to_snapshot(snapshot, provider, payload)
        self.assertIn("signals", snapshot)
        self.assertIn("visual", snapshot["signals"])
        self.assertEqual(snapshot["signals"]["visual"], payload)


if __name__ == "__main__":
    unittest.main()
