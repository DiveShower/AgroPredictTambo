"""Formateadores de sectores, órdenes de enfriamiento y ahorro ESG para Telegram."""

from collections.abc import Sequence

from src.application.dtos.calculate_savings_response_dto import (
    CalculateSavingsResponseDTO,
)
from src.application.dtos.predict_stress_response_dto import (
    PredictStressResponseDTO,
)
from src.application.dtos.sector_status_dto import SectorStatusDTO

_BADGES = {0: "🟢 CONFORT", 1: "🟡 ALERTA", 2: "🔴 PELIGRO"}
_FLOOR_RULE = {True: "Piso hormigón", False: "Anti-Mastitis: sin agua"}


def stress_badge(level: int) -> str:
    """Retorna la insignia visual correspondiente al nivel de estrés térmico."""
    return _BADGES.get(level, "⚪ DESCONOCIDO")


def format_sectors_table(sectors: Sequence[SectorStatusDTO]) -> str:
    """Formatea el listado de sectores con estado, capacidad y regla sanitaria."""
    if not sectors:
        return "🏭 Sectores del Tambo: sin sectores registrados."
    lines = ["🏭 Estado de Sectores del Tambo"]
    for s in sectors:
        occ = "OCUPADO" if s.current_occupancy else "VACÍO"
        lines.append(
            f"• {s.sector_id} ({s.name}) | {s.cow_capacity} vacas | {occ} | {stress_badge(s.current_stress_level)} | {_FLOOR_RULE[s.allows_water_sprinkling]} | {s.cycle_description}"
        )
    return "\n".join(lines)


def format_orders_summary(response: PredictStressResponseDTO) -> str:
    """Formatea resumen de ITH actual/proyectado, deuda nocturna y órdenes."""
    lines = [
        "🌡️ Predicción Bioclimática y Órdenes",
        f"ITH Actual: {response.current_thi:.2f} | ITH Proyectado: {response.predicted_thi:.2f} | Deuda Nocturna: {response.nocturnal_debt_hours} h",
    ]
    for o in response.cooling_orders:
        lines.append(
            f"• {o.sector_id} [{stress_badge(o.stress_level)}]: {o.water_mist_seconds}s agua / {o.fan_ventilation_seconds}s vent — {o.justification}"
        )
    return "\n".join(lines)


def format_savings_summary(response: CalculateSavingsResponseDTO) -> str:
    """Formatea balance hídrico, energético, CO2e CAMMESA y retorno SIGLeA."""
    s, c, e = response.savings, response.carbon_footprint, response.economic_impact
    return (
        "💧 Balance de Ahorro y Sustentabilidad ESG\n"
        f"• Agua ahorrada (software): {s.water_saved_liters:.2f} L ({s.water_saved_pct:.2f}%)\n"
        f"• Ahorro hídrico combinado: {s.combined_water_saved_pct:.2f}%\n"
        f"• Energía ahorrada: {s.energy_saved_kwh:.2f} kWh ({s.energy_saved_pct:.2f}%)\n"
        f"• Carbono evitado (CAMMESA): {c.co2_avoided_kg:.2f} kg CO2e\n"
        f"• Leche protegida (SIGLeA): {e.milk_protected_liters:.2f} L (${e.economic_return_ars:.2f} ARS)"
    )
