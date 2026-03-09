"""Ping tester panel widget."""

from __future__ import annotations

import asyncio

from textual.widgets import Static

from core.ping import ping_series


class PingPanel(Static):
    """Runs ping samples and renders simple bar graph output."""

    def __init__(self) -> None:
        super().__init__(id="ping-panel")
        self.host = "1.1.1.1"

    def on_mount(self) -> None:
        self.run_worker(self.refresh_content, thread=False)

    async def refresh_content(self) -> None:
        results = await ping_series(self.host, samples=8, interval_s=0.3)
        values = [r.latency_ms for r in results if r.success and r.latency_ms is not None]
        if not values:
            self.update(f"[b]Ping Tester[/b]\n{self.host} unreachable")
            return

        max_v = max(values) or 1.0
        bars = []
        for value in values:
            blocks = max(1, int((value / max_v) * 16))
            color = "green" if value < 60 else "yellow" if value < 120 else "red"
            bars.append(f"[{color}]{'█' * blocks}[/{color}] {value:.1f}ms")
        avg = sum(values) / len(values)
        self.update(f"[b]Ping Tester ({self.host})[/b]\n" + "\n".join(bars) + f"\nAvg: {avg:.1f}ms")
        await asyncio.sleep(1.2)
        self.run_worker(self.refresh_content, thread=False)
