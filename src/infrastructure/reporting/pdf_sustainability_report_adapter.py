"""Adaptador generador de reportes PDF de sustentabilidad ESG con fpdf2."""

from datetime import datetime
from pathlib import Path

from fpdf import FPDF

from src.domain.ports.report_generator_port import IReportGenerator
from src.domain.value_objects.carbon_footprint import CarbonFootprint
from src.domain.value_objects.resource_savings import ResourceSavings


class PdfSustainabilityReportAdapter(IReportGenerator):
    """Renderiza el informe formal auditado de eficiencia hídrica y energética."""

    def generate_sustainability_pdf(
        self,
        farm_name: str,
        savings: ResourceSavings,
        output_path: str,
    ) -> str:
        """Genera el documento PDF en disco y retorna la ruta absoluta."""
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        carbon = CarbonFootprint.from_energy_savings(savings.energy_saved_kwh)

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, "REPORTE DE SUSTENTABILIDAD ESG - NESTLE CONECTA", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 8, f"Establecimiento: {farm_name}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 8, f"Fecha de auditoria: {datetime.now().strftime('%Y-%m-%d %H:%M')}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)

        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 9, "1. Balance de Eficiencia Hidrica (Chen et al., 2016)", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 7, f"- Consumo Base (8h fijo 1.3 L/min): {savings.baseline_water_liters} L", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 7, f"- Consumo Predictivo (Micro-ciclos): {savings.predictive_water_liters} L", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 7, f"- Ahorro Software: {savings.water_saved_liters} L ({savings.water_saved_pct}%)", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 7, f"- Ahorro Combinado vs 4.9 L/min: {savings.combined_water_saved_pct}%", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)

        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 9, "2. Ahorro Energetico y Huella de Carbono (CAMMESA)", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 7, f"- Energia Ahorrada: {savings.energy_saved_kwh} kWh ({savings.energy_saved_pct}%)", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 7, f"- Emisiones Evitadas: {carbon.co2_avoided_kg} kg CO2e (Factor {carbon.emission_factor_kg_per_kwh} kg/kWh)", new_x="LMARGIN", new_y="NEXT")

        pdf.output(str(out))
        return str(out)
