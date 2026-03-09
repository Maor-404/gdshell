"""Rust backend bridge for parsing and external command execution."""

from __future__ import annotations

import asyncio
import json
import shutil
import subprocess
from pathlib import Path


class RustBackend:
    """Wrapper around the required `gdsh-rs` backend binary."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self.backend_dir = project_root / "rust_backend"

    def _candidate_paths(self) -> list[list[str]]:
        direct = shutil.which("gdsh-rs")
        candidates: list[list[str]] = []
        if direct:
            candidates.append([direct])
        for path in (
            self.backend_dir / "target" / "release" / "gdsh-rs",
            self.backend_dir / "target" / "debug" / "gdsh-rs",
        ):
            if path.exists():
                candidates.append([str(path)])
        return candidates

    def ensure_available(self) -> None:
        """Ensure the rust backend exists; attempt local build if missing."""
        if self._candidate_paths():
            return
        cargo = shutil.which("cargo")
        if not cargo:
            raise RuntimeError("Rust backend is required but cargo is not installed")
        proc = subprocess.run(
            [cargo, "build", "--release", "--manifest-path", str(self.backend_dir / "Cargo.toml")],
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode != 0:
            raise RuntimeError(f"Failed building rust backend:\n{proc.stdout}\n{proc.stderr}".strip())
        if not self._candidate_paths():
            raise RuntimeError("Rust backend build finished but gdsh-rs binary was not found")

    def _command(self) -> list[str]:
        self.ensure_available()
        return self._candidate_paths()[0]

    def parse(self, line: str) -> tuple[str, list[str]]:
        """Parse a command line through rust and return command + args."""
        base = self._command()
        proc = subprocess.run(base + ["parse", line], capture_output=True, text=True, check=False)
        if proc.returncode != 0:
            raise ValueError(proc.stderr.strip() or "Failed to parse command")
        parsed = json.loads(proc.stdout)
        return str(parsed.get("command", "")), [str(arg) for arg in parsed.get("args", [])]

    async def exec_external(self, command: str, args: list[str]) -> str:
        """Execute external command via rust backend and return combined output."""
        base = self._command()
        proc = await asyncio.create_subprocess_exec(
            *base,
            "exec",
            command,
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        out, _ = await proc.communicate()
        return out.decode("utf-8", errors="replace").strip()
