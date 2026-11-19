"""Helpers para recolectar sectores y contexto bioclimático del reporte ESG."""

from datetime import datetime

from src.application.use_cases.nocturnal_recovery_helper import (
    compute_nocturnal_recovery,
)
from src.domain.entities.sector import Sector
from src.domain.fixtures.default_farm import get_default_sectors
from src.domain.ports.sector_repository_port import ISectorRepository
from src.domain.ports.weather_provider_port import IWeatherProvider
from src.domain.value_objects.report_audit_context import ReportAuditContext
from src.domain.value_objects.thi_score import THI_Score


def collect_report_sectors(sector_repo: ISectorRepository | None) -> tuple[Sector, ...]:
    """Obtiene los sectores del repositorio o los de referencia por defecto."""
    if sector_repo is not None:
        return tuple(sector_repo.get_all_sectors())
    return tuple(get_default_sectors())


def build_report_audit_context(
    weather: IWeatherProvider | None,
    latitude: float,
    longitude: float,
    generated_at: datetime,
) -> ReportAuditContext:
    """Construye el contexto bioclimático para el encabezado del reporte PDF."""
    loc = f"Rafaela, Santa Fe ({latitude:.2f}, {longitude:.2f})"
    if weather is None:
        return ReportAuditContext(location=loc, generated_at=generated_at)
    try:
        curr = weather.get_current_weather(latitude, longitude)
        fore = weather.get_hourly_forecast(latitude, longitude, hours=24)
        thi = THI_Score.calculate(curr.temperature_c, curr.relative_humidity).value
        rec = compute_nocturnal_recovery(fore)
        prof = getattr(weather, "_profile", None)
        label = f"Simulación ({prof})" if prof else "Open-Meteo (Tiempo real)"
        return ReportAuditContext(
            location=loc,
            weather_profile=label,
            nocturnal_debt_hours=rec.debt_hours,
            current_thi=thi,
            generated_at=generated_at,
        )
    except (OSError, RuntimeError, ValueError):
        return ReportAuditContext(
            location=loc,
            weather_profile="Respaldo offline",
            generated_at=generated_at,
        )
