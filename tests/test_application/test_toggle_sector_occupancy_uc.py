"""Pruebas unitarias para ocupación dinámica y estado consolidado del tambo."""

from datetime import datetime
from typing import Any

from src.application.use_cases.get_farm_status_uc import GetFarmStatusUseCase
from src.application.use_cases.toggle_sector_occupancy_uc import (
    ToggleSectorOccupancyUseCase,
)
from src.domain.entities.sector import Sector
from src.domain.value_objects.weather_conditions import WeatherConditions


def test_toggle_sector_occupancy_updates_and_returns_sector(mocker: Any) -> None:
    repo = mocker.Mock()
    updated = Sector("corral_espera", "Corral", 80, False)
    repo.get_by_id.return_value = updated

    uc = ToggleSectorOccupancyUseCase(repo)
    res = uc.execute("corral_espera", False)

    repo.update_occupancy.assert_called_once_with("corral_espera", False)
    repo.get_by_id.assert_called_once_with("corral_espera")
    assert res.current_occupancy is False


def test_get_farm_status_evaluates_occupied_and_empty_sectors(mocker: Any) -> None:
    repo, weather = mocker.Mock(), mocker.Mock()
    repo.get_all_sectors.return_value = [
        Sector("corral_espera", "Corral", 80, False),
        Sector("sombras", "Compost", 100, True, allows_water_sprinkling=False),
    ]
    weather.get_current_weather.return_value = WeatherConditions(
        34.0, 70.0, 8.0, datetime(2026, 1, 15, 14, 0), 800.0
    )

    uc = GetFarmStatusUseCase(repo, weather)
    statuses = uc.execute()

    assert len(statuses) == 2
    assert statuses[0].is_cooling_active is False
    assert statuses[0].current_stress_level == 0
    assert statuses[1].is_cooling_active is True
    assert statuses[1].current_stress_level == 2
    assert "Peligro Sanitario" in statuses[1].cycle_description
