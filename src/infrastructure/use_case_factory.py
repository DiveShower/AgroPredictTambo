"""Fábrica compartida de casos de uso del núcleo basada en AppContainer."""

import src.application.use_cases.calculate_savings_uc as cs
import src.application.use_cases.generate_sustainability_report_uc as gsr
import src.application.use_cases.get_farm_status_uc as gfs
import src.application.use_cases.predict_sector_stress_uc as pss
import src.application.use_cases.toggle_sector_occupancy_uc as tso
from src.domain.ports.sector_repository_port import ISectorRepository
from src.domain.ports.weather_provider_port import IWeatherProvider
from src.infrastructure.ioc_container import AppContainer

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
    c = AppContainer(force_heatwave=force_heatwave, sector_repo=sector_repo)
    return (
        c.weather,
        c.predict_uc,
        c.savings_uc,
        c.toggle_uc,
        c.status_uc,
        c.report_uc,
    )
