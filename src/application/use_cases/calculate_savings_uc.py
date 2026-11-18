"""Caso de uso para el cálculo de ahorro hídrico, energético y retorno financiero."""

from src.application.dtos.calculate_savings_request_dto import (
    CalculateSavingsRequestDTO,
)
from src.application.dtos.calculate_savings_response_dto import (
    CalculateSavingsResponseDTO,
)
from src.domain.value_objects.carbon_footprint import CarbonFootprint
from src.domain.value_objects.cooling_cycle import CoolingCycle
from src.domain.value_objects.economic_impact import EconomicImpact
from src.domain.value_objects.resource_savings import ResourceSavings


class CalculateSavingsUseCase:
    """Modela la reducción de consumo frente al sistema tradicional continuo de 8h."""

    def __init__(self, cycle_config: CoolingCycle = CoolingCycle()) -> None:  # noqa: B008
        self._cfg = cycle_config

    def execute(
        self,
        request: CalculateSavingsRequestDTO = CalculateSavingsRequestDTO(),  # noqa: B008
    ) -> CalculateSavingsResponseDTO:
        """Calcula el balance comparativo entre el sistema tradicional y el predictivo."""
        base_h = max(0.0, request.baseline_operating_hours)
        pred_h = max(0.0, request.predictive_active_hours)

        base_mins = base_h * self._cfg.active_water_minutes_per_hour
        pred_mins = pred_h * self._cfg.active_water_minutes_per_hour

        legacy_w = base_mins * request.sprinkler_count * self._cfg.traditional_flow_lpm
        base_w = base_mins * request.sprinkler_count * self._cfg.sprinkler_flow_lpm
        pred_w = pred_mins * request.sprinkler_count * self._cfg.sprinkler_flow_lpm

        cycle_kw = (
            self._cfg.pump_power_kw * self._cfg.water_duty_cycle
            + request.fan_count * self._cfg.fan_unit_power_kw
        )
        savings = ResourceSavings.calculate(
            baseline_water_liters=base_w,
            predictive_water_liters=pred_w,
            legacy_nozzle_water_liters=legacy_w,
            baseline_energy_kwh=base_h * cycle_kw,
            predictive_energy_kwh=pred_h * cycle_kw,
        )
        carbon = CarbonFootprint.from_energy_savings(savings.energy_saved_kwh)
        h1, h2 = request.hours_level_1, request.hours_level_2
        h_alert = int(h1 if h1 is not None else pred_h)
        fallback_h2 = max(1, h_alert // 2) if h_alert > 0 else 0
        h_danger = int(h2 if h2 is not None else fallback_h2)
        economic = EconomicImpact.calculate(
            cow_count=request.cow_count,
            hours_alert_mitigated=h_alert,
            hours_danger_mitigated=h_danger,
            milk_price_ars=request.milk_price_ars,
        )
        return CalculateSavingsResponseDTO(savings, carbon, economic)
