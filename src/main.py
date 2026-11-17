"""Punto de Entrada Principal (Composition Root) — AgroChallenge 2026."""

import argparse
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
from src.adapters.cli.cli_controller import CliController
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
from src.infrastructure.ui.cli.console_runner import run_cli
from src.infrastructure.weather_api.mock_weather_adapter import MockWeatherAdapter
from src.infrastructure.weather_api.open_meteo_adapter import OpenMeteoAdapter


def build_cli_controller(force_heatwave: bool = False) -> CliController:
    use_mock = force_heatwave or os.getenv("WEATHER_PROVIDER", "open_meteo") == "mock"
    weather = MockWeatherAdapter("heatwave") if use_mock else OpenMeteoAdapter()
    cache = SqliteWeatherCacheAdapter()
    if not cache.is_cache_valid():
        cache.save_forecast(MockWeatherAdapter("heatwave").get_hourly_forecast(-31.25, -61.48))
    repo, predictor = InMemorySectorRepository(), SklearnPredictorAdapter()
    notifier, relay, savings_uc = TelegramNotifierAdapter(), MockRelayAdapter(), CalculateSavingsUseCase()
    return CliController(
        PredictSectorStressUseCase(weather, repo, predictor, notifier, relay, cache),
        savings_uc, ToggleSectorOccupancyUseCase(repo),
        GetFarmStatusUseCase(repo, weather),
        GenerateSustainabilityReportUseCase(PdfSustainabilityReportAdapter(), savings_uc),
    )


def main(argv: list[str] | None = None) -> int:
    load_dotenv()
    p = argparse.ArgumentParser(description="AgroChallenge 2026 - Estrés Térmico")
    for flag in ("--desktop", "--bot", "--cli", "--demo-heatwave", "--benchmark"):
        p.add_argument(flag, action="store_true")
    args = p.parse_args(argv)
    if args.desktop:
        from src.infrastructure.ui.desktop.app import run_desktop_app
        return run_desktop_app(force_heatwave=args.demo_heatwave)
    ctrl = build_cli_controller(force_heatwave=args.demo_heatwave or args.benchmark)
    return run_cli(ctrl, benchmark_mode=args.benchmark)

if __name__ == "__main__":
    raise SystemExit(main())
