"""Thin wrapper around the Twilio REST API for sending WhatsApp messages
and downloading incoming media."""

import logging
import time

import httpx
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client

from calo.config import CaloConfig

log = logging.getLogger("calo.twilio")


def _is_transient(exc: Exception) -> bool:
    """Twilio 5xx / network blips are worth retrying ; 4xx are not."""
    if isinstance(exc, TwilioRestException):
        status = getattr(exc, "status", 0) or 0
        return status == 0 or status >= 500
    return isinstance(exc, (httpx.HTTPError, ConnectionError, TimeoutError))


def _retry(fn, attempts: int = 3, backoff: float = 0.8):
    last: Exception | None = None
    for i in range(attempts):
        try:
            return fn()
        except Exception as exc:  # noqa: BLE001
            last = exc
            if not _is_transient(exc) or i == attempts - 1:
                raise
            wait = backoff * (2 ** i)
            log.warning("twilio call failed (try %d/%d): %s ; retrying in %.1fs",
                        i + 1, attempts, exc, wait)
            time.sleep(wait)
    if last:
        raise last


class TwilioWhatsApp:
    def __init__(self, config: CaloConfig):
        config.require_twilio()
        self.config = config
        self.client = Client(config.twilio_account_sid, config.twilio_auth_token)

    def send_text(self, to: str, body: str) -> str:
        """`to` must be in 'whatsapp:+33...' format. Returns the Twilio message SID."""
        last_sid = ""
        for chunk in _chunk(body, 1500):
            msg = _retry(lambda c=chunk: self.client.messages.create(
                from_=self.config.twilio_whatsapp_from, to=to, body=c,
            ))
            last_sid = msg.sid
        return last_sid

    def send_media(self, to: str, media_url: str, caption: str = "") -> str:
        """Send an image / audio file via WhatsApp. `media_url` must be public HTTPS."""
        msg = _retry(lambda: self.client.messages.create(
            from_=self.config.twilio_whatsapp_from,
            to=to,
            media_url=[media_url],
            body=caption[:1024] if caption else None,
        ))
        return msg.sid

    def download_media(self, media_url: str) -> tuple[bytes, str]:
        """Twilio media URLs require basic auth. Returns (bytes, content_type)."""
        def _dl():
            with httpx.Client(
                auth=(self.config.twilio_account_sid, self.config.twilio_auth_token),
                follow_redirects=True,
                timeout=30.0,
            ) as client:
                r = client.get(media_url)
                r.raise_for_status()
                return r.content, r.headers.get("content-type", "image/jpeg")
        return _retry(_dl)


def _chunk(text: str, size: int):
    for i in range(0, len(text), size):
        yield text[i : i + size]
