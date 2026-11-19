"""Pruebas unitarias para helpers de sectores y contexto del reporte ESG."""

from datetime import datetime
from unittest.mock import MagicMock

from src.application.use_cases.report_audit_helper import (
    build_report_audit_context,
    collect_report_sectors,
)
from src.domain.entities.sector import Sector


def test_collect_report_sectors_default_and_repo() -> None:
    defaults = collect_report_sectors(None)
    assert len(defaults) == 3
    sombras = next(s for s in defaults if s.sector_id == "sombras")
    assert sombras.allows_water_sprinkling is False

    custom = [Sector("s1", "Sector 1", 50, True)]
    repo = MagicMock()
    repo.get_all_sectors.return_value = custom
    assert collect_report_sectors(repo) == tuple(custom)
    repo.get_all_sectors.assert_called_once_with()


def test_build_report_audit_context_none_and_offline() -> None:
    now = datetime(2026, 1, 15, 14, 0)
    default_ctx = build_report_audit_context(None, -31.25, -61.48, now)
    assert default_ctx.weather_profile == "Perfil estacional estándar"
    assert default_ctx.nocturnal_debt_hours == 0
    assert default_ctx.current_thi is None
    assert default_ctx.generated_at == now

    failing_weather = MagicMock()
    failing_weather.get_current_weather.side_effect = OSError("offline")
    offline_ctx = build_report_audit_context(failing_weather, -31.25, -61.48, now)
    assert offline_ctx.weather_profile == "Respaldo offline"
    assert offline_ctx.nocturnal_debt_hours == 0
