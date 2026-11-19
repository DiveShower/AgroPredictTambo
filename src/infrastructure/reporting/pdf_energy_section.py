"""Renderizador de recuperación nocturna, trazabilidad SIGLeA y pie científico."""

from fpdf import FPDF

from src.domain.value_objects.economic_impact import EconomicImpact
from src.domain.value_objects.report_audit_context import ReportAuditContext
from src.infrastructure.reporting import pdf_layout as ly
from src.infrastructure.reporting import pdf_theme as th


def write_thermal_and_footer(
    pdf: FPDF, font: str, audit: ReportAuditContext, eco: EconomicImpact | None
) -> None:
    """Dibuja recuperación nocturna, trazabilidad SIGLeA/Watchdog y pie científico."""
    mx, epw, tm, d = th.MARGIN_X, th.EPW, th.TEXT_MUTED, audit.nocturnal_debt_hours
    title = "3. RECUPERACIÓN NOCTURNA Y TRAZABILIDAD (OLIVEIRA ET AL., 2025)"
    ly.draw_section_title(pdf, font, 161.5, title)
    pen, cool = min(3.0, d * 0.5), max(0, 6 - d)
    fl, ac = (th.TINT_AMBER, th.WARN_AMBER) if d > 0 else (th.TINT_BLUE, th.AGRO_GREEN)
    ly.draw_box(pdf, mx, 167.0, epw, 22.0, fill=fl, accent=ac)
    ly.draw_box(pdf, mx, 193.0, epw, 18.0, fill=th.WHITE, accent=th.ACCENT_BLUE)
    thi = f" | ITH: {audit.current_thi:.2f}" if audit.current_thi is not None else ""
    s = "SIGLeA: sin proyección económica en esta corrida"
    if e := eco:
        a, g = e.hours_alert_mitigated, e.hours_danger_mitigated
        m, r = e.milk_protected_liters, e.economic_return_ars
        s = f"SIGLeA: {a}h Alerta (0.15) + {g}h Peligro (0.35) -> +{m:.1f} L (${r:,.0f} ARS)"
    s1 = "Seguridad: Watchdog máx. 60 s en válvulas | Modo Zero-Waste"
    for x, y, w, txt in (
        (15, 170.5, 108, f"Ventana 21-06h (ITH<65): {cool}/6 h frescas | Deuda: {d} h"),
        (15, 177.5, 108, f"Penalización umbral: -{pen:.1f} pts ITH{thi}"),
        (126, 170.5, 68, f"Efectivos Hormigón: {72.0 - pen:.1f} / {78.0 - pen:.1f}"),
        (126, 177.5, 68, f"Efectivos Sombras: {70.0 - pen:.1f} / {76.0 - pen:.1f}"),
        (15, 196.5, 180, s),
        (15, 203.0, 180, f"{s1} | Fallback offline SQLite"),
    ):
        ly.draw_text(pdf, font, x, y, w, 5.0, txt, size=7.5)
    pdf.set_draw_color(*th.BORDER_SOFT)
    pdf.set_line_width(0.3)
    pdf.line(mx, 266.0, mx + epw, 266.0)
    f1 = "Fuentes: Chen et al. (2016) J. Dairy Sci. | Oliveira et al. (2025) Animals"
    src = f"{f1} | CAMMESA 0.35 | SIGLeA"
    foot = "AgroPredictTambo · Nestlé Conecta · Reporte Ejecutivo Auditado"
    apb, bm = pdf.auto_page_break, pdf.b_margin
    pdf.set_auto_page_break(False)
    ly.draw_text(pdf, font, mx, 268.5, epw, 4.0, src, 7.0, tm)
    ly.draw_text(pdf, font, mx, 276.0, epw, 4.0, foot, 7.0, tm)
    ly.draw_text(pdf, font, mx, 276.0, epw, 4.0, "Página 1 de 1", 7.0, tm, "", "R")
    pdf.set_auto_page_break(apb, bm)
