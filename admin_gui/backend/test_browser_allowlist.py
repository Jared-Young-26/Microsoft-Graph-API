import unittest
from unittest import mock

from fastapi.testclient import TestClient


HTML_SHELL_PATHS = (
    "/",
    "/index.html",
    "/help",
    "/help/security",
    "/investigations",
    "/workspaces",
)

BOOT_ASSET_PATHS = (
    "/styles.css",
    "/portal_schema.js",
    "/service_shells.js",
    "/persistence_security.js",
    "/triage.js",
    "/investigation_summary.js",
    "/next_steps.js",
    "/app.js",
)

ALLOWED_FILE_CHECKS = (
    ("/docs/help/help_manifest.json", '"pages"'),
    ("/docs/help/security.md", "# Security & Safety"),
    ("/install/windows.ps1", "CONTROL_PLANE_URL"),
)

DENIED_PATHS = (
    "/backend/config.json",
    "/backend/control_plane.sqlite",
    "/backend/flask_app.py",
    "/README.md",
    "/json_inspector.js",
    "/static/app.js",
    "/static/backend/config.json",
)


class BrowserAllowlistAssertions:
    client = None

    def fetch(self, path: str):
        response = self.client.get(path)
        try:
            if hasattr(response, "get_data"):
                body = response.get_data(as_text=True)
                content_type = response.headers.get("Content-Type", "")
            else:
                body = response.text
                content_type = response.headers.get("content-type", "")
        finally:
            close = getattr(response, "close", None)
            if callable(close):
                close()
        return response.status_code, body, content_type

    def assert_html_shell(self, path: str):
        status, body, content_type = self.fetch(path)
        self.assertEqual(status, 200, path)
        self.assertIn("text/html", content_type, path)
        self.assertIn("<!doctype html>", body.lower(), path)

    def assert_allowed_file(self, path: str, expected_snippet: str):
        status, body, content_type = self.fetch(path)
        self.assertEqual(status, 200, path)
        self.assertNotIn("text/html", content_type, path)
        self.assertIn(expected_snippet, body, path)

    def assert_denied(self, path: str):
        status, body, content_type = self.fetch(path)
        self.assertEqual(status, 404, path)
        self.assertIn("Not found", body, path)
        self.assertIn("text/plain", content_type, path)

    def test_allows_html_shell_routes(self):
        for path in HTML_SHELL_PATHS:
            with self.subTest(path=path):
                self.assert_html_shell(path)

    def test_allows_boot_assets_and_help_install_files(self):
        for path in BOOT_ASSET_PATHS:
            with self.subTest(path=path):
                status, _, content_type = self.fetch(path)
                self.assertEqual(status, 200, path)
                self.assertNotIn("text/html", content_type, path)
        for path, expected_snippet in ALLOWED_FILE_CHECKS:
            with self.subTest(path=path):
                self.assert_allowed_file(path, expected_snippet)

    def test_denies_backend_state_source_and_static_alias_paths(self):
        for path in DENIED_PATHS:
            with self.subTest(path=path):
                self.assert_denied(path)


class TestFlaskBrowserAllowlist(BrowserAllowlistAssertions, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from admin_gui.backend import flask_app

        cls.client = flask_app.app.test_client()


class TestFastAPIBrowserAllowlist(BrowserAllowlistAssertions, unittest.TestCase):
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


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
