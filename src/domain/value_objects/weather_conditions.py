"""Value Object inmutable que representa condiciones meteorológicas validadas."""

from dataclasses import dataclass
from datetime import datetime
import math

from src.domain.exceptions.invalid_weather_exception import InvalidWeatherException


@dataclass(frozen=True)
class WeatherConditions:
    """Medición o pronóstico horario de variables meteorológicas del tambo."""

    temperature_c: float
    relative_humidity: float
    wind_speed_kmh: float
    timestamp: datetime
    solar_radiation_wm2: float = 0.0

    def __post_init__(self) -> None:
        if not (-15.0 <= self.temperature_c <= 55.0):
            raise InvalidWeatherException(
                f"Temperatura fuera de rango físico [-15, 55] °C: {self.temperature_c}"
            )
        if not (0.0 <= self.relative_humidity <= 100.0):
            raise InvalidWeatherException(
                f"Humedad relativa fuera de rango [0, 100] %: {self.relative_humidity}"
            )
        if self.wind_speed_kmh < 0.0:
            raise InvalidWeatherException(
                f"La velocidad del viento no puede ser negativa: {self.wind_speed_kmh}"
            )
        if self.solar_radiation_wm2 < 0.0:
            raise InvalidWeatherException(
                f"La radiación solar no puede ser negativa: {self.solar_radiation_wm2}"
            )

    @property
    def wet_bulb_depression(self) -> float:
        """Calcula la depresión del bulbo húmedo (T_seca - T_húmeda) mediante Stull (2011)."""
        t = self.temperature_c
        rh = self.relative_humidity
        t_wet = (
            t * math.atan(0.151977 * math.sqrt(rh + 8.313659))
            + math.atan(t + rh)
            - math.atan(rh - 1.676331)
            + 0.00391838 * (rh**1.5) * math.atan(0.023101 * rh)
            - 4.686035
        )
        return max(0.0, round(t - t_wet, 2))
