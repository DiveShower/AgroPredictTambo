"""Helper de dominio/aplicación para evaluar órdenes y alertas por sector."""

from collections.abc import Sequence
from typing import Optional

from src.domain.entities.cooling_order import CoolingOrder
from src.domain.entities.heat_stress_alert import HeatStressAlert
from src.domain.entities.sector import Sector
from src.domain.ports.hardware_controller_port import IHardwareController
from src.domain.ports.model_predictor_port import IModelPredictor
from src.domain.ports.notifier_port import INotifier
from src.domain.value_objects.cooling_cycle import CoolingCycle
from src.domain.value_objects.milking_schedule import MilkingSchedule
from src.domain.value_objects.nocturnal_recovery import NocturnalRecovery
from src.domain.value_objects.weather_conditions import WeatherConditions


def evaluate_sector_order(
    sec: Sector,
    target: WeatherConditions,
    recent_history: Sequence[WeatherConditions],
    p_thi: float,
    recovery: NocturnalRecovery,
    predictor: IModelPredictor,
    milking: MilkingSchedule,
    notifier: Optional[INotifier] = None,
    hardware: Optional[IHardwareController] = None,
) -> tuple[CoolingOrder, Optional[HeatStressAlert]]:
    """Evalúa un sector y emite su CoolingOrder y HeatStressAlert si corresponde."""
    if not sec.current_occupancy:
        return CoolingOrder(sec.sector_id, 0, 0, 0, target.timestamp, "Sector vacío"), None

    danger_lim = sec.effective_danger_threshold(recovery.threshold_penalty)
    precool = sec.sector_id == "corral_espera" and milking.requires_precooling(
        target.timestamp.time(), p_thi, danger_lim
    )
    if precool:
        lvl, just = 2, "Pre-enfriamiento preventivo pre-ordeñe"
    else:
        ml_l = predictor.predict_stress_level(target, recent_history, recovery.debt_hours)
        lvl = max(ml_l, sec.evaluate_stress_level(p_thi, recovery.threshold_penalty))
        just = (
            "Protección anti-mastitis (solo ventilación)"
            if (lvl == 2 and not sec.allows_water_sprinkling)
            else f"Nivel {lvl} (deuda nocturna: {recovery.threshold_penalty} pts)"
        )

    cycle = CoolingCycle.for_stress_level(lvl, sec.allows_water_sprinkling)
    order = CoolingOrder(sec.sector_id, lvl, cycle.water_mist_seconds, cycle.fan_ventilation_seconds, target.timestamp, just)
    if hardware and order.is_active:
        if order.water_mist_seconds > 0:
            hardware.activate_water_valve(sec.sector_id, order.water_mist_seconds)
        if order.fan_ventilation_seconds > 0:
            hardware.activate_ventilation_fan(sec.sector_id, order.fan_ventilation_seconds)

    alert = HeatStressAlert(sec.sector_id, sec.name, p_thi, lvl, target.timestamp, just) if lvl == 2 else None
    if alert and notifier:
        notifier.send_alert(alert)
    return order, alert
