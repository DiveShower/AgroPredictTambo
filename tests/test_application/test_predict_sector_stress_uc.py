"""Pruebas unitarias para PredictSectorStressUseCase con mocks de puertos."""

from datetime import datetime
from typing import Any

from src.application.dtos.predict_stress_request_dto import PredictStressRequestDTO
from src.application.use_cases.predict_sector_stress_uc import PredictSectorStressUseCase
from src.domain.entities.sector import Sector
from src.domain.value_objects.weather_conditions import WeatherConditions


def _w(temp: float, rh: float, hour: int = 14, minute: int = 0) -> WeatherConditions:
    return WeatherConditions(temp, rh, 10.0, datetime(2026, 1, 15, hour, minute), 800.0)


def test_predict_orders_anti_mastitis_and_empty_sector(mocker: Any) -> None:
    weather = mocker.Mock()
    weather.get_current_weather.return_value = _w(34.0, 68.0, 13)
    weather.get_hourly_forecast.return_value = [_w(34.0, 68.0, 13), _w(35.0, 70.0, 14)]
    repo = mocker.Mock()
    repo.get_all_sectors.return_value = [
        Sector("vacio", "Corral Vacío", 80, False, allows_water_sprinkling=True),
        Sector("comederos", "Comederos", 120, True, allows_water_sprinkling=True),
        Sector("sombras", "Compost Barn", 100, True, allows_water_sprinkling=False),
    ]
    predictor = mocker.Mock()
    predictor.predict_stress_level.return_value = 2
    notifier, hw = mocker.Mock(), mocker.Mock()

    uc = PredictSectorStressUseCase(weather, repo, predictor, notifier, hw)
    res = uc.execute(PredictStressRequestDTO())

    assert len(res.cooling_orders) == 3
    assert (res.cooling_orders[0].water_mist_seconds, res.cooling_orders[0].fan_ventilation_seconds) == (0, 0)
    assert (res.cooling_orders[1].water_mist_seconds, res.cooling_orders[1].fan_ventilation_seconds) == (40, 270)
    assert (res.cooling_orders[2].water_mist_seconds, res.cooling_orders[2].fan_ventilation_seconds) == (0, 270)
    assert len(res.alerts) == 2
    assert notifier.send_alert.call_count == 2
    hw.activate_water_valve.assert_called_once_with("comederos", 40)


def test_offline_cache_fallback_and_milking_precooling(mocker: Any) -> None:
    weather, cache, repo, predictor = mocker.Mock(), mocker.Mock(), mocker.Mock(), mocker.Mock()
    weather.get_current_weather.side_effect = RuntimeError("Sin red rural")
    cache.is_cache_valid.return_value = True
    cache.get_cached_forecast.return_value = [_w(33.0, 65.0, 15, 0), _w(35.0, 70.0, 15, 50)]
    repo.get_all_sectors.return_value = [Sector("corral_espera", "Corral", 80, True)]
    predictor.predict_stress_level.return_value = 1

    uc = PredictSectorStressUseCase(weather, repo, predictor, weather_cache=cache)
    res = uc.execute(PredictStressRequestDTO(forecast_lead_hours=1))

    assert res.cooling_orders[0].stress_level == 2
    assert res.cooling_orders[0].water_mist_seconds == 40
    assert "Pre-enfriamiento" in res.cooling_orders[0].justification
