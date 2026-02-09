import unittest

from graph_admin.exchange.mail import send_message_as_user


class _DummyGraphSession:
    """Minimal GraphSession stub for unit tests."""

    def __init__(self):
        self.calls = []

    def post(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return None


class ExchangeMailSendTests(unittest.TestCase):
    """Exchange mail sending tests."""

    def test_send_message_as_user_builds_graph_payload(self):
        """send_message_as_user formats recipients and HTML body correctly."""

        graph = _DummyGraphSession()
        ok = send_message_as_user(
            graph,
            sender="shared@contoso.com",
            to_recipients=["user1@contoso.com", "user2@contoso.com"],
            subject="Hello",
            body_html="<p>Hi</p>",
            cc_recipients=["cc@contoso.com"],
            save_to_sent_items=True,
        )
        self.assertTrue(ok)
        self.assertEqual(len(graph.calls), 1)
        url, kwargs = graph.calls[0]
        self.assertEqual(url, "/users/shared@contoso.com/sendMail")
        payload = kwargs.get("json") or {}
        self.assertTrue(payload.get("saveToSentItems"))
        message = payload.get("message") or {}
        self.assertEqual(message.get("subject"), "Hello")
        self.assertEqual(message.get("body", {}).get("contentType"), "HTML")
        self.assertEqual(message.get("body", {}).get("content"), "<p>Hi</p>")
        self.assertEqual(
            [r.get("emailAddress", {}).get("address") for r in message.get("toRecipients") or []],
            ["user1@contoso.com", "user2@contoso.com"],
        )
        self.assertEqual(
            [r.get("emailAddress", {}).get("address") for r in message.get("ccRecipients") or []],
            ["cc@contoso.com"],
        )

    def test_send_message_as_user_validates_inputs(self):
        """send_message_as_user rejects missing required inputs."""

        graph = _DummyGraphSession()
        with self.assertRaises(ValueError):
            send_message_as_user(
                graph,
                sender="",
                to_recipients=["user@contoso.com"],
                subject="Hello",
                body_html="<p>Hi</p>",
            )
        with self.assertRaises(ValueError):
            send_message_as_user(
                graph,
                sender="user@contoso.com",
                to_recipients=[],
                subject="Hello",
                body_html="<p>Hi</p>",
            )
        with self.assertRaises(ValueError):
            send_message_as_user(
                graph,
                sender="user@contoso.com",
                to_recipients=["user@contoso.com"],
                subject="",
                body_html="<p>Hi</p>",
            )

