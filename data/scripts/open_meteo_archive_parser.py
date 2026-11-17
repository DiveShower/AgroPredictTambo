"""Parser de respuestas JSON de Open-Meteo Archive hacia series enriquecidas."""

from typing import Any

import pandas as pd

from data.scripts.bioclimatic_enricher import enrich_bioclimatic_features

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
