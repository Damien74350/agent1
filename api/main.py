"""FastAPI app: Twilio WhatsApp webhook → Calo coach → Twilio reply."""

import logging
import threading
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, PlainTextResponse, Response
from twilio.request_validator import RequestValidator

from calo.chart_generator import CHART_DIR
from calo.coach import CaloCoach, TurnInput
from calo.config import CaloConfig
from calo.pdf_report import REPORT_DIR
from calo import voice as voice_mod

from .app_api import build_app_router
from .twilio_client import TwilioWhatsApp

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("calo.api")

app = FastAPI(title="Calo API")
config = CaloConfig()
coach = CaloCoach(config)
twilio = TwilioWhatsApp(config)
validator = RequestValidator(config.twilio_auth_token)

# CORS — the mobile app (Expo) and any web client call the /app/* JSON API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the app-facing JSON API (auth, chat, profile, progress).
app.include_router(build_app_router(coach, twilio, config))


@app.get("/")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "calo"}


@app.get("/chart/{token}")
def get_chart(token: str):
    """Serves a generated chart PNG to Twilio (and the client). The token is a
    secret-quality string baked at generation, so no further auth is needed."""
    # Strict allowlist : prevent path traversal.
    safe = "".join(c for c in token if c.isalnum() or c in "-_")
    if safe != token or not safe:
        raise HTTPException(status_code=404, detail="not found")
    path = CHART_DIR / f"{safe}.png"
    if not path.is_file():
        raise HTTPException(status_code=404, detail="not found")
    return FileResponse(path, media_type="image/png", filename="calo-chart.png")


@app.get("/report/{token}")
def get_report(token: str):
    """Serves a generated monthly PDF report to Twilio (and the client)."""
    safe = "".join(c for c in token if c.isalnum() or c in "-_")
    if safe != token or not safe:
        raise HTTPException(status_code=404, detail="not found")
    path = REPORT_DIR / f"{safe}.pdf"
    if not path.is_file():
        raise HTTPException(status_code=404, detail="not found")
    return FileResponse(path, media_type="application/pdf", filename="calo-report.pdf")


@app.get("/vision/{token}")
def get_vision(token: str):
    """Serves a generated motivational vision-board PNG to Twilio (and the client)."""
    from calo.image_gen import VISION_DIR
    safe = "".join(c for c in token if c.isalnum() or c in "-_")
    if safe != token or not safe:
        raise HTTPException(status_code=404, detail="not found")
    path = VISION_DIR / f"{safe}.png"
    if not path.is_file():
        raise HTTPException(status_code=404, detail="not found")
    return FileResponse(path, media_type="image/png", filename="calo-vision.png")


@app.get("/audio/{token}")
def get_audio(token: str):
    """Serves a generated MP3 voice reply to Twilio."""
    safe = "".join(c for c in token if c.isalnum() or c in "-_")
    if safe != token or not safe:
        raise HTTPException(status_code=404, detail="not found")
    path = voice_mod.AUDIO_DIR / f"{safe}.mp3"
    if not path.is_file():
        raise HTTPException(status_code=404, detail="not found")
    return FileResponse(path, media_type="audio/mpeg", filename="calo-voice.mp3")


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
        audio_bytes = None
        is_audio_in = bool(media_content_type and media_content_type.startswith("audio/"))
        if media_url:
            try:
                downloaded, downloaded_type = twilio.download_media(media_url)
                if is_audio_in:
                    audio_bytes = downloaded
                else:
                    photo_bytes = downloaded
                    photo_media_type = downloaded_type
            except Exception as exc:  # noqa: BLE001
                log.exception("failed to download media: %s", exc)

        # Voice IN — transcribe the audio so Calo treats it as plain text.
        transcribed_text = ""
        if audio_bytes:
            transcribed_text = voice_mod.transcribe(
                audio_bytes,
                content_type=media_content_type or "audio/ogg",
                api_key=config.openai_api_key,
            ) or ""
            log.info("transcribed %d bytes → %r", len(audio_bytes), transcribed_text[:80])
            if not transcribed_text:
                twilio.send_text(
                    sender,
                    "Je n'ai pas pu transcrire ton vocal 😕. Réessaye ou écris-moi.",
                )
                return

        effective_text = transcribed_text or text or ""

        # Run the agent.
        out = coach.handle_turn(
            TurnInput(
                user_id=user_id,
                text=effective_text,
                photo_bytes=photo_bytes,
                photo_media_type=photo_media_type,
            )
        )
        log.info("user=%s tools=%s reply_len=%d", user_id, out.tool_calls, len(out.reply_text))

        # Voice OUT — synthesize the reply if the user just spoke to us (or
        # has voice preference). Sent BEFORE the text so the audio lands first
        # in WhatsApp ; we still send the text as a fallback / transcript.
        sent_audio = False
        if is_audio_in and (config.elevenlabs_api_key or config.openai_api_key):
            audio_path = voice_mod.synthesize(
                out.reply_text,
                elevenlabs_key=config.elevenlabs_api_key,
                elevenlabs_voice_id=config.elevenlabs_voice_id,
                openai_key=config.openai_api_key,
            )
            if audio_path and config.public_url:
                token = voice_mod.audio_token(audio_path)
                audio_url = f"{config.public_url.rstrip('/')}/audio/{token}"
                try:
                    twilio.send_media(sender, audio_url, "")
                    sent_audio = True
                except Exception as exc:  # noqa: BLE001
                    log.exception("failed to send audio reply: %s", exc)

        # Send the text reply (always, as transcript + safety net).
        twilio.send_text(sender, out.reply_text)
        for chart_url, caption in zip(out.media_urls, out.media_captions):
            try:
                twilio.send_media(sender, chart_url, caption)
            except Exception as exc:  # noqa: BLE001
                log.exception("failed to send chart %s: %s", chart_url, exc)

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
