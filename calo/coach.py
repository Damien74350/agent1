"""Calo coach — the agent that handles one turn of the conversation.

Storage split:
- AirtableDB → user profile, meals, weights, body photos, foods, knowledge
- MessageStore (SQLite) → conversation history (high frequency, low admin value)
- PhotoStore (encrypted disk) → body photo blobs (sensitive biometric data)
"""

import base64
from dataclasses import dataclass
from typing import Any

import anthropic

from .airtable_db import AirtableDB
from .config import CaloConfig
from .message_store import MessageStore
from .prompts import SYSTEM_PROMPT
from .storage import PhotoStore
from .tools import build_tools


@dataclass
class TurnInput:
    user_id: str  # Airtable record ID
    text: str
    photo_bytes: bytes | None = None
    photo_media_type: str = "image/jpeg"


@dataclass
class TurnOutput:
    reply_text: str
    tool_calls: list[str]


class CaloCoach:
    def __init__(self, config: CaloConfig):
        config.require_anthropic()
        config.require_airtable()
        self.config = config
        self.client = anthropic.Anthropic(api_key=config.anthropic_api_key)
        self.db = AirtableDB(config.airtable_pat)
        self.messages = MessageStore(config.db_path)
        self.photos = (
            PhotoStore(config.photos_dir, config.photo_encryption_key)
            if config.photo_encryption_key
            else None
        )

    def handle_turn(self, turn: TurnInput) -> TurnOutput:
        # 1. Persist incoming photo if present (encrypted).
        photo_ref: str | None = None
        if turn.photo_bytes and self.photos:
            ext = "jpg" if "jpeg" in turn.photo_media_type else "png"
            # We don't know yet if it's a meal or body photo; tag generically.
            # The agent's tool call selects the semantic category.
            try:
                photo_ref = self.photos.save(
                    turn.photo_bytes,
                    kind="meal",
                    user_id=hash(turn.user_id) & 0xFFFFFF,
                    ext=ext,
                )
            except Exception:
                photo_ref = None

        # 2. Build the user content block list.
        user_content: list[dict[str, Any]] = []
        if turn.photo_bytes:
            user_content.append(
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": turn.photo_media_type,
                        "data": base64.b64encode(turn.photo_bytes).decode(),
                    },
                }
            )
        if turn.text:
            user_content.append({"type": "text", "text": turn.text})
        if not user_content:
            user_content.append({"type": "text", "text": "(message vide)"})

        # 3. Append to history + reload last N turns.
        self.messages.add(turn.user_id, "user", user_content)
        history = self.messages.recent(turn.user_id, limit=40)

        # 4. Bind tools for this turn.
        tools = build_tools(self.db, turn.user_id, photo_ref)

        # 5. Inject user state context as a system reminder so the agent knows
        #    where the user is at without invalidating the cached system prompt.
        user = self.db.get_user_by_id(turn.user_id)
        memories = self.db.memories_for_user(turn.user_id, limit=30)
        state_summary = _summarize_user_state(user, memories)
        history = _inject_state_reminder(history, state_summary)

        # 6. Run the tool runner loop.
        runner = self.client.beta.messages.tool_runner(
            model=self.config.model,
            max_tokens=self.config.max_tokens,
            system=[
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            output_config={"effort": self.config.effort},
            tools=tools,
            messages=history,
        )

        final_text = ""
        tool_calls_taken: list[str] = []
        for message in runner:
            for block in message.content:
                if block.type == "text":
                    final_text = block.text
                elif block.type == "tool_use":
                    tool_calls_taken.append(block.name)

        # 7. Persist the assistant's final text reply. Tool_use/tool_result blocks
        #    are intentionally dropped from history — keeping them would require
        #    pairing each tool_use with its matching tool_result on the next turn,
        #    which the tool runner already resolved internally. Text-only history
        #    keeps the next turn simple and correct.
        self.messages.add(turn.user_id, "assistant", final_text or "…")

        return TurnOutput(reply_text=final_text or "…", tool_calls=tool_calls_taken)


def _serialize(blocks) -> list[dict[str, Any]]:
    out = []
    for b in blocks:
        if isinstance(b, dict):
            out.append(b)
        else:
            out.append(b.model_dump(exclude_none=True))
    return out


def _summarize_user_state(
    user: dict[str, Any], memories: list[dict[str, Any]] | None = None
) -> str:
    memories = memories or []
    if not user or not user.get("onboarding_complete"):
        collected = [
            f
            for f in (
                "name",
                "sex",
                "age",
                "height_cm",
                "current_weight_kg",
                "activity_level",
                "goal",
            )
            if user.get(f) not in (None, "")
        ]
        missing = [
            f
            for f in (
                "name",
                "sex",
                "age",
                "height_cm",
                "current_weight_kg",
                "activity_level",
                "goal",
            )
            if not user.get(f)
        ]
        return (
            "ONBOARDING_STATUS = INCOMPLET. "
            f"Champs collectés : {', '.join(collected) or 'aucun pour l\\'instant'}. "
            f"Champs manquants : {', '.join(missing) or 'consentement photo uniquement'}. "
            "Pose la PROCHAINE question d'onboarding (UN champ à la fois, naturellement)."
        )
    base = (
        "ONBOARDING_STATUS = COMPLET ✅ — "
        "TU CONNAIS DÉJÀ CET UTILISATEUR. NE redemande JAMAIS son prénom, son sexe, "
        "son âge, sa taille, son poids, son objectif ou ses cibles. Ces infos sont "
        "ci-dessous, utilise-les directement pour répondre.\n"
        f"• Prénom : {user.get('name')}\n"
        f"• Sexe : {user.get('sex')}\n"
        f"• Âge : {user.get('age')} ans\n"
        f"• Taille : {user.get('height_cm')} cm\n"
        f"• Poids actuel : {user.get('current_weight_kg')} kg\n"
        f"• Niveau d'activité : {user.get('activity_level')}\n"
        f"• Objectif : {user.get('goal')} (cible : {user.get('target_weight_kg')} kg)\n"
        f"• Cibles quotidiennes : {user.get('daily_calories')} kcal · "
        f"P:{user.get('daily_protein_g')}g C:{user.get('daily_carbs_g')}g "
        f"F:{user.get('daily_fat_g')}g\n"
        f"• Consentement photo morpho : {'oui' if user.get('photo_consent') else 'non'}\n"
        f"• Restrictions alimentaires : {user.get('restrictions') or 'aucune'}"
    )
    if memories:
        base += "\n\n# CE QUE TU AS RETENU SUR LUI/ELLE (souvenirs long terme)\n"
        base += (
            "Tu as enregistré ces faits au fil des conversations précédentes. "
            "Utilise-les pour personnaliser ta réponse et montrer que tu te souviens. "
            "Si l'utilisateur partage un NOUVEAU fait important, sauvegarde-le via "
            "l'outil `remember`.\n"
        )
        # group by category
        by_cat: dict[str, list[dict[str, Any]]] = {}
        for m in memories:
            by_cat.setdefault(m.get("category") or "divers", []).append(m)
        order = [
            "santé",
            "sport",
            "objectif",
            "préférence",
            "vie pro",
            "vie perso",
            "événement",
            "divers",
        ]
        for cat in order:
            if cat not in by_cat:
                continue
            base += f"\n## {cat}\n"
            for m in by_cat[cat]:
                stars = "★" * int(m.get("importance") or 3)
                base += f"• {m.get('memory')} {stars}\n"
    return base


def _inject_state_reminder(history: list[dict], state: str) -> list[dict]:
    """Prepend a system-reminder block to the last user turn so the model sees
    fresh state without invalidating the cached system prompt."""
    if not history:
        return history
    last = history[-1]
    if last["role"] != "user":
        return history
    content = last["content"]
    if isinstance(content, str):
        content = [{"type": "text", "text": content}]
    reminder = {
        "type": "text",
        "text": f"<state_reminder>\n{state}\n</state_reminder>",
    }
    return history[:-1] + [{"role": "user", "content": [reminder, *content]}]
