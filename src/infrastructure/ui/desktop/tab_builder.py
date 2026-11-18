"""Constructor de pestañas principales para la ventana SCADA desktop."""

from PyQt6.QtWidgets import QTabWidget, QWidget

from src.adapters.desktop.viewmodels.forecast_viewmodel import ForecastViewModel
from src.adapters.desktop.viewmodels.savings_viewmodel import SavingsViewModel
from src.infrastructure.ui.desktop.views.forecast_view import ForecastView
from src.infrastructure.ui.desktop.views.report_view import ReportView
from src.infrastructure.ui.desktop.views.savings_view import SavingsView
from src.infrastructure.ui.desktop.views.scada_view import ScadaView
from src.infrastructure.ui.desktop.views.simulation_view import SimulationView


def build_tabs(
    tabs: QTabWidget,
    scada_view: ScadaView,
    fore_vm: ForecastViewModel | None,
    sav_vm: SavingsViewModel | None,
    parent: QWidget,
) -> ForecastView | None:
    """Puebla el QTabWidget con las vistas activas y retorna ForecastView si aplica."""
    tabs.addTab(scada_view, "TAB 1: SCADA TAMBO")
    forecast_view: ForecastView | None = None
    if fore_vm is not None:
        forecast_view = ForecastView(fore_vm, parent)
        tabs.addTab(forecast_view, "TAB 2: CURVA ITH 24H")
        tabs.addTab(SimulationView(fore_vm, parent), "TAB 4: SIMULADOR JURADO")
    if sav_vm is not None:
        tabs.addTab(SavingsView(sav_vm, parent), "TAB 3: ROI & ESG")
        tabs.addTab(ReportView(sav_vm, parent), "TAB 5: REPORTE PDF")
    return forecast_view
