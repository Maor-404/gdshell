"""System monitor panel widget."""

from __future__ import annotations

from textual.widgets import Static

from core.sysinfo import capture_snapshot


class SystemPanel(Static):
    """Displays periodic CPU/RAM/GPU/temperature data."""

    def on_mount(self) -> None:
        self.set_interval(1.5, self.refresh_content)
        self.refresh_content()

    def refresh_content(self) -> None:
        snap = capture_snapshot()
        self.update(
            "[b]System Monitor[/b]\n"
            f"CPU: {snap.cpu_percent:.1f}%\n"
            f"RAM: {snap.ram_used_gb:.1f}/{snap.ram_total_gb:.1f}GB ({snap.ram_percent:.1f}%)\n"
            f"GPU: {snap.gpu_summary}\n"
            f"Temp: {snap.temperatures}"
        )
