import subprocess
from pathlib import Path

from anthropic import beta_tool


def build_tools(workspace: Path):
    """Return tool functions bound to a sandboxed workspace directory."""

    def _resolve(relative: str) -> Path:
        target = (workspace / relative).resolve()
        if workspace not in target.parents and target != workspace:
            raise ValueError(f"Path {relative!r} escapes the workspace sandbox.")
        return target

    @beta_tool
    def read_file(path: str) -> str:
        """Read a UTF-8 text file from the workspace.

        Args:
            path: Path relative to the workspace root.
        """
        target = _resolve(path)
        if not target.exists():
            return f"Error: {path} does not exist."
        if not target.is_file():
            return f"Error: {path} is not a file."
        try:
            return target.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return f"Error: {path} is not a UTF-8 text file."

    @beta_tool
    def write_file(path: str, content: str) -> str:
        """Write (or overwrite) a UTF-8 text file in the workspace.

        Args:
            path: Path relative to the workspace root.
            content: Full file contents to write.
        """
        target = _resolve(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return f"Wrote {len(content)} chars to {path}."

    @beta_tool
    def list_dir(path: str = ".") -> str:
        """List directory entries under the workspace.

        Args:
            path: Directory path relative to the workspace root (defaults to root).
        """
        target = _resolve(path)
        if not target.exists():
            return f"Error: {path} does not exist."
        if not target.is_dir():
            return f"Error: {path} is not a directory."
        entries = []
        for child in sorted(target.iterdir()):
            kind = "dir " if child.is_dir() else "file"
            size = child.stat().st_size if child.is_file() else 0
            entries.append(f"{kind}  {size:>10}  {child.name}")
        return "\n".join(entries) if entries else "(empty)"

    @beta_tool
    def run_bash(command: str, timeout: int = 60) -> str:
        """Execute a bash command inside the workspace directory.

        Args:
            command: The bash command to execute.
            timeout: Max execution time in seconds (default 60).
        """
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=workspace,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            return f"Error: command timed out after {timeout}s."
        parts = [f"exit_code: {result.returncode}"]
        if result.stdout:
            parts.append(f"stdout:\n{result.stdout}")
        if result.stderr:
            parts.append(f"stderr:\n{result.stderr}")
        return "\n".join(parts)

    return [read_file, write_file, list_dir, run_bash]
