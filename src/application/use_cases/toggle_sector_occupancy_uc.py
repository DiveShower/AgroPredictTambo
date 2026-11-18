"""Caso de uso para conmutar la presencia de animales en un sector del tambo."""

from src.domain.entities.sector import Sector
from src.domain.ports.sector_repository_port import ISectorRepository


class ToggleSectorOccupancyUseCase:
    """Actualiza dinámicamente el estado de ocupación de un sector."""

    def __init__(self, sector_repository: ISectorRepository) -> None:
        self._sector_repo = sector_repository

    def execute(self, sector_id: str, is_occupied: bool) -> Sector:
        """Modifica la ocupación del sector y devuelve la entidad actualizada."""
        return self._sector_repo.update_occupancy(sector_id, is_occupied)
