"""Utility helpers used by the GDSH command layer."""

from __future__ import annotations

from pathlib import Path


def format_table(headers: list[str], rows: list[list[str]]) -> str:
    """Render a simple fixed-width text table."""
    widths = [len(h) for h in headers]
    for row in rows:
        for idx, col in enumerate(row):
            widths[idx] = max(widths[idx], len(col))

    def _line(cells: list[str]) -> str:
        return " | ".join(cell.ljust(widths[idx]) for idx, cell in enumerate(cells))

    separator = "-+-".join("-" * width for width in widths)
    lines = [_line(headers), separator]
    lines.extend(_line(row) for row in rows)
    return "\n".join(lines)


def resolve_data_path(root: Path) -> Path:
    """Resolve the project-local game storage path."""
    return root / "data" / "games.json"
