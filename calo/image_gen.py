"""Generate motivational 'vision board' images via OpenAI's image API.

These are ASPIRATIONAL ILLUSTRATIONS — a healthy, athletic representative figure
that embodies the user's goal — NOT a photorealistic deepfake of the user and
NOT a medical prediction. Files are written to a temp dir and served via the
FastAPI `/vision/{token}` endpoint; Twilio fetches them via media_url.

Reuses the existing OPENAI_API_KEY (already configured for voice/Whisper), so
no new provider or billing is introduced.
"""

from __future__ import annotations

import base64
import os
import secrets
from pathlib import Path

import httpx

VISION_DIR = Path(os.environ.get("CALO_VISION_DIR", "/tmp/calo_vision"))
VISION_DIR.mkdir(parents=True, exist_ok=True)

_OPENAI_IMAGE_URL = "https://api.openai.com/v1/images/generations"
_MODEL = os.environ.get("CALO_IMAGE_MODEL", "gpt-image-1")


def _new_token() -> str:
    return secrets.token_urlsafe(16)


def build_vision_prompt(
    goal: str,
    sex: str = "",
    sport_context: str = "",
    extra: str = "",
) -> str:
    """Compose a safe, healthy, aspirational illustration prompt.

    Deliberately generic (a representative figure, never the user's face),
    healthy and non-extreme, to avoid harmful body ideals or deepfakes.
    """
    who = {
        "homme": "a man",
        "femme": "a woman",
    }.get(sex.lower().strip(), "a person")
    sport_bit = f" practising {sport_context}" if sport_context else ""
    return (
        f"A clean, uplifting motivational illustration of {who} with a healthy, "
        f"fit, naturally athletic body, radiating confidence and energy{sport_bit}. "
        f"Goal mood: {goal}. Modern flat vector / poster style, warm lighting, "
        f"deep blue (#1F4E79) and orange (#E07B00) accent palette, plain "
        f"background. Wholesome and realistic body proportions — NOT extreme, NOT "
        f"hypersexualised. No text, no logos, no real or recognisable face. "
        f"{extra}"
    ).strip()


def generate_vision_board(
    prompt: str,
    api_key: str | None = None,
    size: str = "1024x1024",
    timeout: float = 60.0,
) -> tuple[str, Path] | None:
    """Generate one image and persist it. Returns (token, path) or None on error.

    Never raises — callers degrade gracefully to a text projection.
    """
    key = api_key or os.environ.get("OPENAI_API_KEY", "")
    if not key:
        return None
    try:
        resp = httpx.post(
            _OPENAI_IMAGE_URL,
            headers={"Authorization": f"Bearer {key}"},
            json={
                "model": _MODEL,
                "prompt": prompt,
                "n": 1,
                "size": size,
            },
            timeout=timeout,
        )
        resp.raise_for_status()
        data = resp.json()["data"][0]
        if data.get("b64_json"):
            raw = base64.b64decode(data["b64_json"])
        elif data.get("url"):
            img = httpx.get(data["url"], timeout=timeout)
            img.raise_for_status()
            raw = img.content
        else:
            return None
        token = _new_token()
        path = VISION_DIR / f"{token}.png"
        path.write_bytes(raw)
        return token, path
    except Exception:  # noqa: BLE001 — degrade gracefully
        return None
