"""Command parsing for GDSH."""

from __future__ import annotations

import shlex


def parse_command(line: str) -> tuple[str, list[str]]:
    """Parse a shell input line into command name and argument list."""
    tokens = shlex.split(line.strip())
    if not tokens:
        return "", []
    return tokens[0], tokens[1:]
