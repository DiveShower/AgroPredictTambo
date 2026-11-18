"""Pruebas unitarias para el asistente de estilo oscuro en gráficos ITH."""

import matplotlib
from matplotlib.axes import Axes
from matplotlib.colors import to_rgba
from matplotlib.figure import Figure

from src.infrastructure.ui.desktop.components.chart_style_helper import (
    apply_dark_chart_theme,
)

matplotlib.use("Agg")


def test_apply_dark_chart_theme_decorates_axes() -> None:
    """Verifica título, color de fondo y leyenda al aplicar el tema oscuro."""
    figure: Figure = Figure()
    ax: Axes = figure.add_subplot(111)
    x_idx: list[int] = list(range(24))
    labels: list[str] = [f"{i}:00" for i in range(24)]

    apply_dark_chart_theme(ax, x_idx, labels, 68.0, 75.0)

    assert ax.get_title() == "Curva Bioclimática ITH 24 Horas"
    assert ax.get_facecolor() == to_rgba("#12181f")
    assert ax.get_legend() is not None
