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

    @router.get("/home")
    def home(user_id: Annotated[str, Depends(current_user_id)]) -> dict[str, Any]:
        """All-in-one dashboard payload: today macros, streak, recent activity
        heatmap (30 days), an insight, the latest weight delta."""
        from datetime import datetime, timezone, timedelta

        now = datetime.now(timezone.utc)
        user = coach.db.get_user_by_id(user_id) or {}
        today_iso = now.strftime("%Y-%m-%d")

        # Today macros
        meals_today = coach.db.meals_for_day(user_id, today_iso)
        consumed = {
            "kcal": sum(int(m.get("total_calories") or 0) for m in meals_today),
            "protein": sum(int(m.get("total_protein_g") or 0) for m in meals_today),
            "carbs": sum(int(m.get("total_carbs_g") or 0) for m in meals_today),
            "fat": sum(int(m.get("total_fat_g") or 0) for m in meals_today),
        }
        targets = {
            "kcal": int(user.get("daily_calories") or 0),
            "protein": int(user.get("daily_protein_g") or 0),
            "carbs": int(user.get("daily_carbs_g") or 0),
            "fat": int(user.get("daily_fat_g") or 0),
        }

        # 30-day activity heatmap (any meal logged on a given day → counts)
        since = (now - timedelta(days=29)).strftime("%Y-%m-%d")
        try:
            recent_meals = coach.db.meals_since(user_id, since)
        except Exception:
            recent_meals = []
        active_days: set[str] = set()
        for m in recent_meals:
            day = (m.get("eaten_at") or "")[:10]
            if day:
                active_days.add(day)
        heatmap = []
        cur = now - timedelta(days=29)
        while cur.date() <= now.date():
            d = cur.strftime("%Y-%m-%d")
            heatmap.append({"date": d, "active": d in active_days})
            cur += timedelta(days=1)

        # Streak: contiguous active days ending today (or yesterday if no log today yet)
        streak = 0
        cursor = now.date()
        if today_iso not in active_days:
            cursor -= timedelta(days=1)
        while cursor.strftime("%Y-%m-%d") in active_days:
            streak += 1
            cursor -= timedelta(days=1)

        # Weight delta (latest vs 30 days ago)
        weights = coach.db.weights_history(user_id, limit=60)
        weight_delta = None
        latest_kg = None
        if weights:
            latest_kg = weights[0].get("weight_kg")
            if len(weights) >= 2:
                oldest_kg = weights[-1].get("weight_kg")
                if latest_kg is not None and oldest_kg is not None:
                    weight_delta = round(latest_kg - oldest_kg, 1)

        # Friendly greeting tied to the hour
        hour = now.hour
        first = (user.get("name") or "").split(" ")[0]
        if 5 <= hour < 11:
            greeting = f"Bonjour {first}".strip() + " ☀️"
        elif 11 <= hour < 14:
            greeting = f"Salut {first}".strip() + " 👋"
        elif 14 <= hour < 18:
            greeting = f"Hello {first}".strip() + " 💪"
        elif 18 <= hour < 23:
            greeting = f"Bonsoir {first}".strip() + " 🌙"
        else:
            greeting = f"Coucou {first}".strip() + " ✨"

        # Pick a contextual insight (a tiny rule engine — no LLM call here).
        insight = _build_insight(consumed, targets, streak, weight_delta, user, len(meals_today))

        return {
            "greeting": greeting,
            "today": {
                "consumed": consumed,
                "targets": targets,
                "meals_count": len(meals_today),
            },
            "streak": streak,
            "heatmap_30d": heatmap,
            "weight": {"latest_kg": latest_kg, "delta_30d_kg": weight_delta},
            "goal": user.get("goal") or "",
            "insight": insight,
        }

    @router.get("/knowledge/search")
    def knowledge_search(
        user_id: Annotated[str, Depends(current_user_id)],
        q: str = "",
        limit: int = 8,
    ) -> dict[str, Any]:
        """Search the Calo knowledge base — feeds the in-app search bar."""
        q = (q or "").strip()
        if not q:
            return {"hits": []}
        try:
            hits = coach.db.search_knowledge(q, max_results=max(1, min(limit, 20)))
        except Exception:
            hits = []
        out = []
        for h in hits:
            text = (h.get("content") or "").strip()
            out.append({
                "title": h.get("title", ""),
                "topic": h.get("topic", ""),
                "snippet": text[:240] + ("…" if len(text) > 240 else ""),
            })
        return {"hits": out}

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
        try:
            out = coach.handle_turn(
                TurnInput(
                    user_id=user_id,
                    text=body.text or "",
                    photo_bytes=photo_bytes,
                    photo_media_type=body.image_media_type,
                )
            )
        except Exception as exc:  # noqa: BLE001
            log.exception("app /chat failed: %s", exc)
            return {
                "reply": (
                    "Désolé, j'ai eu un souci technique en traitant ton message. "
                    "Réessaye dans un instant 🙏"
                ),
                "tool_calls": [],
                "media": [],
                "error": str(exc)[:200],
            }
        return {
            "reply": str(out.reply_text or "…"),
            "tool_calls": list(out.tool_calls or []),
            "media": [{"url": u, "caption": c}
                      for u, c in zip(out.media_urls, out.media_captions)],
        }

    return router


