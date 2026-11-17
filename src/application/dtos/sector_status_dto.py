"""DTO con el estado operativo e higiénico-sanitario de un sector."""

from dataclasses import dataclass


@dataclass(frozen=True)
class SectorStatusDTO:
    """Representación desacoplada del estado de un sector para la UI."""

    sector_id: str
    name: str
    cow_capacity: int
    current_occupancy: bool
    allows_water_sprinkling: bool
    sprinkler_count: int
    fan_count: int
    current_stress_level: int
    cycle_description: str
    is_cooling_active: bool
