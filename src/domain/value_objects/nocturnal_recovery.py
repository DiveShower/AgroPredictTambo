"""Value Object para recuperación térmica nocturna y deuda calórica acumulada."""

from collections.abc import Sequence
from dataclasses import dataclass

from src.domain.value_objects.thi_score import THI_Score
from src.domain.value_objects.weather_conditions import WeatherConditions


@dataclass(frozen=True)
class NocturnalRecovery:
    """Evalúa las horas nocturnas frescas y determina la penalización de umbrales."""

    cool_hours_count: int
    required_cool_hours: int = 6
    thi_recovery_limit: float = 65.0

    @property
    def debt_hours(self) -> int:
        """Cantidad de horas frescas faltantes respecto al mínimo fisiológico."""
        return max(0, self.required_cool_hours - self.cool_hours_count)

    @property
    def has_thermal_debt(self) -> bool:
        """Indica si el rodeo inicia la jornada con deuda térmica acumulada."""
        return self.debt_hours > 0

    @property
    def threshold_penalty(self) -> float:
        """Reducción de umbral diurno en puntos de ITH (0.5 por hora faltante, máx 3.0)."""
        return round(min(3.0, self.debt_hours * 0.5), 2)

    @classmethod
    def from_night_conditions(
        cls,
        night_conditions: Sequence[WeatherConditions],
        thi_recovery_limit: float = 65.0,
    ) -> "NocturnalRecovery":
        """Computa la recuperación nocturna contando horas con ITH menor al límite."""
        cool_hours = sum(
            1
            for cond in night_conditions
            if THI_Score.calculate(cond.temperature_c, cond.relative_humidity).value
            < thi_recovery_limit
        )
        return cls(cool_hours_count=cool_hours, thi_recovery_limit=thi_recovery_limit)
