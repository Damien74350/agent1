"""Local CLI to chat with Calo directly from the terminal.

Usage: python -m calo.cli [--reset]

This bypasses Twilio entirely — useful for iterating on prompts before deploying.
Photos can be passed inline by typing  `photo:/path/to/image.jpg  <optional text>`.
"""

import argparse
import base64
import sys
from pathlib import Path

from rich.console import Console
from rich.markdown import Markdown

from .coach import CaloCoach, TurnInput
from .config import CaloConfig

console = Console()

LOCAL_TEST_NUMBER = "whatsapp:+33000000000"


def main() -> int:
    parser = argparse.ArgumentParser(description="Chat with Calo locally")
    parser.add_argument("--reset", action="store_true", help="Wipe the test user's history")
    args = parser.parse_args()

    config = CaloConfig()
    try:
        config.require_anthropic()
    except RuntimeError as exc:
        console.print(f"[red]{exc}[/red]")
        return 1
    if not config.photo_encryption_key:
        console.print(
            "[yellow]Warning: CALO_PHOTO_ENCRYPTION_KEY missing — photos won't be persisted.[/yellow]"
        )

    coach = CaloCoach(config)
    user = coach.db.get_or_create_user(LOCAL_TEST_NUMBER)

    if args.reset:
        coach.messages.clear(user["id"])
        coach.db.update_user(
            user["id"],
            name=None,
            age=None,
            sex=None,
            height_cm=None,
            current_weight_kg=None,
            activity_level=None,
            goal=None,
            target_weight_kg=None,
            onboarding_complete=False,
            photo_consent=False,
        )
        console.print(
            "[cyan]Reset done. (Airtable profile cleared, conversation history wiped. "
            "Meals/weights/photos in Airtable are NOT deleted — go to Airtable UI if you want.)[/cyan]"
        )

    console.print("[bold cyan]Calo (local CLI)[/bold cyan] — Ctrl-C pour quitter")
    console.print(f"[dim]model: {config.model} · effort: {config.effort}[/dim]\n")

    while True:
        try:
            line = console.input("[bold green]you ❯[/bold green] ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\nbye")
            return 0
        if not line:
            continue

        text = line
        photo_bytes = None
        if line.startswith("photo:"):
            rest = line[6:].strip()
            parts = rest.split(maxsplit=1)
            photo_path = Path(parts[0])
            text = parts[1] if len(parts) > 1 else ""
            if not photo_path.exists():
                console.print(f"[red]File not found: {photo_path}[/red]")
                continue
            photo_bytes = photo_path.read_bytes()
            console.print(f"[dim]📸 attached {photo_path} ({len(photo_bytes)} bytes)[/dim]")

        try:
            out = coach.handle_turn(
                TurnInput(user_id=user["id"], text=text, photo_bytes=photo_bytes)
            )
        except KeyboardInterrupt:
            console.print("[yellow]interrupted[/yellow]")
            continue
        except Exception as exc:  # noqa: BLE001
            console.print(f"[red]{type(exc).__name__}: {exc}[/red]")
            continue

        if out.tool_calls:
            console.print(f"[dim]⚙  {', '.join(out.tool_calls)}[/dim]")
        console.print()
        console.print(Markdown(out.reply_text))
        console.print()


if __name__ == "__main__":
    sys.exit(main())
