"""Value Object inmutable para el Índice de Temperatura y Humedad (ITH/THI)."""

from dataclasses import dataclass


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
        rounded_val = round(val, 2)
        if rounded_val < threshold_alert:
            level = 0
        elif rounded_val < threshold_danger:
            level = 1
        else:
            level = 2
        return cls(value=rounded_val, stress_level=level)

    @property
    def category_name(self) -> str:
        """Devuelve la etiqueta descriptiva correspondiente al nivel de estrés."""
        labels = {0: "Confort", 1: "Alerta Leve", 2: "Peligro"}
        return labels.get(self.stress_level, "Desconocido")
