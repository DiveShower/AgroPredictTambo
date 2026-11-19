"""Constructor unificado de documento PDF ESG A4 de página única."""

from collections.abc import Sequence
from datetime import datetime

from fpdf import FPDF

from src.domain.entities.sector import Sector
from src.domain.value_objects.carbon_footprint import CarbonFootprint
from src.domain.value_objects.economic_impact import EconomicImpact
from src.domain.value_objects.report_audit_context import ReportAuditContext
from src.domain.value_objects.resource_savings import ResourceSavings
from src.infrastructure.reporting import pdf_energy_section as eng
from src.infrastructure.reporting import pdf_header_section as hdr
from src.infrastructure.reporting import pdf_kpi_section as kpi
from src.infrastructure.reporting import pdf_sector_section as sec
from src.infrastructure.reporting import pdf_water_section as wtr
from src.infrastructure.reporting.pdf_asset_loader import render_header_logo


def render_sustainability_document(
    pdf: FPDF,
    font: str,
    farm_name: str,
    savings: ResourceSavings,
    carbon: CarbonFootprint,
    economic: EconomicImpact | None,
    sectors: Sequence[Sector],
    audit: ReportAuditContext,
) -> None:
    """Renderiza el reporte ESG completo en una única página A4 sin saltos."""
    pdf.set_auto_page_break(auto=False)
    pdf.add_page()
    render_header_logo(pdf)
    dt = audit.generated_at or datetime.now()
    date_str = dt.strftime("%Y-%m-%d %H:%M")
    cows = (
        economic.cow_count
        if economic
        else (sum(s.cow_capacity for s in sectors) or 100)
    )
    if sectors:
        spr = sum(s.sprinkler_count for s in sectors)
        fan = sum(s.fan_count for s in sectors)
        eq = f"{spr} asp / {fan} vent"
    else:
        eq = "25 asp / 14 vent"
    hdr.write_header_and_metadata(pdf, font, farm_name, date_str, audit, cows, eq)
    kpi.write_kpi_cards(pdf, font, savings, carbon, economic)
    wtr.write_comparison_table(pdf, font, savings, carbon)
    sec.write_sectors_table(pdf, font, sectors)
    eng.write_thermal_and_footer(pdf, font, audit, economic)
