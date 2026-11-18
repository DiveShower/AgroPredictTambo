"""Tarjeta reactiva de sector con switch de ocupación y tick sincronizado."""

from typing import Any

from PyQt6.QtCore import QSignalBlocker, pyqtSignal
from PyQt6.QtWidgets import QCheckBox, QFrame, QLabel, QVBoxLayout, QWidget

from src.infrastructure.ui.desktop.components.sector_card_formatter import (
    format_fan_label,
    format_water_label,
)


class SectorCardWidget(QFrame):
    """Widget de sector con ciclo regresivo 40s/270s y alerta sanitaria."""

    occupancy_toggled = pyqtSignal(str, bool)

    def __init__(self, sector_id: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.sector_id = sector_id
        self.setObjectName("SectorCard")
        self._water_rem, self._fan_rem, self._allows_w = 0, 0, True
        lay = QVBoxLayout(self)
        self.title_lbl, self.badge_lbl = QLabel(sector_id), QLabel("CONFORT")
        self.occ_chk = QCheckBox("OCUPADO (Vacas en sector)", checked=True)
        self.occ_chk.toggled.connect(self._on_toggled)
        self.water_lbl, self.fan_lbl = QLabel("Bomba: OFF"), QLabel("Ventiladores: OFF")
        ws = self.title_lbl, self.badge_lbl, self.occ_chk, self.water_lbl, self.fan_lbl
        for w in ws:
            lay.addWidget(w)

    def _on_toggled(self, checked: bool) -> None:
        self.occupancy_toggled.emit(self.sector_id, checked)

    def update_from_state(self, state: dict[str, Any]) -> None:
        """Sincroniza colores, textos sanitarios y contadores desde ScadaViewModel."""
        s = state
        self.title_lbl.setText(f"{s['name']} ({s['capacity']} vacas)")
        self.badge_lbl.setText(f"Estado: {s['status_badge']} — {s['cycle_desc']}")
        if (lvl := str(s.get("stress_level", 0))) != self.property("stressLevel"):
            self.setProperty("stressLevel", lvl)
            if st := self.style():
                st.unpolish(self)
                st.polish(self)
        with QSignalBlocker(self.occ_chk):
            self.occ_chk.setChecked(bool(s["is_occupied"]))
        self._allows_w = bool(s["allows_water"])
        self._water_rem, self._fan_rem = int(s["water_seconds"]), int(s["fan_seconds"])
        self._refresh_countdown_labels()

    def tick(self) -> None:
        """Avanza 1 segundo en el ciclo regresivo de agua y ventilación."""
        self._water_rem = max(0, self._water_rem - 1)
        self._fan_rem = max(0, self._fan_rem - 1)
        self._refresh_countdown_labels()

    def _refresh_countdown_labels(self) -> None:
        self.water_lbl.setText(format_water_label(self._allows_w, self._water_rem))
        self.fan_lbl.setText(format_fan_label(self._fan_rem))
