"""Contrato abstracto para proveedores de condiciones meteorológicas y pronóstico."""

from typing import List, Protocol

from src.domain.value_objects.weather_conditions import WeatherConditions


class IWeatherProvider(Protocol):
    """Puerto de acceso a datos meteorológicos actuales y horarios."""

    def get_current_weather(self, lat: float, lon: float) -> WeatherConditions:
        """Obtiene las condiciones meteorológicas actuales para las coordenadas dadas."""
        ...

    def get_hourly_forecast(
        self,
        lat: float,
        lon: float,
        hours: int = 24,
    ) -> List[WeatherConditions]:
        """Obtiene el pronóstico horario para las próximas horas solicitadas."""
        ...
