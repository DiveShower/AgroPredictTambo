"""Entidad Farm que agrupa los sectores y coordenadas del establecimiento."""

from dataclasses import dataclass, field

from src.domain.entities.sector import Sector
from src.domain.exceptions.sector_not_found_exception import SectorNotFoundException


@dataclass
class Farm:
    """Representa el tambo completo con sus sectores y parámetros geográficos."""

    name: str
    latitude: float
    longitude: float
    sectors: list[Sector] = field(default_factory=list)
    milk_price_ars_per_liter: float = 430.0

    def get_sector(self, sector_id: str) -> Sector:
        """Busca un sector por ID o lanza SectorNotFoundException si no existe."""
        for sector in self.sectors:
            if sector.sector_id == sector_id:
                return sector
        raise SectorNotFoundException(
            f"No existe ningún sector con identificador '{sector_id}' en {self.name}."
        )

    def total_occupied_cows(self) -> int:
        """Suma la capacidad de vacas de los sectores actualmente ocupados."""
        return sum(
            sector.cow_capacity for sector in self.sectors if sector.current_occupancy
        )
