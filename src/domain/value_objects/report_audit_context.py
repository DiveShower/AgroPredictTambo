"""Value Object de metadatos bioclimáticos y geográficos para el reporte ESG."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ReportAuditContext:
    """Contexto de auditoría ambiental y operativa incluido en el PDF."""

    location: str = "Rafaela, Santa Fe (-31.25, -61.48)"
    weather_profile: str = "Perfil estacional estándar"
    nocturnal_debt_hours: int = 0
    current_thi: float | None = None
    generated_at: datetime | None = None
