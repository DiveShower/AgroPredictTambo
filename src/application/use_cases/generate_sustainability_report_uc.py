"""Caso de uso para la emisión del reporte formal de sustentabilidad ESG."""

from datetime import datetime
from typing import Optional

from src.application.dtos.calculate_savings_request_dto import (
    CalculateSavingsRequestDTO,
)
from src.application.dtos.sustainability_report_dto import (
    SustainabilityReportDTO,
)
from src.application.use_cases.calculate_savings_uc import (
    CalculateSavingsUseCase,
)
from src.domain.ports.report_generator_port import IReportGenerator


class GenerateSustainabilityReportUseCase:
    """Orquesta la auditoría analítica y exportación del informe en PDF."""

    def __init__(
        self,
        report_generator: IReportGenerator,
        savings_use_case: Optional[CalculateSavingsUseCase] = None,
    ) -> None:
        self._report_gen = report_generator
        self._savings_uc = savings_use_case or CalculateSavingsUseCase()

    def execute(
        self,
        farm_name: str,
        output_path: str,
        request: Optional[CalculateSavingsRequestDTO] = None,
    ) -> SustainabilityReportDTO:
        """Calcula métricas de ahorro y solicita la renderización del documento."""
        req = request or CalculateSavingsRequestDTO()
        savings_dto = self._savings_uc.execute(req)
        pdf_path = self._report_gen.generate_sustainability_pdf(
            farm_name=farm_name,
            savings=savings_dto.savings,
            output_path=output_path,
        )

        return SustainabilityReportDTO(
            farm_name=farm_name,
            generated_at=datetime.now(),
            savings=savings_dto.savings,
            carbon_footprint=savings_dto.carbon_footprint,
            economic_impact=savings_dto.economic_impact,
            pdf_file_path=pdf_path,
        )
