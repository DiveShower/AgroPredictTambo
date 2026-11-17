"""Formateador de tablas de texto para la interfaz de línea de comandos (CLI)."""

from collections.abc import Sequence

from src.application.dtos.calculate_savings_response_dto import (
    CalculateSavingsResponseDTO,
)
from src.application.dtos.predict_stress_response_dto import (
    PredictStressResponseDTO,
)
from src.application.dtos.sector_status_dto import SectorStatusDTO


def format_farm_status(statuses: Sequence[SectorStatusDTO]) -> str:
    """Genera tabla en texto plano con el estado operativo de los sectores."""
    lines = [
        "=== ESTADO OPERATIVO DEL TAMBO (SECTORES) ===",
        f"{'SECTOR':<15} | {'OCUPACION':<10} | {'NIVEL':<5} | {'CICLO ACTIVO'}",
        "-" * 72,
    ]
    for s in statuses:
        occ = "OCUPADO" if s.current_occupancy else "VACIO"
        lines.append(
            f"{s.sector_id:<15} | {occ:<10} | {s.current_stress_level:<5} | {s.cycle_description}"
        )
    return "\n".join(lines)


def format_prediction_response(resp: PredictStressResponseDTO) -> str:
    """Formatea condiciones climáticas, ITH proyectado y órdenes por sector."""
    c, p = resp.current_conditions, resp.predicted_conditions
    lines = [
        "=== PREDICCION BIOCLIMATICA Y ORDENES DE ENFRIAMIENTO ===",
        f"Actual: {c.temperature_c:.1f}C | HR {c.relative_humidity:.0f}% | ITH {resp.current_thi:.2f}",
        f"Proyectado: {p.temperature_c:.1f}C | HR {p.relative_humidity:.0f}% | ITH {resp.predicted_thi:.2f} | Deuda Nocturna: {resp.nocturnal_debt_hours}h",
        f"{'SECTOR':<15} | {'NIVEL':<5} | {'AGUA(s)':<7} | {'VENT(s)':<7} | {'JUSTIFICACION'}",
        "-" * 78,
    ]
    for o in resp.cooling_orders:
        lines.append(
            f"{o.sector_id:<15} | {o.stress_level:<5} | {o.water_mist_seconds:<7} | {o.fan_ventilation_seconds:<7} | {o.justification}"
        )
    return "\n".join(lines)


def format_savings_response(resp: CalculateSavingsResponseDTO) -> str:
    """Formatea el balance hídrico, energético, carbono CAMMESA y leche SIGLeA."""
    s, c, e = resp.savings, resp.carbon_footprint, resp.economic_impact
    return "\n".join([
        "=== BALANCE DE AHORRO Y SUSTENTABILIDAD ESG (8H FIJO VS PREDICTIVO) ===",
        f"Agua Ahorrada (Software 1.3 L/m): {s.water_saved_liters:.2f} L ({s.water_saved_pct:.2f}%)",
        f"Ahorro Hidraulico Combinado (vs 4.9 L/m): {s.combined_water_saved_pct:.2f}%",
        f"Energia Electrica Ahorrada: {s.energy_saved_kwh:.2f} kWh ({s.energy_saved_pct:.2f}%)",
        f"Huella de Carbono Evitada (CAMMESA): {c.co2_avoided_kg:.2f} kg CO2e",
        f"Leche Protegida (SIGLeA): {e.milk_protected_liters:.2f} L/dia (${e.economic_return_ars:.2f} ARS)",
    ])
