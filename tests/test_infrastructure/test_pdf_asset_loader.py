"""Pruebas unitarias para pdf_asset_loader con soporte TrueType Unicode."""

from pathlib import Path

from fpdf import FPDF

from src.infrastructure.reporting.pdf_asset_loader import (
    get_assets_dir,
    render_header_logo,
    setup_pdf_fonts,
)


def test_get_assets_dir_exists() -> None:
    assets_dir = get_assets_dir()
    assert assets_dir.exists()
    assert (assets_dir / "DejaVuSans.ttf").exists()
    assert (assets_dir / "nestle_conecta_logo.png").exists()


def test_setup_pdf_fonts_registers_unicode_dejavu() -> None:
    pdf = FPDF()
    font_family = setup_pdf_fonts(pdf)
    assert font_family == "DejaVu"
    assert "dejavu" in pdf.fonts


def test_render_header_logo_and_unicode_symbols(tmp_path: Path) -> None:
    pdf = FPDF()
    font = setup_pdf_fonts(pdf)
    pdf.add_page()
    render_header_logo(pdf)
    pdf.set_font(font, "B", 14)
    pdf.cell(0, 10, "NESTLÉ CONECTA — 28.5 °C")
    pdf.set_font(font, "", 11)
    pdf.cell(0, 10, "Emisiones: 120.5 kg CO₂e auditadas")
    out_pdf = tmp_path / "unicode_test.pdf"
    pdf.output(str(out_pdf))
    assert out_pdf.exists()
    assert out_pdf.stat().st_size > 0
