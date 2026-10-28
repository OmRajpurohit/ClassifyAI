"""Unit tests for ClassifyAI model evaluation, training, and ranking services.

Verifies:
- Metric computation across binary and multiclass tasks.
- ROC-AUC resilience when probabilities are missing or invalid (returns None, not 0.0).
- Stratified cross-validation fold sizing and automated adjustments.
- Isolated failure handling during cross-validation.
- Train / Held-out Test stratified partitioning.
- Confusion Matrix generation and Feature Importance extraction.
- Deterministic multi-tier model ranking and tie-breaking.
- Statistical ambiguity detection and majority-class baseline warnings.
"""

import numpy as np
import pandas as pd
import pytest
from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from app.algorithms import build_classifier
from app.services.model_evaluator import (
    MetricSummary,
    ModelEvaluationResult,
    compute_metrics,
    determine_valid_cv_folds,
    evaluate_pipeline_cv,
)
from app.services.model_ranker import RankedModel, rank_models
from app.services.model_trainer import (
    extract_feature_importances,
    partition_dataset,
    train_and_evaluate_test_split,
)
from app.services.preprocessing import build_classification_pipeline


# -----------------------------------------------------------------------------
# Fixtures
# -----------------------------------------------------------------------------

@pytest.fixture
def synthetic_binary_df():
    """Generates a small DataFrame for binary classification."""
    X_arr, y_arr = make_classification(
        n_samples=60,
        n_features=4,
        n_informative=3,
        n_redundant=0,
        n_classes=2,
        weights=[0.7, 0.3],
        random_state=42,
    )
    df = pd.DataFrame(X_arr, columns=[f"feat_{i}" for i in range(4)])
    return df, y_arr


# -----------------------------------------------------------------------------
# Metric Computation Tests
# -----------------------------------------------------------------------------

def test_compute_metrics_binary():
    """Ensure standard metrics and ROC-AUC are accurately computed for binary classification."""
    y_true = np.array([0, 0, 1, 1, 1])
    y_pred = np.array([0, 0, 1, 1, 0])
    y_prob = np.array([
        [0.9, 0.1],
        [0.8, 0.2],
        [0.2, 0.8],
        [0.1, 0.9],
        [0.6, 0.4],
    ])

    metrics = compute_metrics(
        y_true=y_true,
        y_pred=y_pred,
        y_prob=y_prob,
        is_multiclass=False,
        n_classes=2,
    )

    assert metrics["accuracy"] == 0.8  # 4 out of 5
    assert metrics["balanced_accuracy"] is not None
    assert metrics["f1_weighted"] is not None
    assert metrics["roc_auc"] is not None
    assert 0.0 <= metrics["roc_auc"] <= 1.0


def test_compute_metrics_missing_probabilities_returns_none():
    """Ensure missing probabilities result in roc_auc=None instead of 0.0."""
    y_true = np.array([0, 1, 0, 1])
    y_pred = np.array([0, 1, 0, 1])

    metrics = compute_metrics(
        y_true=y_true,
        y_pred=y_pred,
        y_prob=None,  # No probabilities provided
        is_multiclass=False,
        n_classes=2,
    )

    assert metrics["accuracy"] == 1.0
    assert metrics["roc_auc"] is None


def test_compute_metrics_multiclass():
    """Ensure multiclass One-vs-Rest ROC-AUC and macro/weighted F1 are calculated."""
    y_true = np.array([0, 1, 2, 0, 1, 2])
    y_pred = np.array([0, 1, 2, 0, 2, 2])
    y_prob = np.array([
        [0.7, 0.2, 0.1],
        [0.1, 0.8, 0.1],
        [0.1, 0.1, 0.8],
        [0.6, 0.3, 0.1],
        [0.2, 0.3, 0.5],
        [0.1, 0.2, 0.7],
    ])

    metrics = compute_metrics(
        y_true=y_true,
        y_pred=y_pred,
        y_prob=y_prob,
        is_multiclass=True,
        n_classes=3,
    )

    assert metrics["accuracy"] == pytest.approx(5 / 6)
    assert metrics["f1_macro"] is not None
    assert metrics["f1_weighted"] is not None
    assert metrics["roc_auc"] is not None


