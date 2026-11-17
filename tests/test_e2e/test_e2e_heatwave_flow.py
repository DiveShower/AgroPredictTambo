"""Pruebas E2E del flujo completo de ola de calor, anti-mastitis y ocupación."""

import pytest

from src.application.dtos.predict_stress_request_dto import PredictStressRequestDTO
from src.application.use_cases.predict_sector_stress_uc import (
    PredictSectorStressUseCase,
)
from src.application.use_cases.toggle_sector_occupancy_uc import (
    ToggleSectorOccupancyUseCase,
)
from src.infrastructure.hardware.mock_relay_adapter import MockRelayAdapter
from src.infrastructure.ml.sklearn_predictor_adapter import SklearnPredictorAdapter
from src.infrastructure.repositories.in_memory_sector_repo import (
    InMemorySectorRepository,
)
from src.infrastructure.weather_api.mock_weather_adapter import MockWeatherAdapter


@pytest.mark.e2e
def test_e2e_heatwave_anti_mastitis_and_occupancy_flow() -> None:
    """Valida ola de calor, bloqueo hídrico en sombras y corte por sector vacío."""
    weather = MockWeatherAdapter("heatwave")
    repo = InMemorySectorRepository()
    predictor = SklearnPredictorAdapter()
    relay = MockRelayAdapter()
    predict_uc = PredictSectorStressUseCase(
        weather, repo, predictor, hardware_controller=relay
    )

    req = PredictStressRequestDTO(forecast_lead_hours=14)
    resp = predict_uc.execute(req)
    assert resp.predicted_thi > 80.0
    orders = {order.sector_id: order for order in resp.cooling_orders}

    for concrete_id in ("corral_espera", "comederos"):
        order = orders[concrete_id]
        assert order.is_active is True
        assert order.water_mist_seconds == 40
        assert order.fan_ventilation_seconds == 270
        assert relay.water_valves_seconds[concrete_id] == 40

    sombras = orders["sombras"]
    assert sombras.is_active is True
    assert sombras.water_mist_seconds == 0
    assert sombras.fan_ventilation_seconds > 0
    assert "sombras" not in relay.water_valves_seconds

    ToggleSectorOccupancyUseCase(repo).execute("corral_espera", False)
    after = {o.sector_id: o for o in predict_uc.execute(req).cooling_orders}
    assert after["corral_espera"].is_active is False
    assert after["corral_espera"].water_mist_seconds == 0
    assert after["corral_espera"].fan_ventilation_seconds == 0
    assert after["comederos"].is_active is True
