"""Punto de Entrada Principal (Composition Root) — AgroChallenge 2026."""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

from src.adapters.cli.cli_controller import CliController
from src.infrastructure.ui.cli.console_runner import run_cli
from src.infrastructure.use_case_factory import build_core_use_cases


def build_cli_controller(force_heatwave: bool = False) -> CliController:
    _, predict_uc, savings_uc, toggle_uc, status_uc, report_uc = build_core_use_cases(
        force_heatwave=force_heatwave
    )
    return CliController(predict_uc, savings_uc, toggle_uc, status_uc, report_uc)


def main(argv: list[str] | None = None) -> int:
    load_dotenv()
    p = argparse.ArgumentParser(description="AgroChallenge 2026 - Estrés Térmico")
    for flag in ("--desktop", "--bot", "--cli", "--demo-heatwave", "--benchmark"):
        p.add_argument(flag, action="store_true")
    p.add_argument("--export-json", type=str, default=None)
    args = p.parse_args(argv)
    if args.desktop:
        from src.infrastructure.ui.desktop.app import run_desktop_app

        return run_desktop_app(force_heatwave=args.demo_heatwave)
    if args.bot:
        from src.infrastructure.ui.telegram_bot.bot_service import run_bot

        return run_bot(force_heatwave=args.demo_heatwave)
    ctrl = build_cli_controller(force_heatwave=args.demo_heatwave or args.benchmark)
    return run_cli(
        ctrl, benchmark_mode=args.benchmark, export_json_path=args.export_json
    )


if __name__ == "__main__":
    raise SystemExit(main())
