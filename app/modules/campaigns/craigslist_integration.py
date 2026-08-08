"""
Craigslist reply integration for campaign automation.

Craigslist enforces replies through an anonymized email relay rather than
a public posting API: every listing exposes a ``.reply.craigslist.org``
mailbox. This service composes the campaign reply and delivers it via an
SMTP relay, mirroring how replies actually reach a seller.

Requires SMTP relay credentials (e.g. SMTP2GO, Resend, SendGrid, Gmail).
When no SMTP is configured the service reports ``not_configured`` so the
campaign workflow can surface a clear next step instead of dropping the
reply silently.
"""

import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

import requests

logger = logging.getLogger(__name__)


class CraigslistReplyService:
    """Service for sending Craigslist replies over SMTP."""

    def __init__(self, config=None):
        config = config or {}
        self.smtp_host = config.get("smtp_host") or os.environ.get("SMTP_HOST")
        self.smtp_port = int(
            config.get("smtp_port") or os.environ.get("SMTP_PORT") or 587
        )
        self.smtp_user = config.get("smtp_user") or os.environ.get("SMTP_USER")
        self.smtp_password = config.get("smtp_password") or os.environ.get(
            "SMTP_PASSWORD"
        )
        self.smtp_use_tls = bool(
            config.get("use_tls", os.environ.get("SMTP_USE_TLS", "1") == "1")
        )
        self.from_email = config.get("from_email") or os.environ.get(
            "SMTP_FROM_EMAIL", "no-reply@street-smart-nyc.com"
        )
        self.from_name = config.get("from_name") or os.environ.get(
            "SMTP_FROM_NAME", "Street Smart NYC"
        )
        self.base_url = "https://www.craigslist.org"
        self.session = requests.Session()

    @property
    def configured(self):
        """True when an SMTP relay can be reached."""
        return bool(self.smtp_host and self.smtp_user and self.smtp_password)

    def send_reply(self, posting_id, reply_content, contact_info, reply_email=None):
        """
        Send a reply to a Craigslist posting.

        Args:
            posting_id: The Craigslist posting ID
            reply_content: The reply message body
            contact_info: Dict with name, email, phone
            reply_email: Optional anonymized reply mailbox
                (``.reply.craigslist.org``). When omitted, defaults to the
                conventional ``<posting_id>@reply.craigslist.org``.

        Returns:
            dict with status ("sent", "failed", "empty", "not_configured")
            and details.
        """
        if not reply_content or not reply_content.strip():
            return {
                "status": "empty",
                "posting_id": posting_id,
                "message": "Reply body is empty; nothing sent.",
            }

        if not self.configured:
            return {
                "status": "not_configured",
                "posting_id": posting_id,
                "message": (
                    "Reply prepared but SMTP is not configured. "
                    "Set SMTP_HOST/SMTP_USER/SMTP_PASSWORD."
                ),
                "reply_content": reply_content,
                "contact_info": contact_info,
            }

        recipient = reply_email or f"{posting_id}@reply.craigslist.org"
        msg = MIMEMultipart()
        msg["From"] = formataddr((self.from_name, self.from_email))
        msg["To"] = recipient
        msg["Subject"] = f"Re: {posting_id}"
        msg.attach(MIMEText(reply_content, "plain"))

        try:
            self._send(msg)
        except Exception as exc:  # noqa: BLE001 - surface as a service result
            logger.warning("Craigslist reply send failed: %s", exc)
            return {
                "status": "failed",
                "posting_id": posting_id,
                "message": f"Reply not sent: {exc}",
                "reply_to": recipient,
            }

        return {
            "status": "sent",
            "posting_id": posting_id,
            "message": f"Reply queued to {recipient}",
            "reply_to": recipient,
        }

    def _send(self, msg):
        """Deliver ``msg`` through the configured SMTP relay."""
        server = smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=30)
        try:
            if self.smtp_use_tls:
                server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            server.send_message(msg)
        finally:
            server.quit()

    def prepare_reply(self, template_name, variables):
        """
        Prepare a reply from a template.

        Args:
            template_name: Name of the template to use
            variables: Dict of template variables

        Returns:
            str: The prepared reply content
        """
        templates = {"initial_reply": self._initial_reply_template()}

        template = templates.get(template_name, templates["initial_reply"])

        # Simple variable substitution with {variable} placeholders.
        for key, value in variables.items():
            template = template.replace(f"{{{key}}}", str(value))

        return template

    def _initial_reply_template(self):
        """Default initial reply template."""
        return """Hey {name},

I saw your post about {post_topic}.

I represent LES Bar — we're {value_prop}.

We're {offer}.

Interested in {cta}?

Best,
{contact_name}
LES Bar
{contact_email}
"""
