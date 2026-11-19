"""Primitivas compartidas de texto, secciones y tarjetas FPDF2 para PDF ESG."""

from fpdf import FPDF

from src.infrastructure.reporting import pdf_theme as th
from src.infrastructure.reporting.pdf_table import Align, FontStyle
from src.infrastructure.reporting.pdf_theme import Rgb


def draw_text(
    pdf: FPDF,
    font: str,
    x: float,
    y: float,
    w: float,
    h: float,
    text: str,
    size: float = 8.0,
    color: Rgb = th.TEXT_DARK,
    style: FontStyle = "",
    align: Align = "L",
) -> None:
    """Dibuja texto posicionado con tipografía, color y alineación indicados."""
    pdf.set_xy(x, y)
    pdf.set_font(font, style, size)
    pdf.set_text_color(*color)
    pdf.cell(w, h, text, align=align)


def draw_section_title(pdf: FPDF, font: str, y: float, title: str) -> None:
    """Dibuja un encabezado de sección ESG con acento vertical y línea base."""
    mx, blue = th.MARGIN_X, th.PRIMARY_BLUE
    pdf.set_fill_color(*blue)
    pdf.rect(mx, y + 0.8, 1.5, 4.4, style="F")
    draw_text(pdf, font, mx + 3.0, y, th.EPW - 3.0, 6.0, title, 10.0, blue, "B")
    pdf.set_draw_color(*th.BORDER_SOFT)
    pdf.set_line_width(0.25)
    pdf.line(mx, y + 6.2, mx + th.EPW, y + 6.2)


def draw_box(
    pdf: FPDF,
    x: float,
    y: float,
    w: float,
    h: float,
    fill: Rgb = th.WHITE,
    accent: Rgb | None = None,
    border: Rgb = th.BORDER_SOFT,
) -> None:
    """Dibuja un recuadro relleno con borde suave y franja superior opcional."""
    pdf.set_fill_color(*fill)
    pdf.set_draw_color(*border)
    pdf.set_line_width(0.2)
    pdf.rect(x, y, w, h, style="FD")
    if accent is not None:
        pdf.set_fill_color(*accent)
        pdf.rect(x, y, w, 1.4, style="F")
