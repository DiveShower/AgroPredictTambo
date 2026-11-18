"""Worker QThread asíncrono para ingesta climática e inferencia ML sin bloquear UI."""

from collections.abc import Callable

from PyQt6.QtCore import QObject, QThread, pyqtSignal

from src.adapters.desktop.viewmodels.scada_viewmodel import ScadaViewModel
from src.domain.ports.model_predictor_port import IModelPredictor


class WeatherSyncWorker(QThread):
    """Ejecuta peticiones HTTP e inferencia ML en segundo plano (60 fps UI)."""

    weather_synced = pyqtSignal(object)
    prediction_ready = pyqtSignal(object)
    sync_failed = pyqtSignal(str)

    def __init__(
        self,
        viewmodel: ScadaViewModel | None = None,
        lat: float = -31.25,
        lon: float = -61.48,
        predictor: IModelPredictor | None = None,
        predict_fn: Callable[[], object] | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._viewmodel = viewmodel
        self._lat = lat
        self._lon = lon
        self._predictor = predictor
        self._predict_fn = predict_fn

    def run(self) -> None:
        """Invoca el caso de uso e inferencia ML fuera del hilo principal de Qt."""
        try:
            if self._predict_fn:
                res = self._predict_fn()
                self.prediction_ready.emit(res)
                return
            if self._viewmodel:
                res = self._viewmodel.sync_weather_and_predict(self._lat, self._lon)
                self.weather_synced.emit(res)
                self.prediction_ready.emit(res)
        except Exception as exc:  # noqa: BLE001
            self.sync_failed.emit(str(exc))

    def stop(self) -> None:
        """Detiene limpiamente el hilo esperando su finalización."""
        self.quit()
        self.wait(2000)
