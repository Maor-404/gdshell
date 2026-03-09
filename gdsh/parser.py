"""Command parsing for GDSH."""

from __future__ import annotations

import shlex
from typing import Protocol


class ParserBackend(Protocol):
    """Protocol for parser backends."""

    def parse(self, line: str) -> tuple[str, list[str]]:
        """Parse a command line into command + args."""


def parse_command(line: str, backend: ParserBackend | None = None) -> tuple[str, list[str]]:
    """Parse shell input into command name and argument list."""
    cleaned = line.strip()
    if not cleaned:
        return "", []

    if backend is not None:
        return backend.parse(cleaned)

    tokens = shlex.split(cleaned)
    if not tokens:
        return "", []
    return tokens[0], tokens[1:]
