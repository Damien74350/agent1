"""Voice in (Whisper transcription) and voice out (ElevenLabs / OpenAI TTS).

Both providers gracefully degrade : if the relevant API key is missing the
helpers return `None`, and the caller falls back to text mode.
"""

from __future__ import annotations

import logging
import os
import secrets
from pathlib import Path

import httpx

log = logging.getLogger("calo.voice")


AUDIO_DIR = Path(os.environ.get("CALO_AUDIO_DIR", "/tmp/calo_audio"))
AUDIO_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# IN — transcription
# ---------------------------------------------------------------------------


def transcribe(
    audio_bytes: bytes,
    content_type: str = "audio/ogg",
    api_key: str = "",
) -> str | None:
    """Send audio to OpenAI Whisper, return the transcript text.

    Returns None if no API key is set or the call fails — the caller should
    then fall back to text mode (apologize to the user).
    """
    api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        log.info("transcribe: no OPENAI_API_KEY, skipping")
        return None
    suffix = _suffix_for(content_type)
    try:
        with httpx.Client(timeout=60.0) as client:
            files = {"file": (f"audio{suffix}", audio_bytes, content_type)}
            data = {"model": "whisper-1", "language": "fr"}
            r = client.post(
                "https://api.openai.com/v1/audio/transcriptions",
                headers={"Authorization": f"Bearer {api_key}"},
                files=files,
                data=data,
            )
            r.raise_for_status()
            return r.json().get("text", "").strip()
    except Exception as exc:  # noqa: BLE001
        log.exception("whisper transcription failed: %s", exc)
        return None


# ---------------------------------------------------------------------------
# OUT — synthesis
# ---------------------------------------------------------------------------


def synthesize(
    text: str,
    elevenlabs_key: str = "",
    elevenlabs_voice_id: str = "",
    openai_key: str = "",
) -> Path | None:
    """Generate an MP3 file for `text` and return its path on disk.

    Prefers ElevenLabs (premium voice, French). Falls back to OpenAI TTS if
    ElevenLabs is not configured. Returns None if neither is available.

    The caller is responsible for exposing the file via the FastAPI endpoint
    and dispatching to Twilio via send_media.
    """
    text = text.strip()
    if not text:
        return None
    # WhatsApp / WhatsApp+Twilio audio messages cap around ~16 MB ; for voice
    # we also want to keep replies sane (under ~60s of speech).
    if len(text) > 1800:
        text = text[:1800].rsplit(".", 1)[0] + "."

    elevenlabs_key = elevenlabs_key or os.environ.get("ELEVENLABS_API_KEY", "")
    elevenlabs_voice_id = elevenlabs_voice_id or os.environ.get(
        "ELEVENLABS_VOICE_ID", "EXAVITQu4vr4xnSDxMaL"  # default to "Charlotte"
    )
    openai_key = openai_key or os.environ.get("OPENAI_API_KEY", "")

    if elevenlabs_key:
        path = _synthesize_elevenlabs(text, elevenlabs_key, elevenlabs_voice_id)
        if path:
            return path
    if openai_key:
        return _synthesize_openai(text, openai_key)
    log.info("synthesize: no voice API configured, skipping")
    return None


def _synthesize_elevenlabs(
    text: str,
    api_key: str,
    voice_id: str,
) -> Path | None:
    try:
        with httpx.Client(timeout=60.0) as client:
            r = client.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
                headers={
                    "xi-api-key": api_key,
                    "Content-Type": "application/json",
                    "Accept": "audio/mpeg",
                },
                json={
                    "text": text,
                    "model_id": "eleven_multilingual_v2",
                    "voice_settings": {
                        "stability": 0.45,
                        "similarity_boost": 0.75,
                        "style": 0.2,
                        "use_speaker_boost": True,
                    },
                },
            )
            r.raise_for_status()
            return _save_audio(r.content, suffix=".mp3")
    except Exception as exc:  # noqa: BLE001
        log.exception("elevenlabs synthesis failed: %s", exc)
        return None


def _synthesize_openai(text: str, api_key: str) -> Path | None:
    try:
        with httpx.Client(timeout=60.0) as client:
            r = client.post(
                "https://api.openai.com/v1/audio/speech",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "tts-1-hd",
                    "voice": "nova",
                    "input": text,
                    "response_format": "mp3",
                },
            )
            r.raise_for_status()
            return _save_audio(r.content, suffix=".mp3")
    except Exception as exc:  # noqa: BLE001
        log.exception("openai TTS failed: %s", exc)
        return None


def _save_audio(audio_bytes: bytes, suffix: str = ".mp3") -> Path:
    token = secrets.token_urlsafe(16)
    path = AUDIO_DIR / f"{token}{suffix}"
    path.write_bytes(audio_bytes)
    return path


def audio_token(path: Path) -> str:
    """Return the public token (basename without suffix) for an audio file."""
    return path.stem


def _suffix_for(content_type: str) -> str:
    return {
        "audio/ogg": ".ogg",
        "audio/mpeg": ".mp3",
        "audio/mp4": ".m4a",
        "audio/x-m4a": ".m4a",
        "audio/wav": ".wav",
        "audio/webm": ".webm",
    }.get(content_type, ".ogg")
