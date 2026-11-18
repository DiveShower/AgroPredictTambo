"""Controlador delgado CLI que rutea comandos hacia los Casos de Uso."""

from src.adapters.cli import cli_formatter as fmt
from src.adapters.cli.benchmark_exporter import export_benchmark_telemetry
from src.application.dtos import calculate_savings_request_dto as s_dto
from src.application.dtos.predict_stress_request_dto import PredictStressRequestDTO
from src.application.use_cases import generate_sustainability_report_uc as r_uc
from src.application.use_cases import predict_sector_stress_uc as p_uc
from src.application.use_cases import toggle_sector_occupancy_uc as t_uc
from src.application.use_cases.calculate_savings_uc import CalculateSavingsUseCase
from src.application.use_cases.get_farm_status_uc import GetFarmStatusUseCase


class CliController:
    """Orquesta las acciones de terminal delegando en la capa de Aplicación."""

    def __init__(
        self,
        predict_uc: p_uc.PredictSectorStressUseCase,
        savings_uc: CalculateSavingsUseCase,
        toggle_uc: t_uc.ToggleSectorOccupancyUseCase,
        status_uc: GetFarmStatusUseCase,
        report_uc: r_uc.GenerateSustainabilityReportUseCase | None = None,
    ) -> None:
        self._predict, self._savings = predict_uc, savings_uc
        self._toggle, self._status = toggle_uc, status_uc
        self._report = report_uc

    def handle_status(self, lat: float = -31.25, lon: float = -61.48) -> str:
        return fmt.format_farm_status(self._status.execute(lat, lon))

    def handle_occupy(self, sector_id: str, is_occupied: bool) -> str:
        sec = self._toggle.execute(sector_id, is_occupied)
        estado = "OCUPADO" if sec.current_occupancy else "VACIO"
        return f"Sector '{sec.sector_id}' actualizado a: {estado}"

    def handle_predict(
        self, lead_hours: int = 1, lat: float = -31.25, lon: float = -61.48
    ) -> str:
        dto = PredictStressRequestDTO(lat, lon, forecast_lead_hours=lead_hours)
        return fmt.format_prediction_response(self._predict.execute(dto))

    def handle_savings(self, active_hours: float = 3.5, cows: int = 100) -> str:
        dto = s_dto.CalculateSavingsRequestDTO(
            predictive_active_hours=active_hours, cow_count=cows
        )
        return fmt.format_savings_response(self._savings.execute(dto))

    def handle_benchmark(
        self, lat: float = -31.25, lon: float = -61.48, export_path: str | None = None
    ) -> str:
        st = self.handle_status(lat, lon)
        pr = self.handle_predict(1, lat, lon)
        sv = self.handle_savings()
        if export_path:
            d = {"lat": lat, "lon": lon, "status": st, "prediction": pr, "savings": sv}
            export_benchmark_telemetry(d, export_path)
        return f"{st}\n\n{pr}\n\n{sv}"
