"""Pruebas unitarias para la actualización incremental en ForecastChartWidget."""

import os
from typing import Any

from matplotlib.lines import Line2D
from PyQt6.QtWidgets import QApplication

from src.infrastructure.ui.desktop.components.forecast_chart_widget import (
    ForecastChartWidget,
)

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
_APP = QApplication.instance() or QApplication([])


def test_forecast_chart_widget_initial_and_incremental_update() -> None:
    """Valida render inicial y actualización incremental sin recrear Line2D."""
    data1: dict[str, Any] = {
        "hours_labels": ["1", "2"],
        "thi_values": [70.0, 72.0],
        "alert_threshold": 68.0,
        "danger_threshold": 75.0,
        "danger_indices": [],
    }
    chart = ForecastChartWidget()
    chart.plot_curve(data1)

    assert chart._line is not None
    assert list(chart._line.get_ydata()) == [70.0, 72.0]

    line_ref: Line2D = chart._line
    assert isinstance(line_ref, Line2D)
    data2: dict[str, Any] = {
        **data1,
        "thi_values": [74.0, 76.0],
    }
    chart.plot_curve(data2)

    assert chart._line is line_ref
    assert list(chart._line.get_ydata()) == [74.0, 76.0]
