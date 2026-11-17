"""Generador sintético horario del verano de Rafaela con olas de calor."""

from pathlib import Path

import numpy as np
import pandas as pd

from data.scripts.bioclimatic_enricher import (
    DEFAULT_OUTPUT_PATH,
    EXPECTED_COLUMNS,
    enrich_bioclimatic_features,
)

__all__ = ["EXPECTED_COLUMNS"]


def generate_synthetic_weather_df(n_hours: int = 2400, seed: int = 42) -> pd.DataFrame:
    """Simula ciclos horarios continuos del verano de Rafaela con 3 clases."""
    rng = np.random.default_rng(seed)
    ts = pd.date_range("2026-01-01 00:00:00", periods=n_hours, freq="1h")
    hrs = ts.hour.to_numpy(dtype=float)
    days = np.arange(n_hours, dtype=float) / 24.0
    diurnal = np.sin(2.0 * np.pi * (hrs - 9.0) / 24.0)
    wave = 5.5 * np.sin(2 * np.pi * days / 9) + 2.0 * np.cos(2 * np.pi * days / 23)
    t_raw = 24.5 + wave + 6.5 * diurnal + rng.normal(0.0, 0.8, n_hours)
    temp = np.clip(t_raw, -10.0, 50.0)
    rh = np.clip(64.0 - 18.0 * diurnal + rng.normal(0.0, 6.0, n_hours), 15.0, 98.0)
    wind = np.clip(11.0 + 4.0 * diurnal + rng.normal(0.0, 4.5, n_hours), 0.5, 45.0)
    cloud = np.clip(rng.normal(0.88, 0.15, n_hours), 0.2, 1.05)
    solar_bell = 950.0 * np.sin(np.pi * (hrs - 6.0) / 14.0) * cloud
    solar = np.where((hrs >= 6.0) & (hrs < 20.0), solar_bell, 0.0)
    base = pd.DataFrame(
        {
            "timestamp": ts,
            "temperature_c": np.round(temp, 2),
            "relative_humidity": np.round(rh, 2),
            "wind_speed_kmh": np.round(wind, 2),
            "solar_radiation_wm2": np.round(np.clip(solar, 0.0, 1200.0), 2),
        }
    )
    return enrich_bioclimatic_features(base)


def save_synthetic_dataset(
    output_path: Path = DEFAULT_OUTPUT_PATH, n_hours: int = 2400, seed: int = 42
) -> Path:
    """Genera y persiste el dataset sintético en CSV sin índice."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df = generate_synthetic_weather_df(n_hours=n_hours, seed=seed)
    df.to_csv(output_path, index=False)
    return output_path


if __name__ == "__main__":
    save_synthetic_dataset()
