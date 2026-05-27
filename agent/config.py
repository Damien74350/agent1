import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    api_key: str = field(default_factory=lambda: os.environ.get("ANTHROPIC_API_KEY", ""))
    model: str = field(default_factory=lambda: os.environ.get("AGENT_MODEL", "claude-opus-4-7"))
    effort: str = field(default_factory=lambda: os.environ.get("AGENT_EFFORT", "high"))
    max_tokens: int = field(default_factory=lambda: int(os.environ.get("AGENT_MAX_TOKENS", "32000")))
    workspace: Path = field(
        default_factory=lambda: Path(os.environ.get("AGENT_WORKSPACE", "./workspace")).resolve()
    )
    conversations_dir: Path = field(
        default_factory=lambda: Path("./conversations").resolve()
    )

    def __post_init__(self) -> None:
        if not self.api_key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY is missing. Copy .env.example to .env and set the key."
            )
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.conversations_dir.mkdir(parents=True, exist_ok=True)
