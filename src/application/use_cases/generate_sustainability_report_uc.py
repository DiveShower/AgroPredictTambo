"""Caso de uso para la emisión del reporte formal de sustentabilidad ESG."""

from datetime import datetime

from src.application.dtos.calculate_savings_request_dto import (
    CalculateSavingsRequestDTO,
)
from src.application.dtos.sustainability_report_dto import SustainabilityReportDTO
from src.application.use_cases import report_audit_helper as audit_helper
from src.application.use_cases.calculate_savings_uc import CalculateSavingsUseCase
from src.domain.ports.report_generator_port import IReportGenerator
from src.domain.ports.sector_repository_port import ISectorRepository
from src.domain.ports.weather_provider_port import IWeatherProvider


class GenerateSustainabilityReportUseCase:
    """Orquesta la auditoría analítica y exportación del informe en PDF."""

    def __init__(
        self,
        report_generator: IReportGenerator,
        savings_use_case: CalculateSavingsUseCase | None = None,
        sector_repository: ISectorRepository | None = None,
        weather_provider: IWeatherProvider | None = None,
    ) -> None:
        self._report_gen = report_generator
        self._savings_uc = savings_use_case or CalculateSavingsUseCase()
        self._sector_repo = sector_repository
        self._weather = weather_provider

    def execute(
        self,
        farm_name: str,
        output_path: str,
        request: CalculateSavingsRequestDTO | None = None,
        latitude: float = -31.25,
        longitude: float = -61.48,
    ) -> SustainabilityReportDTO:
        """Calcula métricas ESG y solicita la renderización del PDF."""
        now = datetime.now()
        sav = self._savings_uc.execute(request or CalculateSavingsRequestDTO())
        cf, eco = sav.carbon_footprint, sav.economic_impact
        sectors = audit_helper.collect_report_sectors(self._sector_repo)
        audit = audit_helper.build_report_audit_context(
            self._weather, latitude, longitude, now
        )
        pdf = self._report_gen.generate_sustainability_pdf(
            farm_name=farm_name,
            savings=sav.savings,
            output_path=output_path,
            carbon_footprint=cf,
            economic_impact=eco,
            sectors=sectors,
            audit_context=audit,
        )
        return SustainabilityReportDTO(
            farm_name, now, sav.savings, cf, eco, pdf, sectors, audit
        )
