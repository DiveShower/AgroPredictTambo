"""Enrutador de comandos del bot de Telegram y fábrica por defecto."""

from collections.abc import Callable
from dataclasses import dataclass

from src.adapters.telegram.handlers.forecast_handler import ForecastHandler
from src.adapters.telegram.handlers.occupy_handler import OccupyHandler
from src.adapters.telegram.handlers.predict_handler import PredictHandler
from src.adapters.telegram.handlers.report_handler import ReportHandler
from src.adapters.telegram.handlers.savings_handler import SavingsHandler
from src.adapters.telegram.handlers.sectors_handler import SectorsHandler
from src.adapters.telegram.handlers.start_handler import StartHandler
from src.adapters.telegram.handlers.state_handler import StateHandler
from src.domain.ports.sector_repository_port import ISectorRepository
from src.infrastructure.use_case_factory import build_core_use_cases


@dataclass
class TelegramCommandRouter:
    """Enruta comandos de texto de Telegram hacia sus handlers de aplicación."""

    start: StartHandler
    state: StateHandler
    forecast: ForecastHandler
    sectors: SectorsHandler
    occupy: OccupyHandler
    predict: PredictHandler
    savings: SavingsHandler
    report: ReportHandler

    def dispatch(self, raw_text: str, chat_id: int = 0) -> tuple[str, str | None]:
        """Despacha un comando de Telegram y retorna (texto, ruta_pdf_opcional)."""
        cmd = (raw_text.split() or ["/start"])[0].lower().split("@")[0]
        if cmd == "/ocupar":
            return self.occupy.handle(*(raw_text.split() + ["", ""])[1:3]), None
        if cmd == "/reporte":
            return self.report.handle()
        routes = {
            "/estado": self.state.handle,
            "/pronostico": self.forecast.handle,
            "/sectores": self.sectors.handle,
            "/prediccion": self.predict.handle,
            "/ahorro": self.savings.handle,
        }
        return (routes[cmd]() if cmd in routes else self.start.handle(chat_id)), None


def build_default_router(
    force_heatwave: bool = False,
    on_occupancy_changed: Callable[[str, bool], None] | None = None,
    sector_repo: ISectorRepository | None = None,
) -> TelegramCommandRouter:
    """Construye el router por defecto con los casos de uso del núcleo."""
    w, p, sav, tog, st, rep = build_core_use_cases(force_heatwave, sector_repo)
    a, b, c = StartHandler(), StateHandler(p), ForecastHandler(w)
    d, e = SectorsHandler(st), OccupyHandler(tog, on_changed=on_occupancy_changed)
    f, g, h = PredictHandler(p), SavingsHandler(sav), ReportHandler(rep)
    return TelegramCommandRouter(a, b, c, d, e, f, g, h)
