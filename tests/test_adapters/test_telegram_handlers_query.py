"""Pruebas unitarias para los handlers de consulta de Telegram."""

from datetime import datetime
from unittest.mock import MagicMock

from src.adapters.telegram.handlers.forecast_handler import ForecastHandler
from src.adapters.telegram.handlers.predict_handler import PredictHandler
from src.adapters.telegram.handlers.sectors_handler import SectorsHandler
from src.adapters.telegram.handlers.start_handler import StartHandler
from src.adapters.telegram.handlers.state_handler import StateHandler
from src.application.dtos.predict_stress_request_dto import PredictStressRequestDTO
from src.application.dtos.predict_stress_response_dto import PredictStressResponseDTO
from src.application.dtos.sector_status_dto import SectorStatusDTO
from src.domain.entities.cooling_order import CoolingOrder
from src.domain.value_objects.thi_score import THI_Score
from src.domain.value_objects.weather_conditions import WeatherConditions

_W = WeatherConditions(31.5, 62.0, 12.0, datetime(2026, 1, 15, 14, 0), 750.0)


def test_start_handler_registers_valid_chat_ids() -> None:
    subs: set[int] = {99}
    handler = StartHandler(subs)
    assert "/estado" in handler.handle(0)
    assert subs == {99}
    assert "Tambo San José" in handler.handle(12345)
    assert handler.subscribed_chat_ids == {99, 12345}


def test_state_and_predict_handlers_delegate_to_use_case() -> None:
    uc = MagicMock()
    order = CoolingOrder("CORRAL_1", 2, 40, 270, _W.timestamp, "ITH crítico")
    uc.execute.return_value = PredictStressResponseDTO(
        _W, _W, 80.5, 81.2, 4, [order], []
    )
    state_msg = StateHandler(uc).handle()
    uc.execute.assert_called_once_with()
    thi = THI_Score.calculate(31.5, 62.0).value
    assert "31.5 °C" in state_msg and "62%" in state_msg and f"{thi:.2f}" in state_msg
    uc.reset_mock()
    pred_msg = PredictHandler(uc).handle()
    uc.execute.assert_called_once_with(PredictStressRequestDTO(forecast_lead_hours=1))
    assert "81.20" in pred_msg and "40s agua / 270s vent" in pred_msg


def test_forecast_and_sectors_handlers_support_empty_and_data() -> None:
    provider = MagicMock()
    provider.get_hourly_forecast.side_effect = [[], [_W]]
    assert "sin datos disponibles" in ForecastHandler(provider).handle()
    provider.get_hourly_forecast.assert_called_with(-31.25, -61.48, hours=24)
    assert "14:00" in ForecastHandler(provider, -31.5, -60.5).handle()
    provider.get_hourly_forecast.assert_called_with(-31.5, -60.5, hours=24)
    sec = SectorStatusDTO("TAMBO", "Ordeñe", 80, True, False, 0, 4, 2, "0s/60s", True)
    uc = MagicMock()
    uc.execute.side_effect = [[], [sec]]
    assert "sin sectores registrados" in SectorsHandler(uc).handle()
    assert "Anti-Mastitis" in SectorsHandler(uc, -31.0, -61.0).handle()
    uc.execute.assert_called_with(-31.0, -61.0)
