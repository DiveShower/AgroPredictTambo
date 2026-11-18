"""Vista principal del tablero SCADA con grilla de sectores y barra de control."""

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from src.adapters.desktop.viewmodels.scada_viewmodel import ScadaViewModel
from src.application.dtos.predict_stress_response_dto import PredictStressResponseDTO
from src.infrastructure.ui.desktop.components.scada_control_bar import ScadaControlBar
from src.infrastructure.ui.desktop.components.sector_card_widget import SectorCardWidget
from src.infrastructure.ui.desktop.components.thi_gauge_widget import ThiGaugeWidget


class ScadaView(QWidget):
    """Pestaña SCADA que muestra el cuadrante ITH y las 3 tarjetas de sectores."""

    sync_requested, demo_heatwave_requested = pyqtSignal(), pyqtSignal()

    def __init__(
        self, viewmodel: ScadaViewModel, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self._viewmodel, self._cards = viewmodel, dict[str, SectorCardWidget]()
        root, grid = QVBoxLayout(self), QHBoxLayout()
        self.gauge = ThiGaugeWidget(self)
        root.addWidget(self.gauge)
        for s in self._viewmodel.get_cards_state():
            c = self._cards[s["sector_id"]] = SectorCardWidget(s["sector_id"], self)
            c.update_from_state(s)
            c.occupancy_toggled.connect(self._on_card_toggled)
            grid.addWidget(c)
        root.addLayout(grid)
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
        for card in self._cards.values():
            card._water_rem, card._fan_rem = 0, 0
            card._refresh_countdown_labels()

    def refresh_cards(self) -> None:
        for state in self._viewmodel.get_cards_state():
            self._cards[state["sector_id"]].update_from_state(state)

    def refresh_from_prediction(self, resp: PredictStressResponseDTO) -> None:
        self.gauge.update_metrics(
            resp.current_thi, resp.predicted_thi, resp.nocturnal_debt_hours
        )
        self.refresh_cards()
