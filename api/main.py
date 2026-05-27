"""FastAPI app: Twilio WhatsApp webhook → Calo coach → Twilio reply."""

import logging
import threading
from typing import Annotated

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import PlainTextResponse, Response
from twilio.request_validator import RequestValidator

from calo.coach import CaloCoach, TurnInput
from calo.config import CaloConfig

from .twilio_client import TwilioWhatsApp

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("calo.api")

app = FastAPI(title="Calo API")
config = CaloConfig()
coach = CaloCoach(config)
twilio = TwilioWhatsApp(config)
validator = RequestValidator(config.twilio_auth_token)


@app.get("/")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "calo"}


@app.post("/twilio/webhook", response_class=Response)
async def twilio_webhook(
    request: Request,
    From: Annotated[str, Form()],
    Body: Annotated[str, Form()] = "",
    NumMedia: Annotated[int, Form()] = 0,
    MediaUrl0: Annotated[str | None, Form()] = None,
    MediaContentType0: Annotated[str | None, Form()] = None,
):
    """Twilio sends form-encoded POSTs here. We validate the signature, ACK fast,
    process the turn in a background thread, then reply via the REST API."""
    if not _validate_signature(request, await _form_dict(request)):
        log.warning("invalid twilio signature; rejecting")
        raise HTTPException(status_code=403, detail="invalid signature")

    log.info("inbound from=%s body=%r media=%d", From, Body[:80], NumMedia)

    # Process the turn in a background thread so we can ACK the webhook
    # immediately (Twilio gives us 15s, but the Claude turn can take longer).
    threading.Thread(
        target=_process_turn,
        args=(From, Body, MediaUrl0 if NumMedia > 0 else None, MediaContentType0),
        daemon=True,
    ).start()

    # Empty TwiML response — we don't reply inline, we POST a reply asynchronously.
    return Response(content="<Response/>", media_type="application/xml")


def _process_turn(
    sender: str,
    text: str,
    media_url: str | None,
    media_content_type: str | None,
) -> None:
    try:
        # Look up or create the user.
        user = coach.db.get_or_create_user(sender)
        user_id = user["id"]

        # Download the media if any.
        photo_bytes = None
        photo_media_type = "image/jpeg"
        if media_url:
            try:
                photo_bytes, photo_media_type = twilio.download_media(media_url)
            except Exception as exc:  # noqa: BLE001
                log.exception("failed to download media: %s", exc)

        # Run the agent.
        out = coach.handle_turn(
            TurnInput(
                user_id=user_id,
                text=text or "",
                photo_bytes=photo_bytes,
                photo_media_type=photo_media_type,
            )
        )
        log.info("user=%d tools=%s reply_len=%d", user_id, out.tool_calls, len(out.reply_text))

        # Send the reply back.
        twilio.send_text(sender, out.reply_text)

    except Exception as exc:  # noqa: BLE001
        log.exception("turn failed: %s", exc)
        try:
            twilio.send_text(
                sender,
                "Désolé, j'ai eu un problème technique. Réessaye dans un instant 🙏",
            )
        except Exception:  # noqa: BLE001
            log.exception("failed to send error reply")


async def _form_dict(request: Request) -> dict[str, str]:
    form = await request.form()
    return {k: str(v) for k, v in form.items()}


def _validate_signature(request: Request, params: dict[str, str]) -> bool:
    # When running locally without HTTPS or in dev, skip validation if no token set.
    if not config.twilio_auth_token:
        return True
    signature = request.headers.get("X-Twilio-Signature", "")
    # The URL Twilio signed includes the full public URL.
    url = config.public_url.rstrip("/") + str(request.url.path) if config.public_url \
        else str(request.url)
    return validator.validate(url, params, signature)
