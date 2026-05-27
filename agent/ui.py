from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text

console = Console()


def banner(model: str, workspace: str) -> None:
    title = Text("Agent1", style="bold cyan")
    body = Text.assemble(
        ("model: ", "dim"), (f"{model}\n", "white"),
        ("workspace: ", "dim"), (f"{workspace}\n", "white"),
        ("commands: ", "dim"),
        ("/help  /clear  /save [name]  /load <name>  /quit", "yellow"),
    )
    console.print(Panel.fit(body, title=title, border_style="cyan"))


def help_text() -> None:
    console.print(
        Panel.fit(
            "[bold]/help[/bold]            show this help\n"
            "[bold]/clear[/bold]           reset conversation history\n"
            "[bold]/save [name][/bold]     save conversation (auto-name if omitted)\n"
            "[bold]/load <name>[/bold]     load a saved conversation\n"
            "[bold]/quit[/bold] or /exit   leave the session",
            title="Commands",
            border_style="yellow",
        )
    )


def user_prompt() -> str:
    return console.input("[bold green]you ❯[/bold green] ")


def show_tool_call(name: str, inp: dict) -> None:
    preview = ", ".join(f"{k}={_truncate(v)}" for k, v in inp.items())
    console.print(f"[dim]⚙  {name}({preview})[/dim]")


def show_assistant(text: str) -> None:
    if not text.strip():
        return
    console.print()
    console.print(Markdown(text))
    console.print()


def show_info(message: str) -> None:
    console.print(f"[cyan]ℹ  {message}[/cyan]")


def show_error(message: str) -> None:
    console.print(f"[red]✖  {message}[/red]")


def _truncate(value, limit: int = 60) -> str:
    text = repr(value)
    return text if len(text) <= limit else text[: limit - 1] + "…"
