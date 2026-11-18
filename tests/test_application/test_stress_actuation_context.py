"""Pruebas unitarias para el DTO StressActuationContext."""

from dataclasses import FrozenInstanceError, is_dataclass

import pytest

from src.application.dtos.stress_actuation_context import StressActuationContext
from src.domain.value_objects.milking_schedule import MilkingSchedule


def test_stress_actuation_context_defaults() -> None:
    ctx = StressActuationContext()
    assert is_dataclass(ctx)
    assert ctx.notifier is None
    assert ctx.hardware_controller is None
    assert ctx.weather_cache is None
    assert ctx.milking_schedule is None


def test_stress_actuation_context_custom_and_immutable() -> None:
    sched = MilkingSchedule()
    ctx = StressActuationContext(milking_schedule=sched)
    assert ctx.milking_schedule is sched
    field_name = "notifier"
    with pytest.raises(FrozenInstanceError):
        setattr(ctx, field_name, None)
