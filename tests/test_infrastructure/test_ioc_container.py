"""Pruebas unitarias para AppContainer e inyección de dependencias."""

from src.application.dtos.predict_stress_request_dto import (
    PredictStressRequestDTO,
)
from src.infrastructure.ioc_container import AppContainer


def test_app_container_wires_all_collaborators() -> None:
    container = AppContainer(force_heatwave=True)
    assert container.weather is not None
    assert container.cache is not None
    assert container.repo is not None
    assert container.predictor is not None
    assert container.notifier is not None
    assert container.relay is not None
    assert container.actuation_ctx.notifier is container.notifier
    assert container.actuation_ctx.hardware_controller is container.relay
    assert container.actuation_ctx.weather_cache is container.cache


def test_app_container_use_cases_executable() -> None:
    container = AppContainer(force_heatwave=True)
    resp = container.predict_uc.execute(PredictStressRequestDTO())
    assert len(resp.cooling_orders) > 0
    status = container.status_uc.execute()
    assert len(status) > 0
