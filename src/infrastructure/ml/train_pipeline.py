"""Pipeline de entrenamiento temporal y evaluación comparativa de estrés calórico."""

import json
import sys
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn import metrics
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier

ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.infrastructure.ml.feature_builder import (
    FEATURE_COLUMNS,
    extract_training_matrix,
)

DEFAULT_DATASET_PATH = (
    ROOT_DIR / "data" / "processed" / "weather_heat_stress_dataset.csv"
)
DEFAULT_ARTIFACTS_DIR = Path(__file__).resolve().parent / "artifacts"
CLASSES = [0, 1, 2]


def temporal_train_test_split(
    df: pd.DataFrame,
    train_ratio: float = 0.8,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Ordena cronológicamente por timestamp y divide sin fuga temporal."""
    ordered = df.assign(_ts=pd.to_datetime(df["timestamp"])).sort_values("_ts")
    ordered = ordered.drop(columns=["_ts"]).reset_index(drop=True)
    split_idx = int(len(ordered) * train_ratio)
    train_df = ordered.iloc[:split_idx].reset_index(drop=True)
    test_df = ordered.iloc[split_idx:].reset_index(drop=True)
    return train_df, test_df


def _predict_static_thi(thi_values: Any) -> list[int]:
    """Regla baseline de ITH estático (<72 normal, <78 alerta, >=78 peligro)."""
    return [0 if thi < 72.0 else (1 if thi < 78.0 else 2) for thi in thi_values]


def _per_class_metric(metric_fn: Any, y_true: Any, y_pred: Any) -> list[float]:
    """Calcula métricas por clase [0, 1, 2] redondeadas a 4 decimales."""
    scores = metric_fn(y_true, y_pred, labels=CLASSES, average=None, zero_division=0)
    return [round(float(v), 4) for v in scores]


def train_and_evaluate(
    dataset_path: Path = DEFAULT_DATASET_PATH,
    artifacts_dir: Path = DEFAULT_ARTIFACTS_DIR,
) -> dict[str, Any]:
    """Entrena baselines y RandomForest final, exporta artefactos y reporta métricas."""
    train_df, test_df = temporal_train_test_split(pd.read_csv(dataset_path))
    X_train = extract_training_matrix(train_df)
    X_test = extract_training_matrix(test_df)
    y_train = train_df["stress_level"].astype(int)
    y_test = test_df["stress_level"].astype(int)

    static_preds = _predict_static_thi(test_df["thi_calculated"])
    static_acc = float(metrics.accuracy_score(y_test, static_preds))

    tree = DecisionTreeClassifier(max_depth=5, random_state=42).fit(X_train, y_train)
    tree_acc = float(metrics.accuracy_score(y_test, tree.predict(X_test)))

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=12,
        class_weight="balanced_subsample",
        random_state=42,
        n_jobs=-1,
    ).fit(X_train, y_train)
    y_pred = model.predict(X_test)

    recalls = _per_class_metric(metrics.recall_score, y_test, y_pred)
    matrix = metrics.confusion_matrix(y_test, y_pred, labels=CLASSES).tolist()
    report: dict[str, Any] = {
        "accuracy": round(float(metrics.accuracy_score(y_test, y_pred)), 4),
        "recall_danger": recalls[2],
        "precision_per_class": _per_class_metric(
            metrics.precision_score, y_test, y_pred
        ),
        "recall_per_class": recalls,
        "confusion_matrix": [[int(c) for c in row] for row in matrix],
        "baseline_tree_accuracy": round(tree_acc, 4),
        "static_thi_accuracy": round(static_acc, 4),
        "feature_columns": list(FEATURE_COLUMNS),
        "train_rows": len(train_df),
        "test_rows": len(test_df),
    }

    artifacts_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, artifacts_dir / "heat_stress_classifier.joblib")
    report_json = json.dumps(report, indent=2)
    (artifacts_dir / "training_report.json").write_text(report_json, encoding="utf-8")
    return report


if __name__ == "__main__":
    print(json.dumps(train_and_evaluate(), indent=2))
