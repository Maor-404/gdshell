"""Mod configuration viewer panel."""

from __future__ import annotations

from pathlib import Path

from textual.widgets import Static

from gdsh.commands import parse_mod_file


class ModsPanel(Static):
    """Displays a preview of the first mod config file found."""

    def __init__(self, project_root: Path) -> None:
        super().__init__(id="mods-panel")
        self.project_root = project_root

    def on_mount(self) -> None:
        self.refresh_content()

    def refresh_content(self) -> None:
        search_root = self.project_root / "data"
        for ext in ("*.ini", "*.cfg", "*.json", "*.xml"):
            for file in search_root.glob(ext):
                contents = parse_mod_file(file)
                snippet = "\n".join(contents.splitlines()[:12])
                self.update(f"[b]Mod Viewer[/b]\n{file.name}\n\n{snippet}")
                return
        self.update("[b]Mod Viewer[/b]\nNo supported mod config found in data/.")
