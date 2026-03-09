"""Async ping helpers for shell and TUI usage."""

from __future__ import annotations

import asyncio
import platform
import re
from dataclasses import dataclass


@dataclass
class PingResult:
    """Represents one ping attempt result."""

    host: str
    success: bool
    latency_ms: float | None
    raw_output: str


_LATENCY_PATTERNS = [
    re.compile(r"time[=<]([0-9.]+)\s*ms", re.IGNORECASE),
    re.compile(r"Average = ([0-9.]+)ms", re.IGNORECASE),
]


async def ping_once(host: str, timeout_s: int = 2) -> PingResult:
    """Ping a host exactly once and return parsed latency information."""
    system = platform.system().lower()
    if "windows" in system:
        cmd = ["ping", "-n", "1", "-w", str(timeout_s * 1000), host]
    else:
        cmd = ["ping", "-c", "1", "-W", str(timeout_s), host]

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )
    out, _ = await proc.communicate()
    text = out.decode("utf-8", errors="replace")

    latency: float | None = None
    for pattern in _LATENCY_PATTERNS:
        match = pattern.search(text)
        if match:
            latency = float(match.group(1))
            break

    return PingResult(host=host, success=proc.returncode == 0, latency_ms=latency, raw_output=text)


async def ping_series(host: str, samples: int = 6, interval_s: float = 0.6) -> list[PingResult]:
    """Collect multiple ping samples with a fixed delay between attempts."""
    results: list[PingResult] = []
    for index in range(samples):
        results.append(await ping_once(host))
        if index < samples - 1:
            await asyncio.sleep(interval_s)
    return results
