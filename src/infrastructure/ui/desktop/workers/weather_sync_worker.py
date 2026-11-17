"""Worker QThread asíncrono para ingesta climática e inferencia ML sin bloquear UI."""

from typing import Optional

from PyQt6.QtCore import QObject, QThread, pyqtSignal

from src.adapters.desktop.viewmodels.scada_viewmodel import ScadaViewModel


class WeatherSyncWorker(QThread):
    """Ejecuta peticiones HTTP y predicciones en segundo plano (60 fps UI)."""

    weather_synced = pyqtSignal(object)
    sync_failed = pyqtSignal(str)

    def __init__(
        self,
        viewmodel: ScadaViewModel,
        lat: float = -31.25,
        lon: float = -61.48,
        parent: Optional[QObject] = None,
    ) -> None:
        super().__init__(parent)
        self._viewmodel = viewmodel
        self._lat = lat
        self._lon = lon

    def run(self) -> None:
        """Invoca el caso de uso de predicción fuera del hilo principal de Qt."""
        try:
            response = self._viewmodel.sync_weather_and_predict(
                self._lat, self._lon
            )
            self.weather_synced.emit(response)
        except Exception as exc:
            self.sync_failed.emit(str(exc))

    def stop(self) -> None:
        """Detiene limpiamente el hilo esperando su finalización."""
        self.quit()
        self.wait(2000)
