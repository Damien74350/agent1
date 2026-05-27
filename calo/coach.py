"""Calo coach — the agent that handles one turn of the conversation."""

import base64
import json
from dataclasses import dataclass
from typing import Any

import anthropic

from .config import CaloConfig
from .db import Database
from .prompts import SYSTEM_PROMPT
from .storage import PhotoStore
from .tools import build_tools


@dataclass
class TurnInput:
    user_id: int
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
        self.config = config
        self.client = anthropic.Anthropic(api_key=config.anthropic_api_key)
        self.db = Database(config.db_path)
        self.photos = (
            PhotoStore(config.photos_dir, config.photo_encryption_key)
            if config.photo_encryption_key
            else None
        )

    def handle_turn(self, turn: TurnInput) -> TurnOutput:
        """Process one inbound message + (optional) photo, persist everything,
        return assistant text reply."""

        # 1. Persist incoming photo if present (encrypted).
        photo_path: str | None = None
        if turn.photo_bytes:
            if not self.photos:
                # Fail soft — agent will still try to analyze the image even without
                # persistence — but we warn so the operator sets the key.
                photo_path = None
            else:
                ext = "jpg" if turn.photo_media_type == "image/jpeg" else "png"
                # We don't know yet if the photo is a meal or body shot; tag generically.
                # The agent's tool call (`log_meal` vs `log_body_photo`) records the
                # semantic category in the right table.
                photo_path = self.photos.save(
                    turn.photo_bytes, kind="meal", user_id=turn.user_id, ext=ext
                )

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
        self.db.add_message(turn.user_id, "user", user_content)
        history = self.db.recent_messages(turn.user_id, limit=40)

        # 4. Bind tools for this turn.
        tools = build_tools(self.db, turn.user_id, photo_path)

        # 5. Inject user state context as a system reminder so the agent knows
        #    where the user is at without us re-prompting the cached system text.
        user = self.db.get_user_by_id(turn.user_id)
        state_summary = _summarize_user_state(user)
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

        # 7. Persist the full assistant trajectory (text + tool_use/tool_result blocks).
        assistant_content = _serialize(runner.messages[-1].content) if runner.messages else []
        self.db.add_message(turn.user_id, "assistant", assistant_content)

        return TurnOutput(reply_text=final_text or "…", tool_calls=tool_calls_taken)


def _serialize(blocks) -> list[dict[str, Any]]:
    out = []
    for b in blocks:
        if isinstance(b, dict):
            out.append(b)
        else:
            out.append(b.model_dump(exclude_none=True))
    return out


def _summarize_user_state(user: dict[str, Any]) -> str:
    if not user.get("onboarding_complete"):
        collected = []
        for field in ("name", "sex", "age", "height_cm", "weight_kg",
                      "activity_level", "goal", "photo_consent"):
            if user.get(field) not in (None, ""):
                collected.append(field)
        missing = [
            f for f in ("name", "sex", "age", "height_cm", "weight_kg",
                        "activity_level", "goal")
            if not user.get(f)
        ]
        return (
            "ONBOARDING IN PROGRESS. "
            f"Collected: {', '.join(collected) or 'nothing yet'}. "
            f"Still missing: {', '.join(missing) or 'photo_consent only'}. "
            "Ask the next missing field naturally, one at a time."
        )
    return (
        f"User: {user.get('name')} ({user.get('sex')}, {user.get('age')}y, "
        f"{user.get('height_cm')}cm, {user.get('weight_kg')}kg). "
        f"Goal: {user.get('goal')} (target: {user.get('target_weight_kg')}kg). "
        f"Daily targets: {user.get('daily_calories')} kcal / "
        f"P:{user.get('daily_protein_g')}g C:{user.get('daily_carbs_g')}g "
        f"F:{user.get('daily_fat_g')}g. "
        f"Photo consent: {'yes' if user.get('photo_consent') else 'no'}. "
        f"Restrictions: {user.get('restrictions') or 'none'}."
    )


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
    reminder = {"type": "text", "text": f"<state_reminder>\n{state}\n</state_reminder>"}
    return history[:-1] + [{"role": "user", "content": [reminder, *content]}]
