"""Renderizador de sección de energía y huella de carbono para PDF ESG."""

from fpdf import FPDF

from src.domain.value_objects.carbon_footprint import CarbonFootprint
from src.domain.value_objects.resource_savings import ResourceSavings


def _cell(pdf: FPDF, font: str, sz: int, txt: str, b: str = "") -> None:
    pdf.set_font(font, b, sz)
    pdf.cell(0, 6, txt, new_x="LMARGIN", new_y="NEXT")


def write_energy_and_carbon(
    pdf: FPDF, font: str, s: ResourceSavings, c: CarbonFootprint
) -> None:
    """Escribe el balance energético y reducción de emisiones CAMMESA."""
    pdf.ln(3)
    _cell(pdf, font, 12, "2. Ahorro Energético y Huella de Carbono (CAMMESA)", "B")
    _cell(
        pdf,
        font,
        10,
        f"- Energía Ahorrada: {s.energy_saved_kwh} kWh ({s.energy_saved_pct}%)",
    )
    fact = f"Factor {c.emission_factor_kg_per_kwh} kg/kWh"
    _cell(pdf, font, 10, f"- Emisiones Evitadas: {c.co2_avoided_kg} kg CO₂e ({fact})")
