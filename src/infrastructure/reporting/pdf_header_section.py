"""Renderizador del encabezado y banda de metadatos de auditoría para PDF ESG."""

from fpdf import FPDF

from src.domain.value_objects.report_audit_context import ReportAuditContext
from src.infrastructure.reporting import pdf_layout as ly
from src.infrastructure.reporting import pdf_theme as th
from src.infrastructure.reporting.pdf_table import FontStyle


def write_header_and_metadata(
    pdf: FPDF,
    font: str,
    farm_name: str,
    date_str: str,
    audit: ReportAuditContext,
    cow_count: int,
    equipment_label: str,
) -> None:
    """Dibuja el membrete superior sin solapamiento y la banda de metadatos ESG."""
    mx = th.MARGIN_X
    header_rows: tuple[tuple[float, float, str, float, th.Rgb, FontStyle], ...] = (
        (
            10.5,
            4.0,
            "INFORME AUDITADO DE SUSTENTABILIDAD ESG",
            7.5,
            th.ACCENT_BLUE,
            "B",
        ),
        (14.5, 6.0, "REPORTE DE SUSTENTABILIDAD ESG", 13.5, th.PRIMARY_BLUE, "B"),
        (
            21.0,
            4.5,
            "AgroPredictTambo - Mitigación Predictiva de Estrés Térmico (ITH)",
            8.0,
            th.TEXT_MUTED,
            "",
        ),
    )
    for y, h, text, size, color, style in header_rows:
        ly.draw_text(
            pdf, font, mx, y, 134.0, h, text, size=size, color=color, style=style
        )
    pdf.set_draw_color(*th.PRIMARY_BLUE)
    pdf.set_line_width(0.5)
    pdf.line(mx, 26.5, mx + th.EPW, 26.5)
    ly.draw_box(pdf, mx, 28.5, th.EPW, 17.0, fill=th.TINT_BLUE, accent=th.PRIMARY_BLUE)
    meta = (
        (15.0, 31.0, 66.0, f"Establecimiento: {farm_name}"),
        (82.0, 31.0, 64.0, f"Ubicación: {audit.location}"),
        (147.0, 31.0, 48.0, f"Auditoría: {date_str}"),
        (15.0, 38.0, 66.0, f"Escenario: {audit.weather_profile}"),
        (82.0, 38.0, 64.0, f"Rodeo: {cow_count} vacas"),
        (147.0, 38.0, 48.0, f"Equipos: {equipment_label}"),
    )
    for x, y, w, text in meta:
        ly.draw_text(pdf, font, x, y, w, 5.0, text, size=7.5)
