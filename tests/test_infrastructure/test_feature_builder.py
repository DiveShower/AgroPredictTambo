"""Tests TDD para el constructor de features sin fuga de datos (Tabla 5.8)."""

from datetime import datetime

import pandas as pd
import pytest

from src.infrastructure.ml.feature_builder import (
    FEATURE_COLUMNS,
    extract_training_matrix,
)

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


def test_feature_columns_has_zero_data_leakage() -> None:
    assert len(FEATURE_COLUMNS) == 8
    assert tuple(FEATURE_COLUMNS) == EXPECTED_FEATURES
    assert set(FORBIDDEN).isdisjoint(FEATURE_COLUMNS)


def test_extract_training_matrix_drops_audit_and_target_columns() -> None:
    row: dict[str, list[float] | list[datetime]] = {
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
