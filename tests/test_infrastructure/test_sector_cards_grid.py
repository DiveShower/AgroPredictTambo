"""Pruebas unitarias para SectorCardsGrid y su timer maestro."""

import os
from typing import Any

import pytest
from PyQt6.QtWidgets import QApplication

from src.infrastructure.ui.desktop.components.sector_cards_grid import SectorCardsGrid


def _sample_state() -> dict[str, Any]:
    return {
        "sector_id": "s1",
        "name": "Corral",
        "capacity": 100,
        "status_badge": "ALERTA",
        "cycle_desc": "Vent",
        "color_hex": "#e74c3c",
        "is_occupied": True,
        "allows_water": True,
        "water_seconds": 30,
        "fan_seconds": 120,
        "stress_level": 1,
    }


@pytest.fixture(scope="module")
def qapp() -> QApplication:
    """Provee una instancia única de QApplication en modo offscreen."""
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance()
    return app if isinstance(app, QApplication) else QApplication([])


def test_sector_cards_grid_master_timer_synchronization(qapp: QApplication) -> None:
    """Valida timer maestro de 1s y sincronización del tick hacia las tarjetas."""
    assert isinstance(qapp, QApplication)
    grid = SectorCardsGrid([_sample_state()])
    assert grid.master_timer.isActive() is True
    assert grid.master_timer.interval() == 1000
    grid.master_timer.timeout.emit()
    card = grid.get_card("s1")
    assert card is not None
    assert card._water_rem == 29
    assert card._fan_rem == 119
    grid.master_timer.stop()


def test_sector_cards_grid_emergency_reset(qapp: QApplication) -> None:
    """Verifica que reset_emergency lleve a cero los contadores de las tarjetas."""
    assert isinstance(qapp, QApplication)
    grid = SectorCardsGrid([_sample_state()])
    grid.reset_emergency()
    card = grid.get_card("s1")
    assert card is not None
    assert card._water_rem == 0
    assert card._fan_rem == 0
    grid.master_timer.stop()
