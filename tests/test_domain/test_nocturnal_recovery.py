"""Tests unitarios para NocturnalRecovery y cálculo de deuda térmica."""

from datetime import datetime
import pytest

from src.domain.value_objects.nocturnal_recovery import NocturnalRecovery
from src.domain.value_objects.weather_conditions import WeatherConditions


def _make_night_obs(hour: int, temp_c: float, rh: float = 55.0) -> WeatherConditions:
    return WeatherConditions(
        temperature_c=temp_c,
        relative_humidity=rh,
        wind_speed_kmh=8.0,
        timestamp=datetime(2026, 1, 15, hour, 0),
    )


def test_full_nocturnal_recovery_yields_zero_penalty() -> None:
    # 17.0°C / 55% -> ITH ~ 61.6 (< 65.0) durante 7 horas
    cool_night = [_make_night_obs(h % 24, 17.0) for h in range(22, 29)]
    recovery = NocturnalRecovery.from_night_conditions(cool_night)

    assert recovery.cool_hours_count == 7
    assert recovery.debt_hours == 0
    assert recovery.has_thermal_debt is False
    assert recovery.threshold_penalty == 0.0


def test_partial_and_tropical_night_debt_penalties() -> None:
    # 2 horas frescas (17°C -> ITH < 65) y 6 horas cálidas (25°C / 70% -> ITH > 74)
    mixed_night = [_make_night_obs(0, 17.0), _make_night_obs(1, 17.0)] + [
        _make_night_obs(h, 25.0, rh=70.0) for h in range(2, 8)
    ]
    partial = NocturnalRecovery.from_night_conditions(mixed_night)

    # 0 horas frescas -> deuda máxima 6h, penalización tope 3.0
    tropical_night = [_make_night_obs(h, 27.0, rh=75.0) for h in range(0, 8)]
    tropical = NocturnalRecovery.from_night_conditions(tropical_night)

    assert partial.cool_hours_count == 2
    assert partial.debt_hours == 4
    assert partial.has_thermal_debt is True
    assert partial.threshold_penalty == pytest.approx(2.0)

    assert tropical.cool_hours_count == 0
    assert tropical.debt_hours == 6
    assert tropical.threshold_penalty == pytest.approx(3.0)
