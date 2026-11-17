"""Entidad CoolingOrder que representa una orden de enfriamiento sectorizada."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class CoolingOrder:
    """Orden de activación de micro-ciclo evaporativo para un sector del tambo."""

    sector_id: str
    stress_level: int
    water_mist_seconds: int
    fan_ventilation_seconds: int
    target_time: datetime
    justification: str

    @property
    def is_active(self) -> bool:
        """Indica si la orden activa algún equipo (aspersión o ventilación)."""
        return self.water_mist_seconds > 0 or self.fan_ventilation_seconds > 0
