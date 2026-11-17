"""Worker QThread para sincronización en vivo entre el Bot de Telegram y el SCADA."""

from typing import Optional

from PyQt6.QtCore import QObject, QThread, pyqtSignal

from src.adapters.desktop.viewmodels.scada_viewmodel import ScadaViewModel


class TelegramBotWorker(QThread):
    """Escucha comandos móviles y emite señal para refrescar el SCADA en <100 ms."""

    sector_state_changed = pyqtSignal()
    command_received = pyqtSignal(str)

    def __init__(
        self,
        viewmodel: ScadaViewModel,
        parent: Optional[QObject] = None,
    ) -> None:
        super().__init__(parent)
        self._viewmodel = viewmodel
        self._running = False

    def apply_remote_occupancy(
        self, sector_id: str, is_occupied: bool
    ) -> None:
        """Aplica el comando /ocupar sobre el repositorio compartido y notifica a Qt."""
        self._viewmodel.toggle_occupancy(sector_id, is_occupied)
        self.command_received.emit(f"/ocupar {sector_id} {is_occupied}")
        self.sector_state_changed.emit()

    def run(self) -> None:
        """Mantiene el hilo de sincronización activo hasta solicitar stop()."""
        self._running = True
        while self._running:
            self.msleep(100)

    def stop(self) -> None:
        """Solicita el cierre limpio del hilo y aguarda su terminación."""
        self._running = False
        self.quit()
        self.wait(2000)
