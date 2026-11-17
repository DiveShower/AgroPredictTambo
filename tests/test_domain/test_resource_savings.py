"""Tests unitarios para ResourceSavings (ahorro hídrico y energético)."""

import pytest

from src.domain.value_objects.resource_savings import ResourceSavings


def test_resource_savings_computes_software_and_combined_savings() -> None:
    # Ejemplo 8h fijas con 25 aspersores (1.3 L/min opt vs 4.9 L/min trad)
    # Software tradicional: 8h * 60m * 0.5 duty = 240 min -> 25 * 1.3 * 240 = 7800 L
    # Legacy 4.9 L/min: 25 * 4.9 * 240 = 29400 L
    # Predictivo sectorizado: 4h de estrés Nivel 2 en corral ocupado (7.74 min/h) -> ~2500 L
    savings = ResourceSavings.calculate(
        baseline_water_liters=7800.0,
        predictive_water_liters=2500.0,
        legacy_nozzle_water_liters=29400.0,
        baseline_energy_kwh=60.0,
        predictive_energy_kwh=24.0,
    )

    assert savings.water_saved_liters == pytest.approx(5300.0)
    assert savings.water_saved_pct == pytest.approx(67.95, abs=0.05)
    assert savings.combined_water_saved_pct == pytest.approx(91.50, abs=0.05)
    assert savings.energy_saved_kwh == pytest.approx(36.0)
    assert savings.energy_saved_pct == pytest.approx(60.0)


def test_resource_savings_handles_zero_baseline_safely() -> None:
    savings = ResourceSavings.calculate(
        baseline_water_liters=0.0,
        predictive_water_liters=0.0,
        legacy_nozzle_water_liters=0.0,
        baseline_energy_kwh=0.0,
        predictive_energy_kwh=0.0,
    )

    assert savings.water_saved_pct == 0.0
    assert savings.combined_water_saved_pct == 0.0
    assert savings.energy_saved_pct == 0.0
