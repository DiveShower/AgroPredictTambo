"""DTO para el informe auditado de sustentabilidad ESG."""

from dataclasses import dataclass
from datetime import datetime

from src.domain.entities.sector import Sector
from src.domain.value_objects.carbon_footprint import CarbonFootprint
from src.domain.value_objects.economic_impact import EconomicImpact
from src.domain.value_objects.report_audit_context import ReportAuditContext
from src.domain.value_objects.resource_savings import ResourceSavings


@dataclass(frozen=True)
class SustainabilityReportDTO:
    """Metadatos y resultados del reporte de sustentabilidad Nestlé Conecta."""

    farm_name: str
    generated_at: datetime
    savings: ResourceSavings
    carbon_footprint: CarbonFootprint
    economic_impact: EconomicImpact
    pdf_file_path: str | None = None
    sectors: tuple[Sector, ...] = ()
    audit_context: ReportAuditContext | None = None
