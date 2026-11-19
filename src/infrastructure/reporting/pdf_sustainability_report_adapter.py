"""Adaptador generador de reportes PDF de sustentabilidad ESG con fpdf2."""

from collections.abc import Sequence
from pathlib import Path

from fpdf import FPDF

from src.domain.entities.sector import Sector
from src.domain.ports.report_generator_port import IReportGenerator
from src.domain.value_objects.carbon_footprint import CarbonFootprint
from src.domain.value_objects.economic_impact import EconomicImpact
from src.domain.value_objects.report_audit_context import ReportAuditContext
from src.domain.value_objects.resource_savings import ResourceSavings
from src.infrastructure.reporting.pdf_asset_loader import setup_pdf_fonts
from src.infrastructure.reporting.pdf_document_builder import (
    render_sustainability_document,
)


class PdfSustainabilityReportAdapter(IReportGenerator):
    """Renderiza el informe formal auditado de eficiencia hídrica y energética."""

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
        """Genera el documento PDF en disco y retorna la ruta absoluta."""
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        carbon = carbon_footprint or CarbonFootprint.from_energy_savings(
            savings.energy_saved_kwh
        )
        audit = audit_context or ReportAuditContext()
        pdf = FPDF()
        font = setup_pdf_fonts(pdf)
        render_sustainability_document(
            pdf, font, farm_name, savings, carbon, economic_impact, sectors, audit
        )
        pdf.output(str(out))
        return str(out)
