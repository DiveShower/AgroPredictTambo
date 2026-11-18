"""Definiciones DDL y consultas SQL para la caché climática local SQLite."""

CREATE_WEATHER_CACHE_TABLE = """
CREATE TABLE IF NOT EXISTS weather_forecast_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    temperature_c REAL NOT NULL,
    relative_humidity REAL NOT NULL,
    wind_speed_kmh REAL NOT NULL,
    solar_radiation_wm2 REAL NOT NULL,
    saved_at TEXT NOT NULL
);
"""

CLEAR_FORECAST_SQL = "DELETE FROM weather_forecast_cache;"

INSERT_FORECAST_SQL = """
INSERT INTO weather_forecast_cache (
    timestamp, temperature_c, relative_humidity,
    wind_speed_kmh, solar_radiation_wm2, saved_at
) VALUES (?, ?, ?, ?, ?, ?);
"""

SELECT_FORECAST_SQL = """
SELECT timestamp, temperature_c, relative_humidity,
       wind_speed_kmh, solar_radiation_wm2
FROM weather_forecast_cache
ORDER BY id ASC;
"""

SELECT_LATEST_SAVED_AT_SQL = """
SELECT saved_at FROM weather_forecast_cache ORDER BY id DESC LIMIT 1;
"""

INIT_AUTO_VACUUM_SQL = "PRAGMA auto_vacuum = 2;"
INCREMENTAL_VACUUM_SQL = "PRAGMA incremental_vacuum;"
