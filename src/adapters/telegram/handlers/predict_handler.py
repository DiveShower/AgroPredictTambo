"""Handler para el comando /prediccion del bot de Telegram."""

from src.adapters.telegram.formatters.message_formatter import TelegramMessageFormatter
from src.application.dtos.predict_stress_request_dto import PredictStressRequestDTO
from src.application.use_cases.predict_sector_stress_uc import (
    PredictSectorStressUseCase,
)


class PredictHandler:
    """Gestiona el comando /prediccion evaluando estrés térmico y órdenes por sector."""

    def __init__(self, predict_uc: PredictSectorStressUseCase) -> None:
        """Inicializa el handler con el caso de uso de predicción de estrés."""
        self._predict_uc = predict_uc

    def handle(self) -> str:
        """Ejecuta la predicción a 1 hora y formatea órdenes y alertas para Telegram."""
        response = self._predict_uc.execute(
            PredictStressRequestDTO(forecast_lead_hours=1)
        )
        return TelegramMessageFormatter.format_prediction(response)
