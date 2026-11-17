"""Handler para el comando /estado del bot de Telegram."""

from src.adapters.telegram.formatters.message_formatter import TelegramMessageFormatter
from src.application.use_cases.predict_sector_stress_uc import (
    PredictSectorStressUseCase,
)
from src.domain.value_objects.thi_score import THI_Score


class StateHandler:
    """Gestiona el comando /estado consultando condiciones climáticas actuales."""

    def __init__(self, predict_uc: PredictSectorStressUseCase) -> None:
        """Inicializa el handler con el caso de uso de predicción de estrés."""
        self._predict_uc = predict_uc

    def handle(self) -> str:
        """Ejecuta el caso de uso y formatea el estado climático actual e ITH."""
        response = self._predict_uc.execute()
        thi = THI_Score.calculate(
            response.current_conditions.temperature_c,
            response.current_conditions.relative_humidity,
        )
        return TelegramMessageFormatter.format_current_state(
            response.current_conditions,
            thi,
        )
