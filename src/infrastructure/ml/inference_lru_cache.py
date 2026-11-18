"""Caché LRU para inferencias ML indexada por firma bioclimática."""

from collections import OrderedDict
from typing import Any

import pandas as pd

from src.infrastructure.ml.feature_builder import FEATURE_COLUMNS


class InferenceLruCache:
    """Caché LRU en memoria para predicciones de modelos según features."""

    def __init__(self, maxsize: int = 128) -> None:
        self._maxsize: int = maxsize
        self._cache: OrderedDict[tuple[float, ...], int] = OrderedDict()

    @property
    def maxsize(self) -> int:
        """Retorna el tamaño máximo configurado para la caché."""
        return self._maxsize

    def get_or_predict(self, model: Any, features: list[float]) -> int:
        """Retorna la predicción en caché o ejecuta inferencia y actualiza LRU."""
        key: tuple[float, ...] = tuple(round(x, 1) for x in features)
        if key in self._cache:
            self._cache.move_to_end(key)
            return self._cache[key]

        df = pd.DataFrame([features], columns=list(FEATURE_COLUMNS))
        prediction = int(model.predict(df)[0])
        self._cache[key] = prediction
        if len(self._cache) > self._maxsize:
            self._cache.popitem(last=False)
        return prediction

    def clear(self) -> None:
        """Vacía todas las entradas almacenadas en la caché."""
        self._cache.clear()

    def __len__(self) -> int:
        """Retorna la cantidad actual de entradas en caché."""
        return len(self._cache)
