"""Ingesta histórica climática de Open-Meteo Archive con fallback sintético."""

import sys
from pathlib import Path
from typing import Any

import pandas as pd
import requests

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from data.scripts.generate_synthetic_dataset import (
    DEFAULT_OUTPUT_PATH,
    enrich_bioclimatic_features,
    generate_synthetic_weather_df,
)

ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
HOURLY_FIELDS = "temperature_2m,relative_humidity_2m,wind_speed_10m,shortwave_radiation"
COLUMN_MAP = {
    "time": "timestamp",
    "temperature_2m": "temperature_c",
    "relative_humidity_2m": "relative_humidity",
    "wind_speed_10m": "wind_speed_kmh",
    "shortwave_radiation": "solar_radiation_wm2",
}


def parse_open_meteo_archive_payload(payload: dict[str, Any]) -> pd.DataFrame:
    """Valida, limpia y enriquece la serie horaria devuelta por Open-Meteo Archive."""
    hourly = payload.get("hourly")
    if not hourly:
        raise ValueError("El payload no contiene el bloque 'hourly'.")
    missing = [key for key in COLUMN_MAP if key not in hourly]
    if missing:
        raise ValueError(f"Faltan claves requeridas en 'hourly': {missing}")

    raw_df = (
        pd.DataFrame({dest: hourly[src] for src, dest in COLUMN_MAP.items()})
        .dropna()
        .reset_index(drop=True)
    )
    if raw_df.empty:
        raise ValueError("El DataFrame climático quedó vacío tras eliminar nulos.")
    return enrich_bioclimatic_features(raw_df)


def fetch_rafaela_historical_weather(
    start_date: str = "2025-12-01",
    end_date: str = "2026-03-15",
    lat: float = -31.25,
    lon: float = -61.48,
    timeout: int = 15,
) -> pd.DataFrame:
    """Descarga clima horario histórico para Rafaela con fallback sintético seguro."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": HOURLY_FIELDS,
        "timezone": "auto",
    }
    try:
        response = requests.get(ARCHIVE_URL, params=params, timeout=timeout)
        response.raise_for_status()
        df = parse_open_meteo_archive_payload(response.json())
        if len(df) < 2000 or df["stress_level"].nunique() < 2:
            return generate_synthetic_weather_df(n_hours=2400)
        return df
    except (requests.RequestException, ValueError, KeyError):
        return generate_synthetic_weather_df(n_hours=2400)


def build_and_save_dataset(
    output_path: Path = DEFAULT_OUTPUT_PATH,
    start_date: str = "2025-12-01",
    end_date: str = "2026-03-15",
) -> Path:
    """Construye el dataset histórico/fallback y lo guarda en CSV sin índice."""
    df = fetch_rafaela_historical_weather(start_date=start_date, end_date=end_date)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    return output_path


if __name__ == "__main__":
    saved_path = build_and_save_dataset()
    dataset = pd.read_csv(saved_path)
    dist = dataset["stress_level"].value_counts().sort_index().to_dict()
    print(f"Dataset guardado en {saved_path} | stress_level={dist}")
