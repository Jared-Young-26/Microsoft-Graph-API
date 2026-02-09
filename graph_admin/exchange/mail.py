"""Exchange mail primitives (Graph-first, app-only friendly).

Single source of truth for sending mail as a specific mailbox using Microsoft
Graph application permissions.

UI endpoints and scripts must call these functions rather than re-implementing
Graph request payloads.
"""

from __future__ import annotations

from typing import Iterable


def _normalize_recipients(recipients: Iterable[str] | None) -> list[str]:
    """Normalize a recipient iterable into a clean list of email addresses."""

    if not recipients:
        return []
    normalized: list[str] = []
    for value in recipients:
        if value is None:
            continue
        addr = str(value).strip()
        if not addr:
            continue
        normalized.append(addr)
    return normalized


def _format_recipients(recipients: list[str]) -> list[dict]:
    """Format recipients into the Graph `emailAddress` envelope."""

    return [{"emailAddress": {"address": address}} for address in recipients]


def send_message_as_user(
    graph_session,
    sender: str,
    to_recipients: list[str],
    subject: str,
    body_html: str,
    cc_recipients: list[str] | None = None,
    save_to_sent_items: bool = False,
) -> bool:
    """Send an HTML email as a specific mailbox via Microsoft Graph.

    Uses Graph endpoint:
      POST /v1.0/users/{sender}/sendMail

    This works with application permissions (no delegated "/me" usage).

    Args:
        graph_session: An authenticated GraphSession (see `microsoft.GraphSession`).
        sender: The sender mailbox identifier (UPN, SMTP address, or user object id).
        to_recipients: List of recipient email addresses.
        subject: Email subject.
        body_html: Email body as HTML.
        cc_recipients: Optional list of CC recipient email addresses.
        save_to_sent_items: Whether to save the message to the sender's Sent Items.

    Returns:
        True when Graph accepted the send request.

    Raises:
        ValueError: If required fields are missing/empty.
        GraphAPIError: If Graph returns a non-2xx response.
    """

    sender = str(sender or "").strip()
    subject = str(subject or "").strip()
    body_html = str(body_html or "")
    to_list = _normalize_recipients(to_recipients)
    cc_list = _normalize_recipients(cc_recipients)

    if not sender:
        raise ValueError("sender is required (UPN/SMTP/object id).")
    if not to_list:
        raise ValueError("to_recipients must include at least one address.")
    if not subject:
        raise ValueError("subject is required.")

    message: dict = {
        "subject": subject,
        "body": {"contentType": "HTML", "content": body_html},
        "toRecipients": _format_recipients(to_list),
    }
    if cc_list:
        message["ccRecipients"] = _format_recipients(cc_list)

    payload = {"message": message, "saveToSentItems": bool(save_to_sent_items)}
    graph_session.post(f"/users/{sender}/sendMail", json=payload)
    return True

