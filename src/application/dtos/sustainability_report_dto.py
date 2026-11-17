"""DTO para el informe auditado de sustentabilidad ESG."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from src.domain.value_objects.carbon_footprint import CarbonFootprint
from src.domain.value_objects.economic_impact import EconomicImpact
from src.domain.value_objects.resource_savings import ResourceSavings


@dataclass(frozen=True)
class SustainabilityReportDTO:
    """Metadatos y resultados del reporte de sustentabilidad Nestlé Conecta."""

    farm_name: str
    generated_at: datetime
    savings: ResourceSavings
    carbon_footprint: CarbonFootprint
    economic_impact: EconomicImpact
    pdf_file_path: Optional[str] = None
