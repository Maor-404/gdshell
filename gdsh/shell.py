"""Interactive GDShell implementation."""

from __future__ import annotations

from pathlib import Path

from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.formatted_text import ANSI
from prompt_toolkit.history import FileHistory
from prompt_toolkit.lexers import PygmentsLexer
from pygments.lexers.shell import BashLexer

from gdsh.commands import CommandRegistry
from gdsh.parser import parse_command
from gdsh.rust_bridge import RustBackend


class GDSHCompleter(Completer):
    """Autocomplete for built-in/custom commands and local files."""

    def __init__(self, registry: CommandRegistry) -> None:
        self.registry = registry

    def get_completions(self, document, complete_event):  # type: ignore[override]
        text = document.text_before_cursor
        parts = text.strip().split()
        if len(parts) <= 1:
            current = parts[0] if parts else ""
            for cmd in self.registry.list_command_names():
                if cmd.startswith(current):
                    yield Completion(cmd, start_position=-len(current))
        else:
            current = parts[-1]
            for entry in Path(".").iterdir():
                name = entry.name + ("/" if entry.is_dir() else "")
                if name.startswith(current):
                    yield Completion(name, start_position=-len(current))


class GDShell:
    """Main event loop and command dispatch for GDSH."""

    def __init__(self, project_root: Path) -> None:
        self.registry = CommandRegistry(project_root)
        self.rust_backend = RustBackend(project_root)
        self.rust_backend.ensure_available()
        history_path = project_root / ".gdsh_history"
        self.session = PromptSession(
            completer=GDSHCompleter(self.registry),
            history=FileHistory(str(history_path)),
            auto_suggest=AutoSuggestFromHistory(),
            lexer=PygmentsLexer(BashLexer),
        )

    async def run(self) -> None:
        """Run the interactive shell until exit."""
        while True:
            prompt = ANSI(f"\x1b[1;36mgdsh\x1b[0m:\x1b[1;33m{Path.cwd().name}\x1b[0m$ ")
            try:
                line = await self.session.prompt_async(prompt)
            except (EOFError, KeyboardInterrupt):
                break

            command, args = parse_command(line, backend=self.rust_backend)
            if not command:
                continue
            try:
                output = await self._dispatch(command, args)
            except Exception as exc:  # noqa: BLE001
                print(f"Error: {exc}")
                continue

            if output == "__EXIT__":
                break
            if output == "__CLEAR__":
                print("\033c", end="")
                continue
            if output:
                print(output)

    async def _dispatch(self, command: str, args: list[str]) -> str:
        try:
            return await self.registry.execute(command, args)
        except ValueError as exc:
            if "Unknown command" not in str(exc):
                raise
        return await self.rust_backend.exec_external(command, args)
