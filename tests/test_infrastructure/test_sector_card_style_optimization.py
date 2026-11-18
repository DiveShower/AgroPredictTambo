"""Pruebas unitarias de optimización QStyle dinámico en SectorCardWidget."""

import os
from typing import Any
from unittest.mock import patch

import pytest
from PyQt6.QtWidgets import QApplication

from src.infrastructure.ui.desktop.components.sector_card_widget import SectorCardWidget


@pytest.fixture(scope="module", autouse=True)
def qapp() -> QApplication:
    """Provee una instancia única de QApplication en modo offscreen."""
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance()
    return app if isinstance(app, QApplication) else QApplication([])


def _base_state(stress_level: int = 2) -> dict[str, Any]:
    return {
        "name": "Corral",
        "capacity": 80,
        "status_badge": "PELIGRO",
        "cycle_desc": "40s/270s",
        "color_hex": "#e74c3c",
        "is_occupied": True,
        "allows_water": True,
        "water_seconds": 40,
        "fan_seconds": 270,
        "stress_level": stress_level,
    }


def test_sector_card_dynamic_property_stress_level() -> None:
    """Verifica actualización de la propiedad dinámica QStyle stressLevel."""
    card = SectorCardWidget("s1")
    state = _base_state(2)
    card.update_from_state(state)
    assert card.property("stressLevel") == "2"
    state["stress_level"] = 0
    card.update_from_state(state)
    assert card.property("stressLevel") == "0"


def test_sector_card_skips_repolish_when_stress_level_unchanged() -> None:
    """Evita unpolish/polish redundante si stressLevel no cambió."""
    card = SectorCardWidget("s1")
    state = _base_state(1)
    style = card.style()
    assert style is not None
    with patch.object(style, "polish", wraps=style.polish) as mock_polish:
        card.update_from_state(state)
        card.update_from_state(state)
        assert mock_polish.call_count == 1
