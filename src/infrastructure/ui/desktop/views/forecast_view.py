"""Vista de proyección horaria ITH a 24h delegando en ForecastViewModel."""

from typing import Optional

from PyQt6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from src.adapters.desktop.viewmodels.forecast_viewmodel import ForecastViewModel
from src.infrastructure.ui.desktop.components.forecast_chart_widget import (
    ForecastChartWidget,
)


class ForecastView(QWidget):
    """Pestaña 2: Muestra el gráfico de curva ITH 24h y penalización nocturna."""

    def __init__(
        self,
        viewmodel: ForecastViewModel,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._viewmodel = viewmodel

        layout = QVBoxLayout(self)
        self.info_label = QLabel(
            "Proyección Horaria ITH (24 Horas) — Umbrales dinámicos y Pre-enfriamiento ML"
        )
        self.info_label.setObjectName("HeaderTitle")
        self.chart = ForecastChartWidget(self)
        self.refresh_btn = QPushButton("Actualizar Proyección 24h")
        self.refresh_btn.clicked.connect(self.refresh_chart)

        layout.addWidget(self.info_label)
        layout.addWidget(self.chart, stretch=1)
        layout.addWidget(self.refresh_btn)
        self.refresh_chart()

    def refresh_chart(self) -> None:
        """Consulta datos procesados al ViewModel y los pasa al lienzo."""
        data = self._viewmodel.get_24h_curve_data()
        pen = data["nocturnal_penalty"]
        self.info_label.setText(
            f"Curva 24h | Alerta: {data['alert_threshold']} | Peligro: {data['danger_threshold']} (Penalización nocturna: -{pen} pts)"
        )
        self.chart.plot_curve(data)
