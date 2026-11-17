"""Tests TDD para la ingesta histórica climática de Open-Meteo (Ciclo 2)."""

from pathlib import Path

import pandas as pd
import requests
from pytest_mock import MockerFixture as MF

from data.scripts import fetch_historical_weather as fhw
from data.scripts.generate_synthetic_dataset import EXPECTED_COLUMNS


def _build_mock_open_meteo_payload(n_hours: int = 24) -> dict:
    """Construye un payload JSON estilo Open-Meteo Archive con noche fresca y día cálido."""
    ts = pd.date_range("2026-01-15 00:00:00", periods=n_hours, freq="1h")
    is_day = (ts.hour >= 8) & (ts.hour <= 19)
    return {
        "hourly": {
            "time": [t.strftime("%Y-%m-%dT%H:%M") for t in ts],
            "temperature_2m": [32.0 if d else 18.0 for d in is_day],
            "relative_humidity_2m": [60.0 if d else 75.0 for d in is_day],
            "wind_speed_10m": [10.0 if d else 6.0 for d in is_day],
            "shortwave_radiation": [750.0 if d else 0.0 for d in is_day],
        }
    }


def test_parse_open_meteo_archive_payload_enriches_columns() -> None:
    df = fhw.parse_open_meteo_archive_payload(_build_mock_open_meteo_payload(24))
    assert len(df) == 24
    assert list(df.columns) == EXPECTED_COLUMNS
    assert df.isna().sum().sum() == 0
    assert min(df["stress_level"]) == 0
    assert max(df["stress_level"]) >= 1


def test_fetch_falls_back_to_synthetic_on_network_error(mocker: MF) -> None:
    mocker.patch("requests.get", side_effect=requests.RequestException("offline"))
    df = fhw.fetch_rafaela_historical_weather()
    assert len(df) >= 2000
    assert list(df.columns) == EXPECTED_COLUMNS
    assert df.isna().sum().sum() == 0


def test_build_and_save_dataset_writes_csv(tmp_path: Path, mocker: MF) -> None:
    mock_resp = mocker.MagicMock(status_code=200)
    mock_resp.raise_for_status.return_value = None
    mock_resp.json.return_value = _build_mock_open_meteo_payload(n_hours=2000)
    mocker.patch("requests.get", return_value=mock_resp)
    out_file = tmp_path / "weather.csv"
    assert fhw.build_and_save_dataset(out_file) == out_file
    assert out_file.exists()
    loaded = pd.read_csv(out_file)
    assert len(loaded) >= 24
    assert list(loaded.columns) == EXPECTED_COLUMNS
    assert loaded.isna().sum().sum() == 0
