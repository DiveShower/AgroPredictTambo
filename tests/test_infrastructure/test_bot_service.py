"""Pruebas de integración para router, worker SCADA y servicio del bot Telegram."""

from pathlib import Path

import pytest
from PyQt6.QtWidgets import QApplication

import src.infrastructure.repositories.in_memory_sector_repo as repo_mod
from src.adapters.desktop.viewmodels.scada_viewmodel import ScadaViewModel
from src.infrastructure.ui.desktop.workers.telegram_bot_worker import TelegramBotWorker
from src.infrastructure.ui.telegram_bot.bot_command_router import build_default_router
from src.infrastructure.ui.telegram_bot.bot_service import TelegramBotService, run_bot
from src.infrastructure.use_case_factory import build_core_use_cases


def test_router_dispatch_all_commands() -> None:
    router = build_default_router(force_heatwave=True)
    cmds = ("/start", "/help", "/estado", "/pronostico", "/sectores")
    for cmd in (*cmds, "/ocupar comederos false", "/prediccion", "/ahorro"):
        text, pdf = router.dispatch(cmd)
        assert text.strip() and pdf is None
    report_text, pdf_path = router.dispatch("/reporte")
    assert report_text.strip()
    assert pdf_path is not None and Path(pdf_path).exists()


def test_telegram_bot_worker_syncs_scada_headless() -> None:
    _app = QApplication.instance() or QApplication([])
    repo = repo_mod.InMemorySectorRepository()
    _, pred_uc, _, toggle_uc, status_uc, _ = build_core_use_cases(True, repo)
    vm = ScadaViewModel(pred_uc, status_uc, toggle_uc)
    worker = TelegramBotWorker(vm, router=build_default_router(True, sector_repo=repo))
    changed: list[bool] = []
    cmds: list[str] = []
    worker.sector_state_changed.connect(lambda: changed.append(True))
    worker.command_received.connect(cmds.append)
    reply = worker.process_command("/ocupar comederos false")
    worker.stop()
    cards = {c["sector_id"]: c["is_occupied"] for c in vm.get_cards_state()}
    assert reply.strip() and cards["comederos"] is False
    assert changed == [True] and cmds == ["/ocupar comederos false"]


def test_bot_service_build_and_failsafe(monkeypatch: pytest.MonkeyPatch) -> None:
    svc = TelegramBotService(build_default_router(True), token="123456:DUMMY_TOKEN")
    text, _ = svc.handle_text("/estado")
    assert text.strip() and svc.build_application() is not None
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "")
    assert run_bot(force_heatwave=True) == 0
    assert Path("data/cache/bot_qr.png").exists()
