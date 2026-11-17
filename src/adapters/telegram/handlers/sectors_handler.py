"""Handler para el comando /sectores del bot de Telegram."""

from src.adapters.telegram.formatters.message_formatter import TelegramMessageFormatter
from src.application.use_cases.get_farm_status_uc import GetFarmStatusUseCase


class SectorsHandler:
    """Gestiona el comando /sectores consultando el estado operativo del tambo."""

    def __init__(
        self,
        status_uc: GetFarmStatusUseCase,
        latitude: float = -31.25,
        longitude: float = -61.48,
    ) -> None:
        """Inicializa el handler con el caso de uso de estado y coordenadas."""
        self._status_uc = status_uc
        self._lat = latitude
        self._lon = longitude

    def handle(self) -> str:
        """Consulta el estado de los sectores y lo formatea para Telegram."""
        sectors = self._status_uc.execute(self._lat, self._lon)
        return TelegramMessageFormatter.format_sectors(sectors)
