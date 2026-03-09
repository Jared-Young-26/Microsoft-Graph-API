import re
import unittest
from unittest import mock

from fastapi.testclient import TestClient


class TestFastAPIAppCacheBusting(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import fastapi.dependencies.utils as fastapi_dependency_utils

        cls._multipart_patch = mock.patch.object(
            fastapi_dependency_utils,
            "ensure_multipart_is_installed",
            return_value=None,
        )
        cls._multipart_patch.start()
        from admin_gui.backend import fastapi_app

        cls.client = TestClient(fastapi_app.app)

    @classmethod
    def tearDownClass(cls):
        cls.client.close()
        cls._multipart_patch.stop()

    def test_shell_routes_version_boot_assets(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        html = response.text

        app_match = re.search(r'src="app\.js\?v=(\d+)"', html)
        schema_match = re.search(r'src="portal_schema\.js\?v=(\d+)"', html)
        shells_match = re.search(r'src="service_shells\.js\?v=(\d+)"', html)
        persistence_match = re.search(r'src="persistence_security\.js\?v=(\d+)"', html)
        styles_match = re.search(r'href="styles\.css\?v=(\d+)"', html)

        self.assertIsNotNone(app_match)
        self.assertIsNotNone(schema_match)
        self.assertIsNotNone(shells_match)
        self.assertIsNotNone(persistence_match)
        self.assertIsNotNone(styles_match)
        self.assertEqual(schema_match.group(1), app_match.group(1))
        self.assertEqual(shells_match.group(1), app_match.group(1))
        self.assertEqual(persistence_match.group(1), app_match.group(1))
        self.assertEqual(styles_match.group(1), app_match.group(1))


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
