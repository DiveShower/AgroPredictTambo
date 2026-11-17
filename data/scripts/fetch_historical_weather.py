"""Cliente HTTP de Open-Meteo Archive con fallback sintético para Rafaela."""

import sys
from pathlib import Path
from typing import Any

import pandas as pd
import requests

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from data.scripts.bioclimatic_enricher import DEFAULT_OUTPUT_PATH
from data.scripts.generate_synthetic_dataset import generate_synthetic_weather_df
from data.scripts.open_meteo_archive_parser import parse_open_meteo_archive_payload

ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
HOURLY = "temperature_2m,relative_humidity_2m,wind_speed_10m,shortwave_radiation"


def fetch_rafaela_historical_weather(
    start_date: str = "2025-12-01",
    end_date: str = "2026-03-15",
    lat: float = -31.25,
    lon: float = -61.48,
    timeout: int = 15,
) -> pd.DataFrame:
    """Descarga clima horario histórico para Rafaela con fallback sintético seguro."""
    q: dict[str, Any] = {"latitude": lat, "longitude": lon, "timezone": "auto"}
    q.update({"start_date": start_date, "end_date": end_date, "hourly": HOURLY})
    try:
        resp = requests.get(ARCHIVE_URL, params=q, timeout=timeout)
        resp.raise_for_status()
        df = parse_open_meteo_archive_payload(resp.json())
        if len(df) >= 2000 and df["stress_level"].nunique() >= 2:
            return df
    except (requests.RequestException, ValueError, KeyError):
        pass
    return generate_synthetic_weather_df(n_hours=2400)


def build_and_save_dataset(
    output_path: Path = DEFAULT_OUTPUT_PATH,
    start_date: str = "2025-12-01",
    end_date: str = "2026-03-15",
) -> Path:
    """Construye el dataset histórico/fallback y lo guarda en CSV sin índice."""
    df = fetch_rafaela_historical_weather(start_date, end_date)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    return output_path


if __name__ == "__main__":
    saved = build_and_save_dataset()
    print(f"Dataset guardado en {saved} | filas={len(pd.read_csv(saved))}")
