"""Worker QThread para sincronización en vivo entre el Bot de Telegram y el SCADA."""

from PyQt6.QtCore import QObject, QThread, pyqtSignal

from src.adapters.desktop.viewmodels.scada_viewmodel import ScadaViewModel
from src.infrastructure.ui.telegram_bot.bot_command_router import TelegramCommandRouter


class TelegramBotWorker(QThread):
    """Escucha comandos móviles y emite señal para refrescar el SCADA en <100 ms."""

    sector_state_changed = pyqtSignal()
    command_received = pyqtSignal(str)

    def __init__(
        self,
        viewmodel: ScadaViewModel,
        parent: QObject | None = None,
        router: TelegramCommandRouter | None = None,
    ) -> None:
        super().__init__(parent)
        self._viewmodel, self._router, self._running = viewmodel, router, False

    def apply_remote_occupancy(self, sector_id: str, is_occupied: bool) -> None:
        """Aplica el comando /ocupar sobre el repositorio compartido y notifica a Qt."""
        self._viewmodel.toggle_occupancy(sector_id, is_occupied)
        self.command_received.emit(f"/ocupar {sector_id} {is_occupied}")
        self.sector_state_changed.emit()

    def process_command(self, raw_text: str, chat_id: int = 0) -> str:
        """Procesa un comando textual con el router o fallback local y notifica a Qt."""
        is_occupy = raw_text.strip().lower().startswith("/ocupar")
        if self._router is not None or not is_occupy:
            self.command_received.emit(raw_text)
            if self._router is None:
                return "Comando procesado."
            reply, _ = self._router.dispatch(raw_text, chat_id)
            if is_occupy:
                self.sector_state_changed.emit()
            return reply
        _, sid, raw = (raw_text.split() + ["", "", ""])[:3]
        if raw.lower() not in {"true", "1", "si", "sí", "false", "0", "no"}:
            return "Uso: /ocupar <sector_id> <true|false>"
        flag = raw.lower() in {"true", "1", "si", "sí"}
        self.apply_remote_occupancy(sid, flag)
        return f"Sector {sid} actualizado: {'OCUPADO' if flag else 'LIBRE'}"

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
