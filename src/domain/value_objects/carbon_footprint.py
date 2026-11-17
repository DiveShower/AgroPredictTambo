"""Value Object para conversión de ahorro eléctrico a huella de carbono evitada."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CarbonFootprint:
    """Cuantifica emisiones de CO2e evitadas según factor oficial de CAMMESA."""

    energy_saved_kwh: float
    co2_avoided_kg: float
    emission_factor_kg_per_kwh: float = 0.35

    @classmethod
    def from_energy_savings(
        cls,
        energy_saved_kwh: float,
        factor: float = 0.35,
    ) -> "CarbonFootprint":
        """Calcula los kilogramos de CO2e evitados a partir de kWh ahorrados."""
        safe_kwh = max(0.0, energy_saved_kwh)
        avoided = round(safe_kwh * factor, 2)
        return cls(
            energy_saved_kwh=round(safe_kwh, 2),
            co2_avoided_kg=avoided,
            emission_factor_kg_per_kwh=factor,
        )
