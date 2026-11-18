"""Caso de uso orquestador para predicción de estrés y emisión de órdenes."""

from typing import Any

from src.application.dtos.predict_stress_request_dto import (
    PredictStressRequestDTO,
)
from src.application.dtos.predict_stress_response_dto import (
    PredictStressResponseDTO,
)
from src.application.dtos.stress_actuation_context import StressActuationContext
from src.application.use_cases.stress_pipeline_runner import run_stress_pipeline
from src.application.use_cases.weather_fetcher_helper import (
    fetch_weather_with_cache,
)
from src.domain.ports.model_predictor_port import IModelPredictor
from src.domain.ports.sector_repository_port import ISectorRepository
from src.domain.ports.weather_provider_port import IWeatherProvider


class PredictSectorStressUseCase:
    """Orquesta clima, inferencia ML, reglas sanitarias y alertas por sector."""

    def __init__(
        self,
        weather: IWeatherProvider,
        repo: ISectorRepository,
        model: IModelPredictor,
        *args: Any,
        context: StressActuationContext | None = None,
        **kwargs: Any,
    ) -> None:
        self._weather, self._sectors, self._model = weather, repo, model
        self._ctx = StressActuationContext.from_args(context, args, kwargs)

    def execute(
        self, req: PredictStressRequestDTO | None = None
    ) -> PredictStressResponseDTO:
        dto = req or PredictStressRequestDTO()
        curr, fore = fetch_weather_with_cache(
            self._weather, self._ctx.weather_cache, dto.latitude, dto.longitude
        )
        return run_stress_pipeline(
            curr, fore, self._sectors.get_all_sectors(), self._model, self._ctx, dto
        )
