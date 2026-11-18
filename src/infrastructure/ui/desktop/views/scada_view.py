"""Vista principal del tablero SCADA con grilla de sectores y barra de control."""

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QVBoxLayout, QWidget

from src.adapters.desktop.viewmodels.scada_viewmodel import ScadaViewModel
from src.application.dtos.predict_stress_response_dto import PredictStressResponseDTO
from src.infrastructure.ui.desktop.components.scada_control_bar import ScadaControlBar
from src.infrastructure.ui.desktop.components.sector_cards_grid import SectorCardsGrid
from src.infrastructure.ui.desktop.components.thi_gauge_widget import ThiGaugeWidget


class ScadaView(QWidget):
    """Pestaña SCADA que muestra el cuadrante ITH y las 3 tarjetas de sectores."""

    sync_requested, demo_heatwave_requested = pyqtSignal(), pyqtSignal()

    def __init__(
        self, viewmodel: ScadaViewModel, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self._viewmodel = viewmodel
        root = QVBoxLayout(self)
        self.gauge = ThiGaugeWidget(self)
        root.addWidget(self.gauge)
        self.grid = SectorCardsGrid(self._viewmodel.get_cards_state(), self)
        self.grid.occupancy_toggled.connect(self._on_card_toggled)
        self._cards = self.grid._cards
        root.addWidget(self.grid)
        b = self.ctrl_bar = ScadaControlBar(self)
        self.sync_btn, self.demo_btn, self.stop_btn = b.sync_btn, b.demo_btn, b.stop_btn
        b.sync_requested.connect(self.sync_requested.emit)
        b.demo_heatwave_requested.connect(self.demo_heatwave_requested.emit)
        b.emergency_requested.connect(self._on_emergency_shutoff)
        root.addWidget(b)

    def set_sync_busy(self, is_busy: bool) -> None:
        self.ctrl_bar.set_sync_busy(is_busy)

    def _on_card_toggled(self, sector_id: str, is_occupied: bool) -> None:
        self._viewmodel.toggle_occupancy(sector_id, is_occupied)
        self.refresh_cards()

    def _on_emergency_shutoff(self) -> None:
        self._viewmodel.emergency_shutoff()
        self.grid.reset_emergency()

    def refresh_cards(self) -> None:
        self.grid.refresh_from_states(self._viewmodel.get_cards_state())

    def refresh_from_prediction(self, resp: PredictStressResponseDTO) -> None:
        self.gauge.update_metrics(
            resp.current_thi, resp.predicted_thi, resp.nocturnal_debt_hours
        )
        self.refresh_cards()
