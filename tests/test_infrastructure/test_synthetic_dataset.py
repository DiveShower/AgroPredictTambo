"""Tests TDD para el generador sintético bioclimático (Tabla 5.8)."""

from pathlib import Path

import pandas as pd
import pytest
from data.scripts.generate_synthetic_dataset import (
    enrich_bioclimatic_features,
    generate_synthetic_weather_df,
    save_synthetic_dataset,
)

EXPECTED_COLUMNS = [
    "timestamp",
    "temperature_c",
    "relative_humidity",
    "wind_speed_kmh",
    "solar_radiation_wm2",
    "hour_of_day",
    "wet_bulb_depression",
    "thi_calculated",
    "thi_rolling_avg_3h",
    "nocturnal_debt_hours",
    "respiratory_rate_est",
    "stress_level",
]


def _build_day_df(
    night_t: float, night_rh: float, pre_t: float, wind: float, solar: float
) -> pd.DataFrame:
    ts = pd.date_range("2026-01-14 20:00:00", periods=19, freq="1h")
    is_night = (ts.hour >= 20) | (ts.hour < 6)
    is_pre = (ts.hour >= 6) & (ts.hour < 14)
    return pd.DataFrame(
        {
            "timestamp": ts,
            "temperature_c": [
                night_t if n else (pre_t if p else 27.6)
                for n, p in zip(is_night, is_pre)
            ],
            "relative_humidity": [night_rh if n else 60.0 for n in is_night],
            "wind_speed_kmh": [4.0 if n else wind for n in is_night],
            "solar_radiation_wm2": [0.0 if n else solar for n in is_night],
        }
    )


def test_generated_dataset_schema_and_nulls() -> None:
    df = generate_synthetic_weather_df()
    assert len(df) >= 2000
    assert list(df.columns) == EXPECTED_COLUMNS
    assert df.isna().sum().sum() == 0


def test_generated_dataset_physical_ranges_and_classes() -> None:
    df = generate_synthetic_weather_df()
    ranges = {
        "temperature_c": (-10.0, 50.0),
        "relative_humidity": (0.0, 100.0),
        "wind_speed_kmh": (0.0, 120.0),
        "solar_radiation_wm2": (0.0, 1200.0),
        "hour_of_day": (0, 23),
        "wet_bulb_depression": (0.0, 30.0),
        "thi_calculated": (40.0, 100.0),
        "thi_rolling_avg_3h": (40.0, 100.0),
        "nocturnal_debt_hours": (0, 6),
        "respiratory_rate_est": (30.0, 120.0),
    }
    for col, (low, high) in ranges.items():
        assert df[col].between(low, high).all(), f"Fuera de rango: {col}"
    assert set(df["stress_level"].unique()) == {0, 1, 2}


def test_effective_heat_load_escalates_and_relieves_stress() -> None:
    warm_df = _build_day_df(25.0, 70.0, pre_t=27.6, wind=1.0, solar=900.0)
    cool_df = _build_day_df(16.0, 50.0, pre_t=21.0, wind=36.0, solar=0.0)
    warm_last = enrich_bioclimatic_features(warm_df).iloc[-1]
    cool_last = enrich_bioclimatic_features(cool_df).iloc[-1]

    assert warm_last["thi_calculated"] == pytest.approx(76.47, abs=0.2)
    assert warm_last["thi_calculated"] < 78.0
    assert warm_last["nocturnal_debt_hours"] > 0
    assert warm_last["stress_level"] == 2

    assert cool_last["thi_calculated"] == pytest.approx(76.47, abs=0.2)
    assert cool_last["nocturnal_debt_hours"] == 0
    assert cool_last["stress_level"] < 2


def test_save_synthetic_dataset_writes_readable_csv(tmp_path: Path) -> None:
    out_file = tmp_path / "out.csv"
    saved_path = save_synthetic_dataset(out_file, n_hours=240)
    assert saved_path == out_file
    assert out_file.exists()
    loaded = pd.read_csv(out_file)
    assert len(loaded) == 240
    assert list(loaded.columns) == EXPECTED_COLUMNS
