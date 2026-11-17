"""Vista principal del tablero SCADA con grilla de sectores y barra de control."""

from typing import Optional
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QPushButton, QVBoxLayout, QWidget
from src.adapters.desktop.viewmodels.scada_viewmodel import ScadaViewModel
from src.application.dtos.predict_stress_response_dto import PredictStressResponseDTO
from src.infrastructure.ui.desktop.components.sector_card_widget import SectorCardWidget
from src.infrastructure.ui.desktop.components.thi_gauge_widget import ThiGaugeWidget


class ScadaView(QWidget):
    """Pestaña SCADA que muestra el cuadrante ITH y las 3 tarjetas de sectores."""

    sync_requested = pyqtSignal()
    demo_heatwave_requested = pyqtSignal()

    def __init__(self, viewmodel: ScadaViewModel, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._viewmodel, self._cards = viewmodel, {}
        root, grid, ctrl = QVBoxLayout(self), QHBoxLayout(), QHBoxLayout()
        self.gauge = ThiGaugeWidget(self)
        root.addWidget(self.gauge)

        for state in self._viewmodel.get_cards_state():
            card = SectorCardWidget(state["sector_id"], self)
            card.update_from_state(state)
            card.occupancy_toggled.connect(self._on_card_toggled)
            self._cards[state["sector_id"]] = card
            grid.addWidget(card)
        root.addLayout(grid)

        self.sync_btn, self.demo_btn = QPushButton("Sincronizar Clima Ahora"), QPushButton("Simular Ola de Calor")
        self.stop_btn = QPushButton("Detencion de Emergencia")
        self.stop_btn.setObjectName("EmergencyBtn")
        self.sync_btn.clicked.connect(self.sync_requested.emit)
        self.demo_btn.clicked.connect(self.demo_heatwave_requested.emit)
        self.stop_btn.clicked.connect(self._on_emergency_shutoff)
        for btn in (self.sync_btn, self.demo_btn, self.stop_btn):
            ctrl.addWidget(btn)
        root.addLayout(ctrl)

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
        self.gauge.update_metrics(resp.current_thi, resp.predicted_thi, resp.nocturnal_debt_hours)
        self.refresh_cards()
