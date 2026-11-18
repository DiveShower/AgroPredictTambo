"""Repositorio de sectores en memoria thread-safe para sincronización SCADA-Bot."""

import threading

from src.domain.entities.sector import Sector
from src.domain.exceptions.sector_not_found_exception import (
    SectorNotFoundException,
)
from src.domain.fixtures.default_farm import get_default_sectors
from src.domain.ports.sector_repository_port import ISectorRepository


class InMemorySectorRepository(ISectorRepository):
    """Almacena los sectores del tambo con bloqueo reentrante para multi-hilo."""

    def __init__(self, initial_sectors: list[Sector] | None = None) -> None:
        self._lock = threading.RLock()
        sectors = (
            initial_sectors if initial_sectors is not None else get_default_sectors()
        )
        self._sectors: dict[str, Sector] = {sec.sector_id: sec for sec in sectors}

    def get_all_sectors(self) -> list[Sector]:
        """Retorna la lista ordenada de todos los sectores registrados."""
        with self._lock:
            return list(self._sectors.values())

    def get_by_id(self, sector_id: str) -> Sector:
        """Busca un sector por ID o lanza SectorNotFoundException."""
        with self._lock:
            sector = self._sectors.get(sector_id)
            if sector is None:
                raise SectorNotFoundException(f"Sector inexistente: '{sector_id}'")
            return sector

    def update_occupancy(self, sector_id: str, is_occupied: bool) -> Sector:
        """Actualiza atómicamente la presencia de animales en el sector."""
        with self._lock:
            sector = self.get_by_id(sector_id)
            sector.set_occupancy(is_occupied)
            return sector
