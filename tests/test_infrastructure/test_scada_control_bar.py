"""Pruebas unitarias para la barra de controles SCADA."""

import os

import pytest
from PyQt6.QtWidgets import QApplication

from src.infrastructure.ui.desktop.components.scada_control_bar import ScadaControlBar


@pytest.fixture(scope="module")
def qapp() -> QApplication:
    """Provee una instancia única de QApplication en modo offscreen."""
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance()
    return app if isinstance(app, QApplication) else QApplication([])


def test_scada_control_bar_initial_and_busy_state(qapp: QApplication) -> None:
    """Valida el estado inicial y las transiciones busy de los botones."""
    assert isinstance(qapp, QApplication)
    bar = ScadaControlBar()

    assert bar.sync_btn.isEnabled() is True
    assert bar.sync_btn.text() == "Sincronizar Clima Ahora"

    bar.set_sync_busy(True)
    assert bar.sync_btn.isEnabled() is False
    assert bar.demo_btn.isEnabled() is False
    assert bar.sync_btn.text() == "Sincronizando..."

    bar.set_sync_busy(False)
    assert bar.sync_btn.isEnabled() is True
    assert bar.demo_btn.isEnabled() is True
    assert bar.sync_btn.text() == "Sincronizar Clima Ahora"


def test_scada_control_bar_signals(qapp: QApplication) -> None:
    """Verifica la emisión de las señales al pulsar cada botón."""
    assert isinstance(qapp, QApplication)
    bar = ScadaControlBar()
    emitted: list[str] = []

    bar.sync_requested.connect(lambda: emitted.append("sync"))
    bar.demo_heatwave_requested.connect(lambda: emitted.append("demo"))
    bar.emergency_requested.connect(lambda: emitted.append("emergency"))

    bar.sync_btn.click()
    bar.demo_btn.click()
    bar.stop_btn.click()

    assert emitted == ["sync", "demo", "emergency"]
