"""Model Evaluation and Cross-Validation Service for ClassifyAI.

Implements rigorous evaluation methodologies:
- Stratified K-Fold Cross-Validation ensuring identical fold partitions across models.
- Support for comprehensive classification metrics:
  Accuracy, Precision, Recall, F1, Macro-F1, Weighted-F1, Balanced Accuracy, ROC-AUC.
- Accurate wall-clock timing for training and inference latency.
- Safe metrics calculation: handles edge-case zero-division and missing probabilities (returns None, not 0.0).
- Graceful error isolation: records individual model failures without aborting the experiment.
"""

from dataclasses import dataclass, field
import time
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, clone
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold

# Recognized primary and secondary metrics supported by ClassifyAI
SUPPORTED_METRICS = {
    "accuracy": "Accuracy",
    "balanced_accuracy": "Balanced Accuracy",
    "f1_weighted": "F1-Score (Weighted)",
    "f1_macro": "F1-Score (Macro)",
    "precision_weighted": "Precision (Weighted)",
    "recall_weighted": "Recall (Weighted)",
    "roc_auc": "ROC-AUC",
}


@dataclass
class MetricSummary:
    """Mean and standard deviation summary for an individual metric across CV folds."""

    mean: Optional[float]
    std: Optional[float]
    fold_values: List[Optional[float]] = field(default_factory=list)


