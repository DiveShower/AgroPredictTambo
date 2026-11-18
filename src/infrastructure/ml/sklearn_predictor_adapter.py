"""Adaptador de inferencia ML con Random Forest y fallback heurístico."""

from collections.abc import Sequence
from pathlib import Path
from pickle import UnpicklingError
from typing import Any

import joblib

from src.domain.ports.model_predictor_port import IModelPredictor
from src.domain.value_objects.weather_conditions import WeatherConditions
from src.infrastructure.ml.feature_builder import build_feature_vector
from src.infrastructure.ml.heuristic_predictor_adapter import HeuristicPredictorAdapter
from src.infrastructure.ml.inference_lru_cache import InferenceLruCache

DEFAULT_PATH = Path(__file__).parent / "artifacts" / "heat_stress_classifier.joblib"


class SklearnPredictorAdapter(IModelPredictor):
    """Adaptador de inferencia Scikit-Learn con fallback automático."""

    def __init__(
        self,
        model_path: Path | str | None = None,
        fallback: IModelPredictor | None = None,
        cache_size: int = 128,
    ) -> None:
        self._path = Path(model_path) if model_path else DEFAULT_PATH
        self._fallback = fallback or HeuristicPredictorAdapter()
        self._model: Any | None = self._load()
        self._cache = InferenceLruCache(maxsize=cache_size)

    def _load(self) -> Any | None:
        try:
            return joblib.load(self._path) if self._path.exists() else None
        except (OSError, EOFError, ValueError, TypeError, UnpicklingError):
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
        args = (conditions, recent_history, nocturnal_debt_hours)
        if self._model is not None:
            try:
                vec = build_feature_vector(*args)
                return self._cache.get_or_predict(self._model, vec)
            except (ValueError, TypeError, RuntimeError, AttributeError, KeyError):
                pass
        return self._fallback.predict_stress_level(*args)
