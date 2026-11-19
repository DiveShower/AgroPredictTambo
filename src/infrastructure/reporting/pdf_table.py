"""Primitiva atómica de filas de tabla FPDF2 para reportes PDF ESG."""

from collections.abc import Sequence
from typing import Literal

from fpdf import FPDF

from src.infrastructure.reporting.pdf_theme import BORDER_SOFT, MARGIN_X, Rgb

Align = Literal["L", "C", "R"]
FontStyle = Literal["", "B"]
TableCol = tuple[float, str, Align, Rgb, Rgb]


def draw_table_row(
    pdf: FPDF,
    font: str,
    y: float,
    h: float,
    cols: Sequence[TableCol],
    size: float = 7.8,
    style: FontStyle = "",
) -> None:
    """Dibuja una fila de tabla alineada a MARGIN_X con borde inferior suave."""
    pdf.set_xy(MARGIN_X, y)
    pdf.set_draw_color(*BORDER_SOFT)
    pdf.set_line_width(0.2)
    pdf.set_font(font, style, size)
    for w, txt, align, bg, fg in cols:
        pdf.set_fill_color(*bg)
        pdf.set_text_color(*fg)
        pdf.cell(w, h, txt, border="B", align=align, fill=True)
