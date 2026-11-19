"""Pruebas del reporte PDF ESG enriquecido y contexto de auditoría."""

import re
from pathlib import Path

from fpdf import FPDF

from src.application.use_cases import calculate_savings_uc as cs_uc
from src.application.use_cases import generate_sustainability_report_uc as gr_uc
from src.domain.fixtures.default_farm import get_default_sectors
from src.domain.value_objects.report_audit_context import ReportAuditContext
from src.infrastructure.reporting import pdf_document_builder as doc
from src.infrastructure.reporting import pdf_sustainability_report_adapter as rep
from src.infrastructure.repositories import in_memory_sector_repo as repo
from src.infrastructure.weather_api.mock_weather_adapter import MockWeatherAdapter


def test_enriched_report_uc_generates_single_page_pdf_with_full_context(
    tmp_path: Path,
) -> None:
    uc = gr_uc.GenerateSustainabilityReportUseCase(
        rep.PdfSustainabilityReportAdapter(),
        cs_uc.CalculateSavingsUseCase(),
        repo.InMemorySectorRepository(),
        MockWeatherAdapter("heatwave"),
    )
    pdf_out = tmp_path / "esg.pdf"
    dto = uc.execute("Tambo San José - Nestlé Conecta", str(pdf_out))
    raw = pdf_out.read_bytes()
    assert pdf_out.exists() and raw.startswith(b"%PDF")
    assert len(re.findall(rb"/Type\s*/Page\b", raw)) == 1
    assert len(dto.sectors) == 3
    sombras = next(s for s in dto.sectors if s.sector_id == "sombras")
    assert not sombras.allows_water_sprinkling
    assert dto.audit_context and dto.audit_context.nocturnal_debt_hours == 6
    assert dto.economic_impact.milk_protected_liters == 80.0


def test_render_sustainability_document_renders_esg_and_anti_mastitis_text() -> None:
    s = cs_uc.CalculateSavingsUseCase().execute()
    pdf = FPDF()
    pdf.set_compression(False)
    audit = ReportAuditContext(nocturnal_debt_hours=6, current_thi=87.75)
    doc.render_sustainability_document(
        pdf,
        "Helvetica",
        "Tambo San José",
        s.savings,
        s.carbon_footprint,
        s.economic_impact,
        get_default_sectors(),
        audit,
    )
    assert pdf.page == 1
    raw = bytes(pdf.output())
    t = (b"BLOQUEADA", b"Anti-Mastitis", b"SIGLeA", b"88.4%", b"34,400", b"Oliveira")
    assert all(x in raw for x in t)
