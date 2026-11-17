"""Tests unitarios para CoolingOrder y CoolingCycle (micro-ciclos y anti-mastitis)."""

from datetime import datetime

import pytest

from src.domain.entities.cooling_order import CoolingOrder
from src.domain.value_objects.cooling_cycle import CoolingCycle


def test_cooling_cycle_parameters_and_duty_cycle() -> None:
    cycle = CoolingCycle()

    assert cycle.total_cycle_seconds == 310
    assert cycle.cycles_per_hour == pytest.approx(3600.0 / 310.0, rel=1e-4)
    assert cycle.water_duty_cycle == pytest.approx(40.0 / 310.0, rel=1e-4)
    assert cycle.active_water_minutes_per_hour == pytest.approx(7.7419, abs=0.01)


def test_cooling_cycle_for_stress_levels_and_anti_mastitis() -> None:
    comfort = CoolingCycle.for_stress_level(0, allows_water_sprinkling=True)
    alert = CoolingCycle.for_stress_level(1, allows_water_sprinkling=True)
    danger_concrete = CoolingCycle.for_stress_level(2, allows_water_sprinkling=True)
    danger_compost = CoolingCycle.for_stress_level(2, allows_water_sprinkling=False)

    assert (comfort.water_mist_seconds, comfort.fan_ventilation_seconds) == (0, 0)
    assert comfort.water_duty_cycle == 0.0
    assert (alert.water_mist_seconds, alert.fan_ventilation_seconds) == (0, 270)
    assert (
        danger_concrete.water_mist_seconds,
        danger_concrete.fan_ventilation_seconds,
    ) == (40, 270)
    assert (
        danger_compost.water_mist_seconds,
        danger_compost.fan_ventilation_seconds,
    ) == (0, 270)


def test_cooling_order_is_active_flag() -> None:
    now = datetime(2026, 1, 15, 14, 0)
    inactive = CoolingOrder("corral_espera", 0, 0, 0, now, "En confort")
    active = CoolingOrder("corral_espera", 2, 40, 270, now, "Peligro térmico")

    assert inactive.is_active is False
    assert active.is_active is True
