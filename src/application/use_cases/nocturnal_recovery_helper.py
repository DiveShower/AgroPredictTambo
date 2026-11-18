"""Cálculo de horas frescas de recuperación nocturna según ITH."""

from collections.abc import Sequence

from src.domain.value_objects.nocturnal_recovery import NocturnalRecovery
from src.domain.value_objects.thi_score import THI_Score
from src.domain.value_objects.weather_conditions import WeatherConditions


def compute_nocturnal_recovery(
    fore: Sequence[WeatherConditions],
) -> NocturnalRecovery:
    """Calcula la recuperación nocturna a partir de la ventana 21h-06h."""
    night = [c for c in fore if c.timestamp.hour >= 21 or c.timestamp.hour < 6][:6]
    warm = sum(
        1
        for c in night
        if THI_Score.calculate(c.temperature_c, c.relative_humidity).value >= 65.0
    )
    return NocturnalRecovery(cool_hours_count=max(0, 6 - warm))
