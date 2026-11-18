"""Renderizador de encabezado y sección de balance hídrico para PDF ESG."""

from fpdf import FPDF

from src.domain.value_objects.resource_savings import ResourceSavings


def _cell(pdf: FPDF, font: str, sz: int, txt: str, b: str = "") -> None:
    pdf.set_font(font, b, sz)
    pdf.cell(0, 6, txt, new_x="LMARGIN", new_y="NEXT")


def write_header_and_water(
    pdf: FPDF, font: str, farm: str, date: str, s: ResourceSavings
) -> None:
    """Escribe el membrete formal y el balance de agua auditado."""
    _cell(pdf, font, 14, "REPORTE DE SUSTENTABILIDAD ESG — NESTLÉ CONECTA", "B")
    _cell(pdf, font, 10, f"Establecimiento: {farm}")
    _cell(pdf, font, 10, f"Fecha de auditoría: {date}")
    pdf.ln(3)
    _cell(pdf, font, 12, "1. Balance de Eficiencia Hídrica (Chen et al., 2016)", "B")
    _cell(
        pdf,
        font,
        10,
        f"- Consumo Base (8h fijo 1.3 L/min): {s.baseline_water_liters} L",
    )
    _cell(
        pdf,
        font,
        10,
        f"- Consumo Predictivo (Micro-ciclos): {s.predictive_water_liters} L",
    )
    _cell(
        pdf,
        font,
        10,
        f"- Ahorro Software: {s.water_saved_liters} L ({s.water_saved_pct}%)",
    )
    _cell(
        pdf,
        font,
        10,
        f"- Ahorro Combinado vs 4.9 L/min: {s.combined_water_saved_pct}%",
    )
