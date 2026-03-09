"""Textual dashboard entry point for GDShell."""

from __future__ import annotations

from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Footer, Header, Static

from core.idea import generate_idea
from tui.panels.games import GamesPanel
from tui.panels.mods import ModsPanel
from tui.panels.ping import PingPanel
from tui.panels.system import SystemPanel


class IdeaPanel(Static):
    """Panel displaying generated game concept snippets."""

    def on_mount(self) -> None:
        self.refresh_idea()

    def refresh_idea(self) -> None:
        self.update(f"[b]Idea Generator[/b]\n{generate_idea().as_text()}")


class GDShellDashboard(App):
    """Retro-themed multi-panel dashboard."""

    CSS = """
    Screen {
        background: #0b0f10;
        color: #8cf88f;
    }
    #grid {
        layout: grid;
        grid-size: 2 3;
        grid-columns: 1fr 1fr;
        grid-rows: 1fr 1fr 1fr;
        grid-gutter: 1 1;
        padding: 1;
    }
    Static {
        border: solid #226622;
        padding: 1;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
        ("i", "idea", "New Idea"),
    ]

    def __init__(self, project_root: Path) -> None:
        super().__init__()
        self.project_root = project_root

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="grid"):
            yield SystemPanel(id="system")
            yield GamesPanel(self.project_root)
            yield PingPanel()
            yield ModsPanel(self.project_root)
            yield IdeaPanel(id="idea")
            yield Static("[b]Controls[/b]\nq: Quit\nr: Refresh\ni: New Idea", id="controls")
        yield Footer()

    def action_refresh(self) -> None:
        self.query_one(SystemPanel).refresh_content()
        self.query_one(GamesPanel).refresh_content()
        self.query_one(ModsPanel).refresh_content()
        self.query_one(IdeaPanel).refresh_idea()

    def action_idea(self) -> None:
        self.query_one(IdeaPanel).refresh_idea()


def main() -> None:
    """Run dashboard app."""
    root = Path(__file__).resolve().parents[1]
    GDShellDashboard(root).run()


if __name__ == "__main__":
    main()
