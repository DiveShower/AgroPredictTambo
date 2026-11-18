"""Funciones auxiliares de estilo oscuro para gráficos Matplotlib ITH."""

from typing import Any


def apply_dark_chart_theme(
    ax: Any,
    x_idx: list[int],
    labels: list[str],
    alert_th: float,
    danger_th: float,
) -> None:
    """Aplica el tema oscuro industrial y los umbrales de referencia al eje."""
    ax.set_facecolor("#12181f")
    ax.axhline(alert_th, color="#f1c40f", linestyle="--", label="Umbral Alerta")
    ax.axhline(danger_th, color="#e74c3c", linestyle="--", label="Umbral Peligro")
    step: int = max(1, len(x_idx) // 8)
    ax.set_xticks(x_idx[::step])
    ax.set_xticklabels(labels[::step], color="#ecf0f1")
    ax.tick_params(axis="y", colors="#ecf0f1")
    ax.set_title("Curva Bioclimática ITH 24 Horas", color="#ecf0f1")
    ax.legend(facecolor="#1b2430", labelcolor="#ecf0f1", loc="upper left")
