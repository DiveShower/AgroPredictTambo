"""Contrato abstracto para generación de reportes de sustentabilidad ESG."""

from collections.abc import Sequence
from typing import Protocol

from src.domain.entities.sector import Sector
from src.domain.value_objects.carbon_footprint import CarbonFootprint
from src.domain.value_objects.economic_impact import EconomicImpact
from src.domain.value_objects.report_audit_context import ReportAuditContext
from src.domain.value_objects.resource_savings import ResourceSavings


class IReportGenerator(Protocol):
    """Puerto para exportar informes auditables de eficiencia hídrica y energética."""

    def generate_sustainability_pdf(
        self,
        farm_name: str,
        savings: ResourceSavings,
        output_path: str,
        carbon_footprint: CarbonFootprint | None = None,
        economic_impact: EconomicImpact | None = None,
        sectors: Sequence[Sector] = (),
        audit_context: ReportAuditContext | None = None,
    ) -> str:
        """Genera el reporte en PDF y devuelve la ruta del archivo generado."""
        ...
