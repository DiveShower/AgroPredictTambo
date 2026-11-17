"""Adaptador primario de clima consumiendo la API REST pública de Open-Meteo."""

from typing import Any

import requests

from src.domain.ports.weather_provider_port import IWeatherProvider
from src.domain.value_objects.weather_conditions import WeatherConditions
from src.infrastructure.weather_api.weather_api_mapper import (
    parse_current_weather,
    parse_hourly_forecast,
)

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
WEATHER_VARS = (
    "temperature_2m,relative_humidity_2m,wind_speed_10m,shortwave_radiation"
)


class OpenMeteoAdapter(IWeatherProvider):
    """Implementa IWeatherProvider mediante peticiones HTTP síncronas a Open-Meteo."""

    def __init__(
        self,
        base_url: str = OPEN_METEO_URL,
        timeout_seconds: int = 8,
    ) -> None:
        self._base_url = base_url
        self._timeout = timeout_seconds

    def _fetch_payload(self, lat: float, lon: float) -> dict[str, Any]:
        params: dict[str, Any] = {
            "latitude": lat,
            "longitude": lon,
            "current": WEATHER_VARS,
            "hourly": WEATHER_VARS,
            "timezone": "America/Argentina/Cordoba",
        }
        response = requests.get(
            self._base_url, params=params, timeout=self._timeout
        )
        response.raise_for_status()
        return dict(response.json())

    def get_current_weather(self, lat: float, lon: float) -> WeatherConditions:
        """Obtiene las condiciones meteorológicas actuales para las coordenadas."""
        payload = self._fetch_payload(lat, lon)
        return parse_current_weather(payload)

    def get_hourly_forecast(
        self,
        lat: float,
        lon: float,
        hours: int = 24,
    ) -> list[WeatherConditions]:
        """Obtiene el pronóstico horario para las próximas horas solicitadas."""
        payload = self._fetch_payload(lat, lon)
        return parse_hourly_forecast(payload, hours=hours)
