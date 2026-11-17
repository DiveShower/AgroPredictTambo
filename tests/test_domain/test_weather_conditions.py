"""Tests unitarios para validación física de WeatherConditions."""

from dataclasses import FrozenInstanceError
from datetime import datetime
import pytest

from src.domain.exceptions.invalid_weather_exception import InvalidWeatherException
from src.domain.value_objects.weather_conditions import WeatherConditions


def test_valid_weather_conditions_and_wet_bulb_depression(
    sample_heatwave_weather: WeatherConditions,
) -> None:
    assert sample_heatwave_weather.temperature_c == 34.5
    assert sample_heatwave_weather.solar_radiation_wm2 == 820.0
    # A 34.5°C y 68% HR existe margen evaporativo positivo
    assert 3.0 < sample_heatwave_weather.wet_bulb_depression < 8.0


def test_saturated_air_has_near_zero_wet_bulb_depression() -> None:
    saturated = WeatherConditions(
        temperature_c=25.0,
        relative_humidity=100.0,
        wind_speed_kmh=5.0,
        timestamp=datetime(2026, 1, 15, 7, 0),
    )
    assert saturated.wet_bulb_depression == 0.0


@pytest.mark.parametrize(
    ("temp_c", "rh", "wind", "rad"),
    [
        (-16.0, 50.0, 10.0, 0.0),
        (56.0, 50.0, 10.0, 0.0),
        (25.0, -1.0, 10.0, 0.0),
        (25.0, 101.0, 10.0, 0.0),
        (25.0, 50.0, -0.5, 0.0),
        (25.0, 50.0, 10.0, -10.0),
    ],
)
def test_invalid_weather_raises_domain_exception(
    temp_c: float,
    rh: float,
    wind: float,
    rad: float,
) -> None:
    with pytest.raises(InvalidWeatherException):
        WeatherConditions(
            temperature_c=temp_c,
            relative_humidity=rh,
            wind_speed_kmh=wind,
            timestamp=datetime(2026, 1, 15, 12, 0),
            solar_radiation_wm2=rad,
        )


def test_weather_conditions_is_immutable(
    sample_temperate_weather: WeatherConditions,
) -> None:
    with pytest.raises(FrozenInstanceError):
        sample_temperate_weather.temperature_c = 30.0  # type: ignore[misc]
