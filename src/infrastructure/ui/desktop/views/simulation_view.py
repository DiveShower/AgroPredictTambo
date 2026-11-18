"""Vista de simulación interactiva con sliders bioclimáticos para el jurado."""

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from src.adapters.desktop.viewmodels.forecast_viewmodel import ForecastViewModel
from src.infrastructure.ui.desktop.components.simulation_slider_group import (
    SimulationSliderGroup,
)


class SimulationView(QWidget):
    """Pestaña 4: Permite al jurado mover sliders de clima y ver respuesta en vivo."""

    def __init__(
        self,
        viewmodel: ForecastViewModel,
        parent: QWidget | None = None,
    ) -> None:
        """Inicializa sliders agrupados, etiquetas de salida y timer debounce."""
        super().__init__(parent)
        self._viewmodel = viewmodel
        root = QVBoxLayout(self)
        self.sliders = SimulationSliderGroup(self)
        self.temp_slider = self.sliders.temp_slider
        self.rh_slider = self.sliders.rh_slider
        self.wind_slider = self.sliders.wind_slider
        self.rad_slider = self.sliders.rad_slider
        root.addWidget(self.sliders)

        self.params_lbl = QLabel()
        self.result_lbl = QLabel()
        self.result_lbl.setObjectName("HeaderTitle")
        root.addWidget(self.params_lbl)
        root.addWidget(self.result_lbl)
        self.debounce_timer = QTimer(self)
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.timeout.connect(self._run_simulation)
        self.sliders.values_changed.connect(self._on_values_changed)
        self._update_params_label()
        self._run_simulation()

    def _update_params_label(self) -> None:
        t, rh, w, rad = self.sliders.current_values()
        self.params_lbl.setText(
            f"Entrada: {t:.0f}C | HR {rh:.0f}% | "
            f"Viento {w:.0f} km/h | Rad {rad:.0f} W/m2"
        )

    def _on_values_changed(self) -> None:
        self._update_params_label()
        self.debounce_timer.start(80)

    def _run_simulation(self) -> None:
        t, rh, w, rad = self.sliders.current_values()
        res = self._viewmodel.simulate_custom_conditions(t, rh, w, rad)
        self.result_lbl.setText(
            f"ITH: {res['thi_value']} ({res['category']}) | "
            f"Hormigon: {res['concrete_order']} | Compost: {res['compost_order']}"
        )
