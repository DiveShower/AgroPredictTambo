"""Adaptador simulado de clima con los 3 perfiles determinísticos para demo."""

from datetime import datetime, timedelta

from src.domain.ports.weather_provider_port import IWeatherProvider
from src.domain.value_objects.weather_conditions import WeatherConditions

PROFILES: dict[str, tuple[float, float, float, float]] = {
    "heatwave": (34.5, 68.0, 6.0, 820.0),
    "nocturnal_debt": (28.5, 62.0, 8.0, 600.0),
    "temperate": (20.0, 45.0, 14.0, 200.0),
}


class MockWeatherAdapter(IWeatherProvider):
    """Genera escenarios climáticos determinísticos offline para jurado y tests."""

    def __init__(self, profile: str = "heatwave") -> None:
        self._profile = profile if profile in PROFILES else "heatwave"

    def set_profile(self, profile: str) -> None:
        """Cambia en caliente el escenario climático de demostración."""
        if profile in PROFILES:
            self._profile = profile

    def get_current_weather(self, lat: float, lon: float) -> WeatherConditions:
        """Devuelve la condición actual según el perfil seleccionado."""
        t, rh, wind, rad = PROFILES[self._profile]
        return WeatherConditions(
            temperature_c=t,
            relative_humidity=rh,
            wind_speed_kmh=wind,
            timestamp=datetime(2026, 1, 15, 14, 0),
            solar_radiation_wm2=rad,
        )

    def get_hourly_forecast(
        self, lat: float, lon: float, hours: int = 24
    ) -> list[WeatherConditions]:
        """Genera una curva horaria de 24h coherente con el perfil activo."""
        base_t, base_rh, wind, peak_rad = PROFILES[self._profile]
        start = datetime(2026, 1, 15, 0, 0)
        forecast: list[WeatherConditions] = []
        for h in range(max(1, hours)):
            ts = start + timedelta(hours=h)
            is_night = ts.hour >= 21 or ts.hour < 6
            if self._profile == "nocturnal_debt" and is_night:
                t, rh, rad = 26.0, 65.0, 0.0
            elif is_night:
                t, rh, rad = max(14.0, base_t - 9.0), min(90.0, base_rh + 10.0), 0.0
            else:
                t, rh, rad = base_t, base_rh, peak_rad
            forecast.append(WeatherConditions(t, rh, wind, ts, rad))
        return forecast
