"""Entidad HeatStressAlert para notificaciones preventivas de estrés térmico."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class HeatStressAlert:
    """Alerta de estrés térmico proyectada o actual para un sector ocupado."""

    sector_id: str
    sector_name: str
    thi_value: float
    stress_level: int
    target_time: datetime
    recommended_action: str
    is_preventive: bool = True
