"""Inicializador de QApplication, hoja de estilo QSS y ventana SCADA."""

from pathlib import Path
import sys
from typing import Optional
from PyQt6.QtWidgets import QApplication
from src.adapters.desktop.viewmodels.scada_viewmodel import ScadaViewModel
from src.application.use_cases.get_farm_status_uc import GetFarmStatusUseCase
from src.application.use_cases.predict_sector_stress_uc import PredictSectorStressUseCase
from src.application.use_cases.toggle_sector_occupancy_uc import ToggleSectorOccupancyUseCase
from src.infrastructure.hardware.mock_relay_adapter import MockRelayAdapter
from src.infrastructure.ml.sklearn_predictor_adapter import SklearnPredictorAdapter
from src.infrastructure.notifications.telegram_notifier_adapter import TelegramNotifierAdapter
from src.infrastructure.persistence.sqlite_weather_cache_adapter import SqliteWeatherCacheAdapter
from src.infrastructure.repositories.in_memory_sector_repo import InMemorySectorRepository
from src.infrastructure.ui.desktop.main_window import MainWindow
from src.infrastructure.weather_api.mock_weather_adapter import MockWeatherAdapter
from src.infrastructure.weather_api.open_meteo_adapter import OpenMeteoAdapter

QSS_PATH = Path(__file__).resolve().parent / "styles" / "dark_agro_theme.qss"


def build_scada_viewmodel(force_heatwave: bool = False) -> ScadaViewModel:
    """Construye el ScadaViewModel con sus dependencias compartidas."""
    weather = MockWeatherAdapter("heatwave") if force_heatwave else OpenMeteoAdapter()
    cache = SqliteWeatherCacheAdapter()
    if not cache.is_cache_valid():
        cache.save_forecast(MockWeatherAdapter("heatwave").get_hourly_forecast(-31.25, -61.48))
    repo, predictor = InMemorySectorRepository(), SklearnPredictorAdapter()
    relay, notifier = MockRelayAdapter(), TelegramNotifierAdapter()
    return ScadaViewModel(
        predict_uc=PredictSectorStressUseCase(weather, repo, predictor, notifier, relay, cache),
        status_uc=GetFarmStatusUseCase(repo, weather),
        toggle_uc=ToggleSectorOccupancyUseCase(repo),
        shutoff_fn=relay.emergency_shutoff_all,
    )


def run_desktop_app(
    force_heatwave: bool = False,
    viewmodel: Optional[ScadaViewModel] = None,
) -> int:
    """Arranca la estación base nativa PyQt6 aplicando dark_agro_theme.qss."""
    app = QApplication.instance() or QApplication(sys.argv)
    if isinstance(app, QApplication) and QSS_PATH.exists():
        app.setStyleSheet(QSS_PATH.read_text(encoding="utf-8"))
    vm = viewmodel or build_scada_viewmodel(force_heatwave=force_heatwave)
    win = MainWindow(vm)
    win.show()
    win.trigger_weather_sync()
    return app.exec() if isinstance(app, QApplication) else 0
