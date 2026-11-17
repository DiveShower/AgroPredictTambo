"""DTO de salida con proyecciones térmicas, órdenes y alertas."""

from collections.abc import Sequence
from dataclasses import dataclass

from src.domain.entities.cooling_order import CoolingOrder
from src.domain.entities.heat_stress_alert import HeatStressAlert
from src.domain.value_objects.weather_conditions import WeatherConditions


@dataclass(frozen=True)
class PredictStressResponseDTO:
    """Resultado consolidado de la evaluación bioclimática del tambo."""

    current_conditions: WeatherConditions
    predicted_conditions: WeatherConditions
    current_thi: float
    predicted_thi: float
    nocturnal_debt_hours: int
    cooling_orders: Sequence[CoolingOrder]
    alerts: Sequence[HeatStressAlert]
