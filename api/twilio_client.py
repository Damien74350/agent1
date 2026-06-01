"""Thin wrapper around the Twilio REST API for sending WhatsApp messages
and downloading incoming media."""

import httpx
from twilio.rest import Client

from calo.config import CaloConfig


class TwilioWhatsApp:
    def __init__(self, config: CaloConfig):
        config.require_twilio()
        self.config = config
        self.client = Client(config.twilio_account_sid, config.twilio_auth_token)

    def send_text(self, to: str, body: str) -> str:
        """`to` must be in 'whatsapp:+33...' format. Returns the Twilio message SID."""
        # Twilio caps WhatsApp messages at 1600 chars — chunk if longer.
        for chunk in _chunk(body, 1500):
            msg = self.client.messages.create(
                from_=self.config.twilio_whatsapp_from,
                to=to,
                body=chunk,
            )
        return msg.sid

    def send_media(self, to: str, media_url: str, caption: str = "") -> str:
        """Send an image / audio file via WhatsApp.

        `media_url` must be a publicly fetchable HTTPS URL (Twilio fetches it
        server-side). For charts we expose them via the FastAPI `/chart/{token}`
        endpoint. Caption is optional, max 1024 chars."""
        msg = self.client.messages.create(
            from_=self.config.twilio_whatsapp_from,
            to=to,
            media_url=[media_url],
            body=caption[:1024] if caption else None,
        )
        return msg.sid

    def download_media(self, media_url: str) -> tuple[bytes, str]:
        """Twilio media URLs require basic auth. Returns (bytes, content_type)."""
        with httpx.Client(
            auth=(self.config.twilio_account_sid, self.config.twilio_auth_token),
            follow_redirects=True,
            timeout=30.0,
        ) as client:
            r = client.get(media_url)
            r.raise_for_status()
            return r.content, r.headers.get("content-type", "image/jpeg")


def _chunk(text: str, size: int):
    for i in range(0, len(text), size):
        yield text[i : i + size]
