"""Vista de simulación interactiva con sliders bioclimáticos para el jurado."""

from typing import Optional
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFormLayout, QLabel, QSlider, QVBoxLayout, QWidget
from src.adapters.desktop.viewmodels.forecast_viewmodel import ForecastViewModel


def _make_slider(min_v: int, max_v: int, val: int) -> QSlider:
    s = QSlider(Qt.Orientation.Horizontal)
    s.setRange(min_v, max_v)
    s.setValue(val)
    return s


class SimulationView(QWidget):
    """Pestaña 4: Permite al jurado mover sliders de clima y ver respuesta en vivo."""

    def __init__(
        self,
        viewmodel: ForecastViewModel,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._viewmodel = viewmodel
        root = QVBoxLayout(self)
        form = QFormLayout()

        self.temp_slider = _make_slider(15, 45, 34)
        self.rh_slider = _make_slider(20, 95, 68)
        self.wind_slider = _make_slider(0, 40, 6)
        self.rad_slider = _make_slider(0, 1000, 820)

        for lbl, sld in (
            ("Temperatura (15 a 45 C):", self.temp_slider),
            ("Humedad Relativa (20 a 95 %):", self.rh_slider),
            ("Velocidad de Viento (0 a 40 km/h):", self.wind_slider),
            ("Radiacion Solar (0 a 1000 W/m2):", self.rad_slider),
        ):
            sld.valueChanged.connect(self._recalculate)
            form.addRow(lbl, sld)

        root.addLayout(form)
        self.params_lbl = QLabel()
        self.result_lbl = QLabel()
        self.result_lbl.setObjectName("HeaderTitle")
        root.addWidget(self.params_lbl)
        root.addWidget(self.result_lbl)
        self._recalculate()

    def _recalculate(self) -> None:
        t, rh = float(self.temp_slider.value()), float(self.rh_slider.value())
        w, rad = float(self.wind_slider.value()), float(self.rad_slider.value())
        res = self._viewmodel.simulate_custom_conditions(t, rh, w, rad)
        self.params_lbl.setText(f"Entrada: {t:.0f}C | HR {rh:.0f}% | Viento {w:.0f} km/h | Rad {rad:.0f} W/m2")
        self.result_lbl.setText(
            f"ITH: {res['thi_value']} ({res['category']}) | Hormigon: {res['concrete_order']} | Compost: {res['compost_order']}"
        )
