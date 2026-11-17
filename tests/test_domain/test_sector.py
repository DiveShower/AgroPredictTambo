"""Tests unitarios para las entidades Sector y Farm y sus reglas sanitarias."""

import pytest

from src.domain.entities.farm import Farm
from src.domain.entities.sector import Sector
from src.domain.exceptions.sector_not_found_exception import SectorNotFoundException


def test_unoccupied_sector_never_requires_cooling(holding_pen_sector: Sector) -> None:
    holding_pen_sector.set_occupancy(False)

    assert holding_pen_sector.current_occupancy is False
    assert holding_pen_sector.requires_cooling(thi_val=85.0) is False


def test_occupied_sector_evaluates_thresholds_and_nocturnal_penalty(
    holding_pen_sector: Sector,
) -> None:
    # Con ITH 70.0 y sin penalización está en confort (< 72.0)
    assert holding_pen_sector.evaluate_stress_level(70.0, nocturnal_penalty=0.0) == 0
    assert holding_pen_sector.requires_cooling(70.0, nocturnal_penalty=0.0) is False

    # Con penalización nocturna de 3.0 pts, umbral baja a 69.0 -> ITH 70.0 ya alerta
    assert holding_pen_sector.effective_alert_threshold(nocturnal_penalty=3.0) == 69.0
    assert holding_pen_sector.effective_danger_threshold(nocturnal_penalty=3.0) == 75.0
    assert holding_pen_sector.evaluate_stress_level(70.0, nocturnal_penalty=3.0) == 1
    assert holding_pen_sector.requires_cooling(70.0, nocturnal_penalty=3.0) is True


def test_default_farm_anti_mastitis_rule_and_lookup(default_farm: Farm) -> None:
    sombras = default_farm.get_sector("sombras")
    corral = default_farm.get_sector("corral_espera")
    comederos = default_farm.get_sector("comederos")

    assert sombras.allows_water_sprinkling is False
    assert sombras.sprinkler_count == 0
    assert sombras.thi_threshold_alert == 70.0
    assert corral.allows_water_sprinkling is True
    assert comederos.allows_water_sprinkling is True
    assert default_farm.total_occupied_cows() == 300

    comederos.set_occupancy(False)
    assert default_farm.total_occupied_cows() == 180


def test_farm_get_unknown_sector_raises_exception(default_farm: Farm) -> None:
    with pytest.raises(SectorNotFoundException):
        default_farm.get_sector("sector_inexistente")
