import re
import unittest


class TestFlaskAppCacheBusting(unittest.TestCase):
    def test_render_index_versions_boot_assets(self):
        from admin_gui.backend import flask_app

        html = flask_app._render_index_html().get_data(as_text=True)

        app_match = re.search(r'src="app\.js\?v=(\d+)"', html)
        schema_match = re.search(r'src="portal_schema\.js\?v=(\d+)"', html)
        shells_match = re.search(r'src="service_shells\.js\?v=(\d+)"', html)

        self.assertIsNotNone(app_match)
        self.assertIsNotNone(schema_match)
        self.assertIsNotNone(shells_match)
        self.assertEqual(schema_match.group(1), app_match.group(1))
        self.assertEqual(shells_match.group(1), app_match.group(1))


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
