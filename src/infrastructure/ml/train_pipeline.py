"""Pipeline de entrenamiento temporal y evaluación de estrés calórico."""

import json
import sys
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.infrastructure.ml import feature_builder as fb
from src.infrastructure.ml.model_evaluator import evaluate_classifier_metrics

DEFAULT_DATASET_PATH = ROOT_DIR / "data/processed/weather_heat_stress_dataset.csv"
DEFAULT_ARTIFACTS_DIR = Path(__file__).resolve().parent / "artifacts"


def temporal_train_test_split(
    df: pd.DataFrame, train_ratio: float = 0.8
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Ordena cronológicamente por timestamp y divide sin fuga temporal."""
    clean = df.sort_values("timestamp", key=pd.to_datetime).reset_index(drop=True)
    cut = int(len(clean) * train_ratio)
    return clean.iloc[:cut].copy(), clean.iloc[cut:].reset_index(drop=True)


def train_and_evaluate(
    dataset_path: Path = DEFAULT_DATASET_PATH,
    artifacts_dir: Path = DEFAULT_ARTIFACTS_DIR,
) -> dict[str, Any]:
    """Entrena RandomForest sin data leakage, evalúa y exporta artefactos."""
    tr, te = temporal_train_test_split(pd.read_csv(dataset_path))
    x_tr, x_te = fb.extract_training_matrix(tr), fb.extract_training_matrix(te)
    y_tr: Any = tr["stress_level"].astype(int)
    y_te: Any = te["stress_level"].astype(int)
    thi_te: Any = te["thi_calculated"]
    rf_cfg: dict[str, Any] = {"n_estimators": 200, "max_depth": 12, "n_jobs": -1}
    model = RandomForestClassifier(
        **rf_cfg, class_weight="balanced_subsample", random_state=42
    ).fit(x_tr, y_tr)
    report = evaluate_classifier_metrics(
        model, x_tr, y_tr, x_te, y_te, thi_te, fb.FEATURE_COLUMNS
    )
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    model_path = artifacts_dir / "heat_stress_classifier.joblib"
    joblib.dump(model, model_path, compress=("zlib", 3))  # type: ignore[arg-type]
    out = artifacts_dir / "training_report.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


if __name__ == "__main__":
    print(json.dumps(train_and_evaluate(), indent=2))
