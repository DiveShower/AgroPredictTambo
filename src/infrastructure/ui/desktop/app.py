"""Inicializador de QApplication, hoja de estilo QSS y ventana SCADA completa."""

import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication

from src.adapters.desktop.viewmodels.forecast_viewmodel import ForecastViewModel
from src.adapters.desktop.viewmodels.savings_viewmodel import SavingsViewModel
from src.adapters.desktop.viewmodels.scada_viewmodel import ScadaViewModel
from src.infrastructure.ioc_container import AppContainer
from src.infrastructure.ui.desktop.main_window import MainWindow

QSS_PATH = Path(__file__).resolve().parent / "styles" / "dark_agro_theme.qss"


def build_desktop_viewmodels(
    force_heatwave: bool = False,
) -> tuple[ScadaViewModel, ForecastViewModel, SavingsViewModel]:
    """Construye los 3 ViewModels del escritorio mediante AppContainer."""
    c = AppContainer(force_heatwave=force_heatwave)
    scada_vm = ScadaViewModel(
        c.predict_uc,
        c.status_uc,
        c.toggle_uc,
        c.relay.emergency_shutoff_all,
        getattr(c.weather, "set_profile", lambda _: None),
    )
    forecast_vm = ForecastViewModel(c.weather, c.predictor)
    savings_vm = SavingsViewModel(c.savings_uc, c.report_uc)
    return scada_vm, forecast_vm, savings_vm


def run_desktop_app(
    force_heatwave: bool = False, viewmodel: ScadaViewModel | None = None
) -> int:
    app = QApplication.instance() or QApplication(sys.argv)
    if isinstance(app, QApplication) and QSS_PATH.exists():
        app.setStyleSheet(QSS_PATH.read_text(encoding="utf-8"))
    scada_vm, fore_vm, sav_vm = build_desktop_viewmodels(force_heatwave=force_heatwave)
    win = MainWindow(viewmodel or scada_vm, fore_vm, sav_vm)
    win.show()
    win.trigger_weather_sync()
    return app.exec() if isinstance(app, QApplication) else 0
