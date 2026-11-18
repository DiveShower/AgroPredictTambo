"""Orquestación del pipeline de inferencia bioclimática, recuperación y órdenes."""

from collections.abc import Sequence

from src.application.dtos.predict_stress_request_dto import (
    PredictStressRequestDTO,
)
from src.application.dtos.predict_stress_response_dto import (
    PredictStressResponseDTO,
)
from src.application.dtos.stress_actuation_context import StressActuationContext
from src.application.use_cases.nocturnal_recovery_helper import (
    compute_nocturnal_recovery,
)
from src.application.use_cases.sector_order_helper import evaluate_sector_order
from src.domain.entities.sector import Sector
from src.domain.ports.model_predictor_port import IModelPredictor
from src.domain.value_objects.milking_schedule import MilkingSchedule
from src.domain.value_objects.thi_score import THI_Score
from src.domain.value_objects.weather_conditions import WeatherConditions


def run_stress_pipeline(
    curr: WeatherConditions,
    fore: Sequence[WeatherConditions],
    sectors: Sequence[Sector],
    model: IModelPredictor,
    ctx: StressActuationContext,
    req: PredictStressRequestDTO,
) -> PredictStressResponseDTO:
    """Ejecuta el cálculo de ITH, recuperación nocturna y órdenes por sector."""
    c_thi = THI_Score.calculate(curr.temperature_c, curr.relative_humidity).value
    idx = min(req.forecast_lead_hours, len(fore) - 1) if fore else 0
    target = fore[idx] if fore else curr
    p_thi = THI_Score.calculate(target.temperature_c, target.relative_humidity).value
    recovery = compute_nocturnal_recovery(fore)
    orders, alerts = [], []
    milking = ctx.milking_schedule or MilkingSchedule()
    for sec in sectors:
        if not req.target_sector_id or sec.sector_id == req.target_sector_id:
            o, a = evaluate_sector_order(
                sec,
                target,
                fore[:idx],
                p_thi,
                recovery,
                model,
                milking,
                ctx.notifier,
                ctx.hardware_controller,
            )
            orders.append(o)
            if a:
                alerts.append(a)
    return PredictStressResponseDTO(
        curr, target, c_thi, p_thi, recovery.debt_hours, orders, alerts
    )
