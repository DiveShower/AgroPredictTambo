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
        water_saved = max(0.0, baseline_water_liters - predictive_water_liters)
        water_pct = (
            (water_saved / baseline_water_liters) * 100.0
            if baseline_water_liters > 0.0
            else 0.0
        )

        combined_saved = max(0.0, legacy_nozzle_water_liters - predictive_water_liters)
        combined_pct = (
            (combined_saved / legacy_nozzle_water_liters) * 100.0
            if legacy_nozzle_water_liters > 0.0
            else 0.0
        )

        energy_saved = max(0.0, baseline_energy_kwh - predictive_energy_kwh)
        energy_pct = (
            (energy_saved / baseline_energy_kwh) * 100.0
            if baseline_energy_kwh > 0.0
            else 0.0
        )

        return cls(
            baseline_water_liters=round(baseline_water_liters, 2),
            predictive_water_liters=round(predictive_water_liters, 2),
            water_saved_liters=round(water_saved, 2),
            water_saved_pct=round(water_pct, 2),
            legacy_nozzle_water_liters=round(legacy_nozzle_water_liters, 2),
            combined_water_saved_pct=round(combined_pct, 2),
            baseline_energy_kwh=round(baseline_energy_kwh, 2),
            predictive_energy_kwh=round(predictive_energy_kwh, 2),
            energy_saved_kwh=round(energy_saved, 2),
            energy_saved_pct=round(energy_pct, 2),
        )
