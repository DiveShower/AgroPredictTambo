"""Resolución de adaptador de clima y caché según entorno."""

import os

from src.domain.ports.weather_provider_port import IWeatherProvider
from src.infrastructure.persistence.sqlite_weather_cache_adapter import (
    SqliteWeatherCacheAdapter,
)
from src.infrastructure.weather_api.mock_weather_adapter import (
    MockWeatherAdapter,
)
from src.infrastructure.weather_api.open_meteo_adapter import OpenMeteoAdapter


def resolve_weather_and_cache(
    force_heatwave: bool = False,
) -> tuple[IWeatherProvider, SqliteWeatherCacheAdapter]:
    """Inicializa el proveedor de clima y la caché SQLite de contingencia."""
    mock = force_heatwave or os.getenv("WEATHER_PROVIDER", "open_meteo") == "mock"
    hw = MockWeatherAdapter("heatwave")
    weather: IWeatherProvider = hw if mock else OpenMeteoAdapter()
    cache = SqliteWeatherCacheAdapter()
    if not cache.is_cache_valid():
        cache.save_forecast(hw.get_hourly_forecast(-31.25, -61.48))
    return weather, cache
