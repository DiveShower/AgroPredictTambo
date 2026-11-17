"""Tests TDD para el generador sintético bioclimático (Tabla 5.8)."""

from data.scripts.generate_synthetic_dataset import (
    EXPECTED_COLUMNS,
    generate_synthetic_weather_df,
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
