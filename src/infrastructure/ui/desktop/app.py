"""Inicializador de QApplication, hoja de estilo QSS y ventana SCADA completa."""

from pathlib import Path
import sys
from typing import Optional
from PyQt6.QtWidgets import QApplication
from src.adapters.desktop.viewmodels.forecast_viewmodel import ForecastViewModel
from src.adapters.desktop.viewmodels.savings_viewmodel import SavingsViewModel
from src.adapters.desktop.viewmodels.scada_viewmodel import ScadaViewModel
from src.application.use_cases.calculate_savings_uc import CalculateSavingsUseCase
from src.application.use_cases.generate_sustainability_report_uc import GenerateSustainabilityReportUseCase
from src.application.use_cases.get_farm_status_uc import GetFarmStatusUseCase
from src.application.use_cases.predict_sector_stress_uc import PredictSectorStressUseCase
from src.application.use_cases.toggle_sector_occupancy_uc import ToggleSectorOccupancyUseCase
from src.infrastructure.hardware.mock_relay_adapter import MockRelayAdapter
from src.infrastructure.ml.sklearn_predictor_adapter import SklearnPredictorAdapter
from src.infrastructure.notifications.telegram_notifier_adapter import TelegramNotifierAdapter
from src.infrastructure.persistence.sqlite_weather_cache_adapter import SqliteWeatherCacheAdapter
from src.infrastructure.reporting.pdf_sustainability_report_adapter import PdfSustainabilityReportAdapter
from src.infrastructure.repositories.in_memory_sector_repo import InMemorySectorRepository
from src.infrastructure.ui.desktop.main_window import MainWindow
from src.infrastructure.weather_api.mock_weather_adapter import MockWeatherAdapter
from src.infrastructure.weather_api.open_meteo_adapter import OpenMeteoAdapter

QSS_PATH = Path(__file__).resolve().parent / "styles" / "dark_agro_theme.qss"


def build_desktop_viewmodels(
    force_heatwave: bool = False,
) -> tuple[ScadaViewModel, ForecastViewModel, SavingsViewModel]:
    """Construye los 3 ViewModels del escritorio con instancias compartidas."""
    weather = MockWeatherAdapter("heatwave") if force_heatwave else OpenMeteoAdapter()
    cache = SqliteWeatherCacheAdapter()
    if not cache.is_cache_valid():
        cache.save_forecast(MockWeatherAdapter("heatwave").get_hourly_forecast(-31.25, -61.48))
    repo, predictor = InMemorySectorRepository(), SklearnPredictorAdapter()
    relay, notifier = MockRelayAdapter(), TelegramNotifierAdapter()
    savings_uc = CalculateSavingsUseCase()
    scada_vm = ScadaViewModel(
        PredictSectorStressUseCase(weather, repo, predictor, notifier, relay, cache),
        GetFarmStatusUseCase(repo, weather),
        ToggleSectorOccupancyUseCase(repo),
        relay.emergency_shutoff_all,
    )
    forecast_vm = ForecastViewModel(weather, predictor)
    savings_vm = SavingsViewModel(savings_uc, GenerateSustainabilityReportUseCase(PdfSustainabilityReportAdapter(), savings_uc))
    return scada_vm, forecast_vm, savings_vm


def run_desktop_app(force_heatwave: bool = False, viewmodel: Optional[ScadaViewModel] = None) -> int:
    app = QApplication.instance() or QApplication(sys.argv)
    if isinstance(app, QApplication) and QSS_PATH.exists():
        app.setStyleSheet(QSS_PATH.read_text(encoding="utf-8"))
    scada_vm, fore_vm, sav_vm = build_desktop_viewmodels(force_heatwave=force_heatwave)
    win = MainWindow(viewmodel or scada_vm, fore_vm, sav_vm)
    win.show()
    win.trigger_weather_sync()
    return app.exec() if isinstance(app, QApplication) else 0
