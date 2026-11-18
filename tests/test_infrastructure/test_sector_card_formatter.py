"""Pruebas unitarias para el formateador de etiquetas de SectorCardWidget."""

from src.infrastructure.ui.desktop.components.sector_card_formatter import (
    format_fan_label,
    format_water_label,
)


def test_format_water_label_scenarios() -> None:
    """Verifica el formateo de la etiqueta de aspersión en todos sus escenarios."""
    assert format_water_label(False, 20) == "ASPERSION BLOQUEADA (Anti-Mastitis)"
    assert format_water_label(True, 15) == "Bomba Aspersion: ACTIVA (15s)"
    assert format_water_label(True, 0) == "Bomba Aspersion: OFF"


def test_format_fan_label_scenarios() -> None:
    """Verifica el formateo de la etiqueta de ventiladores en todos sus escenarios."""
    assert format_fan_label(45) == "Ventiladores: ACTIVOS (45s)"
    assert format_fan_label(0) == "Ventiladores: OFF"
