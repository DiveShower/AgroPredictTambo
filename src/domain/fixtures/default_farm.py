"""Datos semilla de dominio para el establecimiento piloto Tambo San José."""

from src.domain.entities.farm import Farm
from src.domain.entities.sector import Sector


def get_default_sectors() -> list[Sector]:
    """Retorna los 3 sectores de referencia definidos para Rafaela, Santa Fe."""
    return [
        Sector(
            sector_id="corral_espera",
            name="Corral de Espera Pre-ordeñe",
            cow_capacity=80,
            current_occupancy=True,
            thi_threshold_alert=72.0,
            thi_threshold_danger=78.0,
            allows_water_sprinkling=True,
            sprinkler_count=10,
            fan_count=4,
        ),
        Sector(
            sector_id="comederos",
            name="Línea de Comederos y Pista de Alimentación",
            cow_capacity=120,
            current_occupancy=True,
            thi_threshold_alert=72.0,
            thi_threshold_danger=78.0,
            allows_water_sprinkling=True,
            sprinkler_count=15,
            fan_count=6,
        ),
        Sector(
            sector_id="sombras",
            name="Galpón Compost Barn / Sombras y Descanso",
            cow_capacity=100,
            current_occupancy=True,
            thi_threshold_alert=70.0,
            thi_threshold_danger=76.0,
            allows_water_sprinkling=False,
            sprinkler_count=0,
            fan_count=4,
        ),
    ]


def create_default_farm(
    name: str = "Tambo San José - Nestlé Conecta",
    latitude: float = -31.25,
    longitude: float = -61.48,
    milk_price_ars_per_liter: float = 430.0,
) -> Farm:
    """Construye la instancia inicial del tambo con sus 3 sectores configurados."""
    return Farm(
        name=name,
        latitude=latitude,
        longitude=longitude,
        sectors=get_default_sectors(),
        milk_price_ars_per_liter=milk_price_ars_per_liter,
    )
