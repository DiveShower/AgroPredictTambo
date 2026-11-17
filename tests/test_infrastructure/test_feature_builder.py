"""Tests TDD para el constructor de features sin fuga de datos (Tabla 5.8)."""

from datetime import datetime

import pandas as pd
import pytest
from src.infrastructure.ml.feature_builder import (
    FEATURE_COLUMNS,
    build_feature_vector,
    build_inference_frame,
    extract_training_matrix,
)

from src.domain.value_objects.thi_score import THI_Score
from src.domain.value_objects.weather_conditions import WeatherConditions

EXPECTED_FEATURES = (
    "temperature_c",
    "relative_humidity",
    "wind_speed_kmh",
    "solar_radiation_wm2",
    "hour_of_day",
    "wet_bulb_depression",
    "thi_rolling_avg_3h",
    "nocturnal_debt_hours",
)
FORBIDDEN = ("thi_calculated", "respiratory_rate_est", "stress_level", "timestamp")


def _make_weather(temp: float, rh: float, hour: int = 14) -> WeatherConditions:
    return WeatherConditions(
        temperature_c=temp,
        relative_humidity=rh,
        wind_speed_kmh=12.0,
        timestamp=datetime(2026, 1, 15, hour, 0),
        solar_radiation_wm2=650.0,
    )


def _thi(w: WeatherConditions) -> float:
    return THI_Score.calculate(w.temperature_c, w.relative_humidity).value


def test_feature_columns_has_zero_data_leakage() -> None:
    assert len(FEATURE_COLUMNS) == 8
    assert tuple(FEATURE_COLUMNS) == EXPECTED_FEATURES
    assert set(FORBIDDEN).isdisjoint(FEATURE_COLUMNS)


def test_extract_training_matrix_drops_audit_and_target_columns() -> None:
    row = {
        col: [float(i + 1)] for i, col in enumerate((*EXPECTED_FEATURES, *FORBIDDEN))
    }
    row["timestamp"] = [datetime(2026, 1, 15, 14, 0)]
    df = pd.DataFrame(row)

    matrix = extract_training_matrix(df)
    assert list(matrix.columns) == list(FEATURE_COLUMNS)
    assert matrix.shape == (1, 8)
    assert set(FORBIDDEN).isdisjoint(matrix.columns)

    with pytest.raises(ValueError):
        extract_training_matrix(df.drop(columns=["wet_bulb_depression"]))


def test_build_feature_vector_with_history_and_without_history() -> None:
    current = _make_weather(temp=32.0, rh=70.0, hour=15)
    history = [
        _make_weather(temp=18.0, rh=40.0, hour=11),
        _make_weather(temp=28.0, rh=60.0, hour=12),
        _make_weather(temp=30.0, rh=65.0, hour=13),
        _make_weather(temp=31.0, rh=70.0, hour=14),
    ]
    vec = build_feature_vector(current, recent_history=history, nocturnal_debt_hours=10)
    expected_avg = sum(_thi(w) for w in history[-3:]) / 3.0

    assert len(vec) == 8
    assert all(isinstance(val, float) for val in vec)
    assert vec[:6] == [32.0, 70.0, 12.0, 650.0, 15.0, current.wet_bulb_depression]
    assert vec[6] == pytest.approx(expected_avg, abs=0.01)
    assert vec[7] == 6.0

    fallback_vec = build_feature_vector(current, nocturnal_debt_hours=-2)
    assert fallback_vec[6] == pytest.approx(_thi(current), abs=0.01)
    assert fallback_vec[7] == 0.0


def test_build_inference_frame_columns_match_training_matrix() -> None:
    current = _make_weather(temp=29.0, rh=55.0, hour=16)
    frame = build_inference_frame(current, nocturnal_debt_hours=2)
    assert isinstance(frame, pd.DataFrame)
    assert frame.shape == (1, 8)
    assert list(frame.columns) == list(FEATURE_COLUMNS)
    expected = build_feature_vector(current, nocturnal_debt_hours=2)
    assert frame.iloc[0].tolist() == pytest.approx(expected)
