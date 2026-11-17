"""Tests TDD para métricas y artefactos del pipeline de entrenamiento."""

import json
from pathlib import Path

import joblib

from data.scripts.generate_synthetic_dataset import save_synthetic_dataset
from src.infrastructure.ml.feature_builder import FEATURE_COLUMNS
from src.infrastructure.ml.train_pipeline import train_and_evaluate


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
