"""Ventana principal de la estación base de monitoreo SCADA (PyQt6)."""

from typing import Any, Optional
from PyQt6.QtWidgets import QLabel, QMainWindow, QTabWidget, QVBoxLayout, QWidget
from src.adapters.desktop.viewmodels.scada_viewmodel import ScadaViewModel
from src.application.dtos.predict_stress_response_dto import PredictStressResponseDTO
from src.infrastructure.ui.desktop.views.scada_view import ScadaView
from src.infrastructure.ui.desktop.workers.telegram_bot_worker import TelegramBotWorker
from src.infrastructure.ui.desktop.workers.weather_sync_worker import WeatherSyncWorker


class MainWindow(QMainWindow):
    """Shell principal con pestañas y conexión de señales a workers QThread."""

    def __init__(
        self,
        scada_viewmodel: ScadaViewModel,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._viewmodel = scada_viewmodel
        self.setWindowTitle("AGRO-PREDICT 2026 — Estación SCADA Tambo San José")
        self.resize(1100, 680)

        central = QWidget(self)
        lay = QVBoxLayout(central)
        self.header_lbl = QLabel(
            "[AGRO-PREDICT 2026] Tambo San José (Rafaela, SF) | Estado: ONLINE (QThread Sync)"
        )
        self.header_lbl.setObjectName("HeaderTitle")
        lay.addWidget(self.header_lbl)

        self.tabs = QTabWidget(central)
        self.scada_view = ScadaView(self._viewmodel, self)
        self.tabs.addTab(self.scada_view, "TAB 1: SCADA TAMBO")
        lay.addWidget(self.tabs)
        self.setCentralWidget(central)

        self.weather_worker = WeatherSyncWorker(self._viewmodel, parent=self)
        self.bot_worker = TelegramBotWorker(self._viewmodel, parent=self)
        self.weather_worker.weather_synced.connect(self._on_weather_synced)
        self.bot_worker.sector_state_changed.connect(self.scada_view.refresh_cards)
        self.scada_view.sync_requested.connect(self.trigger_weather_sync)
        self.scada_view.demo_heatwave_requested.connect(self.trigger_weather_sync)

    def trigger_weather_sync(self) -> None:
        if not self.weather_worker.isRunning():
            self.weather_worker.start()

    def _on_weather_synced(self, resp: PredictStressResponseDTO) -> None:
        c = resp.current_conditions
        self.header_lbl.setText(
            f"[AGRO-PREDICT 2026] Clima: {c.temperature_c:.1f}C | HR: {c.relative_humidity:.0f}% | ITH: {resp.current_thi:.1f}"
        )
        self.scada_view.refresh_from_prediction(resp)

    def closeEvent(self, event: Any) -> None:
        self.weather_worker.stop()
        self.bot_worker.stop()
        super().closeEvent(event)
