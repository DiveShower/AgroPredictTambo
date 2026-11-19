"""Renderizador de tarjetas KPI ejecutivas de 30 segundos para PDF ESG."""

from fpdf import FPDF

from src.domain.value_objects.carbon_footprint import CarbonFootprint
from src.domain.value_objects.economic_impact import EconomicImpact
from src.domain.value_objects.resource_savings import ResourceSavings
from src.infrastructure.reporting import pdf_layout as ly
from src.infrastructure.reporting import pdf_theme as th

KpiCard = tuple[th.Rgb, th.Rgb, str, str, th.Rgb, str, str]


def write_kpi_cards(
    pdf: FPDF,
    font: str,
    s: ResourceSavings,
    c: CarbonFootprint,
    eco: EconomicImpact | None,
) -> None:
    """Dibuja el resumen ejecutivo de impacto en 3 tarjetas KPI alineadas."""
    title = "RESUMEN EJECUTIVO DE IMPACTO (LECTURA EN 30 SEGUNDOS)"
    ly.draw_section_title(pdf, font, 48.0, title)
    pb, ab, wh = th.PRIMARY_BLUE, th.ACCENT_BLUE, th.WHITE
    tm, td = th.TEXT_MUTED, th.TEXT_DARK
    bw, pw = s.baseline_water_liters, s.predictive_water_liters
    w_h = f"{s.water_saved_liters:,.0f} L (-{s.water_saved_pct:.1f}%)"
    w_s = f"Combinado 4.9 L/m: -{s.combined_water_saved_pct:.1f}%"
    w_m = f"1.3 L/m: {bw:,.0f} -> {pw:,.0f} L"
    e_h = f"{s.energy_saved_kwh:.1f} kWh (-{s.energy_saved_pct:.1f}%)"
    e_s = f"Huella: {c.co2_avoided_kg:.2f} kg CO2e"
    e_m = f"Factor CAMMESA: {c.emission_factor_kg_per_kwh:.2f} kg/kWh"
    if eco is not None:
        r_c = (th.AGRO_GREEN, th.TINT_GREEN, th.AGRO_GREEN)
        r_t = (
            f"+{eco.milk_protected_liters:.1f} L/día",
            f"Retorno: ${eco.economic_return_ars:,.0f} ARS/día",
            f"{eco.cow_count} vacas | ${eco.milk_price_ars:.0f} ARS/L",
        )
    else:
        r_c = (th.BORDER_SOFT, th.ROW_ALT, tm)
        r_t = ("No calculado", "Sin datos SIGLeA", "Modo sin datos de rodeo")
    cards: tuple[KpiCard, KpiCard, KpiCard] = (
        (pb, wh, "AHORRO HÍDRICO DIARIO", w_h, pb, w_s, w_m),
        (ab, wh, "ENERGÍA Y CO2e EVITADO", e_h, pb, e_s, e_m),
        (r_c[0], r_c[1], "RETORNO SIGLeA", r_t[0], r_c[2], r_t[1], r_t[2]),
    )
    for x, card in zip((12.0, 75.5, 139.0), cards, strict=True):
        accent, fill, label, hero, hero_color, sub, micro = card
        ly.draw_box(pdf, x, 53.5, 59.0, 24.0, fill=fill, accent=accent)
        tx = x + 3.0
        ly.draw_text(pdf, font, tx, 56.0, 53.0, 3.5, label, 6.5, tm, "B")
        ly.draw_text(pdf, font, tx, 60.0, 53.0, 6.0, hero, 10.0, hero_color, "B")
        ly.draw_text(pdf, font, tx, 67.0, 53.0, 4.0, sub, 7.2, td)
        ly.draw_text(pdf, font, tx, 71.5, 53.0, 4.0, micro, 6.5, tm)
