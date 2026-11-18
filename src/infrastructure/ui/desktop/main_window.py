"""Ventana principal de la estación base de monitoreo SCADA (PyQt6)."""

from PyQt6.QtWidgets import QLabel, QMainWindow, QTabWidget, QVBoxLayout, QWidget

from src.adapters.desktop.viewmodels.forecast_viewmodel import ForecastViewModel
from src.adapters.desktop.viewmodels.savings_viewmodel import SavingsViewModel
from src.adapters.desktop.viewmodels.scada_viewmodel import ScadaViewModel
from src.application.dtos.predict_stress_response_dto import PredictStressResponseDTO
from src.infrastructure.ui.desktop.tab_builder import build_tabs
from src.infrastructure.ui.desktop.views.scada_view import ScadaView
from src.infrastructure.ui.desktop.workers.telegram_bot_worker import TelegramBotWorker
from src.infrastructure.ui.desktop.workers.weather_sync_worker import WeatherSyncWorker


class MainWindow(QMainWindow):
    """Shell principal con 5 pestañas y conexión de señales a workers QThread."""

    def __init__(
        self,
        scada_vm: ScadaViewModel,
        fore_vm: ForecastViewModel | None = None,
        sav_vm: SavingsViewModel | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._viewmodel = scada_vm
        self.setWindowTitle("AGRO-PREDICT 2026 — Estación SCADA Tambo San José")
        self.resize(1100, 680)
        self.setCentralWidget(central := QWidget(self))
        lay = QVBoxLayout(central)
        h = "[AGRO-PREDICT 2026] Tambo San José (Rafaela, SF) | ONLINE"
        self.header_lbl = QLabel(h, objectName="HeaderTitle")
        tabs = self.tabs = QTabWidget(central)
        scada = self.scada_view = ScadaView(scada_vm, self)
        self.forecast_view = build_tabs(tabs, scada, fore_vm, sav_vm, self)
        lay.addWidget(self.header_lbl)
        lay.addWidget(tabs)
        w = self.weather_worker = WeatherSyncWorker(scada_vm, parent=self)
        b = self.bot_worker = TelegramBotWorker(scada_vm, parent=self)
        w.weather_synced.connect(self._on_weather_synced)
        w.started.connect(lambda: scada.set_sync_busy(True))
        w.finished.connect(lambda: scada.set_sync_busy(False))
        b.sector_state_changed.connect(scada.refresh_cards)
        sync = self.trigger_weather_sync
        scada.sync_requested.connect(lambda: sync("temperate"))
        scada.demo_heatwave_requested.connect(lambda: sync("heatwave"))

    def trigger_weather_sync(self, profile: str | None = None) -> None:
        if profile:
            self._viewmodel.set_weather_profile(profile)
        if not self.weather_worker.isRunning():
            self.weather_worker.start()

    def _on_weather_synced(self, resp: PredictStressResponseDTO) -> None:
        c = resp.current_conditions
        txt = f"[AGRO-PREDICT 2026] {c.temperature_c:.1f}C | HR {c.relative_humidity:.0f}% | ITH {resp.current_thi:.1f}"
        self.header_lbl.setText(txt)
        self.scada_view.refresh_from_prediction(resp)
        if self.forecast_view:
            self.forecast_view.refresh_chart()
