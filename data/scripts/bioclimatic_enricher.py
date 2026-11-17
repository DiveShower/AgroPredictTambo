"""Enriquecedor tabular horario con ITH, deuda nocturna y estrés efectivo."""

import numpy as np
import pandas as pd

from data.scripts.bioclimatic_formulas import (
    DEFAULT_OUTPUT_PATH,
    EXPECTED_COLUMNS,
    compute_effective_heat_load,
    compute_thi_nrc,
    compute_wet_bulb_depression,
)

__all__ = ["DEFAULT_OUTPUT_PATH", "EXPECTED_COLUMNS", "enrich_bioclimatic_features"]


def _roll24(mask: np.ndarray) -> np.ndarray:
    return pd.Series(mask.astype(int)).rolling(24, min_periods=1).sum().to_numpy(int)


def enrich_bioclimatic_features(df: pd.DataFrame) -> pd.DataFrame:
    """Enriquece series horarias con THI, deuda nocturna y Carga Térmica Efectiva."""
    out = df.copy()
    hrs = pd.to_datetime(out["timestamp"]).dt.hour.to_numpy(dtype=int)
    t = out["temperature_c"].to_numpy(float)
    rh = out["relative_humidity"].to_numpy(float)
    thi = compute_thi_nrc(t, rh)
    thi_s = pd.Series(thi)
    roll = (
        thi_s.shift(1)
        .rolling(3, min_periods=1)
        .mean()
        .fillna(thi_s)
        .round(2)
        .to_numpy(float)
    )
    night = (hrs >= 21) | (hrs < 6)
    obs, cool = np.minimum(_roll24(night), 6), _roll24(night & (thi < 65.0))
    debt = np.clip(obs - cool, 0, 6).astype(int)
    ehl = compute_effective_heat_load(
        thi,
        roll,
        debt,
        out["solar_radiation_wm2"].to_numpy(float),
        out["wind_speed_kmh"].to_numpy(float),
    )
    out["hour_of_day"] = hrs
    out["wet_bulb_depression"] = compute_wet_bulb_depression(t, rh)
    out["thi_calculated"], out["thi_rolling_avg_3h"] = thi, roll
    out["nocturnal_debt_hours"] = debt
    rr = np.clip(40.0 + 1.75 * np.maximum(0.0, ehl - 55.0), 30.0, 120.0)
    out["respiratory_rate_est"] = np.round(rr, 2)
    out["stress_level"] = np.where(ehl >= 78.0, 2, np.where(ehl >= 72.0, 1, 0))
    return out[EXPECTED_COLUMNS]
