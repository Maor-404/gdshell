"""Command implementations and registry for GDSH."""

from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Awaitable, Callable
import xml.etree.ElementTree as ET

from core.gamelib import GameEntry, GameLibrary
from core.idea import generate_idea
from core.ping import ping_once
from core.sysinfo import capture_snapshot
from gdsh.utils import format_table

CommandHandler = Callable[[list[str]], Awaitable[str]]


@dataclass
class Command:
    """Registered command metadata."""

    name: str
    help_text: str
    handler: CommandHandler


class CommandRegistry:
    """Registry and dispatcher for built-in and custom shell commands."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self.library = GameLibrary(project_root / "data" / "games.json")
        self.commands: dict[str, Command] = {}
        self._register_defaults()

    def _register(self, name: str, help_text: str, handler: CommandHandler) -> None:
        self.commands[name] = Command(name=name, help_text=help_text, handler=handler)

    def list_command_names(self) -> list[str]:
        """List command names for autocompletion."""
        return sorted(self.commands)

    async def execute(self, name: str, args: list[str]) -> str:
        """Execute a known command."""
        if name not in self.commands:
            raise ValueError(f"Unknown command: {name}")
        return await self.commands[name].handler(args)

    def _register_defaults(self) -> None:
        self._register("help", "Show available commands.", self._help)
        self._register("cd", "cd <path>", self._cd)
        self._register("ls", "ls [path]", self._ls)
        self._register("cat", "cat <file>", self._cat)
        self._register("clear", "Clear terminal output.", self._clear)
        self._register("exit", "Exit GDShell.", self._exit)
        self._register("games", "List all tracked games.", self._games)
        self._register("addgame", "addgame <name>", self._addgame)
        self._register("playtime", "playtime <name> [hours_to_add]", self._playtime)
        self._register("pingtest", "pingtest <host>", self._pingtest)
        self._register("mods", "mods <game>", self._mods)
        self._register("idea", "Generate a random game idea.", self._idea)
        self._register("sysinfo", "Display system health snapshot.", self._sysinfo)
        self._register("dashboard", "Launch Textual dashboard.", self._dashboard)

    async def _help(self, _: list[str]) -> str:
        rows = [[cmd.name, cmd.help_text] for cmd in self.commands.values()]
        return format_table(["command", "description"], sorted(rows, key=lambda r: r[0]))

    async def _cd(self, args: list[str]) -> str:
        target = Path(args[0] if args else Path.home()).expanduser().resolve()
        os.chdir(target)
        return str(target)

    async def _ls(self, args: list[str]) -> str:
        target = Path(args[0] if args else ".")
        entries = sorted(target.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
        return "\n".join((f"{item.name}/" if item.is_dir() else item.name) for item in entries)

    async def _cat(self, args: list[str]) -> str:
        if not args:
            raise ValueError("Usage: cat <file>")
        file_path = Path(args[0])
        return file_path.read_text(encoding="utf-8")

    async def _clear(self, _: list[str]) -> str:
        return "__CLEAR__"

    async def _exit(self, _: list[str]) -> str:
        return "__EXIT__"

    async def _games(self, _: list[str]) -> str:
        games = self.library.list_games()
        if not games:
            return "No games tracked yet. Use: addgame <name>"
        rows = [[g.name, f"{g.playtime_hours:.1f}", str(len(g.mods or []))] for g in games]
        return format_table(["name", "hours", "mods"], rows)

    async def _addgame(self, args: list[str]) -> str:
        if not args:
            raise ValueError("Usage: addgame <name>")
        name = " ".join(args)
        self.library.add_game(GameEntry(name=name, mods=[]))
        return f"Added game: {name}"

    async def _playtime(self, args: list[str]) -> str:
        if not args:
            total = self.library.total_playtime()
            return f"Total playtime: {total:.1f}h"
        game_name = args[0]
        if len(args) == 1:
            game = self.library.get_game(game_name)
            return f"{game.name}: {game.playtime_hours:.1f}h"
        updated = self.library.add_playtime(game_name, float(args[1]))
        return f"Updated {updated.name}: {updated.playtime_hours:.1f}h"

    async def _pingtest(self, args: list[str]) -> str:
        if not args:
            raise ValueError("Usage: pingtest <host>")
        result = await ping_once(args[0])
        if result.success and result.latency_ms is not None:
            return f"{result.host} reachable in {result.latency_ms:.2f} ms"
        return f"{result.host} unreachable\n{result.raw_output.strip()}"

    async def _mods(self, args: list[str]) -> str:
        if not args:
            raise ValueError("Usage: mods <game>")
        game = self.library.get_game(args[0])
        if not game.mods:
            return f"No mods tracked for {game.name}"
        return "\n".join(f"- {mod}" for mod in game.mods)

    async def _idea(self, _: list[str]) -> str:
        return generate_idea().as_text()

    async def _sysinfo(self, _: list[str]) -> str:
        snap = capture_snapshot()
        return (
            f"CPU: {snap.cpu_percent:.1f}%\n"
            f"RAM: {snap.ram_used_gb:.1f}/{snap.ram_total_gb:.1f}GB ({snap.ram_percent:.1f}%)\n"
            f"GPU: {snap.gpu_summary}\n"
            f"Temps: {snap.temperatures}"
        )

    async def _dashboard(self, _: list[str]) -> str:
        proc = await asyncio.create_subprocess_exec("python", "-m", "tui.dashboard", cwd=str(self.project_root))
        await proc.communicate()
        return "Dashboard closed."


def parse_mod_file(path: Path) -> str:
    """Load supported mod config file formats for viewing/search."""
    suffix = path.suffix.lower()
    text = path.read_text(encoding="utf-8", errors="replace")
    if suffix in {".ini", ".cfg", ".json"}:
        return text
    if suffix == ".xml":
        root = ET.fromstring(text)
        return ET.tostring(root, encoding="unicode")
    raise ValueError(f"Unsupported config format: {path.suffix}")
