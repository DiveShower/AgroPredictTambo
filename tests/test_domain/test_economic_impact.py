"""Tests unitarios para EconomicImpact (SIGLeA) y CarbonFootprint (CAMMESA)."""

import pytest

from src.domain.value_objects.carbon_footprint import CarbonFootprint
from src.domain.value_objects.economic_impact import EconomicImpact


def test_economic_impact_proportional_hours_and_daily_cap() -> None:
    # 100 vacas, 2h de alerta (0.30 L) + 4h de peligro (1.40 L) = 1.70 L/vaca -> 170 L
    impact = EconomicImpact.calculate(
        cow_count=100,
        hours_alert_mitigated=2,
        hours_danger_mitigated=4,
        milk_price_ars=430.0,
    )
    assert impact.milk_protected_liters == pytest.approx(170.0)
    assert impact.economic_return_ars == pytest.approx(73100.0)

    # Día extremo (12h peligro -> 4.20 L teóricos -> tope biológico 4.0 L/vaca)
    capped = EconomicImpact.calculate(
        cow_count=100,
        hours_alert_mitigated=2,
        hours_danger_mitigated=12,
        milk_price_ars=430.0,
    )
    assert capped.milk_protected_liters == pytest.approx(400.0)
    assert capped.economic_return_ars == pytest.approx(172000.0)


def test_carbon_footprint_cammesa_factor() -> None:
    footprint = CarbonFootprint.from_energy_savings(energy_saved_kwh=100.0)

    assert footprint.emission_factor_kg_per_kwh == 0.35
    assert footprint.co2_avoided_kg == pytest.approx(35.0)
