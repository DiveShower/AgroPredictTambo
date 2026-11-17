"""Constructor de matriz de features sin fuga de datos para entrenamiento e inferencia."""

from collections.abc import Sequence

import pandas as pd

from src.domain.value_objects.thi_score import THI_Score
from src.domain.value_objects.weather_conditions import WeatherConditions

FEATURE_COLUMNS: tuple[str, ...] = (
    "temperature_c",
    "relative_humidity",
    "wind_speed_kmh",
    "solar_radiation_wm2",
    "hour_of_day",
    "wet_bulb_depression",
    "thi_rolling_avg_3h",
    "nocturnal_debt_hours",
)


def extract_training_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Extrae la matriz X validando presencia de columnas y excluyendo targets/auditoría."""
    missing = [col for col in FEATURE_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(
            f"Faltan columnas requeridas en el DataFrame: {', '.join(missing)}"
        )
    return df.loc[:, list(FEATURE_COLUMNS)].copy()


def build_feature_vector(
    conditions: WeatherConditions,
    recent_history: Sequence[WeatherConditions] = (),
    nocturnal_debt_hours: int = 0,
) -> list[float]:
    """Construye el vector ordenado de 8 features float para inferencia puntual."""
    thi_avg_3h = THI_Score.rolling_average(conditions, recent_history, window=3)
    clamped_debt = max(0, min(6, nocturnal_debt_hours))
    return [
        float(conditions.temperature_c),
        float(conditions.relative_humidity),
        float(conditions.wind_speed_kmh),
        float(conditions.solar_radiation_wm2),
        float(conditions.timestamp.hour),
        float(conditions.wet_bulb_depression),
        float(thi_avg_3h),
        float(clamped_debt),
    ]


def build_inference_frame(
    conditions: WeatherConditions,
    recent_history: Sequence[WeatherConditions] = (),
    nocturnal_debt_hours: int = 0,
) -> pd.DataFrame:
    """Construye un DataFrame de 1 fila con columnas idénticas al entrenamiento."""
    vec = build_feature_vector(conditions, recent_history, nocturnal_debt_hours)
    return pd.DataFrame([vec], columns=list(FEATURE_COLUMNS))
