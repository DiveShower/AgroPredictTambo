"""Widget de lienzo Matplotlib para renderizar la curva ITH proyectada a 24h."""

from typing import Any, Optional

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PyQt6.QtWidgets import QVBoxLayout, QWidget


class ForecastChartWidget(QWidget):
    """Encapsula el FigureCanvas de Matplotlib con tema oscuro industrial."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.figure = Figure(figsize=(8, 4), dpi=100, facecolor="#1b2430")
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.ax = self.figure.add_subplot(111)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)

    def plot_curve(self, data: dict[str, Any]) -> None:
        """Renderiza la serie horaria de ITH, umbrales y puntos críticos."""
        self.ax.clear()
        self.ax.set_facecolor("#12181f")
        labels: list[str] = data["hours_labels"]
        vals: list[float] = data["thi_values"]
        x_idx = list(range(len(vals)))

        self.ax.plot(x_idx, vals, color="#00d2d3", linewidth=2.2, label="ITH Proyectado")
        self.ax.axhline(data["alert_threshold"], color="#f1c40f", linestyle="--", label="Umbral Alerta")
        self.ax.axhline(data["danger_threshold"], color="#e74c3c", linestyle="--", label="Umbral Peligro")

        d_idx: list[int] = data.get("danger_indices", [])
        if d_idx:
            self.ax.scatter(d_idx, [vals[i] for i in d_idx], color="#e74c3c", zorder=5, label="Pre-enfriado ML")

        step = max(1, len(x_idx) // 8)
        self.ax.set_xticks(x_idx[::step])
        self.ax.set_xticklabels(labels[::step], color="#ecf0f1")
        self.ax.tick_params(axis="y", colors="#ecf0f1")
        self.ax.set_title("Curva Bioclimática ITH 24 Horas", color="#ecf0f1")
        self.ax.legend(facecolor="#1b2430", labelcolor="#ecf0f1", loc="upper left")
        self.figure.tight_layout()
        self.canvas.draw_idle()
