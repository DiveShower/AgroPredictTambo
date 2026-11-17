"""Adaptador de persistencia SQLite para resiliencia climática offline rural."""

from datetime import datetime, timedelta
from pathlib import Path
import sqlite3

from src.domain.ports.weather_cache_port import IWeatherCache
from src.domain.value_objects.weather_conditions import WeatherConditions
from src.infrastructure.persistence.cache_schema import (
    CLEAR_FORECAST_SQL,
    CREATE_WEATHER_CACHE_TABLE,
    INSERT_FORECAST_SQL,
    SELECT_FORECAST_SQL,
    SELECT_LATEST_SAVED_AT_SQL,
)


class SqliteWeatherCacheAdapter(IWeatherCache):
    """Almacena y recupera el pronóstico horario en base local SQLite o :memory:."""

    def __init__(self, db_path: str | Path = "data/cache/weather_cache.sqlite") -> None:
        self._db_path = str(db_path)
        if self._db_path != ":memory:":
            Path(self._db_path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self._db_path, check_same_thread=False)
        self._conn.execute(CREATE_WEATHER_CACHE_TABLE)
        self._conn.commit()

    def save_forecast(self, conditions_list: list[WeatherConditions]) -> None:
        """Reemplaza el pronóstico almacenado con la nueva ventana horaria."""
        now_iso = datetime.now().isoformat()
        rows = [
            (c.timestamp.isoformat(), c.temperature_c, c.relative_humidity, c.wind_speed_kmh, c.solar_radiation_wm2, now_iso)
            for c in conditions_list
        ]
        with self._conn:
            self._conn.execute(CLEAR_FORECAST_SQL)
            self._conn.executemany(INSERT_FORECAST_SQL, rows)

    def get_cached_forecast(self) -> list[WeatherConditions]:
        """Recupera las observaciones horarias persistidas en SQLite."""
        cur = self._conn.execute(SELECT_FORECAST_SQL)
        return [
            WeatherConditions(float(t), float(rh), float(w), datetime.fromisoformat(str(ts)), float(rad))
            for ts, t, rh, w, rad in cur.fetchall()
        ]

    def is_cache_valid(self, max_age_hours: int = 6) -> bool:
        """Verifica que existan datos y que no superen la antigüedad máxima."""
        row = self._conn.execute(SELECT_LATEST_SAVED_AT_SQL).fetchone()
        if not row or not row[0]:
            return False
        saved_at = datetime.fromisoformat(str(row[0]))
        return (datetime.now() - saved_at) <= timedelta(hours=max_age_hours)
