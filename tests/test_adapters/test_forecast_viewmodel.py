"""Pruebas unitarias para ForecastViewModel (curva 24h y simulador jurado)."""

from datetime import datetime, timedelta
from typing import Any

from src.adapters.desktop.viewmodels.forecast_viewmodel import ForecastViewModel
from src.domain.value_objects.weather_conditions import WeatherConditions


def test_forecast_viewmodel_24h_curve_with_nocturnal_debt(mocker: Any) -> None:
    weather = mocker.Mock()
    start = datetime(2026, 1, 15, 0, 0)
    # 6 horas nocturnas cálidas (26°C, 65% HR -> ITH > 65) + horas diurnas extremas
    forecast = [
        WeatherConditions(
            temperature_c=26.0 if h < 6 else 34.5,
            relative_humidity=65.0 if h < 6 else 68.0,
            wind_speed_kmh=8.0,
            timestamp=start + timedelta(hours=h),
            solar_radiation_wm2=0.0 if h < 6 else 800.0,
        )
        for h in range(24)
    ]
    weather.get_hourly_forecast.return_value = forecast

    vm = ForecastViewModel(weather)
    data = vm.get_24h_curve_data()

    assert len(data["hours_labels"]) == 24
    assert len(data["thi_values"]) == 24
    assert data["nocturnal_penalty"] == 3.0
    assert data["alert_threshold"] == 69.0
    assert data["danger_threshold"] == 75.0
    assert len(data["danger_indices"]) > 0


def test_forecast_viewmodel_simulate_custom_conditions() -> None:
    vm = ForecastViewModel(weather_provider=None)  # type: ignore[arg-type]
    res = vm.simulate_custom_conditions(35.0, 70.0, 5.0, 850.0)

    assert res["stress_level"] == 2
    assert "Agua: 40s" in res["concrete_order"]
    assert "Agua: 0s (Bloqueo Anti-Mastitis)" in res["compost_order"]
