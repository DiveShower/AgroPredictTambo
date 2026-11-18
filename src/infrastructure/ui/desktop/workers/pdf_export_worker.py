"""Worker QRunnable asíncrono para exportación de informe PDF sin bloquear UI."""

from pathlib import Path

from PyQt6.QtCore import QObject, QRunnable, pyqtSignal

from src.adapters.desktop.viewmodels.savings_viewmodel import SavingsViewModel


class PdfExportWorkerSignals(QObject):
    """Señales Qt emitidas al completar o fallar la exportación del PDF."""

    finished = pyqtSignal(str)
    failed = pyqtSignal(str)


class PdfExportWorker(QRunnable):
    """Ejecuta la generación del informe de sustentabilidad en QThreadPool."""

    def __init__(self, viewmodel: SavingsViewModel) -> None:
        super().__init__()
        self.signals = PdfExportWorkerSignals()
        self._viewmodel = viewmodel

    def run(self) -> None:
        """Exporta el PDF de sustentabilidad fuera del hilo principal de Qt."""
        try:
            path = self._viewmodel.export_sustainability_pdf()
            abs_path = str(Path(path).resolve()) if path else ""
            self.signals.finished.emit(abs_path)
        except Exception as exc:  # noqa: BLE001
            self.signals.failed.emit(str(exc))
