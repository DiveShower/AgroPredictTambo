"""Grilla horizontal de tarjetas de sectores con timer maestro unificado."""

from typing import Any

from PyQt6.QtCore import QTimer, pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QWidget

from src.infrastructure.ui.desktop.components.sector_card_widget import (
    SectorCardWidget,
)


class SectorCardsGrid(QWidget):
    """Contenedor de tarjetas de sectores sincronizado por un único QTimer."""

    occupancy_toggled = pyqtSignal(str, bool)

    def __init__(
        self, states: list[dict[str, Any]], parent: QWidget | None = None
    ) -> None:
        """Inicializa la grilla de tarjetas y arranca el timer maestro de 1s."""
        super().__init__(parent)
        self._cards: dict[str, SectorCardWidget] = {}
        layout = QHBoxLayout(self)
        for state in states:
            sec_id = str(state["sector_id"])
            card = SectorCardWidget(sec_id, self)
            card.update_from_state(state)
            card.occupancy_toggled.connect(self.occupancy_toggled.emit)
            self._cards[sec_id] = card
            layout.addWidget(card)
        self.master_timer = QTimer(self)
        self.master_timer.setInterval(1000)
        self.master_timer.timeout.connect(self._on_tick)
        self.master_timer.start()

    def _on_tick(self) -> None:
        """Propaga el pulso de 1 segundo hacia cada tarjeta del tablero."""
        for card in self._cards.values():
            card.tick()

    def refresh_from_states(self, states: list[dict[str, Any]]) -> None:
        """Actualiza cada tarjeta correspondiente con su nuevo diccionario de estado."""
        for state in states:
            card = self._cards.get(str(state["sector_id"]))
            if card is not None:
                card.update_from_state(state)

    def reset_emergency(self) -> None:
        """Lleva a cero los contadores regresivos de todas las tarjetas."""
        for card in self._cards.values():
            card._water_rem, card._fan_rem = 0, 0
            card._refresh_countdown_labels()

    def get_card(self, sector_id: str) -> SectorCardWidget | None:
        """Retorna la tarjeta asociada al sector indicado o None si no existe."""
        return self._cards.get(sector_id)
