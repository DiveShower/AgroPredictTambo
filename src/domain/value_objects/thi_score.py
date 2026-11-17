"""Value Object inmutable para el Índice de Temperatura y Humedad (ITH/THI)."""

from collections.abc import Sequence
from dataclasses import dataclass

from src.domain.value_objects.weather_conditions import WeatherConditions


@dataclass(frozen=True)
class THI_Score:
    """Resultado numérico del ITH (fórmula NRC/Thom) y su categoría de estrés."""

    value: float
    stress_level: int

    @classmethod
    def calculate(
        cls,
        temp_c: float,
        rh: float,
        threshold_alert: float = 72.0,
        threshold_danger: float = 78.0,
    ) -> "THI_Score":
        """Calcula el ITH en Celsius y clasifica el nivel de estrés (0, 1 o 2)."""
        val = (1.8 * temp_c + 32.0) - ((0.55 - 0.0055 * rh) * (1.8 * temp_c - 26.0))
        rounded = round(val, 2)
        level = (
            0 if rounded < threshold_alert else (1 if rounded < threshold_danger else 2)
        )
        return cls(value=rounded, stress_level=level)

    @classmethod
    def rolling_average(
        cls,
        current: WeatherConditions,
        recent_history: Sequence[WeatherConditions] = (),
        window: int = 3,
    ) -> float:
        """Calcula el promedio móvil de ITH sobre las últimas observaciones previas."""
        samples = recent_history[-window:] if recent_history else (current,)
        values = [
            cls.calculate(obs.temperature_c, obs.relative_humidity).value
            for obs in samples
        ]
        return round(sum(values) / len(values), 2)

    @property
    def category_name(self) -> str:
        """Devuelve la etiqueta descriptiva correspondiente al nivel de estrés."""
        labels = {0: "Confort", 1: "Alerta Leve", 2: "Peligro"}
        return labels.get(self.stress_level, "Desconocido")
