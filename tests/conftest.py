"""Fixtures compartidas para la suite de pruebas unitarias."""

from datetime import datetime
import pytest

from src.domain.entities.farm import Farm
from src.domain.entities.sector import Sector
from src.domain.fixtures.default_farm import create_default_farm
from src.domain.value_objects.weather_conditions import WeatherConditions


@pytest.fixture
def sample_heatwave_weather() -> WeatherConditions:
    """Condición de ola de calor severa típica de verano en Rafaela."""
    return WeatherConditions(
        temperature_c=34.5,
        relative_humidity=68.0,
        wind_speed_kmh=6.0,
        timestamp=datetime(2026, 1, 15, 15, 0),
        solar_radiation_wm2=820.0,
    )


@pytest.fixture
def sample_temperate_weather() -> WeatherConditions:
    """Condición templada de confort térmico."""
    return WeatherConditions(
        temperature_c=20.0,
        relative_humidity=45.0,
        wind_speed_kmh=14.0,
        timestamp=datetime(2026, 1, 15, 6, 0),
        solar_radiation_wm2=120.0,
    )


@pytest.fixture
def holding_pen_sector() -> Sector:
    """Sector de corral de espera con piso de hormigón."""
    return Sector(
        sector_id="corral_espera",
        name="Corral de Espera Pre-ordeñe",
        cow_capacity=80,
        current_occupancy=True,
        thi_threshold_alert=72.0,
        thi_threshold_danger=78.0,
        allows_water_sprinkling=True,
        sprinkler_count=10,
        fan_count=4,
    )


@pytest.fixture
def default_farm() -> Farm:
    """Establecimiento piloto Tambo San José con los 3 sectores iniciales."""
    return create_default_farm()
