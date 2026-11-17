"""Adaptador de inferencia ML con Random Forest y fallback heurístico."""

from collections.abc import Sequence
from pathlib import Path
from typing import Any, Optional
import joblib
from src.domain.ports.model_predictor_port import IModelPredictor
from src.domain.value_objects.weather_conditions import WeatherConditions
from src.infrastructure.ml.feature_builder import build_inference_frame
from src.infrastructure.ml.heuristic_predictor_adapter import HeuristicPredictorAdapter

DEFAULT_PATH = Path(__file__).parent / "artifacts" / "heat_stress_classifier.joblib"


class SklearnPredictorAdapter(IModelPredictor):
    """Adaptador de inferencia Scikit-Learn con fallback automático."""

    def __init__(
        self,
        model_path: Optional[Path | str] = None,
        fallback: Optional[IModelPredictor] = None,
    ) -> None:
        self._path = Path(model_path) if model_path else DEFAULT_PATH
        self._fallback = fallback or HeuristicPredictorAdapter()
        self._model: Optional[Any] = self._load()

    def _load(self) -> Optional[Any]:
        if self._path.exists():
            try:
                return joblib.load(self._path)
            except Exception:
                return None
        return None

    @property
    def is_model_loaded(self) -> bool:
        """Indica si el modelo serializado está cargado en memoria."""
        return self._model is not None

    def predict_stress_level(
        self,
        conditions: WeatherConditions,
        recent_history: Sequence[WeatherConditions] = (),
        nocturnal_debt_hours: int = 0,
    ) -> int:
        """Predice nivel de estrés (0, 1 o 2) con el modelo o su fallback."""
        if self._model is not None:
            try:
                df = build_inference_frame(conditions, recent_history, nocturnal_debt_hours)
                return int(self._model.predict(df)[0])
            except Exception:
                pass
        return self._fallback.predict_stress_level(
            conditions, recent_history, nocturnal_debt_hours
        )
