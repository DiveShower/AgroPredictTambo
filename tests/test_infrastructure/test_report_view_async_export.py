"""Pruebas unitarias para transiciones de estado en ReportView."""

import os
from unittest.mock import MagicMock

from PyQt6.QtWidgets import QApplication

from src.adapters.desktop.viewmodels.savings_viewmodel import SavingsViewModel
from src.infrastructure.ui.desktop.views.report_view import ReportView

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
_APP = QApplication.instance() or QApplication([])

_KPI_DATA: dict[str, str] = {
    "water_software": "120.0 L/día (30.0%)",
    "water_combined": "45.0% (vs pico 4.9 L/min)",
    "energy_kwh": "12.50 kWh/día (20.0%)",
    "carbon_cammesa": "5.10 kg CO2e (Factor 0.408)",
    "milk_siglea": "250.0 L/día (100 vacas)",
    "economic_ars": "$107,500.00 ARS/día",
}


def test_report_view_ui_state_transitions() -> None:
    """Verifica el estado del botón y etiqueta tras éxito o fallo al exportar PDF."""
    mock_vm = MagicMock(spec=SavingsViewModel)
    mock_vm.get_kpi_cards_data.return_value = _KPI_DATA

    view = ReportView(mock_vm)
    assert view.export_btn.isEnabled() is True

    view._on_pdf_ready("/tmp/test.pdf")
    assert view.export_btn.isEnabled() is True
    assert "/tmp/test.pdf" in view.status_lbl.text()

    view._on_pdf_failed("Fallo de escritura")
    assert view.export_btn.isEnabled() is True
    assert "Fallo de escritura" in view.status_lbl.text()
