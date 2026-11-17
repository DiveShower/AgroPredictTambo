"""Pruebas unitarias para CliController y console_runner con mocks de Casos de Uso."""

from datetime import datetime
from typing import Any
from src.adapters.cli.cli_controller import CliController
from src.application.dtos.calculate_savings_response_dto import CalculateSavingsResponseDTO
from src.application.dtos.predict_stress_response_dto import PredictStressResponseDTO
from src.application.dtos.sector_status_dto import SectorStatusDTO
from src.domain.entities.cooling_order import CoolingOrder
from src.domain.entities.sector import Sector
from src.domain.value_objects.carbon_footprint import CarbonFootprint
from src.domain.value_objects.economic_impact import EconomicImpact
from src.domain.value_objects.resource_savings import ResourceSavings
from src.domain.value_objects.weather_conditions import WeatherConditions
from src.infrastructure.ui.cli.console_runner import run_cli


def _make_controller(mocker: Any) -> tuple[CliController, Any, Any, Any, Any]:
    pred_uc, sav_uc, tog_uc, stat_uc = mocker.Mock(), mocker.Mock(), mocker.Mock(), mocker.Mock()
    stat_uc.execute.return_value = [
        SectorStatusDTO("sombras", "Compost", 100, True, False, 0, 4, 2, "Peligro Sanitario", True)
    ]
    tog_uc.execute.return_value = Sector("corral_espera", "Corral", 80, False)
    w = WeatherConditions(34.5, 68.0, 6.0, datetime(2026, 1, 15, 14, 0), 820.0)
    pred_uc.execute.return_value = PredictStressResponseDTO(
        w, w, 87.75, 87.75, 4, [CoolingOrder("sombras", 2, 0, 270, w.timestamp, "Anti-mastitis")], []
    )
    sav = ResourceSavings.calculate(2000.0, 875.0, 7500.0, 86.0, 37.6)
    sav_uc.execute.return_value = CalculateSavingsResponseDTO(
        sav, CarbonFootprint.from_energy_savings(48.4), EconomicImpact.calculate(100, 3, 1, 430.0)
    )
    return CliController(pred_uc, sav_uc, tog_uc, stat_uc), pred_uc, sav_uc, tog_uc, stat_uc


def test_cli_controller_routes_status_occupy_predict_and_savings(mocker: Any) -> None:
    ctrl, pred_uc, sav_uc, tog_uc, stat_uc = _make_controller(mocker)
    assert "sombras" in ctrl.handle_status()
    assert "VACIO" in ctrl.handle_occupy("corral_espera", False)
    assert "Anti-mastitis" in ctrl.handle_predict()
    assert "CAMMESA" in ctrl.handle_savings()
    stat_uc.execute.assert_called_once()
    tog_uc.execute.assert_called_once_with("corral_espera", False)
    pred_uc.execute.assert_called_once()
    sav_uc.execute.assert_called_once()


def test_console_runner_interactive_and_benchmark_modes(mocker: Any) -> None:
    ctrl, _, _, _, _ = _make_controller(mocker)
    outputs: list[str] = []
    assert run_cli(ctrl, benchmark_mode=True, output_fn=outputs.append) == 0
    assert any("BALANCE DE AHORRO" in line for line in outputs)

    inputs = iter(["1", "0"])
    assert run_cli(ctrl, benchmark_mode=False, input_fn=lambda _: next(inputs), output_fn=outputs.append) == 0
