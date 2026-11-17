"""Contrato abstracto para inferencia predictiva de nivel de estrés térmico."""

from typing import Protocol, Sequence

from src.domain.value_objects.weather_conditions import WeatherConditions


class IModelPredictor(Protocol):
    """Puerto de predicción de estrés térmico animal (0=Confort, 1=Alerta, 2=Peligro)."""

    def predict_stress_level(
        self,
        conditions: WeatherConditions,
        recent_history: Sequence[WeatherConditions] = (),
        nocturnal_debt_hours: int = 0,
    ) -> int:
        """Predice el nivel de estrés combinando condiciones actuales e inercia previa."""
        ...
