"""Tests unitarios para el Value Object THI_Score (fórmula NRC/Thom)."""

import pytest

from src.domain.value_objects.thi_score import THI_Score


@pytest.mark.parametrize(
    ("temp_c", "rh", "expected_thi", "expected_level", "expected_label"),
    [
        (20.0, 45.0, 64.98, 0, "Confort"),
        (26.0, 60.0, 74.22, 1, "Alerta Leve"),
        (31.4, 62.0, 82.14, 2, "Peligro"),
        (34.5, 68.0, 87.75, 2, "Peligro"),
    ],
)
def test_thi_calculation_matches_nrc_formula(
    temp_c: float,
    rh: float,
    expected_thi: float,
    expected_level: int,
    expected_label: str,
) -> None:
    score = THI_Score.calculate(temp_c=temp_c, rh=rh)

    assert score.value == pytest.approx(expected_thi, abs=0.05)
    assert score.stress_level == expected_level
    assert score.category_name == expected_label


def test_thi_custom_high_production_thresholds() -> None:
    # 23.0°C y 55% HR -> ITH ~ 69.53 (< 70.0 Confort)
    comfort = THI_Score.calculate(23.0, 55.0, threshold_alert=70.0, threshold_danger=76.0)
    # 24.5°C y 65% HR -> ITH ~ 72.52 (>= 70.0 Alerta para alta producción)
    alert = THI_Score.calculate(24.5, 65.0, threshold_alert=70.0, threshold_danger=76.0)
    # 27.5°C y 65% HR -> ITH ~ 77.01 (>= 76.0 Peligro para alta producción)
    danger = THI_Score.calculate(27.5, 65.0, threshold_alert=70.0, threshold_danger=76.0)

    assert comfort.stress_level == 0
    assert alert.stress_level == 1
    assert danger.stress_level == 2


def test_thi_boundary_thresholds() -> None:
    # Verificación de límites exactos en umbrales estándar 72 / 78
    below_alert = THI_Score.calculate(24.0, 60.0)   # 71.36 < 72.0
    above_alert = THI_Score.calculate(25.0, 60.0)   # 72.79 >= 72.0
    above_danger = THI_Score.calculate(28.5, 62.0)  # 78.10 >= 78.0

    assert below_alert.stress_level == 0
    assert above_alert.stress_level == 1
    assert above_danger.stress_level == 2
