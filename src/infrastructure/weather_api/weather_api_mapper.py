"""Mapeador de payloads JSON de Open-Meteo a objetos WeatherConditions."""

from datetime import datetime
from typing import Any

from src.domain.value_objects.weather_conditions import WeatherConditions


def parse_current_weather(payload: dict[str, Any]) -> WeatherConditions:
    """Convierte el bloque 'current' de Open-Meteo en WeatherConditions."""
    curr = payload.get("current", {})
    raw_time = str(curr.get("time", datetime.now().isoformat()))
    ts = datetime.fromisoformat(raw_time)
    return WeatherConditions(
        temperature_c=float(curr.get("temperature_2m", 20.0)),
        relative_humidity=float(curr.get("relative_humidity_2m", 50.0)),
        wind_speed_kmh=float(curr.get("wind_speed_10m", 10.0)),
        timestamp=ts,
        solar_radiation_wm2=float(curr.get("shortwave_radiation", 0.0)),
    )


def parse_hourly_forecast(
    payload: dict[str, Any], hours: int = 24
) -> list[WeatherConditions]:
    """Convierte el bloque 'hourly' de Open-Meteo en lista de WeatherConditions."""
    hourly = payload.get("hourly", {})
    times = hourly.get("time", [])
    temps = hourly.get("temperature_2m", [])
    humids = hourly.get("relative_humidity_2m", [])
    winds = hourly.get("wind_speed_10m", [])
    rads = hourly.get("shortwave_radiation", [0.0] * len(times))

    limit = min(max(1, hours), len(times))
    results: list[WeatherConditions] = []
    for idx in range(limit):
        results.append(
            WeatherConditions(
                temperature_c=float(temps[idx]),
                relative_humidity=float(humids[idx]),
                wind_speed_kmh=float(winds[idx]),
                timestamp=datetime.fromisoformat(str(times[idx])),
                solar_radiation_wm2=float(rads[idx]) if idx < len(rads) else 0.0,
            )
        )
    return results
