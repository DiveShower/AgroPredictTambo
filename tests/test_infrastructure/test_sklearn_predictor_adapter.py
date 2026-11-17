"""Pruebas de integración para el adaptador de inferencia Scikit-Learn."""

from datetime import datetime
from pathlib import Path

from src.domain.value_objects.weather_conditions import WeatherConditions
from src.infrastructure.ml.sklearn_predictor_adapter import (
    SklearnPredictorAdapter,
)


def _cond(temp: float, rh: float, rad: float = 100.0) -> WeatherConditions:
    return WeatherConditions(
        temperature_c=temp,
        relative_humidity=rh,
        wind_speed_kmh=8.0,
        solar_radiation_wm2=rad,
        timestamp=datetime(2026, 1, 15, 14, 0),
    )


def test_adapter_loads_default_model() -> None:
    adapter = SklearnPredictorAdapter()
    assert adapter.is_model_loaded is True


def test_adapter_predicts_comfort_and_danger() -> None:
    adapter = SklearnPredictorAdapter()
    assert adapter.predict_stress_level(_cond(20.0, 45.0, 50.0)) == 0
    assert (
        adapter.predict_stress_level(
            _cond(36.0, 75.0, 900.0), nocturnal_debt_hours=4
        )
        == 2
    )


def test_adapter_fallback_on_missing_model(tmp_path: Path) -> None:
    missing_path = tmp_path / "missing.joblib"
    adapter = SklearnPredictorAdapter(model_path=missing_path)
    assert adapter.is_model_loaded is False
    assert adapter.predict_stress_level(_cond(34.5, 68.0, 850.0)) == 2
