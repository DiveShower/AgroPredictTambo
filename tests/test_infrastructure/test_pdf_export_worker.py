"""Pruebas unitarias para PdfExportWorker y sus señales Qt asíncronas."""

import os
from pathlib import Path
from typing import Any

from PyQt6.QtWidgets import QApplication

from src.adapters.desktop.viewmodels.savings_viewmodel import SavingsViewModel
from src.infrastructure.ui.desktop.workers.pdf_export_worker import PdfExportWorker

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
_APP = QApplication.instance() or QApplication([])


def test_pdf_export_worker_success(mocker: Any) -> None:
    """Emite finished con la ruta resuelta al exportar el PDF correctamente."""
    mock_vm = mocker.Mock(spec=SavingsViewModel)
    mock_vm.export_sustainability_pdf.return_value = "/tmp/test_audit.pdf"
    worker = PdfExportWorker(mock_vm)
    received: list[str] = []
    worker.signals.finished.connect(received.append)

    worker.run()

    assert received == [str(Path("/tmp/test_audit.pdf").resolve())]
    mock_vm.export_sustainability_pdf.assert_called_once_with()


def test_pdf_export_worker_failure(mocker: Any) -> None:
    """Emite failed con el mensaje de error si falla la exportación del PDF."""
    mock_vm = mocker.Mock(spec=SavingsViewModel)
    mock_vm.export_sustainability_pdf.side_effect = RuntimeError("Disk full")
    worker = PdfExportWorker(mock_vm)
    errors: list[str] = []
    worker.signals.failed.connect(errors.append)

    worker.run()

    assert errors == ["Disk full"]
    mock_vm.export_sustainability_pdf.assert_called_once_with()
