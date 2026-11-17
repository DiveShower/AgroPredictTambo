"""Fachada de formateo de mensajes móviles para el bot de Telegram."""

from collections.abc import Sequence

from src.adapters.telegram.formatters.sector_and_savings_formatter import (
    format_orders_summary,
    format_savings_summary,
    format_sectors_table,
    stress_badge,
)
from src.application.dtos.calculate_savings_response_dto import (
    CalculateSavingsResponseDTO,
)
from src.application.dtos.predict_stress_response_dto import PredictStressResponseDTO
from src.application.dtos.sector_status_dto import SectorStatusDTO
from src.domain.value_objects.thi_score import THI_Score
from src.domain.value_objects.weather_conditions import WeatherConditions


class TelegramMessageFormatter:
    """Formatea respuestas del dominio y casos de uso para Telegram."""

    @staticmethod
    def format_welcome() -> str:
        """Retorna bienvenida y comandos disponibles del bot."""
        return "🐄 Tambo San José — AgroChallenge 2026 (Nestlé Conecta)\nComandos: /estado, /pronostico, /sectores, /ocupar <id> <true/false>, /prediccion, /ahorro, /reporte"

    @staticmethod
    def format_current_state(conditions: WeatherConditions, thi: THI_Score) -> str:
        """Formatea clima actual e índice ITH NRC."""
        return f"🌤️ Estado Actual ({conditions.timestamp:%H:%M})\nTemp: {conditions.temperature_c:.1f} °C | HR: {conditions.relative_humidity:.0f}% | Viento: {conditions.wind_speed_kmh:.1f} km/h | Rad: {conditions.solar_radiation_wm2:.0f} W/m2\nITH NRC: {thi.value:.2f} — {stress_badge(thi.stress_level)}"

    @staticmethod
    def format_forecast_24h(forecast: Sequence[WeatherConditions]) -> str:
        """Formatea pronóstico de hasta 24h en bloque monoespaciado."""
        if not forecast:
            return "📅 Pronóstico 24h: sin datos disponibles."
        rows = ["Hora  Temp  HR%  ITH   Estado"]
        for w in forecast[:24]:
            t = THI_Score.calculate(w.temperature_c, w.relative_humidity)
            row = f"{w.timestamp:%H:%M} {w.temperature_c:4.1f}° {w.relative_humidity:3.0f}% {t.value:5.1f} {stress_badge(t.stress_level).split()[0]} {'█' * max(1, min(8, round((t.value - 54) / 4)))}"
            rows.append(row)
        return "📅 Pronóstico 24h\n```\n" + "\n".join(rows) + "\n```"

    @staticmethod
    def format_sectors(sectors: Sequence[SectorStatusDTO]) -> str:
        """Delega el formateo del estado de sectores."""
        return format_sectors_table(sectors)

    @staticmethod
    def format_prediction(response: PredictStressResponseDTO) -> str:
        """Delega el formateo de predicción y órdenes."""
        return format_orders_summary(response)

    @staticmethod
    def format_savings(response: CalculateSavingsResponseDTO) -> str:
        """Delega el formateo de ahorro hídrico, energético y ESG."""
        return format_savings_summary(response)
