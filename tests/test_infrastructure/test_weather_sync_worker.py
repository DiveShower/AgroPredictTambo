"""Pruebas unitarias para WeatherSyncWorker con ejecución asíncrona QThread."""

from typing import Any

from PyQt6.QtCore import QCoreApplication

from src.infrastructure.ui.desktop.workers.weather_sync_worker import (
    WeatherSyncWorker,
)


def test_weather_sync_worker_emits_synced_signal(mocker: Any) -> None:
    _ = QCoreApplication.instance() or QCoreApplication([])
    vm = mocker.Mock()
    fake_response = mocker.Mock()
    vm.sync_weather_and_predict.return_value = fake_response
    worker = WeatherSyncWorker(viewmodel=vm, lat=-31.25, lon=-61.48)
    synced, ready = [], []
    worker.weather_synced.connect(synced.append)
    worker.prediction_ready.connect(ready.append)
    worker.run()
    assert synced == [fake_response]
    assert ready == [fake_response]


def test_weather_sync_worker_emits_failed_signal_on_error(mocker: Any) -> None:
    _ = QCoreApplication.instance() or QCoreApplication([])
    vm = mocker.Mock()
    vm.sync_weather_and_predict.side_effect = RuntimeError("Conexión perdida")
    worker = WeatherSyncWorker(viewmodel=vm)
    failed = []
    worker.sync_failed.connect(failed.append)
    worker.run()
    assert failed == ["Conexión perdida"]


def test_weather_sync_worker_custom_predict_fn() -> None:
    _ = QCoreApplication.instance() or QCoreApplication([])
    worker = WeatherSyncWorker(predict_fn=lambda: {"stress": 2})
    ready = []
    worker.prediction_ready.connect(ready.append)
    worker.run()
    assert ready == [{"stress": 2}]
