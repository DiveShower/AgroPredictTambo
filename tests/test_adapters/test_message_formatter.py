"""Pruebas unitarias para TelegramMessageFormatter."""

from datetime import datetime

from src.adapters.telegram.formatters.message_formatter import TelegramMessageFormatter
from src.application.dtos.calculate_savings_response_dto import (
    CalculateSavingsResponseDTO,
)
from src.application.dtos.predict_stress_response_dto import PredictStressResponseDTO
from src.application.dtos.sector_status_dto import SectorStatusDTO
from src.domain.entities.cooling_order import CoolingOrder
from src.domain.value_objects.carbon_footprint import CarbonFootprint
from src.domain.value_objects.economic_impact import EconomicImpact
from src.domain.value_objects.resource_savings import ResourceSavings
from src.domain.value_objects.thi_score import THI_Score
from src.domain.value_objects.weather_conditions import WeatherConditions

_FMT = TelegramMessageFormatter
_TS = datetime(2026, 1, 15, 14, 0)
_W = WeatherConditions(31.5, 62.0, 12.0, _TS, 750.0)


def test_welcome_and_current_state_include_commands_and_thi() -> None:
    welcome = _FMT.format_welcome()
    assert all(cmd in welcome for cmd in ("/estado", "/ocupar", "/reporte"))
    thi = THI_Score.calculate(_W.temperature_c, _W.relative_humidity)
    state = _FMT.format_current_state(_W, thi)
    assert "31.5 °C" in state and "62%" in state
    assert f"{thi.value:.2f}" in state and "PELIGRO" in state


def test_forecast_24h_handles_empty_and_populated_series() -> None:
    assert "sin datos disponibles" in _FMT.format_forecast_24h([])
    table = _FMT.format_forecast_24h([_W])
    assert "```" in table and "14:00" in table
    assert f"{THI_Score.calculate(31.5, 62.0).value:.1f}" in table


def test_sectors_orders_and_savings_formatters() -> None:
    sec = SectorStatusDTO("TAMBO", "Ordeñe", 80, True, False, 0, 4, 2, "0s/60s", True)
    assert "Anti-Mastitis" in _FMT.format_sectors([sec])
    order = CoolingOrder("CORRAL_1", 2, 40, 270, _TS, "ITH crítico")
    pred = PredictStressResponseDTO(_W, _W, 80.5, 81.2, 4, [order], [])
    pred_msg = _FMT.format_prediction(pred)
    assert "40s agua / 270s vent" in pred_msg and "81.20" in pred_msg
    sav = ResourceSavings.calculate(1000.0, 400.0, 3800.0, 80.0, 35.0)
    resp = CalculateSavingsResponseDTO(
        sav,
        CarbonFootprint.from_energy_savings(45.0),
        EconomicImpact.calculate(100, 3, 1),
    )
    sav_msg = _FMT.format_savings(resp)
    assert all(tok in sav_msg for tok in ("600.00 L", "45.00 kWh", "kg CO2e", "ARS"))
