"""Random game idea generator."""

from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass
class GameIdea:
    """Represents a generated game concept."""

    genre: str
    setting: str
    mechanics: str
    enemies: str
    plot_twist: str

    def as_text(self) -> str:
        """Render the idea in a human-readable multiline format."""
        return (
            f"Genre: {self.genre}\n"
            f"Setting: {self.setting}\n"
            f"Core Mechanics: {self.mechanics}\n"
            f"Enemies: {self.enemies}\n"
            f"Plot Twist: {self.plot_twist}"
        )


_GENRES = ["Roguelite", "Survival Horror", "Tactical RPG", "Immersive Sim", "Platformer"]
_SETTINGS = ["Floating megacity", "Frozen moon colony", "Sunken arcology", "Dream realm", "Post-singularity ruins"]
_MECHANICS = ["Time rewinding attacks", "Deckbuilding combat", "Physics-based traversal", "Companion command wheel", "Rhythm-driven powers"]
_ENEMIES = ["Corporate exorcists", "Nanite swarms", "Biomechanical knights", "Echo clones", "Rogue terraformers"]
_TWISTS = ["The protagonist is the final boss in disguise", "Every save file alters world history", "Your companion is future-you", "The map is a living organism", "The enemy faction is trying to save humanity"]


def generate_idea() -> GameIdea:
    """Return a random game concept using themed prompt tables."""
    return GameIdea(
        genre=random.choice(_GENRES),
        setting=random.choice(_SETTINGS),
        mechanics=random.choice(_MECHANICS),
        enemies=random.choice(_ENEMIES),
        plot_twist=random.choice(_TWISTS),
    )
