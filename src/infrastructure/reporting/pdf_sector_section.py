"""Renderizador de tabla de sectorización y regla sanitaria anti-mastitis."""

from collections.abc import Sequence

from fpdf import FPDF

from src.domain.entities.sector import Sector
from src.infrastructure.reporting import pdf_layout as ly
from src.infrastructure.reporting import pdf_theme as th
from src.infrastructure.reporting.pdf_table import Align, TableCol, draw_table_row

_W: tuple[float, ...] = (52.0, 20.0, 28.0, 22.0, 24.0, 40.0)
_A: tuple[Align, ...] = ("L", "C", "C", "C", "C", "L")
_HDR = ("Sector", "Rodeo", "Umbral ITH", "Asp/Ven", "Aspersión", "Regla Sanitaria")
_NOTE = (
    "Criterio sanitario: bloqueo estricto de agua en cama orgánica "
    "(Compost Barn) para evitar mastitis."
)


def _sector_cols(s: Sector, bg: th.Rgb) -> list[TableCol]:
    ok = s.allows_water_sprinkling
    s_bg = bg if ok else th.TINT_RED
    s_fg = th.AGRO_GREEN if ok else th.DANGER_RED
    vals = (
        s.sector_id,
        f"{s.cow_capacity}",
        f"{s.thi_threshold_alert:.0f} / {s.thi_threshold_danger:.0f}",
        f"{s.sprinkler_count} / {s.fan_count}",
        "PERMITIDA" if ok else "BLOQUEADA",
        "Ciclo 40s/270s" if ok else "Anti-Mastitis (0% agua)",
    )
    return [
        (w, t, a, s_bg if j == 4 else bg, s_fg if j == 4 else th.TEXT_DARK)
        for j, (w, t, a) in enumerate(zip(_W, vals, _A, strict=True))
    ]


def write_sectors_table(pdf: FPDF, font: str, sectors: Sequence[Sector]) -> None:
    """Dibuja la tabla de sectorización inteligente y regla sanitaria."""
    title = "2. SECTORIZACIÓN INTELIGENTE Y REGLA SANITARIA ANTI-MASTITIS"
    ly.draw_section_title(pdf, font, 123.5, title)
    hdr: list[TableCol] = [
        (w, t, a, th.PRIMARY_BLUE, th.WHITE)
        for w, t, a in zip(_W, _HDR, _A, strict=True)
    ]
    draw_table_row(pdf, font, 129.0, 6.0, hdr, size=7.5, style="B")
    if not sectors:
        msg = "Sin sectores provistos en esta corrida"
        empty: list[TableCol] = [(186.0, msg, "C", th.ROW_ALT, th.TEXT_MUTED)]
        draw_table_row(pdf, font, 135.0, 6.0, empty, size=7.5)
    else:
        for i, s in enumerate(sectors[:3]):
            bg = th.WHITE if i % 2 == 0 else th.ROW_ALT
            draw_table_row(
                pdf, font, 135.0 + i * 6.0, 6.0, _sector_cols(s, bg), size=7.5
            )
    ly.draw_text(pdf, font, th.MARGIN_X, 154.0, th.EPW, 4.5, _NOTE, 7.0, th.TEXT_MUTED)
