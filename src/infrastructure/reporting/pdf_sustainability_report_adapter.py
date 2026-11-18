"""Adaptador generador de reportes PDF de sustentabilidad ESG con fpdf2."""

from datetime import datetime
from pathlib import Path

from fpdf import FPDF

from src.domain.ports.report_generator_port import IReportGenerator
from src.domain.value_objects.carbon_footprint import CarbonFootprint
from src.domain.value_objects.resource_savings import ResourceSavings
from src.infrastructure.reporting.pdf_asset_loader import (
    render_header_logo,
    setup_pdf_fonts,
)
from src.infrastructure.reporting.pdf_energy_section import (
    write_energy_and_carbon,
)
from src.infrastructure.reporting.pdf_water_section import write_header_and_water


class PdfSustainabilityReportAdapter(IReportGenerator):
    """Renderiza el informe formal auditado de eficiencia hídrica y energética."""

    def generate_sustainability_pdf(
        self, farm_name: str, savings: ResourceSavings, output_path: str
    ) -> str:
        """Genera el documento PDF en disco y retorna la ruta absoluta."""
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        carbon = CarbonFootprint.from_energy_savings(savings.energy_saved_kwh)
        pdf = FPDF()
        font = setup_pdf_fonts(pdf)
        pdf.add_page()
        render_header_logo(pdf)
        dt_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        write_header_and_water(pdf, font, farm_name, dt_str, savings)
        write_energy_and_carbon(pdf, font, savings, carbon)
        pdf.output(str(out))
        return str(out)
