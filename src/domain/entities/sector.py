"""Entidad Sector que modela una zona física independiente del tambo."""

from dataclasses import dataclass


@dataclass
class Sector:
    """Zona operativa del tambo con ocupación, umbrales y reglas sanitarias."""

    sector_id: str
    name: str
    cow_capacity: int
    current_occupancy: bool
    thi_threshold_alert: float = 72.0
    thi_threshold_danger: float = 78.0
    allows_water_sprinkling: bool = True
    sprinkler_count: int = 10
    fan_count: int = 4

    def set_occupancy(self, occupied: bool) -> None:
        """Actualiza el estado de presencia animal en el sector."""
        self.current_occupancy = occupied

    def effective_alert_threshold(self, nocturnal_penalty: float = 0.0) -> float:
        """Calcula el umbral de alerta ajustado por deuda térmica nocturna."""
        return round(self.thi_threshold_alert - max(0.0, nocturnal_penalty), 2)

    def effective_danger_threshold(self, nocturnal_penalty: float = 0.0) -> float:
        """Calcula el umbral de peligro ajustado por deuda térmica nocturna."""
        return round(self.thi_threshold_danger - max(0.0, nocturnal_penalty), 2)

    def evaluate_stress_level(
        self, thi_val: float, nocturnal_penalty: float = 0.0
    ) -> int:
        """Clasifica el nivel de estrés (0, 1 o 2) según los umbrales del sector."""
        if thi_val < self.effective_alert_threshold(nocturnal_penalty):
            return 0
        if thi_val < self.effective_danger_threshold(nocturnal_penalty):
            return 1
        return 2

    def requires_cooling(self, thi_val: float, nocturnal_penalty: float = 0.0) -> bool:
        """Determina si el sector ocupado requiere activación de refrigeración."""
        return (
            self.current_occupancy
            and self.evaluate_stress_level(thi_val, nocturnal_penalty) > 0
        )
