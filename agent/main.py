import sys

from . import ui
from .config import Config
from .core import Agent


def run() -> int:
    try:
        config = Config()
    except RuntimeError as exc:
        ui.show_error(str(exc))
        return 1

    agent = Agent(config)
    ui.banner(model=config.model, workspace=str(config.workspace))

    while True:
        try:
            line = ui.user_prompt()
        except (EOFError, KeyboardInterrupt):
            ui.show_info("bye")
            return 0

        line = line.strip()
        if not line:
            continue

        if line.startswith("/"):
            if _handle_command(agent, line):
                return 0
            continue

        try:
            text = agent.chat(line, on_tool=ui.show_tool_call)
            ui.show_assistant(text)
        except KeyboardInterrupt:
            ui.show_info("interrupted")
        except Exception as exc:  # noqa: BLE001
            ui.show_error(f"{type(exc).__name__}: {exc}")


def _handle_command(agent: Agent, line: str) -> bool:
    """Return True when the loop should exit."""
    parts = line.split(maxsplit=1)
    cmd = parts[0].lower()
    arg = parts[1] if len(parts) > 1 else ""

    if cmd in ("/quit", "/exit"):
        ui.show_info("bye")
        return True
    if cmd == "/help":
        ui.help_text()
        return False
    if cmd == "/clear":
        agent.reset()
        ui.show_info("history cleared")
        return False
    if cmd == "/save":
        path = agent.save(arg or None)
        ui.show_info(f"saved to {path}")
        return False
    if cmd == "/load":
        if not arg:
            ui.show_error("usage: /load <name>")
            return False
        try:
            agent.load(arg)
            ui.show_info(f"loaded {arg}")
        except FileNotFoundError:
            ui.show_error(f"no such conversation: {arg}")
        return False

    ui.show_error(f"unknown command: {cmd}")
    return False


if __name__ == "__main__":
    sys.exit(run())
