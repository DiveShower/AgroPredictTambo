"""Pruebas unitarias para CalculateSavingsUseCase y reporte ESG."""

from typing import Any

from src.application.dtos.calculate_savings_request_dto import (
    CalculateSavingsRequestDTO,
)
from src.application.use_cases.calculate_savings_uc import (
    CalculateSavingsUseCase,
)
from src.application.use_cases.generate_sustainability_report_uc import (
    GenerateSustainabilityReportUseCase,
)


def test_calculate_savings_meets_kpi_thresholds() -> None:
    uc = CalculateSavingsUseCase()
    res = uc.execute(
        CalculateSavingsRequestDTO(
            baseline_operating_hours=8.0,
            predictive_active_hours=3.5,
            cow_count=100,
            milk_price_ars=430.0,
        )
    )
    assert res.savings.water_saved_pct >= 35.0
    assert res.savings.combined_water_saved_pct >= 75.0
    assert res.savings.energy_saved_pct >= 40.0
    assert res.carbon_footprint.co2_avoided_kg == round(
        res.savings.energy_saved_kwh * 0.35, 2
    )
    assert res.economic_impact.milk_protected_liters > 0.0
    assert res.economic_impact.economic_return_ars > 0.0


def test_calculate_savings_zero_baseline_is_safe() -> None:
    uc = CalculateSavingsUseCase()
    res = uc.execute(
        CalculateSavingsRequestDTO(
            baseline_operating_hours=0.0,
            predictive_active_hours=0.0,
        )
    )
    assert res.savings.water_saved_pct == 0.0
    assert res.savings.energy_saved_pct == 0.0


def test_generate_sustainability_report_delegates_to_port(mocker: Any) -> None:
    report_port = mocker.Mock()
    report_port.generate_sustainability_pdf.return_value = "/tmp/reporte_esg.pdf"
    uc = GenerateSustainabilityReportUseCase(report_generator=report_port)

    dto = uc.execute("Tambo San José", "/tmp/reporte_esg.pdf")
    assert dto.pdf_file_path == "/tmp/reporte_esg.pdf"
    report_port.generate_sustainability_pdf.assert_called_once()
