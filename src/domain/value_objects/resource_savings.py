"""Value Object para cuantificación comparativa de ahorro de agua y energía."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ResourceSavings:
    """Balance comparativo entre el sistema tradicional (8h fijas) y el predictivo."""

    baseline_water_liters: float
    predictive_water_liters: float
    water_saved_liters: float
    water_saved_pct: float
    legacy_nozzle_water_liters: float
    combined_water_saved_pct: float
    baseline_energy_kwh: float
    predictive_energy_kwh: float
    energy_saved_kwh: float
    energy_saved_pct: float

    @staticmethod
    def _delta_and_pct(baseline: float, current: float) -> tuple[float, float]:
        saved = max(0.0, baseline - current)
        pct = (saved / baseline) * 100.0 if baseline > 0.0 else 0.0
        return round(saved, 2), round(pct, 2)

    @classmethod
    def calculate(
        cls,
        baseline_water_liters: float,
        predictive_water_liters: float,
        legacy_nozzle_water_liters: float,
        baseline_energy_kwh: float,
        predictive_energy_kwh: float,
    ) -> "ResourceSavings":
        """Calcula ahorros absolutos y porcentuales evitando divisiones por cero."""
        water_saved, water_pct = cls._delta_and_pct(
            baseline_water_liters, predictive_water_liters
        )
        _, combined_pct = cls._delta_and_pct(
            legacy_nozzle_water_liters, predictive_water_liters
        )
        energy_saved, energy_pct = cls._delta_and_pct(
            baseline_energy_kwh, predictive_energy_kwh
        )
        return cls(
            baseline_water_liters=round(baseline_water_liters, 2),
            predictive_water_liters=round(predictive_water_liters, 2),
            water_saved_liters=water_saved,
            water_saved_pct=water_pct,
            legacy_nozzle_water_liters=round(legacy_nozzle_water_liters, 2),
            combined_water_saved_pct=combined_pct,
            baseline_energy_kwh=round(baseline_energy_kwh, 2),
            predictive_energy_kwh=round(predictive_energy_kwh, 2),
            energy_saved_kwh=energy_saved,
            energy_saved_pct=energy_pct,
        )
