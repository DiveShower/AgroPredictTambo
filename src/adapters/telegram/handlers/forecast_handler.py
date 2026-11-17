"""Handler para el comando /pronostico del bot de Telegram."""

from src.adapters.telegram.formatters.message_formatter import TelegramMessageFormatter
from src.domain.ports.weather_provider_port import IWeatherProvider


class ForecastHandler:
    """Gestiona el comando /pronostico consultando el pronóstico horario 24h."""

    def __init__(
        self,
        weather_provider: IWeatherProvider,
        lat: float = -31.25,
        lon: float = -61.48,
    ) -> None:
        """Inicializa el handler con el proveedor meteorológico y coordenadas."""
        self._weather_provider = weather_provider
        self._lat = lat
        self._lon = lon

    def handle(self) -> str:
        """Consulta el pronóstico horario de 24 horas y lo formatea para Telegram."""
        forecast = self._weather_provider.get_hourly_forecast(
            self._lat,
            self._lon,
            hours=24,
        )
        return TelegramMessageFormatter.format_forecast_24h(forecast)
