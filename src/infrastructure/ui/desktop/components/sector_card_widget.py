"""Tarjeta reactiva de sector con switch de ocupación y cronómetro QTimer."""

from typing import Any, Optional
from PyQt6.QtCore import QTimer, pyqtSignal
from PyQt6.QtWidgets import QCheckBox, QFrame, QLabel, QVBoxLayout, QWidget


class SectorCardWidget(QFrame):
    """Widget interactivo de sector con ciclo regresivo 40s/270s y alerta sanitaria."""

    occupancy_toggled = pyqtSignal(str, bool)

    def __init__(self, sector_id: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.sector_id = sector_id
        self.setObjectName("SectorCard")
        self._water_rem, self._fan_rem, self._allows_w = 0, 0, True

        lay = QVBoxLayout(self)
        self.title_lbl, self.badge_lbl = QLabel(sector_id), QLabel("CONFORT")
        self.occ_chk = QCheckBox("OCUPADO (Vacas en sector)")
        self.occ_chk.setChecked(True)
        self.occ_chk.toggled.connect(self._on_toggled)
        self.water_lbl, self.fan_lbl = QLabel("Bomba: OFF"), QLabel("Ventiladores: OFF")
        for w in (self.title_lbl, self.badge_lbl, self.occ_chk, self.water_lbl, self.fan_lbl):
            lay.addWidget(w)

        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._tick)
        self._timer.start()

    def _on_toggled(self, checked: bool) -> None:
        self.occupancy_toggled.emit(self.sector_id, checked)

    def update_from_state(self, state: dict[str, Any]) -> None:
        """Sincroniza colores, textos sanitarios y contadores desde ScadaViewModel."""
        self.title_lbl.setText(f"{state['name']} ({state['capacity']} vacas)")
        self.badge_lbl.setText(f"Estado: {state['status_badge']} — {state['cycle_desc']}")
        self.setStyleSheet(f"QFrame#SectorCard {{ border: 2px solid {state['color_hex']}; }}")
        self.occ_chk.blockSignals(True)
        self.occ_chk.setChecked(bool(state["is_occupied"]))
        self.occ_chk.blockSignals(False)
        self._allows_w = bool(state["allows_water"])
        self._water_rem, self._fan_rem = int(state["water_seconds"]), int(state["fan_seconds"])
        self._refresh_countdown_labels()

    def _tick(self) -> None:
        self._water_rem = max(0, self._water_rem - 1)
        self._fan_rem = max(0, self._fan_rem - 1)
        self._refresh_countdown_labels()

    def _refresh_countdown_labels(self) -> None:
        self.water_lbl.setText(
            "ASPERSION BLOQUEADA (Anti-Mastitis)" if not self._allows_w
            else (f"Bomba Aspersion: ACTIVA ({self._water_rem}s)" if self._water_rem > 0 else "Bomba Aspersion: OFF")
        )
        self.fan_lbl.setText(f"Ventiladores: ACTIVOS ({self._fan_rem}s)" if self._fan_rem > 0 else "Ventiladores: OFF")