@dataclass
class ModelEvaluationResult:
    """Detailed evaluation record for a single classification pipeline."""

    algorithm_id: str
    algorithm_name: str
    status: str  # "success" or "failed"
    metrics: Dict[str, MetricSummary]
    training_duration_seconds: float
    prediction_duration_seconds: float
    error_message: Optional[str] = None
    cv_folds_used: int = 5
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert evaluation result into a JSON-serializable dictionary."""
        metrics_dict = {}
        for k, v in self.metrics.items():
            metrics_dict[k] = {
                "mean": round(v.mean, 4) if v.mean is not None else None,
                "std": round(v.std, 4) if v.std is not None else None,
                "fold_values": [round(val, 4) if val is not None else None for val in v.fold_values],
            }

        return {
            "algorithm_id": self.algorithm_id,
            "algorithm_name": self.algorithm_name,
            "status": self.status,
            "metrics": metrics_dict,
            "training_duration_seconds": round(self.training_duration_seconds, 4),
            "prediction_duration_seconds": round(self.prediction_duration_seconds, 4),
            "error_message": self.error_message,
            "cv_folds_used": self.cv_folds_used,
            "notes": self.notes,
        }


def compute_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_prob: Optional[np.ndarray],
    is_multiclass: bool,
    n_classes: int,
) -> Dict[str, Optional[float]]:
    """Compute comprehensive classification performance metrics for a single prediction fold.

    Educational Significance:
    -------------------------
    - Accuracy measures overall correct classifications, but can be misleading for imbalanced data.
    - Balanced Accuracy calculates average recall per class, compensating for unequal class frequencies.
    - Macro-F1 gives equal weight to all classes, highlighting poor minority class performance.
    - Weighted-F1 weights per-class F1 by class support.
    - ROC-AUC measures discrimination capability across decision thresholds.
      If probabilities or required class representations are unavailable, returns None with explanation.

    Args:
        y_true: Ground truth target labels.
        y_pred: Model predicted class labels.
        y_prob: Model predicted class probabilities (None if unsupported).
        is_multiclass: Whether the problem is multiclass (> 2 classes).
        n_classes: Total number of distinct classes.

    Returns:
        Dict[str, Optional[float]]: Dictionary of calculated metric values.
    """
    res: Dict[str, Optional[float]] = {}

    # 1. Base Accuracy
    res["accuracy"] = float(accuracy_score(y_true, y_pred))

    # 2. Balanced Accuracy
    res["balanced_accuracy"] = float(balanced_accuracy_score(y_true, y_pred))

    # 3. Precision (Weighted)
    res["precision_weighted"] = float(
        precision_score(y_true, y_pred, average="weighted", zero_division=0)
    )

    # 4. Recall (Weighted)
    res["recall_weighted"] = float(
        recall_score(y_true, y_pred, average="weighted", zero_division=0)
    )

    # 5. F1-Score (Weighted)
    res["f1_weighted"] = float(
        f1_score(y_true, y_pred, average="weighted", zero_division=0)
    )

    # 6. F1-Score (Macro)
    res["f1_macro"] = float(
        f1_score(y_true, y_pred, average="macro", zero_division=0)
    )

    # 7. ROC-AUC calculation (guarded against unsupported scenarios)
    res["roc_auc"] = None
    if y_prob is not None:
        try:
            if not is_multiclass:
                # Binary classification: use probability of the positive class (column 1)
                if y_prob.shape[1] >= 2 and len(np.unique(y_true)) >= 2:
                    res["roc_auc"] = float(roc_auc_score(y_true, y_prob[:, 1]))
            else:
                # Multiclass classification: compute One-vs-Rest (OvR) weighted ROC-AUC
                unique_y = np.unique(y_true)
                if len(unique_y) == n_classes and y_prob.shape[1] == n_classes:
                    res["roc_auc"] = float(
                        roc_auc_score(y_true, y_prob, multi_class="ovr", average="weighted")
                    )
        except Exception:
            # If fold misses a class or ROC-AUC cannot be computed, maintain None (never fabricate 0.0)
            res["roc_auc"] = None

    return res


def determine_valid_cv_folds(y: np.ndarray, requested_folds: int = 5) -> Tuple[int, List[str]]:
    """Determine a statistically valid fold count for Stratified K-Fold.

    Rule:
    In Stratified K-Fold, each fold must contain at least 1 sample from each class.
    Therefore: n_splits <= min(sample_count_per_class).

    Args:
        y: Target label array.
        requested_folds: User requested fold count (default 5).

    Returns:
        Tuple[int, List[str]]: (Valid fold count, Notes/explanations if adjusted).
    """
    notes = []
    _, class_counts = np.unique(y, return_counts=True)
    min_class_samples = int(np.min(class_counts))

    if min_class_samples < 2:
        raise ValueError(
            f"The minority class has only {min_class_samples} sample(s). "
            f"Cross-validation requires at least 2 samples per class."
        )

    valid_folds = requested_folds
    if min_class_samples < requested_folds:
        valid_folds = max(2, min_class_samples)
        notes.append(
            f"Adjusted cross-validation folds from {requested_folds} to {valid_folds} "
            f"because the minority class contains only {min_class_samples} samples."
        )

    return valid_folds, notes


def evaluate_pipeline_cv(
    pipeline: BaseEstimator,
    algorithm_id: str,
    algorithm_name: str,
    X: pd.DataFrame,
    y: np.ndarray,
    n_splits: int = 5,
    random_state: int = 42,
) -> ModelEvaluationResult:
    """Evaluate a Scikit-Learn Pipeline using Stratified K-Fold cross-validation.

    Methodology:
    1. Uses StratifiedKFold with fixed random_state to ensure identical data splits.
    2. Deep copies the unfitted pipeline for each fold via `clone()`.
    3. Fits the complete pipeline (preprocessing + model) exclusively on the training fold.
    4. Evaluates predictions and probabilities on the held-out validation fold.
    5. Computes fold-level metrics and aggregates them into mean and standard deviation.

    Args:
        pipeline: Unfitted Scikit-Learn Pipeline.
        algorithm_id: Identifier of the algorithm.
        algorithm_name: Human-readable algorithm name.
        X: Feature DataFrame.
        y: Integer-encoded target array.
        n_splits: Number of stratified folds.
        random_state: Seed for cross-validation splitting.

    Returns:
        ModelEvaluationResult: Structured evaluation with fold details and timing.
    """
    total_start_time = time.perf_counter()
    n_classes = len(np.unique(y))
    is_multiclass = n_classes > 2

    valid_folds, adjustment_notes = determine_valid_cv_folds(y, n_splits)
    cv = StratifiedKFold(n_splits=valid_folds, shuffle=True, random_state=random_state)

    fold_metrics_accumulator: Dict[str, List[Optional[float]]] = {
        m: [] for m in SUPPORTED_METRICS.keys()
    }

    total_training_time = 0.0
    total_prediction_time = 0.0

    try:
        for fold_idx, (train_idx, val_idx) in enumerate(cv.split(X, y)):
            X_train_fold, X_val_fold = X.iloc[train_idx], X.iloc[val_idx]
            y_train_fold, y_val_fold = y[train_idx], y[val_idx]

            fold_pipeline = clone(pipeline)

            # Measure training latency
            t_train_start = time.perf_counter()
            fold_pipeline.fit(X_train_fold, y_train_fold)
            total_training_time += time.perf_counter() - t_train_start

            # Measure prediction latency
            t_pred_start = time.perf_counter()
            y_pred = fold_pipeline.predict(X_val_fold)
            total_prediction_time += time.perf_counter() - t_pred_start

            # Predict probabilities if supported
            y_prob = None
            if hasattr(fold_pipeline, "predict_proba"):
                try:
                    y_prob = fold_pipeline.predict_proba(X_val_fold)
                except Exception:
                    y_prob = None

            # Calculate fold metrics
            fold_results = compute_metrics(
                y_true=y_val_fold,
                y_pred=y_pred,
                y_prob=y_prob,
                is_multiclass=is_multiclass,
                n_classes=n_classes,
            )

            for metric_key, metric_val in fold_results.items():
                fold_metrics_accumulator[metric_key].append(metric_val)

        # Aggregate across folds into mean and std
        summary_metrics: Dict[str, MetricSummary] = {}
        for metric_key, values in fold_metrics_accumulator.items():
            valid_values = [v for v in values if v is not None]
            if valid_values:
                mean_val = float(np.mean(valid_values))
                std_val = float(np.std(valid_values))
            else:
                mean_val = None
                std_val = None

            summary_metrics[metric_key] = MetricSummary(
                mean=mean_val,
                std=std_val,
                fold_values=values,
            )

        notes = list(adjustment_notes)
        if summary_metrics["roc_auc"].mean is None:
            notes.append("ROC-AUC metric is unavailable for this estimator or dataset configuration.")

        return ModelEvaluationResult(
            algorithm_id=algorithm_id,
            algorithm_name=algorithm_name,
            status="success",
            metrics=summary_metrics,
            training_duration_seconds=total_training_time,
            prediction_duration_seconds=total_prediction_time,
            cv_folds_used=valid_folds,
            notes=notes,
        )

    except Exception as exc:
        # Graceful failure isolation
        return ModelEvaluationResult(
            algorithm_id=algorithm_id,
            algorithm_name=algorithm_name,
            status="failed",
            metrics={},
            training_duration_seconds=total_training_time,
            prediction_duration_seconds=total_prediction_time,
            error_message=str(exc),
            cv_folds_used=valid_folds,
            notes=[f"Evaluation failed with error: {str(exc)}"],
        )
