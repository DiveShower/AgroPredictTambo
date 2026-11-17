"""Pruebas unitarias para los handlers de acción de Telegram."""

from datetime import datetime
from unittest.mock import MagicMock, call

from src.adapters.telegram.handlers.occupy_handler import OccupyHandler
from src.adapters.telegram.handlers.report_handler import ReportHandler
from src.adapters.telegram.handlers.savings_handler import SavingsHandler
from src.application.dtos.calculate_savings_response_dto import (
    CalculateSavingsResponseDTO,
)
from src.application.dtos.sustainability_report_dto import SustainabilityReportDTO
from src.domain.entities.sector import Sector
from src.domain.exceptions.sector_not_found_exception import SectorNotFoundException
from src.domain.value_objects.carbon_footprint import CarbonFootprint
from src.domain.value_objects.economic_impact import EconomicImpact
from src.domain.value_objects.resource_savings import ResourceSavings

_SAV = ResourceSavings.calculate(1000.0, 400.0, 1200.0, 100.0, 40.0)
_CO2 = CarbonFootprint.from_energy_savings(60.0)
_ECO = EconomicImpact.calculate(100, 2, 1)


def test_occupy_handler_handles_flags_callback_and_errors() -> None:
    uc, cb = MagicMock(), MagicMock()
    uc.execute.side_effect = [
        Sector("C1", "Corral 1", 100, True),
        Sector("C1", "Corral 1", 100, False),
        SectorNotFoundException("X"),
    ]
    h = OccupyHandler(uc, on_changed=cb)
    assert "Uso:" in h.handle("C1", "bad") and "Uso:" in h.handle(" ", True)
    assert "OCUPADO" in h.handle(" C1 ", "si") and "VACÍO" in h.handle("C1", "0")
    assert h.handle("X", "true") == "Sector no encontrado: X."
    uc.execute.assert_has_calls([call("C1", True), call("C1", False), call("X", True)])
    cb.assert_has_calls([call("C1", True), call("C1", False)])


def test_savings_handler_delegates_and_formats() -> None:
    uc = MagicMock()
    uc.execute.return_value = CalculateSavingsResponseDTO(_SAV, _CO2, _ECO)
    msg = SavingsHandler(uc).handle()
    uc.execute.assert_called_once_with()
    assert "600.00 L" in msg and "21.00 kg CO2e" in msg and "65.00 L" in msg


def test_report_handler_returns_summary_and_optional_pdf_path() -> None:
    uc, now = MagicMock(), datetime(2026, 1, 15, 14, 0)
    uc.execute.side_effect = [
        SustainabilityReportDTO("Tambo A", now, _SAV, _CO2, _ECO, "/tmp/r.pdf"),
        SustainabilityReportDTO("Tambo A", now, _SAV, _CO2, _ECO, None),
    ]
    h = ReportHandler(uc, farm_name="Tambo A", output_path="/tmp/r.pdf")
    msg1, path1 = h.handle()
    uc.execute.assert_called_with(farm_name="Tambo A", output_path="/tmp/r.pdf")
    assert path1 == "/tmp/r.pdf" and "Tambo A" in msg1 and "/tmp/r.pdf" in msg1
    msg2, path2 = h.handle()
    assert path2 is None and "No generado" in msg2