# -----------------------------------------------------------------------------
# Cross-Validation Evaluator Tests
# -----------------------------------------------------------------------------

def test_determine_valid_cv_folds_standard():
    """Ensure requested 5 folds are honored when class counts are sufficient."""
    y = np.array([0] * 50 + [1] * 30)
    folds, notes = determine_valid_cv_folds(y, requested_folds=5)
    assert folds == 5
    assert len(notes) == 0


def test_determine_valid_cv_folds_adjusted_for_small_minority():
    """Ensure folds are reduced automatically when minority class has fewer samples than requested."""
    y = np.array([0] * 20 + [1] * 3)  # Minority class has only 3 samples
    folds, notes = determine_valid_cv_folds(y, requested_folds=5)
    assert folds == 3
    assert any("Adjusted cross-validation folds" in note for note in notes)


def test_determine_valid_cv_folds_fails_on_singleton():
    """Ensure ValueError is raised if minority class has only 1 sample."""
    y = np.array([0] * 20 + [1] * 1)
    with pytest.raises(ValueError, match="requires at least 2 samples per class"):
        determine_valid_cv_folds(y, requested_folds=5)


def test_evaluate_pipeline_cv_success(synthetic_binary_df):
    """Ensure cross-validation computes fold summaries and timing accurately."""
    X, y = synthetic_binary_df
    pipe = build_classification_pipeline(
        estimator=RandomForestClassifier(n_estimators=10, random_state=42),
        numeric_features=list(X.columns),
        categorical_features=[],
        requires_scaling=False,
    )

    res = evaluate_pipeline_cv(
        pipeline=pipe,
        algorithm_id="random_forest",
        algorithm_name="Random Forest",
        X=X,
        y=y,
        n_splits=3,
        random_state=42,
    )

    assert res.status == "success"
    assert res.training_duration_seconds > 0
    assert res.prediction_duration_seconds > 0
    assert res.cv_folds_used == 3
    assert "accuracy" in res.metrics
    assert res.metrics["accuracy"].mean is not None
    assert len(res.metrics["accuracy"].fold_values) == 3


def test_evaluate_pipeline_cv_error_isolation(synthetic_binary_df):
    """Ensure a crashing pipeline records an isolated error without breaking execution."""
    X, y = synthetic_binary_df

    class BrokenEstimator(LogisticRegression):
        def fit(self, X, y):
            raise RuntimeError("Simulated algorithm crash during training.")

    pipe = Pipeline([("classifier", BrokenEstimator())])
    res = evaluate_pipeline_cv(
        pipeline=pipe,
        algorithm_id="broken",
        algorithm_name="Broken Model",
        X=X,
        y=y,
        n_splits=2,
    )

    assert res.status == "failed"
    assert "Simulated algorithm crash" in res.error_message


# -----------------------------------------------------------------------------
# Model Trainer & Feature Importance Tests
# -----------------------------------------------------------------------------

def test_partition_dataset(synthetic_binary_df):
    """Ensure stratified train/test split maintains target class proportions."""
    X, y = synthetic_binary_df
    X_train, X_test, y_train, y_test, notes = partition_dataset(X, y, test_size=0.2, random_state=42)

    assert len(X_train) == 48
    assert len(X_test) == 12
    assert len(y_train) == 48
    assert len(y_test) == 12
    # Verify stratification
    assert pytest.approx(np.mean(y_train), abs=0.05) == np.mean(y_test)


