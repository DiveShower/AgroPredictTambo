"""Pruebas unitarias para ScadaViewModel y workers QThread sin abrir GUI."""

from datetime import datetime
from typing import Any
from src.adapters.desktop.viewmodels.scada_viewmodel import ScadaViewModel
from src.application.dtos.predict_stress_response_dto import PredictStressResponseDTO
from src.application.dtos.sector_status_dto import SectorStatusDTO
from src.domain.entities.cooling_order import CoolingOrder
from src.domain.entities.sector import Sector
from src.domain.value_objects.weather_conditions import WeatherConditions
from src.infrastructure.ui.desktop.workers.telegram_bot_worker import TelegramBotWorker
from src.infrastructure.ui.desktop.workers.weather_sync_worker import WeatherSyncWorker


def _make_vm(mocker: Any) -> tuple[ScadaViewModel, Any, Any, Any, Any]:
    pred_uc, stat_uc, tog_uc, shutoff = mocker.Mock(), mocker.Mock(), mocker.Mock(), mocker.Mock()
    stat_uc.execute.return_value = [
        SectorStatusDTO("comederos", "Comederos", 120, True, True, 15, 6, 2, "Peligro", True),
        SectorStatusDTO("sombras", "Compost Barn", 100, True, False, 0, 4, 2, "Peligro Sanitario", True),
    ]
    tog_uc.execute.return_value = Sector("comederos", "Comederos", 120, False)
    w = WeatherConditions(34.5, 68.0, 6.0, datetime(2026, 1, 15, 14, 0), 820.0)
    pred_uc.execute.return_value = PredictStressResponseDTO(
        w, w, 87.75, 87.75, 4, [CoolingOrder("sombras", 2, 0, 270, w.timestamp, "Anti-mastitis")], []
    )
    return ScadaViewModel(pred_uc, stat_uc, tog_uc, shutoff), pred_uc, stat_uc, tog_uc, shutoff


def test_scada_viewmodel_formats_cards_and_anti_mastitis(mocker: Any) -> None:
    vm, _, _, tog_uc, shutoff = _make_vm(mocker)
    cards = vm.get_cards_state()
    assert len(cards) == 2
    assert (cards[0]["water_seconds"], cards[0]["fan_seconds"], cards[0]["color_hex"]) == (40, 270, "#e74c3c")
    assert cards[1]["water_seconds"] == 0
    assert "Anti-Mastitis" in cards[1]["water_text"]

    vm.toggle_occupancy("comederos", False)
    tog_uc.execute.assert_called_once_with("comederos", False)
    vm.emergency_shutoff()
    shutoff.assert_called_once()


def test_weather_and_telegram_workers_emit_signals_cleanly(mocker: Any) -> None:
    vm, _, _, _, _ = _make_vm(mocker)
    synced: list[Any] = []
    w_worker = WeatherSyncWorker(vm)
    w_worker.weather_synced.connect(synced.append)
    w_worker.run()
    w_worker.stop()
    assert len(synced) == 1 and synced[0].predicted_thi == 87.75

    changed: list[bool] = []
    bot_worker = TelegramBotWorker(vm)
    bot_worker.sector_state_changed.connect(lambda: changed.append(True))
    bot_worker.apply_remote_occupancy("sombras", False)
    bot_worker.stop()
    assert changed == [True]
