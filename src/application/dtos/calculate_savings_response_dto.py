"""DTO de salida con métricas hídricas, energéticas, de carbono y leche."""

from dataclasses import dataclass

from src.domain.value_objects.carbon_footprint import CarbonFootprint
from src.domain.value_objects.economic_impact import EconomicImpact
from src.domain.value_objects.resource_savings import ResourceSavings


@dataclass(frozen=True)
class CalculateSavingsResponseDTO:
    """Balance integral de ahorro y sustentabilidad del establecimiento."""

    savings: ResourceSavings
    carbon_footprint: CarbonFootprint
    economic_impact: EconomicImpact