def test_train_and_evaluate_test_split(synthetic_binary_df):
    """Ensure final model fitting produces valid test metrics, confusion matrix, and feature importances."""
    X, y = synthetic_binary_df
    X_train, X_test, y_train, y_test, _ = partition_dataset(X, y, test_size=0.2, random_state=42)

    pipe = build_classification_pipeline(
        estimator=RandomForestClassifier(n_estimators=10, random_state=42),
        numeric_features=list(X.columns),
        categorical_features=[],
        requires_scaling=False,
    )

    result = train_and_evaluate_test_split(
        pipeline=pipe,
        X_train=X_train,
        y_train=y_train,
        X_test=X_test,
        y_test=y_test,
        class_names=["Negative", "Positive"],
    )

    assert result["has_test_evaluation"] is True
    assert "test_metrics" in result
    assert result["test_metrics"]["accuracy"] is not None

    # Confusion matrix structure
    cm = result["confusion_matrix"]
    assert cm["labels"] == ["Negative", "Positive"]
    assert len(cm["matrix"]) == 2
    assert len(cm["matrix"][0]) == 2

    # Feature importance structure
    importances = result["feature_importances"]
    assert len(importances) == 4
    assert sum(item["importance"] for item in importances) == pytest.approx(100.0, abs=1e-1)


# -----------------------------------------------------------------------------
# Model Ranker Tests
# -----------------------------------------------------------------------------

def test_rank_models_ordering_and_tie_breaking():
    """Ensure models are ranked deterministically by primary score and tiebreakers."""
    m1 = ModelEvaluationResult(
        algorithm_id="algo_1",
        algorithm_name="Model 1 (Lower Score)",
        status="success",
        metrics={
            "f1_weighted": MetricSummary(mean=0.80, std=0.02),
            "balanced_accuracy": MetricSummary(mean=0.79, std=0.02),
        },
        training_duration_seconds=0.5,
        prediction_duration_seconds=0.01,
    )

    m2 = ModelEvaluationResult(
        algorithm_id="algo_2",
        algorithm_name="Model 2 (Higher Score)",
        status="success",
        metrics={
            "f1_weighted": MetricSummary(mean=0.92, std=0.01),
            "balanced_accuracy": MetricSummary(mean=0.90, std=0.01),
        },
        training_duration_seconds=0.8,
        prediction_duration_seconds=0.02,
    )

    # Identical score to m2, but higher std (less stable)
    m3 = ModelEvaluationResult(
        algorithm_id="algo_3",
        algorithm_name="Model 3 (Tied Score, High Std)",
        status="success",
        metrics={
            "f1_weighted": MetricSummary(mean=0.92, std=0.05),
            "balanced_accuracy": MetricSummary(mean=0.90, std=0.05),
        },
        training_duration_seconds=0.4,
        prediction_duration_seconds=0.01,
    )

    ranking = rank_models([m1, m2, m3], primary_metric="f1_weighted")

    assert ranking.winner.algorithm_id == "algo_2"  # Lower std wins tie!
    assert ranking.runner_up.algorithm_id == "algo_3"
    assert ranking.ranked_models[2].algorithm_id == "algo_1"
    assert ranking.score_difference == 0.0  # Difference between #1 and #2 is 0.0


def test_rank_models_detects_poor_performance_against_baseline():
    """Ensure poor performance warning is triggered when best score barely beats majority baseline."""
    m_poor = ModelEvaluationResult(
        algorithm_id="dummy_like",
        algorithm_name="Dummy Like Model",
        status="success",
        metrics={
            "accuracy": MetricSummary(mean=0.71, std=0.01),
            "balanced_accuracy": MetricSummary(mean=0.51, std=0.01),
        },
        training_duration_seconds=0.1,
        prediction_duration_seconds=0.01,
    )

    # Majority class baseline is 70% (0.70)
    ranking = rank_models([m_poor], primary_metric="accuracy", majority_class_baseline=0.70)
    assert ranking.poor_performance_warning is not None
    assert "comparable to a trivial" in ranking.poor_performance_warning


def test_rank_models_handles_all_failed():
    """Ensure ranker handles experiments where all models failed gracefully."""
    m_failed = ModelEvaluationResult(
        algorithm_id="failing_algo",
        algorithm_name="Failing Algo",
        status="failed",
        metrics={},
        training_duration_seconds=0.0,
        prediction_duration_seconds=0.0,
        error_message="Severe solver divergence",
    )

    ranking = rank_models([m_failed], primary_metric="f1_weighted")
    assert ranking.winner is None
    assert len(ranking.failed_models) == 1
    assert "No models completed cross-validation" in ranking.summary_explanation
