"""Pruebas unitarias para el adaptador predictor heurístico."""

from datetime import datetime

from src.domain.value_objects.weather_conditions import WeatherConditions
from src.infrastructure.ml.heuristic_predictor_adapter import (
    HeuristicPredictorAdapter,
)


def _cond(
    temp: float, rh: float, wind: float = 10.0, rad: float = 100.0
) -> WeatherConditions:
    return WeatherConditions(
        temperature_c=temp,
        relative_humidity=rh,
        wind_speed_kmh=wind,
        solar_radiation_wm2=rad,
        timestamp=datetime(2026, 1, 15, 12, 0),
    )


def test_heuristic_comfort() -> None:
    pred = HeuristicPredictorAdapter()
    assert pred.predict_stress_level(_cond(20.0, 45.0)) == 0


def test_heuristic_alert() -> None:
    pred = HeuristicPredictorAdapter()
    assert pred.predict_stress_level(_cond(26.0, 60.0)) == 1


def test_heuristic_danger() -> None:
    pred = HeuristicPredictorAdapter()
    assert pred.predict_stress_level(_cond(34.5, 68.0, rad=850.0)) == 2


def test_heuristic_nocturnal_debt_escalation() -> None:
    pred = HeuristicPredictorAdapter()
    c = _cond(26.5, 50.0, rad=650.0)
    assert pred.predict_stress_level(
        c, nocturnal_debt_hours=6
    ) >= pred.predict_stress_level(c, nocturnal_debt_hours=0)
