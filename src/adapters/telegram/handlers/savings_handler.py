"""Handler para el comando /ahorro del bot de Telegram."""

from src.adapters.telegram.formatters.message_formatter import TelegramMessageFormatter
from src.application.use_cases.calculate_savings_uc import CalculateSavingsUseCase


class SavingsHandler:
    """Gestiona el comando /ahorro calculando el ahorro hídrico, energético y ESG."""

    def __init__(self, savings_uc: CalculateSavingsUseCase) -> None:
        """Inicializa el handler con el caso de uso de cálculo de ahorros."""
        self._savings_uc = savings_uc

    def handle(self) -> str:
        """Ejecuta el cálculo de ahorro y formatea el resumen para Telegram."""
        response = self._savings_uc.execute()
        return TelegramMessageFormatter.format_savings(response)
