"""Value Object para estimación económica de leche protegida (Panel SIGLeA)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class EconomicImpact:
    """Cuantifica litros de leche defendidos y retorno financiero por mitigación."""

    cow_count: int
    hours_alert_mitigated: int
    hours_danger_mitigated: int
    milk_protected_liters: float
    milk_price_ars: float
    economic_return_ars: float

    @classmethod
    def calculate(
        cls,
        cow_count: int,
        hours_alert_mitigated: int,
        hours_danger_mitigated: int,
        milk_price_ars: float = 430.0,
    ) -> "EconomicImpact":
        """Estima leche protegida proporcional a horas mitigadas (tope 4.0 L/vaca/día)."""
        safe_cows = max(0, cow_count)
        safe_h1 = max(0, hours_alert_mitigated)
        safe_h2 = max(0, hours_danger_mitigated)
        per_cow_protected = min(4.0, 0.15 * safe_h1 + 0.35 * safe_h2)
        milk_protected = round(safe_cows * per_cow_protected, 2)
        economic_return = round(milk_protected * max(0.0, milk_price_ars), 2)
        return cls(
            cow_count=safe_cows,
            hours_alert_mitigated=safe_h1,
            hours_danger_mitigated=safe_h2,
            milk_protected_liters=milk_protected,
            milk_price_ars=milk_price_ars,
            economic_return_ars=economic_return,
        )
