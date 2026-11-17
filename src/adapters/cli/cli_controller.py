"""Controlador delgado CLI que rutea comandos hacia los Casos de Uso."""

from typing import Optional
from src.adapters.cli.cli_formatter import (
    format_farm_status,
    format_prediction_response,
    format_savings_response,
)
from src.application.dtos.calculate_savings_request_dto import CalculateSavingsRequestDTO
from src.application.dtos.predict_stress_request_dto import PredictStressRequestDTO
from src.application.use_cases.calculate_savings_uc import CalculateSavingsUseCase
from src.application.use_cases.generate_sustainability_report_uc import (
    GenerateSustainabilityReportUseCase,
)
from src.application.use_cases.get_farm_status_uc import GetFarmStatusUseCase
from src.application.use_cases.predict_sector_stress_uc import PredictSectorStressUseCase
from src.application.use_cases.toggle_sector_occupancy_uc import (
    ToggleSectorOccupancyUseCase,
)


class CliController:
    """Orquesta las acciones de terminal delegando en la capa de Aplicación."""

    def __init__(
        self,
        predict_uc: PredictSectorStressUseCase,
        savings_uc: CalculateSavingsUseCase,
        toggle_uc: ToggleSectorOccupancyUseCase,
        status_uc: GetFarmStatusUseCase,
        report_uc: Optional[GenerateSustainabilityReportUseCase] = None,
    ) -> None:
        self._predict, self._savings = predict_uc, savings_uc
        self._toggle, self._status = toggle_uc, status_uc
        self._report = report_uc

    def handle_status(self, lat: float = -31.25, lon: float = -61.48) -> str:
        return format_farm_status(self._status.execute(lat, lon))

    def handle_occupy(self, sector_id: str, is_occupied: bool) -> str:
        sec = self._toggle.execute(sector_id, is_occupied)
        estado = "OCUPADO" if sec.current_occupancy else "VACIO"
        return f"Sector '{sec.sector_id}' actualizado a: {estado}"

    def handle_predict(self, lead_hours: int = 1, lat: float = -31.25, lon: float = -61.48) -> str:
        resp = self._predict.execute(PredictStressRequestDTO(lat, lon, forecast_lead_hours=lead_hours))
        return format_prediction_response(resp)

    def handle_savings(self, active_hours: float = 3.5, cows: int = 100) -> str:
        resp = self._savings.execute(CalculateSavingsRequestDTO(predictive_active_hours=active_hours, cow_count=cows))
        return format_savings_response(resp)

    def handle_benchmark(self, lat: float = -31.25, lon: float = -61.48) -> str:
        return "\n\n".join([self.handle_status(lat, lon), self.handle_predict(1, lat, lon), self.handle_savings()])
