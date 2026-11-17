"""Caso de uso orquestador para predicción de estrés y emisión de órdenes."""

from typing import Optional
from src.application.dtos.predict_stress_request_dto import PredictStressRequestDTO
from src.application.dtos.predict_stress_response_dto import PredictStressResponseDTO
from src.application.use_cases.sector_order_helper import evaluate_sector_order
from src.domain.ports.hardware_controller_port import IHardwareController
from src.domain.ports.model_predictor_port import IModelPredictor
from src.domain.ports.notifier_port import INotifier
from src.domain.ports.sector_repository_port import ISectorRepository
from src.domain.ports.weather_cache_port import IWeatherCache
from src.domain.ports.weather_provider_port import IWeatherProvider
from src.domain.value_objects.milking_schedule import MilkingSchedule
from src.domain.value_objects.nocturnal_recovery import NocturnalRecovery
from src.domain.value_objects.thi_score import THI_Score
from src.domain.value_objects.weather_conditions import WeatherConditions


class PredictSectorStressUseCase:
    """Orquesta clima, inferencia ML, reglas sanitarias y alertas por sector."""

    def __init__(
        self, weather_provider: IWeatherProvider, sector_repository: ISectorRepository,
        model_predictor: IModelPredictor, notifier: Optional[INotifier] = None,
        hardware_controller: Optional[IHardwareController] = None,
        weather_cache: Optional[IWeatherCache] = None,
        milking_schedule: Optional[MilkingSchedule] = None,
    ) -> None:
        self._weather, self._sectors = weather_provider, sector_repository
        self._model, self._notifier = model_predictor, notifier
        self._hardware, self._cache = hardware_controller, weather_cache
        self._milking = milking_schedule or MilkingSchedule()

    def _fetch(self, lat: float, lon: float) -> tuple[WeatherConditions, list[WeatherConditions]]:
        try:
            curr, fore = self._weather.get_current_weather(lat, lon), self._weather.get_hourly_forecast(lat, lon, hours=24)
            if self._cache:
                self._cache.save_forecast(fore)
            return curr, fore
        except Exception:
            if self._cache and self._cache.is_cache_valid():
                cached = self._cache.get_cached_forecast()
                return cached[0], cached
            raise

    def execute(self, req: PredictStressRequestDTO = PredictStressRequestDTO()) -> PredictStressResponseDTO:
        curr, fore = self._fetch(req.latitude, req.longitude)
        c_thi = THI_Score.calculate(curr.temperature_c, curr.relative_humidity).value
        idx = min(req.forecast_lead_hours, len(fore) - 1) if fore else 0
        target = fore[idx] if fore else curr
        p_thi = THI_Score.calculate(target.temperature_c, target.relative_humidity).value
        night = [c for c in fore if c.timestamp.hour >= 21 or c.timestamp.hour < 6][:6]
        warm_n = sum(1 for c in night if THI_Score.calculate(c.temperature_c, c.relative_humidity).value >= 65.0)
        recovery, orders, alerts = NocturnalRecovery(cool_hours_count=max(0, 6 - warm_n)), [], []
        for sec in self._sectors.get_all_sectors():
            if not req.target_sector_id or sec.sector_id == req.target_sector_id:
                o, a = evaluate_sector_order(sec, target, fore[:idx], p_thi, recovery, self._model, self._milking, self._notifier, self._hardware)
                orders.append(o)
                alerts.extend([a] if a else [])
        return PredictStressResponseDTO(curr, target, c_thi, p_thi, recovery.debt_hours, orders, alerts)