def _build_insight(
    consumed: dict[str, int],
    targets: dict[str, int],
    streak: int,
    weight_delta: float | None,
    user: dict[str, Any],
    meals_count: int,
) -> dict[str, str]:
    """Tiny rule-based insight engine — never blocks on an LLM, always cheerful,
    always actionable. Returns {title, body, icon}."""
    kcal_t = targets.get("kcal") or 0
    kcal_c = consumed.get("kcal") or 0
    prot_t = targets.get("protein") or 0
    prot_c = consumed.get("protein") or 0
    name = (user.get("name") or "").split(" ")[0] or "champion"

    if streak >= 7:
        return {
            "icon": "🔥",
            "title": f"{streak} jours de suite",
            "body": f"{name}, t'es en feu. La régularité bat l'intensité — continue exactement comme ça.",
        }
    if not user.get("onboarding_complete"):
        return {
            "icon": "🎯",
            "title": "Démarre ton profil",
            "body": "Pose-moi tes infos (poids, objectif, dispo sport) et je calibre ton plan sur-mesure.",
        }
    if kcal_t and kcal_c == 0:
        return {
            "icon": "🍽️",
            "title": "Pas encore de repas aujourd'hui",
            "body": "Envoie une photo de ton prochain repas, je l'analyse direct.",
        }
    if kcal_t and kcal_c < kcal_t * 0.4 and meals_count <= 1:
        return {
            "icon": "⚡",
            "title": "Énergie un peu basse",
            "body": f"Tu en es à {kcal_c} / {kcal_t} kcal. Une collation protéinée maintenant éviterait le craquage du soir.",
        }
    if kcal_t and kcal_c > kcal_t * 1.05:
        return {
            "icon": "🚶",
            "title": "Petit débord aujourd'hui",
            "body": "Une marche de 30 min compense très bien — et tu reviens en kiff demain.",
        }
    if prot_t and prot_c < prot_t * 0.5:
        return {
            "icon": "💪",
            "title": "Protéines à booster",
            "body": f"Tu es à {prot_c} g / {prot_t} g. Œufs, yaourt grec, poulet, légumineuses — pioche.",
        }
    if weight_delta is not None and weight_delta <= -0.5:
        return {
            "icon": "📉",
            "title": f"-{abs(weight_delta)} kg sur 30 jours",
            "body": "Progression saine. On garde le rythme et on ajoute du sommeil de qualité.",
        }
    if weight_delta is not None and weight_delta >= 0.5:
        return {
            "icon": "📈",
            "title": f"+{weight_delta} kg sur 30 jours",
            "body": "Si c'est de la masse → top. Sinon on regarde ensemble sommeil, stress et fenêtres glucidiques.",
        }
    return {
        "icon": "✨",
        "title": "Une petite action aujourd'hui",
        "body": "Hydratation, marche, sommeil : choisis-en une et écris-la moi, je te tiens responsable.",
    }


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
