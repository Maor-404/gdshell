"""Game library persistence and operations."""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any


@dataclass
class GameEntry:
    """Represents a single game in the local library."""

    name: str
    playtime_hours: float = 0.0
    notes: str = ""
    mods: list[str] | None = None

    def normalized(self) -> "GameEntry":
        """Return a normalized copy with a guaranteed mod list."""
        return GameEntry(
            name=self.name.strip(),
            playtime_hours=max(0.0, float(self.playtime_hours)),
            notes=self.notes.strip(),
            mods=list(self.mods or []),
        )


class GameLibrary:
    """Manages game data stored in a JSON file."""

    def __init__(self, data_path: Path) -> None:
        self.data_path = data_path
        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.data_path.exists():
            self._save([])

    def _load(self) -> list[dict[str, Any]]:
        with self.data_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        if not isinstance(data, list):
            raise ValueError("games.json must contain a list")
        return data

    def _save(self, games: list[dict[str, Any]]) -> None:
        with self.data_path.open("w", encoding="utf-8") as handle:
            json.dump(games, handle, indent=2)

    def list_games(self) -> list[GameEntry]:
        """Return all games sorted by name."""
        games = [
            GameEntry(
                name=str(item.get("name", "")).strip(),
                playtime_hours=float(item.get("playtime_hours", 0.0)),
                notes=str(item.get("notes", "")),
                mods=list(item.get("mods", [])),
            ).normalized()
            for item in self._load()
        ]
        return sorted(games, key=lambda g: g.name.lower())

    def add_game(self, entry: GameEntry) -> None:
        """Insert a new game into storage."""
        normalized = entry.normalized()
        games = self._load()
        if any(str(g.get("name", "")).lower() == normalized.name.lower() for g in games):
            raise ValueError(f"Game already exists: {normalized.name}")
        games.append(asdict(normalized))
        self._save(games)

    def add_playtime(self, game_name: str, hours: float) -> GameEntry:
        """Add hours to an existing game and return the updated record."""
        if hours <= 0:
            raise ValueError("Playtime increment must be positive")
        games = self._load()
        for item in games:
            if str(item.get("name", "")).lower() == game_name.lower():
                item["playtime_hours"] = float(item.get("playtime_hours", 0.0)) + hours
                updated = GameEntry(
                    name=item["name"],
                    playtime_hours=item["playtime_hours"],
                    notes=str(item.get("notes", "")),
                    mods=list(item.get("mods", [])),
                ).normalized()
                self._save(games)
                return updated
        raise ValueError(f"Game not found: {game_name}")

    def get_game(self, game_name: str) -> GameEntry:
        """Get one game by case-insensitive name."""
        for game in self.list_games():
            if game.name.lower() == game_name.lower():
                return game
        raise ValueError(f"Game not found: {game_name}")

    def total_playtime(self) -> float:
        """Calculate total tracked playtime in hours."""
        return sum(game.playtime_hours for game in self.list_games())
