"""DTO de entrada para el cálculo comparativo de ahorro de recursos."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CalculateSavingsRequestDTO:
    """Parámetros operativos para contrastar esquema tradicional vs predictivo."""

    baseline_operating_hours: float = 8.0
    predictive_active_hours: float = 3.5
    cow_count: int = 100
    milk_price_ars: float = 430.0
    sprinkler_count: int = 25
    fan_count: int = 14
    hours_level_1: float | None = None
    hours_level_2: float | None = None
