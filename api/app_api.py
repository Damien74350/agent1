"""App-facing JSON API for the Calo mobile app (iOS/Android).

This sits alongside the Twilio WhatsApp webhook and reuses the SAME Calo brain
(`CaloCoach`) and the SAME user records, so a client can talk to Calo through
the app OR through WhatsApp interchangeably — both keyed on the phone number.

Auth: phone number + 6-digit OTP (sent by SMS via Twilio; in dev, logged).
On success we issue a stateless HMAC-signed bearer token carrying the user id.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import logging
import secrets
import threading
import time
from typing import Annotated, Any

from fastapi import APIRouter, Body, Depends, Header, HTTPException
from pydantic import BaseModel

from calo.coach import CaloCoach, TurnInput
from calo.config import CaloConfig

log = logging.getLogger("calo.app_api")

# OTPs live in-memory: {phone: (code_hash, expires_at, attempts)}.
# Good enough for launch (single worker). Move to Redis/Airtable if scaling out.
_OTP_STORE: dict[str, tuple[str, float, int]] = {}
_OTP_LOCK = threading.Lock()
_OTP_TTL = 300  # 5 min
_OTP_MAX_ATTEMPTS = 5
_TOKEN_TTL = 60 * 60 * 24 * 60  # 60 days


def _app_secret(config: CaloConfig) -> bytes:
    """Signing key for tokens. Prefer an explicit secret, fall back to existing."""
    import os

    secret = (
        os.environ.get("CALO_APP_SECRET")
        or config.photo_encryption_key
        or config.anthropic_api_key
        or "calo-dev-secret-change-me"
    )
    return hashlib.sha256(secret.encode("utf-8")).digest()


def _normalize_phone(raw: str) -> str:
    """Return an E.164-ish '+41...' string. Keep it strict but forgiving."""
    cleaned = "".join(c for c in raw.strip() if c.isdigit() or c == "+")
    if not cleaned.startswith("+"):
        cleaned = "+" + cleaned
    if len(cleaned) < 8:
        raise HTTPException(status_code=400, detail="invalid phone number")
    return cleaned


def _whatsapp_id(phone: str) -> str:
    """The backend keys users on 'whatsapp:+...'; we reuse it so the app and
    WhatsApp resolve to the SAME user record."""
    return f"whatsapp:{phone}"


def _issue_token(user_id: str, secret: bytes) -> str:
    issued = str(int(time.time()))
    payload = f"{user_id}|{issued}"
    sig = hmac.new(secret, payload.encode(), hashlib.sha256).hexdigest()
    raw = f"{payload}|{sig}"
    return base64.urlsafe_b64encode(raw.encode()).decode()


def _verify_token(token: str, secret: bytes) -> str:
    try:
        raw = base64.urlsafe_b64decode(token.encode()).decode()
        user_id, issued, sig = raw.split("|")
    except Exception:
        raise HTTPException(status_code=401, detail="invalid token")
    expected = hmac.new(secret, f"{user_id}|{issued}".encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(sig, expected):
        raise HTTPException(status_code=401, detail="invalid token")
    if int(time.time()) - int(issued) > _TOKEN_TTL:
        raise HTTPException(status_code=401, detail="token expired")
    return user_id


# ---- request/response models -------------------------------------------------

class AuthStart(BaseModel):
    phone: str


class AuthVerify(BaseModel):
    phone: str
    code: str


class ChatIn(BaseModel):
    text: str = ""
    image_base64: str | None = None
    image_media_type: str = "image/jpeg"


def build_app_router(coach: CaloCoach, twilio: Any, config: CaloConfig) -> APIRouter:
    router = APIRouter(prefix="/app", tags=["app"])
    secret = _app_secret(config)

    def current_user_id(authorization: Annotated[str | None, Header()] = None) -> str:
        if not authorization or not authorization.lower().startswith("bearer "):
            raise HTTPException(status_code=401, detail="missing bearer token")
        return _verify_token(authorization.split(" ", 1)[1].strip(), secret)

    @router.post("/auth/start")
    def auth_start(body: AuthStart) -> dict[str, Any]:
        phone = _normalize_phone(body.phone)
        code = f"{secrets.randbelow(1_000_000):06d}"
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        _OTP_STORE[phone] = (code_hash, time.time() + _OTP_TTL, 0)

        sms_from = getattr(config, "twilio_sms_from", "") or ""
        body_txt = f"Ton code Calo : {code} (valable 5 min)."
        sent = False
        if twilio is not None and sms_from:
            try:
                twilio.client.messages.create(from_=sms_from, to=phone, body=body_txt)
                sent = True
            except Exception as exc:  # noqa: BLE001
                log.warning("SMS send failed for %s: %s", phone, exc)
        if not sent:
            # Dev / no SMS configured: log it so we can still test end-to-end.
            log.info("OTP for %s = %s (no SMS sender configured)", phone, code)
        return {"sent": sent, "dev_hint": None if sent else "OTP logged server-side"}

    @router.post("/auth/verify")
    def auth_verify(body: AuthVerify) -> dict[str, Any]:
        phone = _normalize_phone(body.phone)
        with _OTP_LOCK:
            entry = _OTP_STORE.get(phone)
            if not entry:
                raise HTTPException(status_code=400, detail="no code requested")
            code_hash, expires_at, attempts = entry
            if time.time() > expires_at:
                _OTP_STORE.pop(phone, None)
                raise HTTPException(status_code=400, detail="code expired")
            if attempts >= _OTP_MAX_ATTEMPTS:
                _OTP_STORE.pop(phone, None)
                raise HTTPException(status_code=429, detail="too many attempts")
            if not hmac.compare_digest(
                code_hash, hashlib.sha256(body.code.strip().encode()).hexdigest()
            ):
                _OTP_STORE[phone] = (code_hash, expires_at, attempts + 1)
                raise HTTPException(status_code=401, detail="wrong code")
            _OTP_STORE.pop(phone, None)

        user = coach.db.get_or_create_user(_whatsapp_id(phone))
        token = _issue_token(user["id"], secret)
        return {"token": token, "user": _public_user(user)}

    @router.get("/me")
    def me(user_id: Annotated[str, Depends(current_user_id)]) -> dict[str, Any]:
        return {"user": _public_user(coach.db.get_user_by_id(user_id))}

    @router.get("/profile")
    def profile(user_id: Annotated[str, Depends(current_user_id)]) -> dict[str, Any]:
        return {"user": _public_user(coach.db.get_user_by_id(user_id))}

    @router.get("/progress")
    def progress(user_id: Annotated[str, Depends(current_user_id)]) -> dict[str, Any]:
        from datetime import datetime, timezone

        weights = coach.db.weights_history(user_id, limit=60)
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        meals = coach.db.meals_for_day(user_id, today)
        consumed = sum(int(m.get("total_calories") or 0) for m in meals)
        user = coach.db.get_user_by_id(user_id)
        target = int(user.get("daily_calories") or 0)
        return {
            "weights": [
                {"kg": w.get("weight_kg"), "at": w.get("logged_at")}
                for w in weights if w.get("weight_kg") is not None
            ],
            "today": {"consumed_kcal": consumed, "target_kcal": target,
                      "remaining_kcal": max(0, target - consumed) if target else None},
            "meals_today": len(meals),
        }

    @router.post("/chat")
    def chat(
        user_id: Annotated[str, Depends(current_user_id)],
        body: ChatIn = Body(...),
    ) -> dict[str, Any]:
        photo_bytes = None
        if body.image_base64:
            try:
                photo_bytes = base64.b64decode(body.image_base64)
            except Exception:
                raise HTTPException(status_code=400, detail="invalid image_base64")
        out = coach.handle_turn(
            TurnInput(
                user_id=user_id,
                text=body.text or "",
                photo_bytes=photo_bytes,
                photo_media_type=body.image_media_type,
            )
        )
        return {
            "reply": out.reply_text,
            "tool_calls": out.tool_calls,
            "media": [{"url": u, "caption": c}
                      for u, c in zip(out.media_urls, out.media_captions)],
        }

    return router


def _public_user(user: dict[str, Any]) -> dict[str, Any]:
    """Whitelist the fields we expose to the app (never leak internal blobs)."""
    if not user:
        return {}
    keys = [
        "id", "name", "sex", "age", "height_cm", "weight_kg", "target_weight_kg",
        "goal", "activity_level", "daily_calories", "daily_protein_g",
        "daily_carbs_g", "daily_fat_g", "onboarding_complete",
    ]
    return {k: user.get(k) for k in keys if k in user}
