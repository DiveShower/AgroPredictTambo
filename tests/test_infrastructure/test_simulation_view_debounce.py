"""Pruebas unitarias para SimulationView y su temporizador debounce."""

import os
from unittest.mock import MagicMock

import pytest
from PyQt6.QtWidgets import QApplication

from src.adapters.desktop.viewmodels.forecast_viewmodel import ForecastViewModel
from src.infrastructure.ui.desktop.views.simulation_view import SimulationView


def _sim(t: float, c: str) -> dict[str, object]:
    return {"thi_value": t, "category": c, "concrete_order": "C", "compost_order": "M"}


class _StubViewModel(ForecastViewModel):
    def __init__(self) -> None:
        self.mock = MagicMock(return_value=_sim(75.0, "Alerta"))

    def simulate_custom_conditions(
        self, temp_c: float, rh: float, wind_kmh: float, rad_wm2: float
    ) -> dict[str, object]:
        return self.mock(temp_c, rh, wind_kmh, rad_wm2)


@pytest.fixture(scope="module")
def qapp() -> QApplication:
    """Provee una instancia única de QApplication en modo offscreen."""
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance()
    return app if isinstance(app, QApplication) else QApplication([])


def test_simulation_view_debounce_timer_configured(qapp: QApplication) -> None:
    """Valida single-shot, activación del timer y etiqueta inmediata al mover slider."""
    assert isinstance(qapp, QApplication)
    view = SimulationView(_StubViewModel())
    assert view.debounce_timer.isSingleShot() is True
    view.temp_slider.setValue(38)
    assert view.debounce_timer.isActive() is True
    assert "38C" in view.params_lbl.text()
    view.debounce_timer.stop()


def test_simulation_view_runs_simulation_on_timeout(qapp: QApplication) -> None:
    """Verifica que timeout ejecute la simulación y formatee result_lbl."""
    assert isinstance(qapp, QApplication)
    vm = _StubViewModel()
    view = SimulationView(vm)
    vm.mock.return_value = _sim(84.0, "Peligro")
    view.temp_slider.setValue(38)
    view.debounce_timer.stop()
    view.debounce_timer.timeout.emit()

    assert "ITH: 84.0 (Peligro)" in view.result_lbl.text()
    assert "Hormigon: C | Compost: M" in view.result_lbl.text()
    vm.mock.assert_called_with(38.0, 68.0, 6.0, 820.0)
