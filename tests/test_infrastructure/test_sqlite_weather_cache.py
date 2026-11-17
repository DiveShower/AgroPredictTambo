"""Pruebas de integración para SqliteWeatherCacheAdapter en memoria (:memory:)."""

from datetime import datetime, timedelta

from src.domain.value_objects.weather_conditions import WeatherConditions
from src.infrastructure.persistence.sqlite_weather_cache_adapter import (
    SqliteWeatherCacheAdapter,
)


def _sample_forecast() -> list[WeatherConditions]:
    return [
        WeatherConditions(
            temperature_c=31.0,
            relative_humidity=62.0,
            wind_speed_kmh=10.0,
            timestamp=datetime(2026, 1, 15, 14, 0),
            solar_radiation_wm2=750.0,
        ),
        WeatherConditions(
            temperature_c=33.0,
            relative_humidity=58.0,
            wind_speed_kmh=9.0,
            timestamp=datetime(2026, 1, 15, 15, 0),
            solar_radiation_wm2=790.0,
        ),
    ]


def test_sqlite_cache_save_and_retrieve_in_memory() -> None:
    cache = SqliteWeatherCacheAdapter(db_path=":memory:")
    assert cache.is_cache_valid() is False

    items = _sample_forecast()
    cache.save_forecast(items)
    assert cache.is_cache_valid(max_age_hours=6) is True

    recovered = cache.get_cached_forecast()
    assert len(recovered) == 2
    assert recovered[0].temperature_c == 31.0
    assert recovered[1].solar_radiation_wm2 == 790.0


def test_sqlite_cache_ttl_expiration_in_memory() -> None:
    cache = SqliteWeatherCacheAdapter(db_path=":memory:")
    cache.save_forecast(_sample_forecast())

    expired_iso = (datetime.now() - timedelta(hours=8)).isoformat()
    cache._conn.execute(
        "UPDATE weather_forecast_cache SET saved_at = ?;", (expired_iso,)
    )
    cache._conn.commit()

    assert cache.is_cache_valid(max_age_hours=6) is False
