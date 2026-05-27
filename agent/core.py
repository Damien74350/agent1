import json
from datetime import datetime
from pathlib import Path
from typing import Any

import anthropic

from .config import Config
from .tools import build_tools

SYSTEM_PROMPT = """You are a capable general-purpose assistant agent.

You operate inside a sandboxed workspace directory and have file, shell, and web tools \
to accomplish tasks autonomously. Follow these principles:

- Think carefully before acting. Use tools when they materially help; otherwise respond directly.
- When editing code or files, read first, then modify. Prefer precise, minimal changes.
- For shell commands, prefer safe, reversible operations. Explain destructive actions before running them.
- For web searches, cite sources by URL.
- Be concise. Don't restate the user's request before answering.
- If you cannot complete a task, say so plainly and propose what's missing.
"""


class Agent:
    def __init__(self, config: Config):
        self.config = config
        self.client = anthropic.Anthropic(api_key=config.api_key)
        self.tools = build_tools(config.workspace)
        self.messages: list[dict[str, Any]] = []

    # ----- conversation lifecycle -----

    def reset(self) -> None:
        self.messages = []

    def save(self, name: str | None = None) -> Path:
        name = name or datetime.now().strftime("conv_%Y%m%d_%H%M%S")
        path = self.config.conversations_dir / f"{name}.json"
        path.write_text(
            json.dumps(
                {"model": self.config.model, "messages": _serialize(self.messages)},
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        return path

    def load(self, name: str) -> None:
        path = self.config.conversations_dir / (
            name if name.endswith(".json") else f"{name}.json"
        )
        data = json.loads(path.read_text(encoding="utf-8"))
        self.messages = data["messages"]

    # ----- main run loop -----

    def chat(self, user_message: str, on_text=None, on_tool=None) -> str:
        """Send a user message and run the tool-use loop until the agent stops.

        Callbacks:
            on_text(delta_str): receives streaming text deltas.
            on_tool(name, input_dict): called when a tool is about to execute.

        Returns the final assistant text.
        """
        self.messages.append({"role": "user", "content": user_message})

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
            thinking={"type": "adaptive"},
            output_config={"effort": self.config.effort},
            tools=[
                *self.tools,
                {"type": "web_search_20260209", "name": "web_search"},
            ],
            messages=self.messages,
        )

        final_text = ""
        for message in runner:
            for block in message.content:
                if block.type == "text":
                    final_text = block.text
                    if on_text:
                        on_text(block.text)
                elif block.type == "tool_use":
                    if on_tool:
                        on_tool(block.name, block.input)
                elif block.type == "server_tool_use":
                    if on_tool:
                        on_tool(block.name, block.input)

        # Persist the full assistant trajectory (including tool_use blocks)
        # so context is intact for the next turn.
        self.messages = _serialize(runner.messages)
        return final_text


def _serialize(messages) -> list[dict[str, Any]]:
    """Convert SDK message objects to plain dicts for storage / re-sending."""
    out = []
    for msg in messages:
        if isinstance(msg, dict):
            content = msg["content"]
            if isinstance(content, list):
                content = [_block_to_dict(b) for b in content]
            out.append({"role": msg["role"], "content": content})
        else:
            content = msg.content
            if isinstance(content, str):
                out.append({"role": msg.role, "content": content})
            else:
                out.append(
                    {"role": msg.role, "content": [_block_to_dict(b) for b in content]}
                )
    return out


def _block_to_dict(block) -> dict[str, Any]:
    if isinstance(block, dict):
        return block
    # Pydantic model from the SDK
    return block.model_dump(exclude_none=True)
