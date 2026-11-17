"""Tests TDD para el pipeline de entrenamiento temporal sin data leakage."""

import json
from pathlib import Path

import joblib
import pandas as pd
from src.infrastructure.ml.train_pipeline import (
    temporal_train_test_split,
    train_and_evaluate,
)

from data.scripts.generate_synthetic_dataset import save_synthetic_dataset
from src.infrastructure.ml.feature_builder import FEATURE_COLUMNS


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


def test_train_and_evaluate_exports_artifacts_and_meets_metrics(tmp_path: Path) -> None:
    csv_path = tmp_path / "dataset.csv"
    artifacts_dir = tmp_path / "artifacts"
    save_synthetic_dataset(csv_path, n_hours=2400)

    report = train_and_evaluate(dataset_path=csv_path, artifacts_dir=artifacts_dir)

    model_path = artifacts_dir / "heat_stress_classifier.joblib"
    report_path = artifacts_dir / "training_report.json"
    assert model_path.exists()
    assert report_path.exists()

    model = joblib.load(model_path)
    assert model.n_features_in_ == 8
    feature_names = list(model.feature_names_in_)
    assert "thi_calculated" not in feature_names
    assert "respiratory_rate_est" not in feature_names
    assert feature_names == list(FEATURE_COLUMNS)

    assert report["accuracy"] >= 0.85
    assert report["recall_danger"] >= 0.90
    assert report["train_rows"] + report["test_rows"] == 2400
    assert report["feature_columns"] == list(FEATURE_COLUMNS)
    for key in (
        "precision_per_class",
        "recall_per_class",
        "baseline_tree_accuracy",
        "static_thi_accuracy",
    ):
        assert key in report

    saved_report = json.loads(report_path.read_text(encoding="utf-8"))
    assert saved_report == report
    matrix = saved_report["confusion_matrix"]
    assert len(matrix) == 3
    assert all(len(row) == 3 for row in matrix)
