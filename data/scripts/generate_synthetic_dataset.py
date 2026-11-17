"""Generador sintético bioclimático para estrés calórico bovino (Rafaela)."""

from pathlib import Path

import numpy as np
import pandas as pd

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
DATA_DIR = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = DATA_DIR / "processed/weather_heat_stress_dataset.csv"


def _stull_wbd(t: np.ndarray, rh: np.ndarray) -> np.ndarray:
    """Depresión de bulbo húmedo Stull (2011) en [0, 30]."""
    a = t * np.arctan(0.151977 * np.sqrt(rh + 8.313659))
    b = np.arctan(t + rh) - np.arctan(rh - 1.676331)
    c = 0.00391838 * (rh**1.5) * np.arctan(0.023101 * rh) - 4.686035
    return np.round(np.clip(t - (a + b + c), 0.0, 30.0), 2)


def _roll24(mask: np.ndarray) -> np.ndarray:
    return pd.Series(mask.astype(int)).rolling(24, min_periods=1).sum().to_numpy(int)


def enrich_bioclimatic_features(df: pd.DataFrame) -> pd.DataFrame:
    """Enriquece series horarias con THI, deuda nocturna y carga térmica efectiva."""
    out = df.copy()
    hours = pd.to_datetime(out["timestamp"]).dt.hour.to_numpy(dtype=int)
    t = out["temperature_c"].to_numpy(float)
    rh = out["relative_humidity"].to_numpy(float)
    wind = out["wind_speed_kmh"].to_numpy(float)
    rad = out["solar_radiation_wm2"].to_numpy(float)

    thi_raw = (1.8 * t + 32.0) - ((0.55 - 0.0055 * rh) * (1.8 * t - 26.0))
    thi = np.clip(np.round(thi_raw, 2), 40.0, 100.0)
    thi_s = pd.Series(thi)
    thi_roll = thi_s.shift(1).rolling(3, min_periods=1).mean().fillna(thi_s).round(2)
    thi_roll_arr = thi_roll.to_numpy(dtype=float)

    is_night = (hours >= 21) | (hours < 6)
    obs, cool = np.minimum(_roll24(is_night), 6), _roll24(is_night & (thi < 65.0))
    debt = np.clip(obs - cool, 0, 6).astype(int)

    rad_s = np.clip((rad - 500.0) / 500.0, 0.0, 1.0)
    rad_pen = np.where(rad > 500.0, 0.5 + 2.0 * rad_s, 0.0)
    inertia = 0.15 * np.maximum(0.0, thi_roll_arr - 72.0)
    ehl = thi + rad_pen + inertia + 0.35 * debt - 0.3 * (wind / 3.6)

    out["hour_of_day"] = hours
    out["wet_bulb_depression"] = _stull_wbd(t, rh)
    out["thi_calculated"] = thi
    out["thi_rolling_avg_3h"] = thi_roll_arr
    out["nocturnal_debt_hours"] = debt
    rr = np.clip(40.0 + 1.75 * np.maximum(0.0, ehl - 55.0), 30.0, 120.0)
    out["respiratory_rate_est"] = np.round(rr, 2)
    out["stress_level"] = np.where(ehl >= 78.0, 2, np.where(ehl >= 72.0, 1, 0))
    return out[EXPECTED_COLUMNS]


def generate_synthetic_weather_df(n_hours: int = 2400, seed: int = 42) -> pd.DataFrame:
    """Simula ciclos horarios continuos del verano de Rafaela con 3 clases."""
    rng = np.random.default_rng(seed)
    ts = pd.date_range("2026-01-01 00:00:00", periods=n_hours, freq="1h")
    hours = ts.hour.to_numpy(dtype=float)
    days = np.arange(n_hours, dtype=float) / 24.0
    diurnal = np.sin(2.0 * np.pi * (hours - 9.0) / 24.0)
    wave = 5.5 * np.sin(2 * np.pi * days / 9) + 2.0 * np.cos(2 * np.pi * days / 23)
    t_raw = 24.5 + wave + 6.5 * diurnal + rng.normal(0.0, 0.8, n_hours)
    temp = np.clip(t_raw, -10.0, 50.0)
    rh = np.clip(64.0 - 18.0 * diurnal + rng.normal(0.0, 6.0, n_hours), 15.0, 98.0)
    wind = np.clip(11.0 + 4.0 * diurnal + rng.normal(0.0, 4.5, n_hours), 0.5, 45.0)
    cloud = np.clip(rng.normal(0.88, 0.15, n_hours), 0.2, 1.05)
    solar_bell = 950.0 * np.sin(np.pi * (hours - 6.0) / 14.0) * cloud
    solar = np.where((hours >= 6.0) & (hours < 20.0), solar_bell, 0.0)
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
