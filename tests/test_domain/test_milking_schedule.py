"""Tests unitarios para MilkingSchedule y ventanas de pre-enfriamiento."""

from datetime import time

from src.domain.value_objects.milking_schedule import MilkingSchedule


def test_milking_schedule_shift_detection() -> None:
    schedule = MilkingSchedule()

    assert schedule.is_milking_time(time(5, 30)) is True
    assert schedule.is_milking_time(time(16, 0)) is True
    assert schedule.is_milking_time(time(18, 30)) is True
    assert schedule.is_milking_time(time(12, 0)) is False
    assert schedule.is_milking_time(time(15, 50)) is False


def test_precooling_triggers_only_within_lead_window_and_danger_thi() -> None:
    schedule = MilkingSchedule()

    # 15:45 y 15:50 están dentro de los 15 min previos a 16:00 con ITH >= 78
    assert schedule.requires_precooling(time(15, 45), projected_thi=80.0) is True
    assert schedule.requires_precooling(time(15, 50), projected_thi=78.0) is True
    assert schedule.requires_precooling(time(4, 20), projected_thi=79.5) is True

    # ITH bajo umbral de peligro -> no requiere pre-enfriamiento
    assert schedule.requires_precooling(time(15, 50), projected_thi=75.0) is False
    # Fuera de ventana de 15 minutos -> False
    assert schedule.requires_precooling(time(15, 30), projected_thi=82.0) is False
    assert schedule.requires_precooling(time(16, 5), projected_thi=82.0) is False
