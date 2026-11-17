"""Pruebas para TelegramNotifierAdapter, PdfSustainabilityReportAdapter, Repo y Relés."""

from datetime import datetime
from pathlib import Path
from typing import Any
import pytest
from src.domain.entities.heat_stress_alert import HeatStressAlert
from src.domain.exceptions.sector_not_found_exception import SectorNotFoundException
from src.domain.value_objects.resource_savings import ResourceSavings
from src.infrastructure.hardware.mock_relay_adapter import MockRelayAdapter
from src.infrastructure.notifications.telegram_notifier_adapter import TelegramNotifierAdapter
from src.infrastructure.reporting.pdf_sustainability_report_adapter import PdfSustainabilityReportAdapter
from src.infrastructure.repositories.in_memory_sector_repo import InMemorySectorRepository


def test_telegram_notifier_sync_post_and_empty_token(mocker: Any) -> None:
    alert = HeatStressAlert("comederos", "Comederos", 82.5, 2, datetime(2026, 1, 15, 14, 0), "Aspersión")
    assert TelegramNotifierAdapter(bot_token="", admin_chat_id="").send_alert(alert) is False

    resp = mocker.Mock(status_code=200)
    post = mocker.patch("requests.post", return_value=resp)
    notifier = TelegramNotifierAdapter(bot_token="tok123", admin_chat_id="999")
    assert notifier.send_alert(alert) is True
    post.assert_called_once()


def test_pdf_sustainability_report_creates_valid_pdf(tmp_path: Path) -> None:
    savings = ResourceSavings.calculate(1000.0, 420.0, 3800.0, 96.0, 42.0)
    pdf_file = tmp_path / "esg_nestle.pdf"
    out = PdfSustainabilityReportAdapter().generate_sustainability_pdf("Tambo San José", savings, str(pdf_file))
    assert Path(out).exists()
    assert pdf_file.read_bytes().startswith(b"%PDF")


def test_in_memory_repo_and_mock_relay_watchdog() -> None:
    repo = InMemorySectorRepository()
    assert len(repo.get_all_sectors()) == 3
    repo.update_occupancy("corral_espera", False)
    assert repo.get_by_id("corral_espera").current_occupancy is False
    with pytest.raises(SectorNotFoundException):
        repo.get_by_id("inexistente")

    relay = MockRelayAdapter()
    assert relay.activate_water_valve("comederos", 120) is True
    assert relay.water_valves_seconds["comederos"] == 60
    relay.emergency_shutoff_all()
    assert relay.water_valves_seconds["comederos"] == 0
