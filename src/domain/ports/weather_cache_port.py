"""Contrato abstracto para cache local de pronóstico meteorológico offline."""

from typing import Protocol

from src.domain.value_objects.weather_conditions import WeatherConditions


class IWeatherCache(Protocol):
    """Puerto de almacenamiento local para resiliencia ante cortes de red rural."""

    def save_forecast(self, conditions_list: list[WeatherConditions]) -> None:
        """Persiste localmente la lista de pronósticos horarios."""
        ...

    def get_cached_forecast(self) -> list[WeatherConditions]:
        """Recupera el último pronóstico horario almacenado en cache."""
        ...

    def is_cache_valid(self, max_age_hours: int = 6) -> bool:
        """Verifica si el cache local es más reciente que la antigüedad máxima."""
        ...
