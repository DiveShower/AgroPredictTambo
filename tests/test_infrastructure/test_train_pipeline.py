"""Tests TDD para el pipeline de entrenamiento temporal sin data leakage."""

import pandas as pd

from src.infrastructure.ml.train_pipeline import temporal_train_test_split


def test_temporal_split_preserves_chronological_order() -> None:
    timestamps = pd.date_range("2026-01-01 00:00:00", periods=100, freq="1h")
    df = pd.DataFrame(
        {
            "timestamp": timestamps.astype(str),
            "temperature_c": list(range(100)),
        }
    )
    shuffled = df.sample(frac=1.0, random_state=42).reset_index(drop=True)

    train, test = temporal_train_test_split(shuffled, train_ratio=0.8)

    assert len(train) == 80
    assert len(test) == 20
    assert pd.to_datetime(train["timestamp"]).is_monotonic_increasing
    assert pd.to_datetime(test["timestamp"]).is_monotonic_increasing
    assert (
        pd.to_datetime(train["timestamp"]).max()
        < pd.to_datetime(test["timestamp"]).min()
    )
