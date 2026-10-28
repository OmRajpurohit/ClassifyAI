"""Model Training, Partitioning, and Held-Out Test Evaluation Service for ClassifyAI.

Responsibilities:
- Stratified Train / Held-Out Test partitioning.
- Fitting the final winning pipeline on the designated training partition.
- Computing unbiased held-out test metrics.
- Generating interactive Confusion Matrix data structures.
- Extracting and ranking normalized Feature Importances from fitted pipelines.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split

from app.services.model_evaluator import compute_metrics


def partition_dataset(
    X: pd.DataFrame,
    y: np.ndarray,
    test_size: float = 0.2,
    random_state: int = 42,
) -> Tuple[pd.DataFrame, Optional[pd.DataFrame], np.ndarray, Optional[np.ndarray], List[str]]:
    """Partition dataset into training and optional held-out test partitions using stratification.

    Methodology:
    - If test_size is 0, entire dataset is used for model selection via cross-validation.
    - If test_size > 0, the test split is sequestered until after model selection.

    Args:
        X: Feature matrix DataFrame.
        y: Target label array.
        test_size: Proportion of dataset reserved for held-out evaluation (e.g., 0.2).
        random_state: Seed for reproducible partitioning.

    Returns:
        Tuple: (X_train, X_test, y_train, y_test, notes).
    """
    notes = []
    if test_size <= 0.0:
        notes.append("No held-out test split requested. Entire dataset utilized for cross-validation.")
        return X, None, y, None, notes

    # Check that each class has at least 2 samples for stratified split
    _, class_counts = np.unique(y, return_counts=True)
    if np.min(class_counts) < 2:
        notes.append(
            "Stratified train/test splitting disabled because minority class has fewer than 2 samples. "
            "Using full dataset for cross-validation."
        )
        return X, None, y, None, notes

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        stratify=y,
        random_state=random_state,
    )

    notes.append(
        f"Partitioned dataset into {len(X_train)} training samples and "
        f"{len(X_test)} held-out test samples ({int(test_size * 100)}% split)."
    )

    return X_train, X_test, y_train, y_test, notes


def extract_feature_importances(
    fitted_pipeline: BaseEstimator,
    top_n: int = 15,
) -> List[Dict[str, Any]]:
    """Extract, normalize, and rank feature importances from a fitted Scikit-Learn Pipeline.

    Supports:
    - Tree-based models (Random Forest, Decision Tree, Gradient Boosting) via `feature_importances_`.
    - Linear models (Logistic Regression) via absolute coefficients `abs(coef_)`.

    Args:
        fitted_pipeline: A trained Pipeline containing 'preprocessor' and 'classifier'.
        top_n: Maximum number of top features to return.

    Returns:
        List[Dict[str, Any]]: Ranked list of feature dictionaries with 'feature' and 'importance'.
    """
    try:
        classifier = fitted_pipeline.named_steps["classifier"]
        preprocessor = fitted_pipeline.named_steps["preprocessor"]

        # Retrieve transformed feature names
        try:
            raw_feature_names = preprocessor.get_feature_names_out()
            # Clean prefixes like 'num__' and 'cat__' for human readability
            feature_names = [
                name.replace("num__", "").replace("cat__", "") for name in raw_feature_names
            ]
        except Exception:
            feature_names = [f"Feature_{i}" for i in range(100)]

        raw_scores = None

        # 1. Tree ensemble MDI / Gini feature importances
        if hasattr(classifier, "feature_importances_"):
            raw_scores = np.array(classifier.feature_importances_)

        # 2. Linear model coefficients
        elif hasattr(classifier, "coef_"):
            coef = np.array(classifier.coef_)
            if coef.ndim == 1:
                raw_scores = np.abs(coef)
            elif coef.shape[0] == 1:
                raw_scores = np.abs(coef[0])
            else:
                # Multiclass: take mean of absolute coefficients across all class hyperplanes
                raw_scores = np.mean(np.abs(coef), axis=0)

        if raw_scores is None or len(raw_scores) == 0:
            return []

        # Align length if discrepancy occurs
        min_len = min(len(feature_names), len(raw_scores))
        feature_names = feature_names[:min_len]
        raw_scores = raw_scores[:min_len]

        # Normalize to percentage (summing to 100%)
        total = float(np.sum(raw_scores))
        if total > 0:
            norm_scores = (raw_scores / total) * 100.0
        else:
            norm_scores = raw_scores

        ranked_indices = np.argsort(norm_scores)[::-1][:top_n]
        return [
            {
                "feature": feature_names[idx],
                "importance": round(float(norm_scores[idx]), 2),
            }
            for idx in ranked_indices
        ]

    except Exception:
        return []


def train_and_evaluate_test_split(
    pipeline: BaseEstimator,
    X_train: pd.DataFrame,
    y_train: np.ndarray,
    X_test: Optional[pd.DataFrame],
    y_test: Optional[np.ndarray],
    class_names: List[str],
) -> Dict[str, Any]:
    """Train the final pipeline on training data and evaluate against the held-out test split.

    Args:
        pipeline: Unfitted pipeline.
        X_train: Training features.
        y_train: Training labels.
        X_test: Optional held-out test features.
        y_test: Optional held-out test labels.
        class_names: Original string class names.

    Returns:
        Dict[str, Any]: Test metrics, confusion matrix, and feature importances.
    """
    # Fit the full pipeline on training split
    pipeline.fit(X_train, y_train)

    # Feature importance extraction
    feature_importances = extract_feature_importances(pipeline)

    if X_test is None or y_test is None:
        return {
            "has_test_evaluation": False,
            "test_metrics": None,
            "confusion_matrix": None,
            "feature_importances": feature_importances,
            "notes": ["No held-out test set evaluated."],
        }

    # Evaluate on held-out test split
    y_pred = pipeline.predict(X_test)
    y_prob = None
    if hasattr(pipeline, "predict_proba"):
        try:
            y_prob = pipeline.predict_proba(X_test)
        except Exception:
            y_prob = None

    n_classes = len(class_names)
    is_multiclass = n_classes > 2

    test_metrics = compute_metrics(
        y_true=y_test,
        y_pred=y_pred,
        y_prob=y_prob,
        is_multiclass=is_multiclass,
        n_classes=n_classes,
    )

    # Compute confusion matrix
    cm_array = confusion_matrix(y_test, y_pred)
    cm_dict = {
        "matrix": cm_array.tolist(),
        "labels": class_names,
    }

    return {
        "has_test_evaluation": True,
        "test_metrics": {k: round(v, 4) if v is not None else None for k, v in test_metrics.items()},
        "confusion_matrix": cm_dict,
        "feature_importances": feature_importances,
        "notes": [f"Evaluated on {len(X_test)} held-out test samples."],
    }
