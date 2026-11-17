"""Fábrica compartida de casos de uso del núcleo."""

import os

import src.application.use_cases.calculate_savings_uc as cs
import src.application.use_cases.generate_sustainability_report_uc as gsr
import src.application.use_cases.get_farm_status_uc as gfs
import src.application.use_cases.predict_sector_stress_uc as pss
import src.application.use_cases.toggle_sector_occupancy_uc as tso
import src.infrastructure.notifications.telegram_notifier_adapter as tg_mod
import src.infrastructure.persistence.sqlite_weather_cache_adapter as cache_mod
import src.infrastructure.reporting.pdf_sustainability_report_adapter as pdf_mod
import src.infrastructure.repositories.in_memory_sector_repo as repo_mod
from src.domain.ports.sector_repository_port import ISectorRepository
from src.domain.ports.weather_provider_port import IWeatherProvider
from src.infrastructure.hardware.mock_relay_adapter import MockRelayAdapter
from src.infrastructure.ml.sklearn_predictor_adapter import SklearnPredictorAdapter
from src.infrastructure.weather_api import mock_weather_adapter, open_meteo_adapter

CoreUseCasesTuple = tuple[
    IWeatherProvider,
    pss.PredictSectorStressUseCase,
    cs.CalculateSavingsUseCase,
    tso.ToggleSectorOccupancyUseCase,
    gfs.GetFarmStatusUseCase,
    gsr.GenerateSustainabilityReportUseCase,
]


def build_core_use_cases(
    force_heatwave: bool = False, sector_repo: ISectorRepository | None = None
) -> CoreUseCasesTuple:
    """Construye el grafo compartido de casos de uso del núcleo."""
    use_mock = force_heatwave or os.getenv("WEATHER_PROVIDER", "open_meteo") == "mock"
    heatwave = mock_weather_adapter.MockWeatherAdapter("heatwave")
    weather: IWeatherProvider = (
        heatwave if use_mock else open_meteo_adapter.OpenMeteoAdapter()
    )
    cache = cache_mod.SqliteWeatherCacheAdapter()
    if not cache.is_cache_valid():
        cache.save_forecast(heatwave.get_hourly_forecast(-31.25, -61.48))
    repo = sector_repo or repo_mod.InMemorySectorRepository()
    predictor = SklearnPredictorAdapter()
    notifier = tg_mod.TelegramNotifierAdapter()
    relay = MockRelayAdapter()
    savings_uc = cs.CalculateSavingsUseCase()
    predict_uc = pss.PredictSectorStressUseCase(
        weather, repo, predictor, notifier, relay, cache
    )
    toggle_uc = tso.ToggleSectorOccupancyUseCase(repo)
    status_uc = gfs.GetFarmStatusUseCase(repo, weather)
    pdf_adapter = pdf_mod.PdfSustainabilityReportAdapter()
    report_uc = gsr.GenerateSustainabilityReportUseCase(pdf_adapter, savings_uc)
    return (weather, predict_uc, savings_uc, toggle_uc, status_uc, report_uc)
