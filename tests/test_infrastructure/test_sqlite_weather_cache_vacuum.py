"""Pruebas de persistencia SQLite en disco: auto_vacuum e incremental_vacuum."""

from datetime import datetime
from pathlib import Path

from src.domain.value_objects.weather_conditions import WeatherConditions
from src.infrastructure.persistence.sqlite_weather_cache_adapter import (
    SqliteWeatherCacheAdapter,
)


def _build_forecast(base_temp: float) -> list[WeatherConditions]:
    return [
        WeatherConditions(
            temperature_c=base_temp,
            relative_humidity=60.0,
            wind_speed_kmh=11.0,
            timestamp=datetime(2026, 2, 10, 12, 0),
            solar_radiation_wm2=700.0,
        ),
        WeatherConditions(
            temperature_c=base_temp + 2.0,
            relative_humidity=55.0,
            wind_speed_kmh=13.0,
            timestamp=datetime(2026, 2, 10, 13, 0),
            solar_radiation_wm2=820.0,
        ),
    ]


def test_sqlite_cache_auto_vacuum_on_disk(tmp_path: Path) -> None:
    db_file = tmp_path / "cache.sqlite"
    adapter = SqliteWeatherCacheAdapter(db_path=db_file)

    assert adapter._conn.execute("PRAGMA auto_vacuum;").fetchone()[0] == 2

    adapter.save_forecast(_build_forecast(28.0))
    adapter.save_forecast(_build_forecast(31.5))

    assert db_file.exists()
    assert adapter.is_cache_valid(max_age_hours=6) is True
    recovered = adapter.get_cached_forecast()
    assert len(recovered) == 2
    assert recovered[0].temperature_c == 31.5
    assert recovered[1].temperature_c == 33.5
    adapter._conn.close()


def test_sqlite_cache_retention_across_reopen_on_disk(tmp_path: Path) -> None:
    db_file = tmp_path / "cache.sqlite"
    writer = SqliteWeatherCacheAdapter(db_path=db_file)
    writer.save_forecast(_build_forecast(26.0))
    writer._conn.close()

    reader = SqliteWeatherCacheAdapter(db_path=db_file)
    assert reader._conn.execute("PRAGMA auto_vacuum;").fetchone()[0] == 2
    recovered = reader.get_cached_forecast()
    assert len(recovered) == 2
    assert recovered[0].temperature_c == 26.0
    reader._conn.close()
