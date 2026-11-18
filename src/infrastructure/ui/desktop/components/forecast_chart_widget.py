"""Widget de lienzo Matplotlib para renderizar la curva ITH proyectada a 24h."""

from typing import Any

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PyQt6.QtWidgets import QVBoxLayout, QWidget

from src.infrastructure.ui.desktop.components.chart_style_helper import (
    apply_dark_chart_theme,
)


class ForecastChartWidget(QWidget):
    """Encapsula el FigureCanvas de Matplotlib con tema oscuro industrial."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.figure = Figure(figsize=(8, 4), dpi=100, facecolor="#1b2430")
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.ax = self.figure.add_subplot(111)
        self._line: Any | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)

    def plot_curve(self, data: dict[str, Any]) -> None:
        """Renderiza o actualiza incrementalmente la serie horaria de ITH."""
        vals: list[float] = data["thi_values"]
        if self._line is not None and len(self._line.get_xdata()) == len(vals):
            self._line.set_ydata(vals)
            self.canvas.draw_idle()
            return

        self.ax.clear()
        labels: list[str] = data["hours_labels"]
        x_idx = list(range(len(vals)))
        self._line = self.ax.plot(
            x_idx, vals, color="#00d2d3", linewidth=2.2, label="ITH Proyectado"
        )[0]
        d_idx: list[int] = data.get("danger_indices", [])
        if d_idx:
            self.ax.scatter(
                d_idx,
                [vals[i] for i in d_idx],
                color="#e74c3c",
                zorder=5,
                label="Pre-enfriado ML",
            )
        apply_dark_chart_theme(
            self.ax, x_idx, labels, data["alert_threshold"], data["danger_threshold"]
        )
        self.figure.tight_layout()
        self.canvas.draw_idle()
