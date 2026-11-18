"""Pruebas unitarias para InferenceLruCache."""

from unittest.mock import MagicMock

from src.infrastructure.ml.inference_lru_cache import InferenceLruCache


def _features(temp: float, rh: float = 60.0) -> list[float]:
    return [temp, rh, 10.0, 500.0, 14.0, 5.0, 72.0, 0.0]


def test_cache_hit_and_rounding() -> None:
    cache = InferenceLruCache(maxsize=4)
    model = MagicMock()
    model.predict.return_value = [1]

    first = cache.get_or_predict(model, _features(25.01, 60.02))
    second = cache.get_or_predict(model, _features(25.04, 60.04))

    assert first == 1
    assert second == 1
    assert len(cache) == 1
    model.predict.assert_called_once()


def test_cache_lru_eviction() -> None:
    cache = InferenceLruCache(maxsize=2)
    model = MagicMock()
    model.predict.side_effect = [[0], [1], [2], [1]]

    assert cache.get_or_predict(model, _features(20.0)) == 0
    assert cache.get_or_predict(model, _features(25.0)) == 1
    assert cache.get_or_predict(model, _features(20.0)) == 0
    assert cache.get_or_predict(model, _features(30.0)) == 2
    assert len(cache) == 2
    assert cache.get_or_predict(model, _features(20.0)) == 0
    assert model.predict.call_count == 3
    assert cache.get_or_predict(model, _features(25.0)) == 1
    assert model.predict.call_count == 4


def test_cache_clear_and_len() -> None:
    cache = InferenceLruCache(maxsize=4)
    model = MagicMock()
    model.predict.return_value = [2]

    assert len(cache) == 0
    cache.get_or_predict(model, _features(22.0))
    cache.get_or_predict(model, _features(28.0))
    assert len(cache) == 2
    cache.clear()
    assert len(cache) == 0
