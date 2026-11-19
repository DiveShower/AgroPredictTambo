"""Renderizador de tabla comparativa operativa ESG para PDF."""

from fpdf import FPDF

from src.domain.value_objects.carbon_footprint import CarbonFootprint
from src.domain.value_objects.resource_savings import ResourceSavings
from src.infrastructure.reporting import pdf_layout as ly
from src.infrastructure.reporting import pdf_theme as th
from src.infrastructure.reporting.pdf_table import Align, TableCol, draw_table_row

_W: tuple[float, ...] = (54.0, 42.0, 42.0, 48.0)
_A: tuple[Align, ...] = ("L", "C", "C", "C")
_HDR = ("Métrica Operativa", "Trad. (4.9 L/m)", "Base (1.3 L/m)", "AgroPredictTambo")
_R0 = ("Régimen / Boquilla", "8h · 4.9 L/m", "8h · 1.3 L/m", "IA · 1.3 L/m (40s/270s)")


def _cols(
    texts: tuple[str, ...], bg: th.Rgb, fg: th.Rgb, last: tuple[th.Rgb, th.Rgb]
) -> list[TableCol]:
    return [
        (w, t, a, last[0] if j == 3 else bg, last[1] if j == 3 else fg)
        for j, (w, t, a) in enumerate(zip(_W, texts, _A, strict=True))
    ]


def write_comparison_table(
    pdf: FPDF, font: str, s: ResourceSavings, c: CarbonFootprint
) -> None:
    """Dibuja la comparativa operativa Tradicional vs AgroPredictTambo."""
    title = "1. COMPARATIVA OPERATIVA: TRADICIONAL VS AGROPREDICTTAMBO"
    ly.draw_section_title(pdf, font, 82.5, title)
    hdr = _cols(_HDR, th.PRIMARY_BLUE, th.WHITE, (th.PRIMARY_BLUE, th.WHITE))
    draw_table_row(pdf, font, 88.0, 6.5, hdr, size=7.5, style="B")
    bw, pw = s.baseline_water_liters, s.predictive_water_liters
    lw, f = s.legacy_nozzle_water_liters, c.emission_factor_kg_per_kwh
    be, pe = s.baseline_energy_kwh, s.predictive_energy_kwh
    w3 = f"{pw:,.1f} L (-{s.combined_water_saved_pct:.1f}%)"
    e3 = f"{pe:.2f} kWh (-{s.energy_saved_pct:.1f}%)"
    c3 = f"{pe * f:.2f} kg (-{c.co2_avoided_kg:.2f} kg)"
    rows = (
        _R0,
        ("Agua diaria (L)", f"{lw:,.1f} L", f"{bw:,.1f} L", w3),
        ("Energía (kWh/día)", "N/D", f"{be:.2f} kWh", e3),
        ("Emisiones CAMMESA", "—", f"{be * f:.2f} kg", c3),
    )
    for i, row in enumerate(rows):
        bg = th.WHITE if i % 2 == 0 else th.ROW_ALT
        cols = _cols(row, bg, th.TEXT_DARK, (th.TINT_GREEN, th.AGRO_GREEN))
        draw_table_row(pdf, font, 94.5 + i * 6.0, 6.0, cols, size=7.5)


def write_header_and_water(
    pdf: FPDF, font: str, farm: str, date: str, s: ResourceSavings
) -> None:
    """Wrapper temporal hasta migrar el adaptador PDF en el paso B.9."""
    _ = (farm, date)
    carbon = CarbonFootprint.from_energy_savings(s.energy_saved_kwh)
    write_comparison_table(pdf, font, s, carbon)
