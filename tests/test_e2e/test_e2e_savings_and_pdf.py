"""Pruebas E2E de ahorro hídrico/energético ESG, carbono y reporte PDF."""

from pathlib import Path

import pytest

from src.application.dtos.calculate_savings_request_dto import (
    CalculateSavingsRequestDTO,
)
from src.application.use_cases.calculate_savings_uc import CalculateSavingsUseCase
from src.application.use_cases.generate_sustainability_report_uc import (
    GenerateSustainabilityReportUseCase,
)
from src.infrastructure.reporting.pdf_sustainability_report_adapter import (
    PdfSustainabilityReportAdapter,
)


@pytest.mark.e2e
def test_e2e_savings_calculation_and_pdf_report(tmp_path: Path) -> None:
    """Valida ahorro hídrico/eléctrico, CO2 CAMMESA, SIGLeA y PDF real."""
    req = CalculateSavingsRequestDTO()
    savings_uc = CalculateSavingsUseCase()
    direct = savings_uc.execute(req)

    pdf_out = tmp_path / "sustainability_report_nestle.pdf"
    report_uc = GenerateSustainabilityReportUseCase(
        PdfSustainabilityReportAdapter(),
        savings_uc,
    )
    report = report_uc.execute("Tambo Modelo Rafaela", str(pdf_out), req)

    assert pdf_out.exists()
    assert pdf_out.stat().st_size > 0
    assert pdf_out.read_bytes().startswith(b"%PDF")
    assert report.pdf_file_path == str(pdf_out)
    assert report.farm_name == "Tambo Modelo Rafaela"
    assert report.savings == direct.savings

    assert report.savings.water_saved_pct >= 35.0
    assert report.savings.combined_water_saved_pct >= 75.0
    assert report.savings.water_saved_liters > 0.0
    assert report.savings.energy_saved_pct >= 40.0
    assert report.savings.energy_saved_kwh > 0.0

    assert report.carbon_footprint == direct.carbon_footprint
    assert report.carbon_footprint.emission_factor_kg_per_kwh == 0.35
    assert report.carbon_footprint.co2_avoided_kg > 0.0

    assert report.economic_impact == direct.economic_impact
    assert report.economic_impact.milk_protected_liters > 0.0
    assert report.economic_impact.economic_return_ars > 0.0
