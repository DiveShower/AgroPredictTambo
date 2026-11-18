"""Pruebas unitarias para el grupo de sliders de simulación bioclimática."""

import os

import pytest
from PyQt6.QtWidgets import QApplication

from src.infrastructure.ui.desktop.components.simulation_slider_group import (
    SimulationSliderGroup,
)


@pytest.fixture(scope="module")
def qapp() -> QApplication:
    """Provee una instancia única de QApplication en modo offscreen."""
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance()
    return app if isinstance(app, QApplication) else QApplication([])


def test_simulation_slider_group_initial_values(qapp: QApplication) -> None:
    """Verifica los valores iniciales retornados por current_values()."""
    assert isinstance(qapp, QApplication)
    group = SimulationSliderGroup()

    assert group.current_values() == (34.0, 68.0, 6.0, 820.0)


def test_simulation_slider_group_updates(qapp: QApplication) -> None:
    """Valida actualización de valores y emisión de values_changed al mover un slider."""
    assert isinstance(qapp, QApplication)
    group = SimulationSliderGroup()
    emitted: list[bool] = []
    group.values_changed.connect(lambda: emitted.append(True))

    group.temp_slider.setValue(40)

    assert group.current_values()[0] == 40.0
    assert emitted == [True]
