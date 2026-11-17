"""Pruebas unitarias para SavingsViewModel (formateo de moneda SIGLeA, kWh y PDF)."""

from datetime import datetime
from typing import Any

from src.adapters.desktop.viewmodels.savings_viewmodel import SavingsViewModel
from src.application.dtos.sustainability_report_dto import (
    SustainabilityReportDTO,
)
from src.application.use_cases.calculate_savings_uc import (
    CalculateSavingsUseCase,
)
from src.domain.value_objects.carbon_footprint import CarbonFootprint
from src.domain.value_objects.economic_impact import EconomicImpact
from src.domain.value_objects.resource_savings import ResourceSavings


def test_savings_viewmodel_formats_siglea_currency_kwh_and_water() -> None:
    vm = SavingsViewModel(savings_uc=CalculateSavingsUseCase())
    kpis = vm.get_kpi_cards_data(
        active_hours=3.5, cow_count=100, milk_price_ars=430.0
    )

    assert "L/día" in kpis["water_software"]
    assert "4.9 L/min" in kpis["water_combined"]
    assert "kWh/día" in kpis["energy_kwh"]
    assert "kg CO2e" in kpis["carbon_cammesa"]
    assert "100 vacas" in kpis["milk_siglea"]
    assert "ARS/día" in kpis["economic_ars"]
    assert kpis["economic_ars"].startswith("$")


def test_savings_viewmodel_exports_pdf_via_use_case(mocker: Any) -> None:
    sav_uc = CalculateSavingsUseCase()
    rep_uc = mocker.Mock()
    sav = ResourceSavings.calculate(1000.0, 400.0, 3800.0, 80.0, 35.0)
    rep_uc.execute.return_value = SustainabilityReportDTO(
        farm_name="Tambo San José",
        generated_at=datetime(2026, 1, 15, 14, 0),
        savings=sav,
        carbon_footprint=CarbonFootprint.from_energy_savings(45.0),
        economic_impact=EconomicImpact.calculate(100, 3, 1, 430.0),
        pdf_file_path="/tmp/nestle_esg.pdf",
    )

    vm = SavingsViewModel(savings_uc=sav_uc, report_uc=rep_uc)
    path = vm.export_sustainability_pdf("Tambo San José", "/tmp/nestle_esg.pdf")
    assert path == "/tmp/nestle_esg.pdf"
    rep_uc.execute.assert_called_once()
