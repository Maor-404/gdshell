"""Game panel widget."""

from __future__ import annotations

from pathlib import Path

from textual.widgets import Static

from core.gamelib import GameLibrary


class GamesPanel(Static):
    """Displays the current game library."""

    def __init__(self, project_root: Path) -> None:
        super().__init__(id="games-panel")
        self.library = GameLibrary(project_root / "data" / "games.json")

    def on_mount(self) -> None:
        self.refresh_content()

    def refresh_content(self) -> None:
        games = self.library.list_games()
        if not games:
            self.update("[b]Game Library[/b]\nNo games added yet.")
            return
        body = "\n".join(f"• {g.name} — {g.playtime_hours:.1f}h" for g in games)
        self.update(f"[b]Game Library[/b]\n{body}")
