"""GDShell launcher."""

from __future__ import annotations

import asyncio
from pathlib import Path

from gdsh.shell import GDShell


def main() -> None:
    """Run interactive shell."""
    project_root = Path(__file__).resolve().parent
    shell = GDShell(project_root)
    asyncio.run(shell.run())


if __name__ == "__main__":
    main()
