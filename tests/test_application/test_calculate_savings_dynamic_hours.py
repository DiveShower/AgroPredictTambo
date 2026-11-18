"""Pruebas unitarias para horas mitigadas dinámicas H1/H2 en CalculateSavingsUseCase."""

from src.application.dtos.calculate_savings_request_dto import (
    CalculateSavingsRequestDTO,
)
from src.application.use_cases.calculate_savings_uc import (
    CalculateSavingsUseCase,
)


def test_calculate_savings_with_explicit_h1_h2_hours() -> None:
    """Verifica el cálculo económico con horas explícitas de nivel 1 y nivel 2."""
    uc = CalculateSavingsUseCase()
    res = uc.execute(
        CalculateSavingsRequestDTO(
            hours_level_1=5.0,
            hours_level_2=3.0,
            cow_count=100,
            milk_price_ars=430.0,
        )
    )
    assert res.economic_impact.hours_alert_mitigated == 5
    assert res.economic_impact.hours_danger_mitigated == 3
    assert res.economic_impact.milk_protected_liters == 180.0
    assert res.economic_impact.economic_return_ars == 77400.0
