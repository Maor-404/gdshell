"""System information collection helpers."""

from __future__ import annotations

from dataclasses import dataclass

import psutil


@dataclass
class SystemSnapshot:
    """A compact snapshot of machine health metrics."""

    cpu_percent: float
    ram_percent: float
    ram_used_gb: float
    ram_total_gb: float
    gpu_summary: str
    temperatures: str


def _temperature_summary() -> str:
    temps = psutil.sensors_temperatures(fahrenheit=False)
    if not temps:
        return "N/A"
    values: list[str] = []
    for label, readings in temps.items():
        for reading in readings:
            name = reading.label or label
            values.append(f"{name}:{reading.current:.1f}°C")
    return ", ".join(values[:4]) if values else "N/A"


def _gpu_summary() -> str:
    # Portable fallback; optionally enriched by platform-specific tools in future.
    return "Unavailable (install optional GPU probe backend)"


def capture_snapshot() -> SystemSnapshot:
    """Capture current system metrics for shell output and TUI rendering."""
    mem = psutil.virtual_memory()
    return SystemSnapshot(
        cpu_percent=psutil.cpu_percent(interval=0.1),
        ram_percent=mem.percent,
        ram_used_gb=mem.used / (1024**3),
        ram_total_gb=mem.total / (1024**3),
        gpu_summary=_gpu_summary(),
        temperatures=_temperature_summary(),
    )
