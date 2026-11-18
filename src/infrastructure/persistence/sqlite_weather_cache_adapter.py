"""Adaptador de persistencia SQLite para resiliencia climática offline rural."""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

from src.domain.ports.weather_cache_port import IWeatherCache
from src.domain.value_objects.weather_conditions import WeatherConditions
from src.infrastructure.persistence import cache_schema as cs
from src.infrastructure.persistence.cache_schema import (
    INCREMENTAL_VACUUM_SQL,
    INIT_AUTO_VACUUM_SQL,
)


class SqliteWeatherCacheAdapter(IWeatherCache):
    """Almacena y recupera el pronóstico horario en base local SQLite o :memory:."""

    def __init__(self, db_path: str | Path = "data/cache/weather_cache.sqlite") -> None:
        self._db_path = str(db_path)
        if self._db_path != ":memory:":
            Path(self._db_path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self._db_path, check_same_thread=False)
        self._conn.execute(INIT_AUTO_VACUUM_SQL)
        self._conn.execute(cs.CREATE_WEATHER_CACHE_TABLE)
        self._conn.commit()

    def save_forecast(self, conditions_list: list[WeatherConditions]) -> None:
        """Reemplaza el pronóstico almacenado con la nueva ventana horaria."""
        now = datetime.now().isoformat()
        rows = [
            (c.timestamp.isoformat(), c.temperature_c, c.relative_humidity)
            + (c.wind_speed_kmh, c.solar_radiation_wm2, now)
            for c in conditions_list
        ]
        with self._conn:
            self._conn.execute(cs.CLEAR_FORECAST_SQL)
            self._conn.executemany(cs.INSERT_FORECAST_SQL, rows)
        if self._db_path != ":memory:":
            self._conn.execute(INCREMENTAL_VACUUM_SQL)

    def get_cached_forecast(self) -> list[WeatherConditions]:
        """Recupera las observaciones horarias persistidas en SQLite."""
        parse = datetime.fromisoformat
        rows = self._conn.execute(cs.SELECT_FORECAST_SQL).fetchall()
        return [
            WeatherConditions(float(t), float(rh), float(w), parse(str(ts)), float(rad))
            for ts, t, rh, w, rad in rows
        ]

    def is_cache_valid(self, max_age_hours: int = 6) -> bool:
        """Verifica que existan datos y que no superen la antigüedad máxima."""
        row = self._conn.execute(cs.SELECT_LATEST_SAVED_AT_SQL).fetchone()
        if not row or not row[0]:
            return False
        saved_at = datetime.fromisoformat(str(row[0]))
        return (datetime.now() - saved_at) <= timedelta(hours=max_age_hours)
