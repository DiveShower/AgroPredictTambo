"""Evaluador de métricas y baselines comparativos para modelos de estrés térmico."""

from collections.abc import Sequence
from typing import Any

import pandas as pd
from sklearn import metrics
from sklearn.tree import DecisionTreeClassifier

CLASSES = [0, 1, 2]


def _predict_static_thi(thi_values: Any) -> list[int]:
    """Regla baseline de ITH estático (<72 normal, <78 alerta, >=78 peligro)."""
    return [0 if thi < 72.0 else (1 if thi < 78.0 else 2) for thi in thi_values]


def _per_class_metric(metric_fn: Any, y_true: Any, y_pred: Any) -> list[float]:
    """Calcula métricas por clase [0, 1, 2] redondeadas a 4 decimales."""
    scores = metric_fn(y_true, y_pred, labels=CLASSES, average=None, zero_division=0)
    return [round(float(val), 4) for val in scores]


def evaluate_classifier_metrics(
    model: Any,
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    test_thi: pd.Series,
    feature_columns: Sequence[str],
) -> dict[str, Any]:
    """Evalúa modelo final frente a baselines estático y DecisionTree."""
    static_acc = float(metrics.accuracy_score(y_test, _predict_static_thi(test_thi)))
    tree = DecisionTreeClassifier(max_depth=5, random_state=42).fit(X_train, y_train)
    tree_acc = float(metrics.accuracy_score(y_test, tree.predict(X_test)))

    y_pred = model.predict(X_test)
    recalls = _per_class_metric(metrics.recall_score, y_test, y_pred)
    matrix = metrics.confusion_matrix(y_test, y_pred, labels=CLASSES).tolist()
    return {
        "accuracy": round(float(metrics.accuracy_score(y_test, y_pred)), 4),
        "recall_danger": recalls[2],
        "precision_per_class": _per_class_metric(
            metrics.precision_score, y_test, y_pred
        ),
        "recall_per_class": recalls,
        "confusion_matrix": [[int(c) for c in row] for row in matrix],
        "baseline_tree_accuracy": round(tree_acc, 4),
        "static_thi_accuracy": round(static_acc, 4),
        "feature_columns": list(feature_columns),
        "train_rows": len(X_train),
        "test_rows": len(X_test),
    }
