"""Helper para adquisición resiliente de clima y caché offline."""

from src.domain.ports.weather_cache_port import IWeatherCache
from src.domain.ports.weather_provider_port import IWeatherProvider
from src.domain.value_objects.weather_conditions import WeatherConditions


def fetch_weather_with_cache(
    weather: IWeatherProvider,
    cache: IWeatherCache | None,
    lat: float,
    lon: float,
) -> tuple[WeatherConditions, list[WeatherConditions]]:
    """Obtiene clima actual y pronóstico 24h, usando caché local como contingencia."""
    try:
        curr = weather.get_current_weather(lat, lon)
        fore = weather.get_hourly_forecast(lat, lon, hours=24)
        if cache:
            cache.save_forecast(fore)
        return curr, fore
    except Exception:
        if cache and cache.is_cache_valid():
            cached = cache.get_cached_forecast()
            return cached[0], cached
        raise
