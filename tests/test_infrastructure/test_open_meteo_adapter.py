"""Pruebas de integración para OpenMeteoAdapter y MockWeatherAdapter."""

from typing import Any

from src.infrastructure.weather_api.mock_weather_adapter import (
    MockWeatherAdapter,
)
from src.infrastructure.weather_api.open_meteo_adapter import OpenMeteoAdapter


def test_open_meteo_adapter_parses_current_and_hourly(mocker: Any) -> None:
    fake_payload = {
        "current": {
            "time": "2026-01-15T14:00",
            "temperature_2m": 32.5,
            "relative_humidity_2m": 64.0,
            "wind_speed_10m": 12.0,
            "shortwave_radiation": 780.0,
        },
        "hourly": {
            "time": ["2026-01-15T14:00", "2026-01-15T15:00"],
            "temperature_2m": [32.5, 33.8],
            "relative_humidity_2m": [64.0, 60.0],
            "wind_speed_10m": [12.0, 10.5],
            "shortwave_radiation": [780.0, 810.0],
        },
    }
    mock_resp = mocker.Mock()
    mock_resp.json.return_value = fake_payload
    mock_get = mocker.patch("requests.get", return_value=mock_resp)

    adapter = OpenMeteoAdapter()
    curr = adapter.get_current_weather(-31.25, -61.48)
    fore = adapter.get_hourly_forecast(-31.25, -61.48, hours=2)

    assert mock_get.call_count == 2
    assert curr.temperature_c == 32.5
    assert curr.solar_radiation_wm2 == 780.0
    assert len(fore) == 2
    assert fore[1].temperature_c == 33.8


def test_mock_weather_adapter_profiles() -> None:
    adapter = MockWeatherAdapter(profile="heatwave")
    assert adapter.get_current_weather(-31.25, -61.48).temperature_c == 34.5

    adapter.set_profile("temperate")
    assert adapter.get_current_weather(-31.25, -61.48).temperature_c == 20.0

    adapter.set_profile("nocturnal_debt")
    fore = adapter.get_hourly_forecast(-31.25, -61.48, hours=6)
    assert len(fore) == 6
    assert all(c.temperature_c == 26.0 for c in fore)
