"""Contrato abstracto para persistencia y consulta de sectores del tambo."""

from typing import Protocol

from src.domain.entities.sector import Sector


class ISectorRepository(Protocol):
    """Puerto de repositorio para administrar los sectores del establecimiento."""

    def get_all_sectors(self) -> list[Sector]:
        """Retorna todos los sectores registrados del tambo."""
        ...

    def get_by_id(self, sector_id: str) -> Sector:
        """Busca y retorna un sector por su identificador único."""
        ...

    def update_occupancy(self, sector_id: str, is_occupied: bool) -> None:
        """Actualiza el estado de ocupación animal de un sector."""
        ...
