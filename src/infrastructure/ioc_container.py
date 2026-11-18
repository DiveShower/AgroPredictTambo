"""Contenedor de Inversión de Control (IoC) para cableado de casos de uso."""

from src.application.dtos.stress_actuation_context import StressActuationContext
from src.application.use_cases.calculate_savings_uc import CalculateSavingsUseCase
from src.application.use_cases.generate_sustainability_report_uc import (
    GenerateSustainabilityReportUseCase,
)
from src.application.use_cases.get_farm_status_uc import GetFarmStatusUseCase
from src.application.use_cases.predict_sector_stress_uc import (
    PredictSectorStressUseCase,
)
from src.application.use_cases.toggle_sector_occupancy_uc import (
    ToggleSectorOccupancyUseCase,
)
from src.domain.ports.sector_repository_port import ISectorRepository
from src.infrastructure.hardware.mock_relay_adapter import MockRelayAdapter
from src.infrastructure.ioc_weather_resolver import resolve_weather_and_cache
from src.infrastructure.ml.sklearn_predictor_adapter import (
    SklearnPredictorAdapter,
)
from src.infrastructure.notifications.telegram_notifier_adapter import (
    TelegramNotifierAdapter,
)
from src.infrastructure.reporting.pdf_sustainability_report_adapter import (
    PdfSustainabilityReportAdapter,
)
from src.infrastructure.repositories.in_memory_sector_repo import (
    InMemorySectorRepository,
)


class AppContainer:
    """Ensambla puertos y casos de uso según entorno y configuración."""

    def __init__(
        self,
        force_heatwave: bool = False,
        sector_repo: ISectorRepository | None = None,
    ) -> None:
        self.weather, self.cache = resolve_weather_and_cache(force_heatwave)
        self.repo = sector_repo or InMemorySectorRepository()
        self.predictor = SklearnPredictorAdapter()
        self.notifier = TelegramNotifierAdapter()
        self.relay = MockRelayAdapter()
        self.actuation_ctx = StressActuationContext(
            self.notifier, self.relay, self.cache
        )
        self.predict_uc = PredictSectorStressUseCase(
            self.weather, self.repo, self.predictor, context=self.actuation_ctx
        )
        self.savings_uc = CalculateSavingsUseCase()
        self.toggle_uc = ToggleSectorOccupancyUseCase(self.repo)
        self.status_uc = GetFarmStatusUseCase(self.repo, self.weather)
        self.report_uc = GenerateSustainabilityReportUseCase(
            PdfSustainabilityReportAdapter(), self.savings_uc
        )
