"""DTO de entrada para la evaluación predictiva de estrés térmico."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class PredictStressRequestDTO:
    """Parámetros de consulta climática y horizonte de predicción."""

    latitude: float = -31.25
    longitude: float = -61.48
    target_sector_id: Optional[str] = None
    forecast_lead_hours: int = 1
