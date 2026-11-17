"""Fórmulas bioclimáticas vectorizadas (paridad con src/domain/) y esquema CSV."""

from pathlib import Path

import numpy as np

EXPECTED_COLUMNS: list[str] = [
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
DATA_DIR = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = DATA_DIR / "processed/weather_heat_stress_dataset.csv"


def compute_wet_bulb_depression(t: np.ndarray, rh: np.ndarray) -> np.ndarray:
    """Depresión de bulbo húmedo Stull (2011) en [0, 30] (paridad con dominio)."""
    a = t * np.arctan(0.151977 * np.sqrt(rh + 8.313659))
    b = np.arctan(t + rh) - np.arctan(rh - 1.676331)
    c = 0.00391838 * (rh**1.5) * np.arctan(0.023101 * rh) - 4.686035
    return np.round(np.clip(t - (a + b + c), 0.0, 30.0), 2)


def compute_thi_nrc(t: np.ndarray, rh: np.ndarray) -> np.ndarray:
    """Calcula el ITH NRC en grados Celsius acotado en [40, 100]."""
    raw = (1.8 * t + 32.0) - ((0.55 - 0.0055 * rh) * (1.8 * t - 26.0))
    return np.clip(np.round(raw, 2), 40.0, 100.0)


def compute_effective_heat_load(
    thi: np.ndarray,
    roll: np.ndarray,
    debt: np.ndarray,
    rad: np.ndarray,
    wind: np.ndarray,
) -> np.ndarray:
    """Índice de Carga Térmica Efectiva (Oliveira et al., 2025)."""
    rad_s = np.clip((rad - 500.0) / 500.0, 0.0, 1.0)
    rad_pen = np.where(rad > 500.0, 0.5 + 2.0 * rad_s, 0.0)
    inertia = 0.15 * np.maximum(0.0, roll - 72.0)
    return thi + rad_pen + inertia + 0.35 * debt - 0.3 * (wind / 3.6)
