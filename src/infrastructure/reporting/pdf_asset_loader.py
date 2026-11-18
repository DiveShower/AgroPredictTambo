"""Cargador de fuentes TrueType y membrete institucional para reportes PDF."""

from pathlib import Path

from fpdf import FPDF


def get_assets_dir() -> Path:
    """Retorna la ruta al directorio de assets empaquetados."""
    return Path(__file__).resolve().parent / "assets"


def setup_pdf_fonts(pdf: FPDF) -> str:
    """Configura fuentes TrueType Unicode si están disponibles o recurre a Helvetica."""
    ttf_path = get_assets_dir() / "DejaVuSans.ttf"
    if ttf_path.exists():
        pdf.add_font("DejaVu", style="", fname=str(ttf_path))
        pdf.add_font("DejaVu", style="B", fname=str(ttf_path))
        return "DejaVu"
    return "Helvetica"


def render_header_logo(pdf: FPDF) -> None:
    """Renderiza el logotipo de Nestlé Conecta en el encabezado si existe."""
    logo_path = get_assets_dir() / "nestle_conecta_logo.png"
    if logo_path.exists():
        pdf.image(str(logo_path), x=155, y=10, w=45)
